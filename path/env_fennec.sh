#!/bin/bash

MOZ_CONFIG=.mozconfigfennec
MOZ_OBJDIR=obj-ff-fennec

[ -z $MOZHELPER_NDK ] && {
  echo "MOZHELPER_NDK not set"
  exit
}

[ -z $MOZHELPER_SDK ] && {
  echo "MOZHELPER_SDK not set"
  exit
}

cat << EOF > $MOZ_CONFIG
# Add the correct paths here:
ac_add_options --with-android-ndk="$MOZHELPER_NDK"
ac_add_options --with-android-sdk="$MOZHELPER_SDK"
ac_add_options --with-android-version=9
ac_add_options --with-android-gnu-compiler-version=4.6

# android options
ac_add_options --enable-application=mobile/android
ac_add_options --target=arm-linux-androideabi
ac_add_options --enable-tests
ac_add_options --with-ccache
ac_add_options --enable-optimize
ac_add_options --enable-profiling
ac_add_options --enable-gtest
ac_add_options --disable-elf-hack
ac_add_options --disable-crashreporter
ac_add_options --disable-jemalloc

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/../builds/$MOZ_OBJDIR
mk_add_options MOZ_MAKE_FLAGS="-j10"

#STRIP_FLAGS="--strip-debug"

# clang complete
#CC='~/.visafsam/bin/cc_args.py gcc'
#CXX='~/.visdfm/bin/cc_args.py g++'
EOF

MOZ_TREE=$(PWD)
MOZ_BUILD=$(cd .. && pwd)/builds/$MOZ_OBJDIR/

mkdir .config 2> /dev/null

echo "$MOZ_TREE/$MOZ_CONFIG" > .config/moz_config
echo $MOZ_BUILD > .config/moz_tree
echo $(cat .config/moz_tree)
