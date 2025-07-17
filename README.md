# Alcatel OmniSwitch Software Update Ansible Role
> Automated software update management for Alcatel-Lucent OmniSwitch devices (AOS6/AOS8)

[![Ansible Galaxy](https://img.shields.io/ansible/role/d/phillipyosief/alcatel-omniswitch-software-update)](https://galaxy.ansible.com/ui/standalone/roles/phillipyosief/alcatel-omniswitch-software-update/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Ansible role provides safe and automated software updates for Alcatel-Lucent OmniSwitch devices running AOS6 and AOS8. It supports firmware, FPGA, and U-Boot updates with comprehensive safety checks, rollback protection, and state validation. The role includes built-in error handling, virtual chassis support, and extensive logging capabilities to ensure reliable network infrastructure updates. Name
> Short blurb about what your product does.


[\[!\[Downloads Stats\]\[npm-downloads\]\]\[npm-url\]](https://img.shields.io/ansible/role/d/phillipyosief/alcatel-omniswitch-software-update)

One to two paragraph statement about your product and what it does.

![](header.png)

## Installation

### Requirements

- Ansible 2.1 or higher
- Python 3.6 or higher
- Network access to Alcatel OmniSwitch devices
- Administrative credentials for target switches

### Install from Ansible Galaxy

```sh
ansible-galaxy install phillipyosief.alcatel-omniswitch-software-update
```

### Install Required Collections

```sh
ansible-galaxy collection install alcatel.aos8
ansible-galaxy collection install ansible.netcommon
```

### Install Python Dependencies

```sh
pip install paramiko textfsm
```

## Usage Example

### Basic Firmware Update

```yaml
---
- name: Update Alcatel OmniSwitch Firmware
  hosts: alcatel_switches
  gather_facts: no
  vars:
    omniswitch_username: "admin"
    omniswitch_password: "switch"
    firmware_files:
      - "/path/to/OS6360_firmware_8.10.115.R01.img"
    backup_chassis_state_folder: "./backups"
    
  roles:
    - phillipyosief.alcatel-omniswitch-software-update
```

### Complete Software Update (Firmware + FPGA + U-Boot)

```yaml
---
- name: Complete Software Update
  hosts: alcatel_switches
  gather_facts: no
  vars:
    firmware_files:
      - "/path/to/firmware.img"
    fpga_files:
      - "/path/to/fpga.img"
    uboot_files:
      - "/path/to/uboot.img"
    backup_chassis_state_folder: "./backups"
    rollback_timeout: 30
    wait_for_timeout: 900
    
  roles:
    - phillipyosief.alcatel-omniswitch-software-update
```

_For more examples and usage, please refer to the [Wiki](https://github.com/phillipyosief/alcatel-omniswitch-software-update/wiki)._

## Features

- ✅ **Safe Updates**: Comprehensive safety checks before updates
- ✅ **Rollback Protection**: Automatic rollback on update failure
- ✅ **Multi-Component**: Supports firmware, FPGA, and U-Boot updates
- ✅ **AOS6/AOS8 Support**: Compatible with both AOS versions
- ✅ **Virtual Chassis**: Full support for virtual chassis configurations
- ✅ **State Validation**: Chassis state comparison before/after updates
- ✅ **File Management**: Automatic upload and cleanup of firmware files
- ✅ **Error Handling**: Comprehensive error detection and reporting

## Testing

```sh
# Syntax check
ansible-playbook --syntax-check update-playbook.yml

# Dry run (check mode)
ansible-playbook -i inventory.ini update-playbook.yml --check

# Run actual update
ansible-playbook -i inventory.ini update-playbook.yml
```

## Author & License

**Phillip Jerome Yosief** – [@phillipyosief](https://github.com/phillipyosief) – phillip.yosief@stadt-frankfurt.de

Distributed under the MIT license. See `LICENSE` for more information.

- **GitHub Repository**: [https://github.com/phillipyosief/alcatel-omniswitch-software-update](https://github.com/phillipyosief/alcatel-omniswitch-software-update)
- **Ansible Galaxy**: [https://galaxy.ansible.com/ui/standalone/roles/phillipyosief/alcatel-omniswitch-software-update](https://galaxy.ansible.com/ui/standalone/roles/phillipyosief/alcatel-omniswitch-software-update/)
- **Documentation**: [Wiki](https://github.com/phillipyosief/alcatel-omniswitch-software-update/wiki)

## Contributing

1. Fork it (<https://github.com/phillipyosief/alcatel-omniswitch-software-update/fork>)
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a new Pull Request

## Support

- 📖 [Documentation Wiki](https://github.com/phillipyosief/alcatel-omniswitch-software-update/wiki)
- 🐛 [Report Issues](https://github.com/phillipyosief/alcatel-omniswitch-software-update/issues)
- 💬 [Discussions](https://github.com/phillipyosief/alcatel-omniswitch-software-update/discussions)

<!-- Markdown link & img dfn's -->
[wiki]: https://github.com/phillipyosief/alcatel-omniswitch-software-update/wiki
