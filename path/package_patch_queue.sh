tar -C .hg/patches-$(hg qqueue --active) -zcvf patches-$(hg qqueue --active).tar . && {
  echo "Created: " patches-$(hg qqueue --active).tar
}
