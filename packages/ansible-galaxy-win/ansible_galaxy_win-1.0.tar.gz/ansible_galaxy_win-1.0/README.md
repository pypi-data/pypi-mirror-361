# ansible-galaxy-win

> Allows use of ansible-galaxy to download a collection on Windows.... **_Sorta?_**

---

## Why?

Look, I get it - I'm not here to judge. We all know you can't use Windows as a Control Node... but sometimes you don't care about having a POSIX compliant fork implementation, and just want to download a collection from a Windows environment - no questions asked. I got you.

### THIS DOES NOT FULLY PORT ANSIBLE (OR ITS GALAXY SUB COMMAND) TO WINDOWS. IT SIMPLY ENABLES THE ABILITY TO DOWNLOAD A COLLECTION AND CALLING ANYTHING OTHER THAN EXECUTE_DOWNLOAD IS UNDEFINED. YOU HAVE BEEN WARNED!

### After installing the wheel, you can use it a few ways:

From the command line:
```text
C:\> pip install ansible-galaxy-win
C:\> ansible-galaxy-win
Calling ansible-galaxy with []
[FAKE_LIBC] Called function: wcwidth
[FAKE_LIBC] Called function: wcswidth
usage: ansible-galaxy [-h] [--version] [-v] TYPE ...
ansible-galaxy: error: the following arguments are required: TYPE

usage: ansible-galaxy [-h] [--version] [-v] TYPE ...

Perform various Role and Collection related operations.

positional arguments:
  TYPE
    collection   Manage an Ansible Galaxy collection.
    role         Manage an Ansible Galaxy role.

options:
  --version      show program's version number, config file location, configured module search path, module location, executable location and exit
  -h, --help     show this help message and exit
  -v, --verbose  Causes Ansible to print more debug messages. Adding multiple -v will increase the verbosity, the builtin plugins currently evaluate up to
                 -vvvvvv. A reasonable level to start is -vvv, connection debugging might require -vvvv. This argument may be specified multiple times.
```
You'll often see some debugging output, which you can ignore. Downloading a collection works as expected:
```text
C:\> ansible-galaxy-win collection download community.general
Calling ansible-galaxy with ['collection', 'download', 'community.general']
[FAKE_LIBC] Called function: wcwidth
[FAKE_LIBC] Called function: wcswidth
[WARNING]: Galaxy cache has world writable access
(C:\Users\goober\.ansible\galaxy_cache\api.json), ignoring it as a cache source.
Process download dependency map
Starting collection download process to 'C:\collections'
Downloading https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/artifacts/community-general-11.0.0.tar.gz to C:\Users\goober\.ansible\tmp\ansible-local-36608wg8dfz1\tmpti2jmnp7\community-general-11.0.0-bwehmf1i
Downloading collection 'community.general:11.0.0' to 'C:\collections'
Collection 'community.general:11.0.0' was downloaded successfully
Writing requirements.yml file of downloaded collections to 'C:\collections\requirements.yml'
```

If you prefer to use it in a scripted scenario, you either use the convenience function:
```python
>>> from ansible_galaxy_win.galaxy_win import execute_download_win
>>> args = ['collection', 'download', '-p', 'C:\\sometestdir\\', 'community.general']
>>> execute_download_win(args)
[FAKE_LIBC] Called function: wcwidth
[FAKE_LIBC] Called function: wcswidth
[WARNING]: Galaxy cache has world writable access
(C:\Users\goober\.ansible\galaxy_cache\api.json), ignoring it as a cache source.
Process download dependency map
Starting collection download process to 'C:\sometestdir'
Downloading https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/artifacts/community-general-11.0.0.tar.gz to C:\Users\goober\.ansible\tmp\ansible-local-29380lauhao81\tmpfe4ozhlq\community-general-11.0.0-qo7ehcuf
Downloading collection 'community.general:11.0.0' to 'C:\sometestdir'
Collection 'community.general:11.0.0' was downloaded successfully
Writing requirements.yml file of downloaded collections to 'C:\sometestdir\requirements.yml'
```

Or you can call the Ansible APIs yourself, just make sure you import `ansible-galaxy-win` FIRST, before importing any other Ansible modules.

## Caution - read the source
> If you just jumped straight into using this code based on the examples above, without reading what it does first, you may have already fucked up. I'm assuming your use case is like mine, and you simply want to download a collection (and not run too much other code.)
> 
> `ansible-galaxy-win` will do some very sketchy patching, so you probably want a dedicated process that just serves to run it, and then die after you have your offline collections.

## FAQs
* Did you vibe code this?
  * Next question
* I'm surprised this works, why don't the Ansible maintainers support it directly?
  * Good question! Try asking your favorite LLM, maybe it will have a better answer. I'll be curious to see how many people would actually use this
* Uh-oh, I ran into an error/issue
  * Awesome, submit a PR and I'll blindly merge it