#!/bin/bash

function error {
      echo "Error:" $1
      exit
}


# Check git
type port >/dev/null 2>&1 || {
    error "Port is not installed: http://www.macports.org/install.php"
}

echo "Password required to install dependencies"
set -o verbose
sudo port sync
sudo port install mercurial libidl autoconf213 yasm
