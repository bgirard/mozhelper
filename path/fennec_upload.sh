#!/bin/bash

set -e

cd $(cat ~/.config/moz_tree)
make -C $(cat ~/.config/moz_tree) package

cd dist
echo -n "Install: "
adb install -r fennec*.apk
hash say 2> /dev/null && say "Upload complete"
