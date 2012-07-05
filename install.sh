#!/bin/bash
function error {
    echo "Error:" $1
    exit
}

# Check git
type git >/dev/null 2>&1 || { 
  error "Git is not installed"
}

[ -d ~/mozhelper ] >/dev/null 2>&1 && {
  read -p "mozhelper is already installed, would you like to clobber your installation and reinstall a fresh copy? [y/n] " yn
  [ "$yn" != "n" ] && {
    files=$(find ~/mozhelper | wc -l)
    rm -rf ~/mozhelper
    echo "Deleted $files files"
  }
}

# Clone mozhelper
[ ! -d ~/mozhelper ] >/dev/null 2>&1 && { 
  git clone https://github.com/bgirard/mozhelper ~/mozhelper || {
    error "Could not clone ~/mozhelper"
  }
}

# PWD=mozhelper
cd ~/mozhelper

# Update mozhelper
git pull || {
  error "Failed to update mozhelper"
}

# Source mozhelper
grep "source ~/mozhelper/bash_source.sh" ~/.bash_profile >/dev/null 2>&1 || {
  cat >> ~/.bash_profile <<EOF

# Source mozhelper utilies to your path
source ~/mozhelper/bash_source.sh

EOF
}

