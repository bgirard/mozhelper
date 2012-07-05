#o $MOZ/bin/bash

if [ -d ~/mozhelper/path ] ; then
  PATH="$PATH:"$(echo ~/mozhelper/path)
  export MOZHELPER_LOCATION=$(echo ~/mozhelper/)
fi

