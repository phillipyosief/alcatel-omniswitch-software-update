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
        time.sleep(2)
        stdin.write("Y\n")
        stdin.flush()
        
        # Kurz warten, um sicherzustellen, dass der Befehl gesendet wurde
        time.sleep(3)
        
        # Versuche, eine kurze Antwort zu lesen, aber erwarte, dass die Verbindung abbricht
        output = ""
        error = ""
        try:
            # Verwende einen Thread-basierten Timeout-Ansatz
            import threading
            import queue
            
            def read_output(stdout, stderr, result_queue):
                try:
                    out = stdout.read().decode()
                    err = stderr.read().decode()
                    result_queue.put((out, err))
                except Exception:
                    result_queue.put(("", ""))
            
            result_queue = queue.Queue()
            read_thread = threading.Thread(target=read_output, args=(stdout, stderr, result_queue))
            read_thread.daemon = True
            read_thread.start()
            read_thread.join(timeout=5)
            
            if not result_queue.empty():
                output, error = result_queue.get()
        except Exception:
            # Erwarteter Fall: Verbindung wird durch Neustart unterbrochen
            pass

        client.close()
        return output, error

    except Exception as e:
        # Bei einem Neustart-Befehl ist es normal, dass die Verbindung abbricht
        # Dies sollte nicht als Fehler gewertet werden
        if "connection" in str(e).lower() or "broken pipe" in str(e).lower():
            return "Reload command sent successfully, connection terminated as expected", ""
        raise RuntimeError(f"SSH Fehler: {e}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            rollback_timeout=dict(type='int', required=True),
            directory=dict(type='str', choices=["working", "running"], required=True),
            release=dict(type='str', choices=["6", "8"], required=True),
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
    command = ""
    if release == "6":
        command = f"reload {directory} rollback-timeout {rollback_timeout}"
    elif release == "8":
        command = f"reload from {directory} rollback-timeout {rollback_timeout}"
    else:
        module.fail_json(msg=f"Unsupported release version: {release}")
    
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
