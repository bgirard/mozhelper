#!/bin/bash

set -e
MOZ_TREE=$(cat .config/moz_tree)
cd $MOZ_TREE
make -C $MOZ_TREE package
echo 2

cd dist
echo -n "Install: "
adb install -r fennec*.apk
hash say 2> /dev/null && say "Upload complete"
