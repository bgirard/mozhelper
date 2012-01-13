#!/bin/bash

read -p "Enter a configuration name
> " MOZCONFIG_NAME

# Create the builds dir if it does not exist
mkdir -p "$PWD/../builds"

# Set the configuration
echo "$PWD" > ~/.config/moz_tree
echo "$PWD/../builds/mozconfig-$MOZCONFIG_NAME" > ~/.config/moz_config
echo "$PWD/../builds/$MOZCONFIG_NAME/" > ~/.config/moz_objdir

# Write the mozconfig
mozconfig.py 2> "$PWD/../builds/mozconfig-$MOZCONFIG_NAME"
#echo "$MOZCONFIG" > "$PWD/../builds/mozconfig-$MOZCONFIG_NAME"

# Show the configuration
echo $MOZCONFIG_NAME

