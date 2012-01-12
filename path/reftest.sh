#!/bin/bash
echo $(cat ~/.config/moz_tree)/$1
make -C $(cat ~/.config/moz_tree)/$1 reftest
