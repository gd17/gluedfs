# gluedfs
Glued Filesystem - Tag Filesystem in Linux (Gnu-Linux-Unified-Enhanced-Dbtagged )
------------------------------------------------------------------------
GLUEDFS
Glued Filesystem
Gnu-Linux-Unified-Enhanced-Dbtagged
by gd@linux.it
------------------------------------------------------------------------
dependencies: tmsu (https://github.com/oniony/TMSU) , python 2.7, python module fusepy
------------------------------------------------------------------------
How to use it
------------------------------------------------------------------------
-cmdline only by now
:YOURDIR must be root in cwd Current Working Directory
:command tmsu (bin) must be defined in variable TMSU in gluedfsV_v.py
-you must go this way by now:
mount:
:python gluedfs2_6.py YOURDIR mountpoint
umount:
interrupt process or fusermount -u mountpoint (by superuser?)
------------------------------------------------------------------------
How it works
------------------------------------------------------------------------
---root_dir is direct access to YOURDIR
- inside root_dir you can do everything as usual, in fact is a loop of YOURDIR
- inside root_dir GLUEDFS puts his DB in .tmsu hidden dir

---tag_dir is is your tags you can create, rename, delete tags and tag/untag items
- tagging items is made by moving from root_dir items to a specific tag in tagdir
- inside tag_dir you can access files or dirs of YOURDIR
- if you delete items in tag_dir you're untagging items, you don't delete items
- if more than one item has same name in one tag others are symbolic
  links to your items in YOURDIR
- you can only tag items in root_dir

---query_dir is is a way to filter your tags
- browse tags and special dir # (and query)
- inside query_dir you can access files or dirs of YOURDIR
- if more than one item has same name in one tag others are symbolic
  links to your items in YOURDIR
