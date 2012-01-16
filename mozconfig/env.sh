#!/bin/bash
MOZCONFIG_NAME="obj-ff-64gdb"

MOZCONFIG=$( cat <<EOF
. $topsrcdir/browser/config/mozconfig

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/../builds/$MOZCONFIG_NAME
mk_add_options MOZ_MAKE_FLAGS="-w -s -j6"
ac_add_options --disable-tests
ac_add_options --disable-debug
ac_add_options --enable-debug-symbols
ac_add_options --enable-profiling
EOF
)

# Create the builds dir if it does not exist
mkdir -p "$PWD/../builds"

# Set the configuration
echo "$PWD" > ~/.config/moz_tree
echo "$PWD/../builds/mozconfig-$MOZCONFIG_NAME" > ~/.config/moz_config
echo "$PWD/../builds/$MOZCONFIG_NAME/" > ~/.config/moz_objdir

# Write the mozconfig
echo "$MOZCONFIG" > "$PWD/../builds/mozconfig-$MOZCONFIG_NAME"

# Show the configuration
echo $MOZCONFIG_NAME

