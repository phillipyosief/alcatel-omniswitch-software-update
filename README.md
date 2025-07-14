# Alcatel OmniSwitch Software Update Role

Ansible role for automated software updates of Alcatel-Lucent OmniSwitch devices (AOS6/AOS8).

## Requirements

- Ansible >= 2.1
- Python 3.6+
- Alcatel AOS Collection (`alcatel.aos8`)
- Paramiko library

## Role Variables

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `omniswitch_username` | `"admin"` | Switch username |
| `omniswitch_password` | `"switch"` | Switch password |
| `textfsm_folder` | `"{{ role_path }}/textfsm/"` | TextFSM templates path |
| `rollback_timeout` | `15` | Rollback timeout in minutes |
| `directory` | `working` | Target directory (working/running) |

### Runtime Variables

| Variable | Description |
|----------|-------------|
| `release` | Detected AOS version (R6/R8) |
| `model_name` | Switch model name |
| `firmware_version` | Current firmware version |

## Tasks

### `tasks/check_release.yml`
Detects AOS version and sets `release` variable.

### `tasks/get_model_name.yml`
Extracts switch model name and sets `model_name` variable.

### `tasks/get_firmware_version.yml`
Collects firmware information and sets `firmware_version` variable.
- Outputs warnings for inconsistent versions

**Dependencies:** Requires `check_release.yml`

## Custom Modules

### `library/upload_file.py`
**Purpose:** SFTP upload of files to the switch

**Parameters:**
- `host`: Switch IP address
- `port`: SSH port (default: 22)
- `username`: SSH username
- `password`: SSH password
- `remote_path`: Target directory on the switch
- `files`: List of files to upload

**Returns:**
```json
{
  "uploaded": [
    {
      "src": "/path/to/local/file.img",
      "dest": "/flash/file.img",
      "status": "uploaded"
    }
  ]
}
```

**Example:**
```yaml
- name: Upload firmware files
  upload_file:
    host: "{{ ansible_host }}"
    username: "{{ omniswitch_username }}"
    password: "{{ omniswitch_password }}"
    remote_path: "/flash"
    files:
      - "/path/to/firmware.img"
      - "/path/to/boot.img"
```

### `library/reload_switch.py`
**Purpose:** Performs a controlled switch restart

**Parameters:**
- `host`: Switch IP address
- `username`: SSH username
- `password`: SSH password
- `rollback_timeout`: Timeout for automatic rollback
- `directory`: Source directory (working/running)
- `release`: AOS version (R6/R8)

**Behavior:**
- AOS6: `reload {directory} rollback-timeout {timeout}`
- AOS8: `reload from {directory} rollback-timeout {timeout}`
- Automatic confirmation with "Y"

**Example:**
```yaml
- name: Reload switch with rollback
  reload_switch:
    host: "{{ ansible_host }}"
    username: "{{ omniswitch_username }}"
    password: "{{ omniswitch_password }}"
    rollback_timeout: "{{ rollback_timeout }}"
    directory: "{{ directory }}"
    release: "{{ release }}"
```

### `library/reload_cancel.py`
**Purpose:** Cancels a planned restart

**Parameters:**
- `host`: Switch IP address
- `username`: SSH username
- `password`: SSH password

**Example:**
```yaml
- name: Cancel planned reload
  reload_cancel:
    host: "{{ ansible_host }}"
    username: "{{ omniswitch_username }}"
    password: "{{ omniswitch_password }}"
```

## Usage

### Basic Playbook
```yaml
---
- hosts: alcatel_switches
  gather_facts: false
  roles:
    - role: alcatel-omniswitch-software-update
      vars:
        omniswitch_username: "admin"
        omniswitch_password: "mysecretpassword"
        rollback_timeout: 10
```

### Advanced Usage with Host Variables
```yaml
---
- hosts: alcatel_switches
  gather_facts: false
  vars:
    firmware_files:
      - "/firmware/aos8/switch_firmware_8.9.1.img"
      - "/firmware/aos8/switch_boot_8.9.1.img"
  roles:
    - alcatel-omniswitch-software-update
```

### Inventory Example
```ini
[alcatel_switches]
switch01 ansible_host=192.168.1.10
switch02 ansible_host=192.168.1.11

[alcatel_switches:vars]
ansible_connection=network_cli
ansible_network_os=alcatel.aos8.aos8
omniswitch_username=admin
omniswitch_password=switch123
```

## Example Playbooks

### Complete Update Playbook
```yaml
---
- name: Alcatel OmniSwitch Software Update
  hosts: alcatel_switches
  gather_facts: false
  vars:
    firmware_directory: "/opt/firmware/alcatel"
    
  tasks:
    # Gather information
    - include_role:
        name: alcatel-omniswitch-software-update
        tasks_from: get_firmware_version
        
    - include_role:
        name: alcatel-omniswitch-software-update  
        tasks_from: get_model_name
        
    - name: Display current firmware info
      debug:
        msg: |
          Switch: {{ inventory_hostname }}
          Model: {{ model_name }}
          Current Firmware: {{ firmware_version }}
          AOS Release: {{ release }}
    
    # Upload firmware
    - name: Upload firmware files
      upload_file:
        host: "{{ ansible_host }}"
        username: "{{ omniswitch_username }}"
        password: "{{ omniswitch_password }}"
        remote_path: "/flash"
        files:
          - "{{ firmware_directory }}/{{ model_name }}_firmware.img"
          - "{{ firmware_directory }}/{{ model_name }}_boot.img"
      when: firmware_files is defined
      
    # Restart switch
    - name: Reload switch with new firmware
      reload_switch:
        host: "{{ ansible_host }}"
        username: "{{ omniswitch_username }}"
        password: "{{ omniswitch_password }}"
        rollback_timeout: 15
        directory: working
        release: "{{ release }}"
      when: perform_reload | default(false)
```

### Rollback Playbook
```yaml
---
- name: Cancel planned reload
  hosts: alcatel_switches
  gather_facts: false
  
  tasks:
    - name: Cancel reload operation
      reload_cancel:
        host: "{{ ansible_host }}"
        username: "{{ omniswitch_username }}"
        password: "{{ omniswitch_password }}"
```

## Security Notes

- **Password Security:** Use Ansible Vault for passwords
- **Rollback Timeout:** Set appropriate timeouts for automatic rollback
- **Backup:** Always create configuration backups before updates
- **Test Environment:** Test updates in a test environment first

## Troubleshooting

### Common Issues

1. **SSH Connection Errors**
   - Check network connection and SSH access
   - Verify username and password

2. **SFTP Upload Errors**
   - Check available storage space on the switch
   - Verify file permissions

3. **TextFSM Parsing Errors**
   - Ensure TextFSM templates are present
   - Check AOS version detection

## Dependencies

- `alcatel.aos8` - Alcatel AOS8 Ansible Collection
- `ansible.netcommon` - For TextFSM parsing
- `paramiko` - Python SSH library

## Installation

```bash
# Install Ansible Collection
ansible-galaxy collection install alcatel.aos8
ansible-galaxy collection install ansible.netcommon

# Python dependencies
pip install paramiko textfsm
```

## License

MIT

## Contributing

Contributions are welcome! Please create issues or pull requests for improvements.
