#!/bin/bash

set -e
cd $(cat .config/moz_tree)

cd dist
echo -n "Install: "
adb install -r fennec*.apk
