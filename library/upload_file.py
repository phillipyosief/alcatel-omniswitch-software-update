from ansible.module_utils.basic import AnsibleModule
import paramiko
import os

def upload_files(host, port, username, password, remote_path, files):
    results = []

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    for file in files:
        if os.path.isfile(file):
            file_name = os.path.basename(file)
            remote_file_path = os.path.join(remote_path, file_name)
            sftp.put(file, remote_file_path)
            results.append({
                "src": file,
                "dest": remote_file_path,
                "status": "uploaded"
            })
        else:
            results.append({
                "src": file,
                "status": "skipped (not found)"
            })

    sftp.close()
    transport.close()

    return results

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            port=dict(type='int', default=22),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            remote_path=dict(type='str', required=True),
            files=dict(type='list', elements='str', required=True),
        ),
        supports_check_mode=False
    )

    try:
        result = upload_files(
            module.params['host'],
            module.params['port'],
            module.params['username'],
            module.params['password'],
            module.params['remote_path'],
            module.params['files']
        )

        module.exit_json(changed=True, uploaded=result)

    except Exception as e:
        module.fail_json(msg=f"SFTP-Fehler: {str(e)}")

if __name__ == '__main__':
    main()