# gluedfs
Glued Filesystem - Tag Filesystem in Linux (Gnu-Linux-Unified-Enhanced-Dbtagged )

**GLUEDFS**
Glued Filesystem
Gnu-Linux-Unified-Enhanced-Dbtagged
by gd@linux.it

dependencies: tmsu (https://github.com/oniony/TMSU) , python 2.7, python module fusepy

# HOW TO USE IT
## cmdline only by now
* YOURDIR must be root in cwd Current Working Directory
* command tmsu (bin) must be defined in variable TMSU in gluedfsV_v.py
## you must go this way by now:
*mount:*
## python gluedfs2_6.py YOURDIR mountpoint
*umount:*
## interrupt process or fusermount -u mountpoint (by superuser?)

# HOW IT WORKS
## root_dir is direct access to YOURDIR
- inside root_dir you can do everything as usual, in fact is a loop of YOURDIR
- inside root_dir GLUEDFS puts his DB in .tmsu hidden dir

## tag_dir is is your tags you can create, rename, delete tags and tag/untag items
- tagging items is made by moving from root_dir items to a specific tag in tagdir
- inside tag_dir you can access files or dirs of YOURDIR
- if you delete items in tag_dir you're untagging items, you don't delete items
- if more than one item has same name in one tag others are symbolic
  links to your items in YOURDIR
- you can only tag items in root_dir

## query_dir is is a way to filter your tags
- browse tags and special dir # (and query)
- inside query_dir you can access files or dirs of YOURDIR
- if more than one item has same name in one tag others are symbolic
  links to your items in YOURDIR

# Getting started
- Fill testdir
- check TMSU point to your tmsu bin 
- in a terminal shell execute (pwd same as testdir) : **python gluedfs2_6.py testdir/ mnt_test/**
- leave terminal open
- start using tagging and enjoy **GLUEDFS**

# Other info
- I wrote this because I was bored to search files in filesystem, I wanted to keep order but not 
 change years of organization. Don't bother if you do something wrong in tag_dir or query_dir, you can
  delete files and dir **only** in root_dir, that is a trasparent copy of your-mounted-dir, in 
  tag_dir you can only tag, untag items **nothing else**. 
 - You can only tag files in root_dir not across filesystem. You'll find same name resolved by symlink.
- I wrote it to have some-kind-file-organization transparent to apps but accessible from every
 app. You can easily export your tags or queries to other filesytems by copying them.
 - Some filebrowsers expect something in changing filesystems to optimize their view, simply refresh
  window if something is not as you expected.
- In the example tags begin with **#** e.g. **#tag1, #tag2, #photo** this is my personal convention to 
 distinguish tag from dirs, but it'not mandatory at all. You can choose names as you like.
