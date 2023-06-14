"""
This script allows you to install or install either filebeat, auditbeat, sysmon, or a combination of these agents
to a list of linux hosts identified by the target list.
The agents are pushed using scp/ssh wrapped in python subprocess.Popen()
Agents are installed as services on the remote hosts and the systemd unit files are created on the fly in the script and sent with the agent package.
"""

import argparse
import subprocess
from getpass import getpass, getuser

__author__ = "Mason Brott"

# Set up command line parameters using argparse
class uniqueappendaction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        unique_values = set(values)
        setattr(namespace, self.dest, unique_values)

# Defines the argument parser
parser = argparse.ArgumentParser(
    prog="Agent Deployer",
    description="Deploy agents to any target over SSH"
)
# Add argument for install or uninstall
parser.add_argument("action",
                    action='store',
                    choices=['install', 'uninstall'],
                    help='Either install or uninstall your agents.')

# Add argument for agent type
parser.add_argument("program",
                    action=uniqueappendaction,
                    choices=['filebeat', 'auditbeat', 'sysmon'],
                    nargs='+',
                    help='Select agents to install or uninstall.')

# Add argument for username to be used for remote systems
parser.add_argument("-u", "--user",
                    action="store",
                    help="Username for target systems")

# Add argument for target list. Should be path to a file containing one host per line
parser.add_argument("-t", "--target-list",
                    action="store", 
                    help="File containing list of targets to run on. One on each line")

args = parser.parse_args()

# Keep the values of params passed in so we can use them
action = args.action
program = list(args.program)
user = args.user
# Use getuser() to get user who ran the script. Used to find home directory
localuser = getuser()
# Use getpass() to get password more securely
pw = getpass("Password for target machines: ")
target_list = args.target_list

# Grab contents of the target list
with open (target_list, "r") as file:
    targets = file.read().splitlines()

# Initialize request array
requests = []

# Set up our SSH request structure
for target in targets:
    requests.append(user + "@" + target)

# Defining the function for filebeat install/uninstalls
def filebeat(action, requests):
    # Setting up the installation of filebeat
    if action == 'install':
        
        response = []

        # Creates the systemd unit file that will be used for the filebeat service
        unit = ["[Unit]\n",
                "Description=Filebeat\n",
                "After=network.target\n",
                "[Service]\n",
                "ExecStart=/usr/share/filebeat/filebeat --path.config /usr/share/filebeat/\n",
                "Restart=always\n",
                "User=root\n",
                "RestartSec=3\n", "\n",
                "[Install]\n",
                "WantedBy=multi-user.target\n"]
        try:
            with open("/home/" + localuser + "/agent/filebeat/filebeat.service", "w+") as serviceFile:
                serviceFile.writelines(unit)
        except IOError as e:
            print("File can not be opened. Make sure file is not already in use.")
            SystemExit
        
        # Set of commands that need to be run on the remote machine
        # Adding "-S" to sudo allows for password to be read from standardin
        commands = [("sudo -S mkdir /usr/share/filebeat"),
                    ("sudo -S tar -xf /tmp/filebeat.tar -C /usr/share/"),
                    ('sudo -S chown -R root:root /usr/share/filebeat'),
                    ('sudo -S mv /usr/share/filebeat/filebeat.service /etc/systemd/system/filebeat.service'),
                    ('sudo -S systemctl daemon-reload'),
                    ('sudo -S systemctl start filebeat'),
                    ('sudo -S systemctl enable filebeat')
                    ]
        
        # Creating the tar file to be copied over to the remote machines
        with (subprocess.Popen(['tar', '-cf', 'filebeat.tar', 'filebeat'])) as tar:
            print("filebeat.tar created")

        # Iterate over each host in the target list
        for request in requests:
            try:
                ip = request.split("@")

                # Copying the tar file to remote host using scp
                with subprocess.Popen(['sshpass', '-p', str(pw), 'scp', '-T', '-o', 'StrictHostKeyChecking=no', ('/home/' + localuser + '/agent/filebeat.tar'), (request + ':/tmp/')]) as scp:
                    print("Copying filebeat.tar to " + ip[1])
                
                print("Installing filebeat on " + ip[1])

                # Iterate over each command that will need to be run
                for command in commands:
                    if "sudo" in command:
                        # Run the command through ssh
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            # Write the password given through stdin to your command
                            process.stdin.write((pw + "\n").encode())
                            process.stdin.flush()
                            while True:
                                # Capturing response from stdout if that functionality is needed in a later iteration of the script
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                    
                    # Same as above but without sudo. Not currently being used.
                    else:
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            while True:
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                print("Finished installing filebeat")
            except Exception as e:
                print("There was an error while running: " + e)
                print("Error on host: " + ip)
                pass

        with (subprocess.Popen(['rm', 'filebeat.tar'])):
            pass
        
    # Setting up the uninstall/removal of filebeat
    elif action == 'uninstall':

        response = []

        # Set of commands that need to be run on the remote machine
        # Adding "-S" to sudo allows for password to be read from standardin
        commands = [("sudo -S systemctl stop filebeat"),
                    ("sudo -S rm /etc/systemd/system/filebeat.service"),
                    ("sudo -S rm -rf /usr/share/filebeat"),
                    ("sudo -S rm /tmp/filebeat.tar"),
                    ("sudo -S systemctl daemon-reload")
                    ]

        # Iterate over each host in the target list
        for request in requests:
            try:
                ip = request.split("@")
                print('Uninstalling filebeat on ' + ip[1])

                # Iterate over each command that will need to be run
                for command in commands:
                        # Run the command through ssh
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            # Write the password given through stdin to your command
                            process.stdin.write((pw + "\n").encode())
                            process.stdin.flush()
                            while True:
                                # Capturing response from stdout if that functionality is needed in a later iteration of the script
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                print("Done uninstalling filebeat")
            except Exception as e:
                print("There was an error while running: " + e)
                print("Error on host: " + ip)
                pass

# Defining the function for auditbeat install/uninstalls
def auditbeat(action, requests):
    # Setting up the install of auditbeat
    if action == 'install':
        
        response = []

        # Creates the systemd unit file that will be used for the auditbeat service
        unit = ["[Unit]\n",
                "Description=Auditbeat\n",
                "After=network.target\n",
                "[Service]\n",
                "ExecStart=/usr/share/auditbeat/auditbeat run -c /usr/share/auditbeat/auditbeat.yml\n",
                "Restart=always\n",
                "User=root\n",
                "RestartSec=3\n", "\n",
                "[Install]\n",
                "WantedBy=multi-user.target\n"]
        
        try:
            with open("/home/" + localuser + "/agent/auditbeat/auditbeat.service", "w+") as serviceFile:
                serviceFile.writelines(unit)
        except IOError as e:
            print("File can not be opened. Make sure file is not already in use.")
            SystemExit
        
        # Set of commands that need to be run on the remote machine
        # Adding "-S" to sudo allows for password to be read from standardin
        commands = [("sudo mkdir /usr/share/auditbeat"),
                    ("sudo -S tar -xf /tmp/auditbeat.tar -C /usr/share/"),
                    ('sudo -S chown -R root:root /usr/share/auditbeat'),
                    ('sudo -S mv /usr/share/auditbeat/auditbeat.service /etc/systemd/system/auditbeat.service'),
                    ('sudo -S systemctl daemon-reload'),
                    ('sudo -S systemctl start auditbeat'),
                    ('sudo -S systemctl enable auditbeat')
                    ]

        # Creating the tar file to be copied over to the remote machines
        with (subprocess.Popen(['tar', '-cf', 'auditbeat.tar', 'auditbeat'])) as tar:
            print("auditbeat.tar created")
        
        # Iterate over each host in the target list
        for request in requests:
            try:
                ip = request.split("@")

                # Copying the tar file to remote host using scp
                with subprocess.Popen(['sshpass', '-p', str(pw), 'scp', '-T', '-o', 'StrictHostKeyChecking=no', ('/home/' + localuser + '/agent/auditbeat.tar'), (request + ':/tmp/')]) as scp:
                    print("Copying auditbeat.tar to " + ip[1])
                
                print("Installing auditbeat on " + ip[1])

                # Iterate over each command that will need to be run
                for command in commands:
                    if "sudo" in command:
                        # Run the command through ssh
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            # Write the password given through stdin to your command
                            process.stdin.write((pw + "\n").encode())
                            process.stdin.flush()
                            while True:
                                # Capturing response from stdout if that functionality is needed in a later iteration of the script
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                    
                    # Same as above but without sudo. Not currently being used.
                    else:
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            while True:
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                print("Finished installing auditbeat")
            except Exception as e:
                print("There was an error while running: " + e)
                print("Error on host: " + ip)
                pass

        with (subprocess.Popen(['rm', 'auditbeat.tar'])):
            pass

    # Setting up the uninstall/removal of auditbeat
    elif action == 'uninstall':
        response = []

        # Set of commands that need to be run on the remote machine
        # Adding "-S" to sudo allows for password to be read from standardin
        commands = [("sudo -S systemctl stop auditbeat"),
                    ("sudo -S rm /etc/systemd/system/auditbeat.service"),
                    ("sudo -S rm -rf /usr/share/auditbeat"),
                    ("sudo -S rm /tmp/auditbeat.tar"),
                    ("sudo -S systemctl daemon-reload")
                    ]

        # Iterate over each host in the target list         
        for request in requests:
            try:
                ip = request.split("@")
                print('Uninstalling auditbeat on ' + ip[1])
                # Iterate over each command that will need to be run
                for command in commands:
                        # Run the command through ssh
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            # Write the password given through stdin to your command
                            process.stdin.write((pw + "\n").encode())
                            process.stdin.flush()
                            while True:
                                # Capturing response from stdout if that functionality is needed in a later iteration of the script
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                print("Done uninstalling auditbeat")
            except Exception as e:
                print("There was an error while running: " + e)
                print("Error on host: " + ip)
                pass

# Defining the function for sysmon install/uninstalls
# No unit file needed as sysmon installs itself as a service by default
def sysmon(action, requests):
    # Setting up the install of sysmon
    if action == 'install':

        response = []
        
        # Set of commands that need to be run on the remote machine
        # Adding "-S" to sudo allows for password to be read from standardin
        commands = [("sudo -S mkdir /opt/sysinternalsEBPF"),
                    ("sudo -S mkdir /opt/sysmon"),
                    ("sudo -S tar -xf /tmp/ebpf.tar -C /opt/"),
                    ('sudo -S chown -R root:root /opt/sysinternalsEBPF'),
                    ("sudo -S /opt/sysinternalsEBPF/libsysinternalsEBPFinstaller -i"),
                    ("sudo -S tar -xf /tmp/sysmon.tar -C /opt/"),
                    ('sudo -S chown -R root:root /opt/sysmon'),
                    ('sudo -S /opt/sysmon/sysmon -i /opt/sysmon/main.xml')
                    ]

        # Creating the tar file to be copied over to the remote machines
        # Sysmon needs to have the "sysinternalsEBPF" folder copied as well due to dependencies involved
        # So two tar files are being created
        with (subprocess.Popen(['tar', '-cf', 'ebpf.tar', 'sysinternalsEBPF'])) as tar:
            pass
        
        with (subprocess.Popen(['tar', '-cf', 'sysmon.tar', 'sysmon'])) as tar:
            print("sysmon.tar created")

        # Iterate over each host in the target list
        for request in requests:
            try:
                ip = request.split("@")

                # Copying the tar files (ebpf dependencies and sysmon) to remote host using scp
                with subprocess.Popen(['sshpass', '-p', str(pw), 'scp', '-T', '-o', 'StrictHostKeyChecking=no', ('/home/' + localuser + '/agent/ebpf.tar'), (request + ':/tmp/')]) as scp:
                    pass

                with subprocess.Popen(['sshpass', '-p', str(pw), 'scp', '-T', '-o', 'StrictHostKeyChecking=no', ('/home/' + localuser + '/agent/sysmon.tar'), (request + ':/tmp/')]) as scp:
                    print("Copying sysmon.tar to " + ip[1])
                
                print("Installing sysmon on " + ip[1])

                # Iterate over each command that will need to be run
                for command in commands:
                    if "sudo" in command:
                        # Run the command through ssh
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            # Write the password given through stdin to your command
                            process.stdin.write((pw + "\n").encode())
                            process.stdin.flush()
                            while True:
                                # Capturing response from stdout if that functionality is needed in a later iteration of the script
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                    
                    # Same as above but without sudo. Not currently being used.
                    else:
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            while True:
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                print("Finished installing sysmon")
            except Exception as e:
                print("There was an error while running: " + e)
                print("Error on host: " + ip)

        with (subprocess.Popen(['rm', 'sysmon.tar'])):
            pass
        
        with (subprocess.Popen(['rm', 'ebpf.tar'])):
            pass

    # Setting up the uninstall/removal of sysmon
    elif action == 'uninstall':

        response = []

        # Set of commands that need to be run on the remote machine
        # Adding "-S" to sudo allows for password to be read from standardin
        commands = [("sudo -S systemctl stop sysmon"),
                    ("sudo -S /opt/sysinternalsEBPF/libsysinternalsEBPFinstaller -u"),
                    ("sudo -S /opt/sysmon -u force"),
                    ("sudo -S rm /etc/systemd/system/sysmon.service"),
                    ("sudo -S rm -rf /opt/sysinternalsEBPF"),
                    ("sudo -S rm -rf /opt/sysmon"),
                    ("sudo -S rm /tmp/ebpf.tar"),
                    ("sudo -S rm /tmp/sysmon.tar"),
                    ("sudo -S systemctl daemon-reload")
                    ]

        # Iterate over each host in the target list  
        for request in requests:
            try:
                ip = request.split("@")
                print('Uninstalling sysmon on ' + ip[1])
                # Iterate over each command that will need to be run
                for command in commands:
                        # Run the command through ssh
                        with subprocess.Popen(['sshpass', '-p', str(pw), 'ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-t', request, command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                            # Write the password given through stdin to your command
                            process.stdin.write((pw + "\n").encode())
                            process.stdin.flush()
                            while True:
                                # Capturing response from stdout if that functionality is needed in a later iteration of the script
                                response.append(process.stdout.readline().decode('ascii').strip())
                                break
                print("Done uninstalling sysmon")
            except Exception as e:
                print("There was an error while running: " + e)
                print("Error on host: " + ip)

# Basic logic that will set the different functions in motion
# Will run the install or uninstall portion of each function given
# In the "program" command line parameter
try:
    for prog in program:   
        if prog == "filebeat":
            filebeat(action, requests)
        elif prog == "auditbeat":
            auditbeat(action, requests)
        elif prog == "sysmon":
            sysmon(action, requests)
except KeyboardInterrupt:
    print("\nExiting")
    SystemExit
