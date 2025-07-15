from ansible.module_utils.basic import AnsibleModule
import paramiko
import time

def execute_command(host, username, password, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command)

        # Warten, dann 'Y' bestätigen
        time.sleep(10)
        stdin.write("Y\n")
        stdin.flush()
        time.sleep(10)

        output = stdout.read().decode()
        error = stderr.read().decode()

        client.close()
        return output, error

    except Exception as e:
        raise RuntimeError(f"SSH Fehler: {e}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            rollback_timeout=dict(type='int', required=True),
            directory=dict(type='str', choices=["working", "running"], required=True),
            release=dict(type='str', choices=["R6", "R8"], required=True),
        ),
        supports_check_mode=False
    )

    params = module.params
    host = params['host']
    username = params['username']
    password = params['password']
    rollback_timeout = params['rollback_timeout']
    directory = params['directory']
    release = params['release']

    # Befehl erzeugen
    if release == "6":
        command = f"reload {directory} rollback-timeout {rollback_timeout}"
    elif release == "8":
        command = f"reload from {directory} rollback-timeout {rollback_timeout}"
    
    try:
        output, error = execute_command(host, username, password, command)

        module.exit_json(
            changed=True,
            command=command,
            stdout=output.strip(),
            stderr=error.strip()
        )

    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
