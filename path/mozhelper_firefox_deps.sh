#!/bin/bash

function error {
      echo "Error:" $1
      exit
}

[ "$OSTYPE" == "darwin11" ] && {
  "$MOZHELPER_LOCATION"/path/utils/mozhelper_firefox_deps_darwin.sh
  exit
}

error "$OSTYPE is not supported"
