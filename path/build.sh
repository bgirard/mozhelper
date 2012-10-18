#!/bin/bash
export MOZCONFIG=$(cat ~/.config/moz_config)
cd $(dirname ${MOZCONFIG})
echo $MOZCONFIG
echo $PWD
cat $MOZCONFIG
time ./mach build
hash say 2> /dev/null && say "Build complete"
