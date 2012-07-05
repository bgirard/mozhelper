CURR_DUR$PWD
echo .hg/patches-$(hg qqueue --active)
tar -C .hg/patches-$(hg qqueue --active) -zxvf patches-$(hg qqueue --active).tar . 
