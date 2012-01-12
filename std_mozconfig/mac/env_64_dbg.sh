#!/bin/bash
echo "/Users/bgirard/ssd-mozilla/mozilla-central/tree/.mozconfig64dbg" > ~/.config/moz_config
echo "/Users/bgirard/ssd-mozilla/mozilla-central/builds/obj-ff-64dbg/" > ~/.config/moz_tree 
echo $(cat ~/.config/moz_tree)
