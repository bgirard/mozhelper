#!/bin/sh

name=$1

if [ $# -ne 1 ]
then
    name=org.mozilla.fennec_$USER
    echo "  $0 $name"
fi

p=`adb shell ps | grep $name | awk '{print $2}'`
if [ "$p" = "" ];
then
    echo "ERROR: That doesn't seem to be a running process. Please make sure your"
    echo "application has been started and that you are using the correct"
    echo "namespace argument."
    exit
fi

adb shell run-as $name kill $p
