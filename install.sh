#!/bin/bash
function error {
    echo "Error:" $1
}

# Check git
type git >/dev/null 2>&1 || { 
  error "Git is not installed"
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
grep "source ~/mozhelper/bash_source.sh" ~/.bash_profile || {
  cat >> ~/.bash_profile <<EOF

# Source mozhelper utilies to your path
source ~/mozhelper/bash_source.sh

EOF
}

