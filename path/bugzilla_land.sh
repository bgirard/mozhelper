#!/bin/bash
set -e
hg pull -u
PATHID=${1##*=}
wget $1 -O - > patch_$PATHID
echo "Downloaded patch_$PATHID"
hg qimport patch_$PATHID
rm patch_$PATHID
hg qpush
hg qref -e
hg outgoing
read -p "Land now (y/n)?"; [ "$REPLY" == "y" ] && hg qfinish -a && hg push && open https://tbpl.mozilla.org/?tree=Mozilla-Inbound
