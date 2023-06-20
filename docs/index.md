# Command line arguments

At the start of the script, we're using argparse to handle command-line arguments. This built-in Python module makes it easy to write user-friendly command-line interfaces. The argparse module also automatically generates help and usage messages and throws errors when users provide invalid arguments.

Here's how the arguments are defined and used:

1. `action` - This argument specifies the operation to be performed. It should be either 'install' or 'uninstall', and this determines whether the specified services will be installed or removed from the specified hosts.

2. `program` - This argument is used to list the services that the action will be performed on. Possible values are 'filebeat', 'auditbeat', and 'sysmon'. 

3. `user` - This argument is used to specify the username for authentication on the target machines. This is used along with `target-list` to form the `requests` variable, which is a list of the target hosts in the format username@hostname or username@IP_address.

4. `target-list` - This argument provides a list of target hosts (hostname or IP address) where the services (filebeat, auditbeat, sysmon) will be installed or uninstalled.

The argparse module is utilized as follows:

- `ArgumentParser` is initialized with a description of the script.
- The `add_argument` method is called to specify the command-line options that the program is expecting. In this script, those are '--action', '--program', '--user', and '--target-list'.
- The `parse_args()` method is invoked to transform the arguments given at the command-line into an object with the appropriate attributes.

For instance, if you execute the script with the following command-line arguments:
```
python3 deployAgents.py install filebeat auditbeat --user myuser --target-list targets.txt
```
The variables within the script would hold these values:
- `action = 'install'`
- `program = ['filebeat', 'auditbeat']`
- `user = 'myuser'`
- `target_list = [contents of targets.txt]`

And `requests` list will be created as: `['myuser@host1', 'myuser@host2']` within the script, serving as the list of target hosts in the required format.

Additionally there are two more parameters being captured not using argparse:

1. 'localuser' - This argument is used to specify the username of the user on the local machine, which is running the script. It's used later in the script in constructing the path of the tar files to be copied to the remote machines.
                 This is captured automatically using getuser() from the getpass library.
               
2. 'pw' - The password for the remote user. This is used to run sudo commands on the remote machines.
          This is captured from the terminal after the script starts to run using getpass() from the getpass library
          
# Script Execution

Three functions are used to handle install / uninstall for each agent (one function for each agent type):

1. **`filebeat(action, requests)`** - This function is responsible for installing or uninstalling the `filebeat` service on remote hosts. The service is part of the Elastic stack and is used to send log files to an Elasticsearch instance.

    The function accepts two arguments:
    - `action`: A string that can be either 'install' or 'uninstall'.
    - `requests`: A list of target hosts.

    The 'install' action creates a systemd service unit file for `filebeat`, sets up commands for installing the service on the remote machines, creates a tar file, copies the tar file to each target host, and then runs the installation commands.

    The 'uninstall' action sets up commands for uninstalling the service on the remote machines and runs them on each target host.

    The default config from elastic is currently being shipped this should be changed.

3. **`auditbeat(action, requests)`** - This function is responsible for installing or uninstalling the `auditbeat` service on remote hosts. The service is also part of the Elastic stack and is used for auditing the activities of a system.

    The function accepts two arguments:
    - `action`: A string that can be either 'install' or 'uninstall'.
    - `requests`: A list of target hosts.

    The 'install' action creates a systemd service unit file for `auditbeat`, sets up commands for installing the service on the remote machines, creates a tar file, copies the tar file to each target host, and then runs the installation commands.

    The 'uninstall' action sets up commands for uninstalling the service on the remote machines and runs them on each target host.

    Default config being shipped is from https://github.com/bfuzzy/auditd-attack/tree/master

4. **`sysmon(action, requests)`** - This function is responsible for installing or uninstalling the `sysmon` service on remote hosts. The service is part of the Sysinternals Suite from Microsoft and is used for monitoring and logging system activity to `/var/syslog`.

    The function accepts two arguments:
    - `action`: A string that can be either 'install' or 'uninstall'.
    - `requests`: A list of target hosts.

    The 'install' action sets up commands for installing the service on the remote machines, creates two tar files (one for sysmon and one for its dependencies), copies the tar files to each target host, and then runs the installation commands.

    The 'uninstall' action sets up commands for uninstalling the service on the remote machines and runs them on each target host.

    Default config being shipped is from https://github.com/microsoft/MSTIC-Sysmon/tree/main/linux/configs

5. Lastly, there is a try-except block that calls the appropriate function based on the values of the `program` and `action` variables, and handles a keyboard interrupt exception.

Note: Each function uses the subprocess module to run shell commands and SSH commands for copying files and executing commands on the remote hosts. The sshpass command is used to provide the password for SSH connections.
