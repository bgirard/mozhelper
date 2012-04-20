#!/bin/bash

if [ -d ~/mozhelper/path ] ; then
  PATH="$PATH:"$(echo ~/mozhelper/path)
fi

