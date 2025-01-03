import toml
import decman
from UserManager import UserManager

CONFIG="./decman.toml"
decman.modules += [UserManager()]

# These functions convert TOML tables to decman Files/Directories/UserPackages.

def toml_to_decman_file(toml_dict) -> decman.File:
    return decman.File(content=toml_dict.get("content"),
                       source_file=toml_dict.get("source_file"),
                       bin_file=toml_dict.get("bin_file", False),
                       encoding=toml_dict.get("encoding", "utf-8"),
                       owner=toml_dict.get("owner"),
                       group=toml_dict.get("group"),
                       permissions=toml_dict.get("permissions", 0o644))


def toml_to_decman_directory(toml_dict) -> decman.Directory:
    return decman.Directory(source_directory=toml_dict["source_directory"],
                            bin_files=toml_dict.get("bin_files", False),
                            encoding=toml_dict.get("encoding", "utf-8"),
                            owner=toml_dict.get("owner"),
                            group=toml_dict.get("group"),
                            permissions=toml_dict.get("permissions", 0o644))

def toml_to_decman_user_package(toml_dict) -> decman.UserPackage:
    return decman.UserPackage(pkgname=toml_dict["pkgname"],
                              version=toml_dict["version"],
                              dependencies=toml_dict["dependencies"],
                              git_url=toml_dict["git_url"],
                              pkgbase=toml_dict.get("pkgbase"),
                              provides=toml_dict.get("provides"),
                              make_dependencies=toml_dict.get("make_dependencies"),
                              check_dependencies=toml_dict.get("check_dependencies"))

def toml_to_decman_user(username,toml_dict):
    groups=toml_dict.get("groups",[])
    shell=toml_dict.get("shell",None)
    home=toml_dict.get("home",None)
    comment=toml_dict.get("comment",None)
    uid=toml_dict.get("uid",None)
    user = {
            "groups":[username]+groups,
            "shell": shell,
            "comment": fullname,
            "home": home,
            "uid":uid
        }
    return user



# Parse TOML into a Python dictionary
toml_source = toml.load(CONFIG)

# Set decman variables using the parsed dictionary.


decman.packages = toml_source.get("packages", [])
decman.aur_packages = toml_source.get("aur_packages", [])
decman.ignored_packages = toml_source.get("ignored_packages", [])
decman.enabled_systemd_units = toml_source.get("enabled_systemd_units", [])
decman.enabled_systemd_user_units = toml_source.get("enabled_systemd_user_units", {})

for filename, toml_file_dec in toml_source.get("files", {}).items():
    decman.files[filename] = toml_to_decman_file(toml_file_dec)

for dirname, toml_dir_dec in toml_source.get("directories", {}).items():
    decman.directories[dirname] = toml_to_decman_directory(toml_dir_dec)

for toml_user_package_dec in toml_source.get("user_packages", []):
    decman.user_packages.append(toml_to_decman_user_package(toml_user_package_dec))

for username, toml_user in toml_source.get("users",{}).items():
    user=toml_to_decman_user(username,toml_user)
    decman.modules.UserManager.add_user(username,
    user["uid"],
    user["shell"],
    user["groups"],
    user["fullname"],
    user["home"])