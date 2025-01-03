#!/bin/bash

#   This script expects /mnt to be the root disk and /mnt/boot/efi to be the 
#   mounted esp partition. it runs some basic setup to prepare for decman. Everything
#   else is configured by decman.

root="/mnt"
cwd=$(pwd)
esp="$root/boot/efi"
pacstrap="/usr/bin/pacstrap"
chroot="/usr/bin/arch-chroot"
deps=false
tombl_vers="0.2.3"
tombl_url="https://github.com/snyball/tombl/releases/download/v$tombl_vers/tombl-v$tombl_vers.tar.gz"

# base-devel and git are required for the script to correctly bootstrap a decman config
pacstrap_packages="base base-devel linux linux-headers linux-firmware git python python-toml python-deepdiff "


while [ "$#" -gt 0 ]; do
case "$1" in
    -h|--help) 
    echo """Usage ./setup.sh [OPTIONS]
Options:
    -h, --help              Displays this help message
    -r, --root=DIR          sets root to DIR
    -P, --assume-pacstrap   Assumes pacstrap already ran"""; exit 1;;
    -r) root="$2";shift 2;;
    --root=*) root="${1#*=}"; shift 1;;
    -P|--assume-pacstrap) pacstrap_ran=true; shift 1;;
    *) echo "$1 is not a known option. ignoring"; shift 1;;
esac
done

if [ ${cwd: -11} != "ArchDeclare"]
    echo "We aren't running in the root of the git repo. Please cd into it or rename it to \"ArchDeclare\""
    exit 1
fi

if [ -d "$root" ]
    echo "The root partition not mounted or doesn't exist. Please check $root exists and the filesystem is mounted"
    exit 1
fi

if [ -d "$efi" ]
    echo "The efi partition not mounted or doesn't exist. Please check $efi"
    exit 1
fi

if [ -d "$pacstrap" ] && [ $pacstrap_ran != true]
    echo "Couldn't find pacstrap. Please check your install"
    exit 1
fi

if [ $pacstrap_ran != true ]
    $pacstrap -k $pacstrap_packages
    genfstab -U $root >> $root/etc/fstab
fi

if [ -d "$chroot" ]
    fallback_chroot=true
    echo "can't find arch-chroot. check if it is installed"
    exit 1
fi

# Create known builder user
$chroot /mnt useradd -m builder
# Copy this directory to it's final location
cp . $root/etc/ArchDeclare

#temporarily give builder sudo priviledges without need for password
$chroot /mnt echo "builder ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers
$chroot -u builder /mnt bash -c '
cd /home/builder
git clone "https://github.com/kiviktnm/decman-pkgbuild.git"
cd decman-pkgbuild
makepkg -si
'

#Remove builder user and its sudo priviliges
$chroot /mnt userdel -r builder
$chroot /mnt sed -n 's/builder ALL=(ALL:ALL) NOPASSWD: ALL/' /etc/sudoers

$chroot /mnt decman --source /etc/ArchDeclare/source.py

echo "Install complete. please chroot into the environment and set user and root passwords with passwd to finish your install then restart"
