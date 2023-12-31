<h1>Agent Deployment</h1>
Deploy logging agents to linux hosts over SSH using python. Specifically filebeat, auditbeat, and sysmonforlinux.

deployAgents.py will install/uninstall filebeat and auditbeat correctly during my testing on an Ubuntu 22.04 VM as well as a Centos 7 VM
Installing/Uninstalling sysmonforlinux works correctly on Ubuntu 22.04 but is missing dependencies for the Centos 7 deployment.
<br><br>
<a href="https://masonbrott.github.io/AgentDeployment/"><strong>DOCS LOCATED HERE</strong></a> <br>

<h3>Installation</h3>

You can install this repo locally using one of two methods:

- Clicking on "code" and downloading the zip

  - This will require separately downloading the filebeat and auditbeat executables and placing them within the correct directories

- Installing "git-lfs" and running `git lfs clone`

  - This will download all of the files correctly

<h3>File Structure</h3>

```
-- agent

        |-- deployAgents.py
    
        |-- auditbeat
    
        |-- filebeat
    
        |-- sysinternalsEBPF
    
        |-- sysmon
```
        

<h3>Usage</h3>

        python3 deployAgents.py <action> <agent/s> -u <user> -t <target-list>

- action  
        Choose from either install or uninstall
- agent <br>
        Choose filebeat, auditbeat, sysmon, or a combination of these seperated by a space
- -u --user <br>
        Give the username that will be used on the remote machines
- -t --target-list <br>
        Give the path to a target list with containing a list of hosts one per line

<h3>Considerations</h3>
- deployagents.py relies on the folders for the agents being in the same directory as the script <br>
- The working dir for the script as I have it set up is /home/(--localuser--)/agent/ where agent houses the script and all of the agent files <br>
- The current configs being shipped with these agents are not set to call back to any specific elastic database or logstash pipeline <br>
