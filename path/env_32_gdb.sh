#!/bin/bash

MOZ_CONFIG=.mozconfig32gdb
MOZ_OBJDIR=obj-ff-32gdb

cat << EOF > $MOZ_CONFIG
. \$topsrcdir/browser/config/mozconfig
mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/../builds/obj-ff-32gdb
mk_add_options MOZ_MAKE_FLAGS="-w -s -j4"
mk_add_options AUTOCONF=autoconf213
#ac_add_options --disable-tests
ac_add_options --disable-optimize
ac_add_options --disable-debug
ac_add_options --enable-profiling
#Don't do this, see: https://developer.mozilla.org/en/Building_Firefox_with_Debug_Symbols
#ac_add_options --enable-optimize
export MOZ_DEBUG_SYMBOLS=1
ac_add_options --enable-debug-symbols="-gdwarf-2"
ac_add_options --disable-install-strip
ac_add_options --disable-crashreporter

# Compile 32-bit
CC="gcc-4.2 -arch i386 -DDEBUG_COREANIMATION"
CXX="g++-4.2 -arch i386 -DDEBUG_COREANIMATION"
export CFLAGS="-gdwarf-2"
export CXXFLAGS="-gdwarf-2"

ac_add_options --target=i386-apple-darwin9.2.0
ac_add_options --enable-macos-target=10.5
# bug 491774. crashreporter won't build in cross compile
ac_add_options --disable-crashreporter

HOST_CC="gcc-4.2 -DDEBUG_COREANIMATION"
HOST_CXX="g++-4.2 -DDEBUG_COREANIMATION"
RANLIB=ranlib
AR=ar
AS=$CC
LD=ld
STRIP="strip -x -S"
CROSS_COMPILE=1
EOF

MOZ_TREE=$(PWD)
MOZ_BUILD=$(cd .. && pwd)/builds/$MOZ_OBJDIR/

mkdir .config 2> /dev/null

echo "$MOZ_TREE/$MOZ_CONFIG" > .config/moz_config
echo $MOZ_BUILD > .config/moz_tree
echo $(cat .config/moz_tree)
