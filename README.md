# ArchDeclare
A script to setup arch in a declarative manner using [Decman](https://github.com/kiviktnm/decman)

# Usage
Clone this repo to an installation medium, copy `decman.toml.example` to `decman.toml` and configure to your required setup, mount your partitions and run setup.sh

setup.sh sets up a minimal arch setup, installs decman and runs decman on your config. If any commands need to be run after installing packages you will currently need to run those after setup.sh finished.

# UserManager Decman module
I have included a Decman module to attempt to manage users within decman. The module creates a dictionary based on the `add_user()` `add_group()` and `add_groups()` functions called, and when the module's on_update is called it compares that dictionary to the config in `/etc/UserMan/users.json`. any differences between them will call `useradd` `userdel` and `usermod` as required. Groups managed outside of this module **will not** be tracked.

This module ***DOES NOT*** delete the user home directory or mail spool (`userdel -r`), this admin task is left to the administrator to avoid data loss.

## Manual Module example
```python
import decman
from UserMnaager import UserManager

decman.modules += [UserManager()]

decman.packages = ["base","linux","linux-firmware","sudo"]

decman.modules.UserManager.add_user("Grand",1000,"/bin/bash",["wheel"],"Grand_UK","/home/grand")
decman.modules.UserManager.add_group("Grand","video")
```

## Module Functions
### UserManager.add_user(self,username,uid,shell="/bin/bash",groups=[],fullname="",home=None)
Creates a new user. username and uid are required arguments. default behaviour creates user with no home directory. If run twice the 2nd execution does nothing
### UserManager.add_group(self,username,group)
Add a user to a group. Expects the group to exist
### UserManager.add_groups(self,username,groups)
Adds a user to multiple groups. groups is a python list of groups. Expects all the groups to exist