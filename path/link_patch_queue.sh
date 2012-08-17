cp -r .hg/patches-$(hg qqueue --active) ~/Dropbox/patches/ && {
  echo "Copied patches to dropbox"
  ln -s ~/Dropbox/patches/patches-$(hg qqueue --active) .hg/patches-$(hg qqueue --active)-$HOSTNAME && {
    echo "Link created"
    echo $(hg qqueue --active)-$HOSTNAME >> .hg/patches.queues
  }
}
