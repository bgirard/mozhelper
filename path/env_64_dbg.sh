#!/bin/bash

MOZ_CONFIG=.mozconfig64dbg
MOZ_OBJDIR=obj-ff-64dbg

cat << EOF > $MOZ_CONFIG
. $topsrcdir/browser/config/mozconfig

CC=clang
CXX=clang++

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/../builds/$MOZ_OBJDIR
mk_add_options MOZ_MAKE_FLAGS="-w -s -j8"
#mk_add_options MOZ_MAKE_FLAGS="CC='distcc /usr/bin/gcc' CXX='distcc /usr/bin/g++' -j20"
mk_add_options AUTOCONF=autoconf213
ac_add_options --disable-crashreporter
ac_add_options --enable-tests
ac_add_options --disable-debug
ac_add_options --enable-debug-symbols
#Not an optimize build so don't profile
ac_add_options --enable-profiling
ac_add_options --enable-optimize
ac_add_options --enable-warnings-as-errors
ac_add_options --enable-replace-malloc

#export CC="distcc gcc"
#export CXX="distcc g++"
EOF

MOZ_TREE=$(PWD)
MOZ_BUILD=$(cd .. && pwd)/builds/$MOZ_OBJDIR/

mkdir .config 2> /dev/null

echo "$MOZ_TREE/$MOZ_CONFIG" > .config/moz_config
echo $MOZ_BUILD > .config/moz_tree
echo $(cat .config/moz_tree)
