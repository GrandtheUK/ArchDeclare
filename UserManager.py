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
        groups_updates=False
        group_update_users=[]
        
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

        
        for value in diff.get("values_changed",[]):
            keys = re.findall(r"\['(.*?)'\]", value)
            index = int(re.findall(r"\[(.*?)\]", value)[2])
            # new_value = new_dict.get("new_value")
            new_value = self._users[username][keys[1]][index]
            username = keys[0]
            match keys[1]:
                case "shell":
                    print("new shell for", username,":",dic.get("new_value"))
                    prg(["usermod","-s",new_value,username])
                case "comment":
                    print("new comment for", username,":",new_dict.get("new_value"))
                    prg(["usermod","-c",new_value,username])
                case "uid":
                    print("new uid for", username,":",new_dict.get("new_value"))
                    prg(["usermod","-u",new_value,username])
                case "create-home":
                    print("changed create-home for", username,":",new_dict.get("new_value"))
                    prg(["usermod","-m",new_value,username])
                case "groups":
                    groups_updates=True
                    if username not in group_update_users:
                        group_update_users.append(username)
                case _:
                    print("Something has gone wrong")
                    exit(1)

        
        for value in diff.get("iterable_item_added",[]):
            # matches = re.findall(r"\['(.*?)'\]", value)
            keys = re.findall(r"\['(.*?)'\]", value)
            index = int(re.findall(r"\[(.*?)\]", value)[2])
            # new_value = new_dict.get("new_value")
            username = keys[0]
            new_value = d[username][keys[1]][index]

            match keys[1]:
                case "groups":
                    # group = self._users[keys[0]]["groups"][index]
                    # print("new group for", matchess[0],":",group)
                    # prg(["gpasswd","-a",username,group])
                    groups_updates=True
                    if username not in group_update_users:
                        group_update_users.append(username)

                case _:
                    print("Something has gone wrong")
                    exit(1)
        

        for value in diff.get("iterable_item_removed",[]):
            keys = re.findall(r"\['(.*?)'\]", value)
            index = int(re.findall(r"\[(.*?)\]", value)[2])
            username = keys[0]
            removed_value = [username][keys[1]][index]

            match keys[1]:
                case "groups":
                    # print("removed group for", username,":",removed_value)
                    # prg(["gpasswd","-d",username,removed_value])
                    groups_updates=True
                    if username not in group_update_users:
                        group_update_users.append(username)
                case _:
                    print("Something has gone wrong")
                    exit(1)
        
        # group management
        if (groups_updates):
            for username in group_update_users:
                #groups to remove
                for group in list(set(self._usersprev[username]['groups']) - set(self._users[username]['groups'])):
                    prg(["gpasswd","-d",username,group])
                #groups to add
                for group in list(set(self._userprev[username]['groups']) - set(self._users[username]['groups'])):
                    prg(["gpasswd","-a",username,group])
        
        with open("/etc/UserMan/users.json",'w') as file:
            text=json.dumps(self._users)
            file.write(text)