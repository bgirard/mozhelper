#!/bin/bash
set -e

echo "Build: $(cat .config/moz_tree)"

if [ "$#" == "0" ]
then
  ./fastbuild.sh $(cat .config/moz_tree)
  exit
fi

for i in $*
do
  echo "Building $i"
  echo make -C $(cat .config/moz_tree)/$i
  make -C $(cat .config/moz_tree)/$i #> /dev/null
done

echo "Linking"
make -C $(cat .config/moz_tree)/toolkit/library #> /dev/null

