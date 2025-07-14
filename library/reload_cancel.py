from ansible.module_utils.basic import AnsibleModule
import paramiko
import time

def cancel_reload(host, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)

        command = "reload cancel"
        stdin, stdout, stderr = client.exec_command(command)

        # Warte kurz und bestätige mit "Y"
        time.sleep(5)
        stdin.write("Y\n")
        stdin.flush()
        time.sleep(5)

        output = stdout.read().decode()
        error = stderr.read().decode()

        client.close()

        return output, error

    except Exception as e:
        raise RuntimeError(f"SSH-Fehler: {e}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
        ),
        supports_check_mode=False
    )

    params = module.params
    host = params['host']
    username = params['username']
    password = params['password']

    try:
        output, error = cancel_reload(host, username, password)

        module.exit_json(
            changed=True,
            command="reload cancel",
            stdout=output.strip(),
            stderr=error.strip()
        )

    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
