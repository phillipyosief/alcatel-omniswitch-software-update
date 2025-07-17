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
| `textfsm_folder` | `"textfsm/"` | TextFSM templates path |
| `rollback_timeout` | `15` | Rollback timeout in minutes |
| `directory` | `working` | Target directory (working/running) |
| `no_firmware_update` | `false` | Skip firmware update if true |
| `no_fpga_update` | `false` | Skip FPGA update if true |
| `no_uboot_update` | `false` | Skip U-Boot update if true |

### Required Variables

| Variable | Description |
|----------|-------------|
| `versions_file` | Path to JSON file containing firmware versions |
| `backup_chassis_state_folder` | Directory for chassis state backups |
| `firmware_files` | List of firmware files to upload |
| `fpga_files` | List of FPGA files to upload |
| `uboot_files` | List of U-Boot files to upload |
| `wait_for_timeout` | Timeout for switch availability checks |

### Runtime Variables

| Variable | Description |
|----------|-------------|
| `release` | Detected AOS version (R6/R8) |
| `model_name` | Switch model name |
| `firmware_version` | Current firmware version |
| `fpga_version` | Current FPGA version |
| `uboot_version` | Current U-Boot version |
| `is_switch_safe_to_update` | Boolean indicating if switch is safe to update |
| `is_synchronized` | Boolean indicating if configuration is synchronized |
| `firmware_update_required` | Boolean indicating if firmware update is needed |
| `fpga_update_required` | Boolean indicating if FPGA update is needed |
| `uboot_update_required` | Boolean indicating if U-Boot update is needed |

## Tasks

### Core Tasks

#### `tasks/main.yml`
Main orchestration task that coordinates the complete update process:
- Loads version information from JSON file
- Checks if switch is safe to update
- Determines what updates are required
- Uploads necessary files
- Performs updates with rollback protection
- Validates update success

#### `tasks/check_release.yml`
Detects AOS version and sets `release` variable (R6 or R8).

### Information Gathering Tasks

#### `tasks/get_model_name.yml`
Extracts switch model name using TextFSM parsing and sets `model_name` variable.

#### `tasks/get_firmware_version.yml`
Collects current firmware version from microcode output and sets `firmware_version` variable.

#### `tasks/get_fpga_version.yml`
Extracts FPGA version from hardware-info output and sets `fpga_version` variable.

#### `tasks/get_uboot_version.yml`
Extracts U-Boot version from hardware-info output and sets `uboot_version` variable.

### Safety and Validation Tasks

#### `tasks/is_switch_safe_to_update.yml`
Comprehensive safety check that validates:
- Running directory is WORKING
- Configuration is SYNCHRONIZED  
- Flash between CMMs is synchronized
- No chassis members are Not-Joined or Unassigned
Sets `is_switch_safe_to_update` boolean variable.

#### `tasks/is_switch_synchronized.yml`
Checks if running configuration is synchronized and sets `is_synchronized` variable.

#### `tasks/is_switch_ready.yml`
Waits for switch to be fully operational by checking:
- Network reachability via ping
- All chassis/slots are in UP status
Includes configurable timeout and retry logic.

### State Management Tasks

#### `tasks/save_chassis_state.yml`
Captures current chassis topology state before updates:
- AOS6: Uses `show stack topology`
- AOS8: Uses `show virtual-chassis topology`
Saves output to local backup file.

#### `tasks/compare_chassis_state.yml`
Compares current chassis state with saved backup to detect changes.
Sets `is_chassis_different` boolean variable.

### Update Tasks

#### `tasks/update_fpga.yml`
Performs FPGA updates with version-specific commands:
- AOS8: `update fpga-cpld cmm all file {filename}`
- AOS6: `update fpga ni all`

#### `tasks/update_uboot.yml`
Performs U-Boot updates with version-specific commands:
- AOS8: `update uboot cmm all file {filename}`
- AOS6: `update uboot cmm all`

#### `tasks/write_memory.yml`
Executes `write memory flash-synchro` command for both AOS6 and AOS8.

#### `tasks/delete_update_junk.yml`
Cleans up temporary update files:
- AOS8: Removes `uboot*` and `fpga*` files
- AOS6: Removes `KFfpga.upgrade_kit` file

## Files

### `files/versions.json`
JSON configuration file containing target firmware versions for each switch model:
```json
{
    "OS6360": {
        "uboot": "",
        "fpga": "",
        "firmware": "8.10.115.R01"
    },
    "OS6850": {
        "uboot": "",
        "fpga": "",
        "firmware": "6.4.4.743.R01"
    }
}
```

## Update Process Flow

1. **Pre-Update Validation**
   - Check if switch is safe to update
   - Gather current firmware/FPGA/U-Boot versions
   - Load target versions from JSON file
   - Determine which updates are required

2. **State Backup**
   - Save current chassis topology state

3. **File Upload** 
   - Upload required firmware, FPGA, and U-Boot files via SFTP

4. **Update Execution**
   - Update U-Boot (if required)
   - Update FPGA (if required)
   - Reload switch with rollback timeout

5. **Post-Update Validation**
   - Wait for switch to become unreachable (reboot)
   - Wait for switch to become reachable again
   - Verify chassis state hasn't changed
   - Confirm switch is healthy

6. **Finalization**
   - Cancel planned reload (if validation successful)
   - Write memory flash-synchro
   - Clean up temporary files

## Custom Modules

### `upload_file`
SFTP upload of files to the switch.

**Parameters:**
- `host`: Switch IP address
- `port`: SSH port (default: 22)
- `username`: SSH username
- `password`: SSH password
- `remote_path`: Target directory on the switch
- `files`: List of files to upload

### `reload_switch`
Performs controlled switch reload with rollback protection.

**Parameters:**
- `host`: Switch IP address
- `username`: SSH username
- `password`: SSH password
- `rollback_timeout`: Rollback timeout in minutes
- `directory`: Source directory (working/running)
- `release`: AOS version (R6/R8)

### `reload_cancel`
Cancels a planned reload operation.

**Parameters:**
- `host`: Switch IP address
- `username`: SSH username
- `password`: SSH password

## Usage

### Basic Usage
```yaml
- hosts: alcatel_switches
  vars:
    versions_file: "{{ role_path }}/files/versions.json"
    backup_chassis_state_folder: "/tmp/chassis_backups"
    firmware_files: ["{{ firmware_dir }}/firmware.img"]
    fpga_files: ["{{ firmware_dir }}/fpga.img"]  
    uboot_files: ["{{ firmware_dir }}/uboot.img"]
    wait_for_timeout: 300
  roles:
    - alcatel-omniswitch-software-update
```

## Dependencies

```bash
ansible-galaxy collection install alcatel.aos8
ansible-galaxy collection install ansible.netcommon
pip install paramiko textfsm
```

## License

MIT

## Contributing

Contributions are welcome! Please create issues or pull requests for improvements.
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
