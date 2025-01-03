from decman import Module, prg, sh
from deepdiff import DeepDiff
import pwd, grp, json, re
from json import JSONDecodeError

class UserManager(Module):
    

    def __init__(self):
        super().__init__(name="UserManager", enabled=True, version="1")
        try:
            with open("/etc/UserMan/users.json",'r') as file:
                self._usersprev = json.load(file)
        except JSONDecodeError:
            prg(["mkdir","-p","/etc/UserMan"])
            prg(["touch","/etc/UserMan/users.json"])
            self._usersprev = {}
        self._users = {}


    def on_enable(self):
        prg(["mkdir","-p","/etc/UserMan"])

        print("Decman is now managing users")

    def on_disable(self):
        print("Decman is no longer managing users. You're on your own from here")

    def add_user(self,username,uid,shell="/bin/bash",groups=[],fullname="",home=None):
        username=username.lower()
        users=self._users.items()
        for user,config in users:
            if user==username:
                return
        user = {
            "groups":groups,
            "shell": shell,
            "comment": fullname,
            "home": home,
            "uid":uid
        }
        self._users[username]=user

    def __add_user(self,username,user):
        command = ["useradd","-s",user["shell"]]
        if user["home"]:
            command+=["-m"]
            command+=["-d",user["home"]]
        if len(user["groups"])>0:
            command=command+["-G"]+[",".join(user["groups"])]
        if user["comment"]:
            command+=["-c",user["comment"]]
        if user["uid"]:
            command+=["-u",str(user["uid"])]
        command+=[username]
        print(command)
        prg(command)

    def add_group(self,username,group):
        groups = self._users.get(username,{}).get("groups")
        if group in user.groups:
            return
        # prg(["groupmod","-aG",group,username])

    def __add_group(self,username,group):
        groups = self._users.get(username,{}).get("groups")
        if group in user.groups:
            return
        prg(["groupmod","-aG",group,username])

    def add_groups(self,username,groups):
        for group in groups:
            self.add_group(username,group)
    
    def pacman_packages(self) -> list[str]:
        return ["python", "python-deepdiff"]
    
    def after_update(self):
        # Get difference in configuration.
        diff = DeepDiff(self._usersprev,self._users)
        print(self._users)
        
        for value in diff.get("dictionary_item_added",{}):
            matches = re.findall(r"\['(.*?)'\]", value)
            user = self._users.get(matches[0])
            self.__add_user(matches[0],user)
            print("Added user", matches[0])
            prg(["pkexec","passwd",value])

        
        for value in diff.get("dictionary_item_removed",{}):
            matches = re.findall(r"\['(.*?)'\]", value)
            prg(["userdel",matches[0]])
            print("Removed user", matches[0]+". Manual intervention required for home folder")

        
        for value,new_dict in diff.get("values_changed",[]).items():
            matches = re.findall(r"\['(.*?)'\]", value)
            new_value = new_dict.get("new_value")
            username = matches[0]
            match matches[1]:
                case "shell":
                    print("new shell for", matches[0],":",dic.get("new_value"))
                    prg(["usermod","-s",new_value,username])
                case "comment":
                    print("new comment for", matches[0],":",new_dict.get("new_value"))
                    prg(["usermod","-c",new_value,username])
                case "uid":
                    print("new uid for", matches[0],":",new_dict.get("new_value"))
                    prg(["usermod","-u",new_value,username])
                case "create-home":
                    print("changed create-home for", matches[0],":",new_dict.get("new_value"))
                    prg(["usermod","-m",new_value,username])
                case _:
                    print("Something has gone wrong")
                    exit(1)

        
        for value,group in diff.get("iterable_item_added",[]).items():
            matches = re.findall(r"\['(.*?)'\]", value)
            match matches[1]:
                case "groups":
                    print("new group for", matches[0],":",group)
                    prg(["gpasswd","-a",username,group])
                case _:
                    print("Something has gone wrong")
                    exit(1)

        for value,new_dict in diff.get("iterable_item_removed",[]).items():
            matches = re.findall(r"\[(.*?)\]", value)
            value = new_dict.get("i ")
            match matches[1]:
                case "'groups'":
                    print("removed group for", matches[0],":",item,matches[2])
                    prg(["gpasswd","-d",username,group])
                case _:
                    print("Something has gone wrong")
                    exit(1)
        
        with open("/etc/UserMan/users.json",'w') as file:
            json.dump(self._users,file)