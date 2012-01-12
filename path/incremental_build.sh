#!/bin/bash
set -e

echo "Build: $(cat ~/.config/moz_tree)"

for i in $*
do
  echo "Building $i"
  echo make -C $(cat ~/.config/moz_tree)/$i
  make -C $(cat ~/.config/moz_tree)/$i #> /dev/null
done

echo "Linking"
make -C $(cat ~/.config/moz_tree)/toolkit/library > /dev/null

