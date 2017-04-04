#!/usr/bin/env python
# coding=utf-8

from __future__ import with_statement

import os
import sys
import errno
import subprocess as sub

from stat import S_IFDIR, S_IFLNK, S_IFREG
from fuse import FUSE, FuseOSError, Operations, fuse_get_context
from time import time

reload(sys)
sys.setdefaultencoding('utf8')

TMSU="~/src/tmsu-x86_64-0.6.1/bin/tmsu "

#### Global Helpers

def printdbg(level,string):
    if level>1:
        print string
def sanitize(x):
        if x.startswith('/'):
            x=x[1:]
        if x.startswith('/'):
            x=x[1:]
        if x.find("//")>0:
                x=x.replace("//","/",1)
        if x.find("\\ ")>0:
                x=x.replace("\\ "," ")
        return x

def list2uniqueidlist(mylist):
    newlist=[]
    for x in mylist:
        quanti=newlist.count(x)
        print x,quanti
        if quanti<1:
            newlist.append(x)
        else:
            newlist.append(x+".altro-"+str(quanti))
    return newlist

### Class for Tags

class tagmanager():
    def __init__(self,root):
        self.cmd=TMSU
        self.root=root
        printdbg(1,"New tagman in: "+root)

    def dbcmd(self,command,args="",args2=""):
        if args!="":
            args=str("\""+args+"\"")
        if args!="":
            args=str("\""+args+"\"")
        if args2!="":
            args2=str("\""+args2+"\"")
        if args2!="":
            args2=str("\""+args2+"\"")
        comando=str("cd "+self.root+";"+TMSU+command+" "+args+" "+args2)
        comando=comando.replace('""','"')
        printdbg(2,comando)
        output=sub.check_output(comando,shell=True)
        printdbg(1,output)
        return output

    def db_init(self):
        self.dbcmd("init")

    def taglist(self):
        output=self.dbcmd("tags")
        printdbg(1,output)
        lista=output.splitlines()
        lista = [sanitize(item) for item in lista]
        printdbg(1,lista)
        return lista

    def tagfiles(self,tag):
        tag=sanitize(tag)
        printdbg(1,"tag files :"+tag)
        output=self.dbcmd("files",tag)
        printdbg(1,output)
        lista=output.splitlines()
        lista = [sanitize(item) for item in lista]
        printdbg(1,lista)
        return lista

    def tagfilescache(self,tag):
        listafile=self.tagfiles(tag)
        basefiles=dict()
        for x in listafile:
            basefiles[x]=x.split('/')[-1]
        #####da fare link a nuovi file (come le dir)
        #da togliere se non funnziona
        newlist=[]
        print basefiles
        for k in basefiles.keys():
            quanti=newlist.count(basefiles[k])
            print x,quanti
            if quanti<1:
                newlist.append(basefiles[k])
            else:
                newname=basefiles[k]+".altro-"+str(quanti)
                newlist.append(newname)
                basefiles[k]=newname
        inverse=dict()
        for k in basefiles.keys():
            inverse[basefiles[k]]=k
        print inverse
        return inverse

    def gettagfile(self,tagpath):
        tagpath=sanitize(tagpath)
        printdbg(2,"---------------in gettagfile :"+tagpath)
        listatag= self.taglist()
        #gestire se sub
        if tagpath.find('/')>0:
            #da aggiustare bisogna dividere tutti (prendere il primo e l'ultimo)
            # si usera' poi.... tags=tag.split("/")
            mytag,subtag=tagpath.split("/")
            printdbg(1,"sarebbe subtag "+subtag+" in "+mytag)
            #controlla se e' file o tag
            #prima se e' tag
            #poi se e' file
            reverse=self.tagfilescache(mytag)
            if subtag in reverse.keys():
                printdbg(1,"file "+subtag+" is in "+mytag)
                realfile=reverse[subtag]
            else:
                printdbg(1,"(tagstat) file not exist "+subtag)
                raise FuseOSError(errno.ENOENT)
            printdbg(2,"------------ realfile is:"+realfile)
            return realfile
        else:
            raise FuseOSError(errno.EPERM)

    def getqueryfile(self,querytagpath):
        querytagpath=sanitize(querytagpath)
        printdbg(2,"in getqueryfile :"+querytagpath)
        listatag= self.taglist()
        #gestire se sub
        #gestire se sub
        if querytagpath.find('/#/')>-1:
            printdbg(2,"----- query getattr ------------"+querytagpath)
            #si deve creare la query e passarla
            query=querytagpath.split("/#/")
            printdbg(2,query)
            #da gestire la query (ispirandosi alla tagstat)
            #gestendo anche la querymal formata
            tags_inquery=query[0].replace("/"," ")
            reverse=self.tagfilescache(query[0])
            if query[1] in reverse.keys():
                printdbg(1,"file "+query[1]+" is in "+query[0])
                realfile=reverse[query[1]]
            else:
                printdbg(1,"(tagstat) file not exist "+subtag)
                raise FuseOSError(errno.ENOENT)
            printdbg(2,"------------ realfile is:"+realfile)
            return realfile
        else:
            raise FuseOSError(errno.EPERM)

    def tagstat(self,tag=""):
        printdbg(2,"in tagstat")
        via=1
        tag=sanitize(tag)
        print "in tagstat tag:"+tag
        listatag= self.taglist()
        st = dict(st_mode=(S_IFDIR | 0o775),st_size =4096)
        if tag=="":
            st['st_nlink']=len(listatag) + 1
        else:
            st['st_nlink']=2
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        st['st_uid'] = st['st_gid'] = 1000
        st['st_ino'] = 20000000
        #gestire se sub
        if tag.find('/')>0:
            printdbg(1,"-----------------tag--------------------")
            printdbg(1,tag)
            printdbg(1,"-----------------tag--------------------")
            #da aggiustare bisogna dividere tutti (prendere il primo e l'ultimo)
            # si usera' poi.... tags=tag.split("/")
            mytag,subtag=tag.split("/")
            printdbg(1,"sarebbe subtag "+subtag+" in "+mytag)
            #controlla se e' file o tag
            #prima se e' tag
            #poi se e' file
            reverse=self.tagfilescache(mytag)
            if subtag  in reverse.keys():
                printdbg(2,"-----------------subtag--------------------")
                printdbg(2,"file "+subtag+" is in "+mytag)
                printdbg(2,"-----------------subtag--------------------")
                realfile=reverse[subtag]
                printdbg(2,"(tagstat) leggo lstat di "+self.root+"/"+realfile)
                if(os.path.isdir(self.root+"/"+realfile)):
                    st['st_mode']=(S_IFLNK | 0o775)
                    via=1
                #### link
                elif subtag.find(".altro-")>0:
                    printdbg(2,"trovato link!")
                    st['st_mode']=(S_IFLNK | 0o775)
                    via=1
                ####
                else:
                    st = os.lstat(self.root+"/"+realfile)
                    via=0
            else:
                raise FuseOSError(errno.EPERM)

        #gestire se non esiste
        elif tag != "" and tag not in self.taglist():
            printdbg(1, "tag: "+tag+" is new")
            raise FuseOSError(errno.ENOENT)

        printdbg(1,st)
        return st,via

    def querystat(self,querytagpath=""):
        via=1
        printdbg(2,"in querystat")
        querytagpath=sanitize(querytagpath)
        printdbg(2,"in querystat tag:"+querytagpath)
        listatag= self.taglist()
        st = dict(st_mode=(S_IFDIR | 0o555),st_size =4096)
        st['st_nlink']=len(listatag) + 1
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        st['st_uid'] = st['st_gid'] = 1000
        st['st_ino'] = 20000000
        #gestire se sub
        if querytagpath.find('/#/')>-1:
            printdbg(2,"----- query getattr ------------"+querytagpath)
            #si deve creare la query e passarla
            query=querytagpath.split("/#/")
            printdbg(2,query)
            #da gestire la query (ispirandosi alla tagstat)
            #gestendo anche la querymal formata
            tags_inquery=query[0].replace("/"," ")
            ####paste
            reverse=self.tagfilescache(tags_inquery)
            if query[1]  in reverse.keys():
                printdbg(2,"-----------------querytag--------------------")
                printdbg(2,"file "+query[1]+" is in "+query[0])
                printdbg(2,"-----------------querytag--------------------")
                realfile=reverse[query[1]]
                printdbg(2,"(tagstat) leggo lstat di "+self.root+"/"+realfile)
                if(os.path.isdir(self.root+"/"+realfile)):
                    st['st_mode']=(S_IFLNK | 0o775)
                    via=1
                #### link
                elif query[1].find(".altro-")>0:
                        printdbg(2,"trovato link!")
                        st['st_mode']=(S_IFLNK | 0o775)
                        via=1
                    ####
                else:
                    st = os.lstat(self.root+"/"+realfile)
                    via=0
            else:
                raise FuseOSError(errno.EPERM)

        printdbg(1,st)
        return st,via

    def newtag(self,name):
        name=sanitize(name)
        printdbg(1,name)
        #output=sub.check_output(TMSU+" -c "+name, shell=True)
    	#print(output)
        self.dbcmd("tag -c",name)
        return
        #raise FuseOSError(errno.EPERM)

    def add2tag(self,tag,realfile):
        tag=sanitize(tag)
        realfile=sanitize(realfile)
        mytag,subtag=tag.split("/")
        printdbg(2,tag+" "+realfile)
        self.dbcmd("tag",realfile,mytag)
        return
        #raise FuseOSError(errno.EPERM)

    def delfromtag(self,tag,realfile):
        tag=sanitize(tag)
        realfile=sanitize(realfile)
        mytag,subtag=tag.split("/")
        printdbg(2,tag+" "+realfile)
        self.dbcmd("untag",realfile,mytag)
        return
        #raise FuseOSError(errno.EPERM)

    def deltag(self,name):
        name=sanitize(name)
        printdbg(1,name)
        self.dbcmd("delete",name)
        return
        #raise FuseOSError(errno.EPERM)

    def renametag(self,old,new):
        old=sanitize(old)
        new=sanitize(new)
        printdbg(2,"tag rename "+old+" "+new)
        self.dbcmd("rename",old,new)
        return
        #raise FuseOSError(errno.EPERM)



class gluedfs(Operations):
    def __init__(self, root):
        if root.endswith('/'):
            root=root[:-1]
        self.root = root
        self.fileroot = "root_"+root
        self.tagroot = "tag_"+root
        self.queryroot = "query_"+root
        self.tagman=tagmanager(root)
        #init database
        #output=sub.check_output("~/tmsu-x86_64-0.5.2/bin/tmsu tag \""+filepath+"\" "+self.mylabel, shell=True)
        self.tagman.db_init()

    # Helpers
    # =======

    def _full_path(self, partial):
        myroot=self.root
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(myroot, partial)
        if path.find(self.fileroot):
            printdbg(1,"elimino "+self.fileroot)
            partial=path.replace(self.fileroot, "", 1)
            printdbg(1,"sostituito "+partial)
            path=partial
        path=sanitize(path)
        printdbg(1,"sanato "+path)
        return path

    def path2tagfile(self,path):
        # ritorna il path del file se in in tag se no...? da definire
        printdbg(2,"---------------in gettagfile :"+path)
        if path.find(self.tagroot)>0:
            printdbg(2,"in path2tagfile "+path)
            partial=path.replace(self.tagroot, "", 1)
            path=self.tagman.gettagfile(partial)
            printdbg(2,"in path2tagfile realpath:"+path)
        if path.find(self.queryroot)>0:
            printdbg(2,"in path2tagfile "+path)
            partial=path.replace(self.queryroot, "", 1)
            path=self.tagman.getqueryfile(partial)
            printdbg(2,"in path2tagfile realpath:"+path)
        return path

    def path2tagname(self,path):
        # ritorna il path del tag in tag se no?
        if path.find(self.tagroot)>0:
            path=path.replace(self.tagroot, "", 1)
            printdbg(2,"in path2tagname "+path)
            partial=path.rsplit('/',1)
            path=partial[0]
            # da definire come fare
            printdbg(2,"in path2tagnames path:"+path)
        return path

    def is_tag(self,path):
        # ritorna il path del tag in tag se no?
        if path.find(self.tagroot)>0:
            # da definire come fare
            printdbg(2,"in is_tag path:"+path)
        return FALSE

    def is_tag_object(self,path):
        # ritorna il path del tag in tag se no?
        if path.find(self.tagroot)>0:
            # da definire come fare
            printdbg(2,"in is_tag_object path:"+path)
        return FALSE

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        if path.find(self.tagroot)>0 or path.find(self.queryroot)>0:
            printdbg(1,"in tag access "+path)
            return
        printdbg(2, "in access: "+path)
        full_path = self._full_path(path)
        printdbg(1,path)
        printdbg(1,full_path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        printdbg(2,"in getattr :"+path)
        if path.find(self.tagroot)>0:
            raise FuseOSError(errno.EPERM)
        full_path = self._full_path(path)
        printdbg(1,full_path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        printdbg(2,"in chown :"+path)
        if path.find(self.tagroot)>0:
            raise FuseOSError(errno.EPERM)
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        printdbg(2,"in getattr "+path)
        # daggiungere nei posti opportuni
        #if path.find(".altro-")>0:
        #    st=os.lstat("/")
        #    return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
        #                 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

        if path.find(self.tagroot)>0:
            (st,via) = self.tagman.tagstat(path.replace(self.tagroot, "", 1))
            #if len(st)==0:
            #    raise FuseOSError(errno.ENOENT)
            #else:
            printdbg(1, st)
            if via==1:
                return st
        elif path.find(self.queryroot)>0:
            (st,via) = self.tagman.querystat(path.replace(self.queryroot, "", 1))
            printdbg(1, st)
            if (via==1):
                return st
        else:
            full_path = self._full_path(path)
            printdbg(2,"leggo lstat di :"+full_path)
            st = os.lstat(full_path)
        printdbg(1,st)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        printdbg(2,"readdir "+path)
        full_path = self._full_path(path)
        dirents = ['.', '..']
        if path=="/":
            dirents.append(self.fileroot)
            dirents.append(self.tagroot)
            dirents.append(self.queryroot)
        elif path==str("/"+self.fileroot):
            full_path = self._full_path("/")
            printdbg(2,"in readdir radice file:"+full_path)
            dirents.extend(os.listdir(full_path))
        elif path==str("/"+self.tagroot):
            full_path = self._full_path(path)
            printdbg(2,"in readdir radice tag:"+full_path)
            dirents.extend(self.tagman.taglist())
        elif path.find(self.tagroot)>0:
            listafile=self.tagman.tagfiles(path.replace(self.tagroot, "", 1))
            printdbg(2,"---------------------in readdir dentro tag"+path)
            printdbg(2,listafile)
            #dirents.extend([ x.replace('./',"") for x in listafile])
            ###### in listafile potrebbero esserci dei duplicati ##############
            listanomi=[ x.split('/')[-1] for x in listafile]
            listanomiconsost=list2uniqueidlist(listanomi)
            printdbg(2,listanomiconsost)
            ######
            #dirents.extend([ x.split('/')[-1] for x in listafile])
            dirents.extend(listanomiconsost)
        #elif path==str("/"+self.queryroot):
        #    full_path = self._full_path(path)
        #    printdbg(2,"in readdir radice tag:"+full_path)
        #    dirents.extend(self.tagman.taglist())
        #    dirents.append('#')
        elif path.find(self.queryroot)>-1:
            full_path = self._full_path(path)
            printdbg(2,"in readdir query:"+full_path)
            if path[-1]=='#':
                tags_inquery=path[1:-2].split('/')
                del tags_inquery[0] # remove dir entity
                printdbg(2,tags_inquery)
                path=path.replace(self.queryroot,"")
                querytag=path[1:-2].replace('/',' ')
                queryresult=self.tagman.tagfiles(querytag)
                printdbg(2,queryresult)
                listanomi=[ x.split('/')[-1] for x in queryresult]
                listanomiconsost=list2uniqueidlist(listanomi)
                printdbg(2,"listanomiconsost--------------")
                printdbg(2,listanomiconsost)
                ######
                #dirents.extend([ x.split('/')[-1] for x in listafile])
                dirents.extend(listanomiconsost)
            else:
                tags_inquery=path[1:].split('/')
                #rimanenti tag
                rimanenti=[ x for x in self.tagman.taglist() if not x in tags_inquery]
                print(rimanenti)
                #dirents.extend(self.tagman.taglist())
                dirents.extend(rimanenti)
                dirents.append('#')
        else:
            if os.path.isdir(full_path):
                dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        printdbg(2,"in readlink :"+path)
        if path.find(self.tagroot)>0:
            printdbg(2,"in tag readlink"+path)
            path=self.path2tagfile(path)
            #attenzione messa stringa (da mettere variabile) vale solo senza subtag
            pathname = "../../root_"+self._full_path(path)
        elif path.find(self.queryroot)>0:
                    printdbg(2,"----------->in tag readlink:"+path+"\npercorso: "+str(path.count('/')))
                    n=path.count('/')-1
                    i=0
                    relpath=""
                    while i<n:
                        relpath+="../"
                        i+=1
                    path=self.path2tagfile(path)

                    #attenzione messa stringa (da mettere variabile) vale solo senza subtag
                    pathname = relpath+"root_"+self._full_path(path)
                    printdbg(2,"----------->relpath"+relpath+"percorso: ")

        else:
            pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        if path.find(self.tagroot)>0:
            printdbg(2,"in mknod :"+path)
            raise FuseOSError(errno.EPERM)
        elif path.find(self.fileroot)>0:
            return os.mknod(self._full_path(path), mode, dev)
        raise FuseOSError(errno.EPERM)

    def rmdir(self, path):
        printdbg(2,"in rmdir :"+path)
        if path.find(self.tagroot)>0:
            printdbg(2,"in tag rmdir"+path)
            partial=path.replace(self.tagroot, "", 1)
            return self.tagman.deltag(partial)
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        if path.find(self.tagroot)>0:
            printdbg(2,"in tag mkdir"+path)
            partial=path.replace(self.tagroot, "", 1)
            return self.tagman.newtag(partial)
        elif path.find(self.queryroot)>-1:
            raise FuseOSError(errno.EPERM)
        elif path.find(self.fileroot)>0:
            printdbg(2,"in mkdir :"+path)
            return os.mkdir(self._full_path(path), mode)
        raise FuseOSError(errno.EPERM)

    def statfs(self, path):
        printdbg(2,"in statfs :"+path)
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        printdbg(2,"in unlink :"+path)
        if path.find(self.tagroot)>0:
            partial=path.replace(self.tagroot, "", 1)
            realfile=self.path2tagfile(path)
            printdbg(2,"in remove tag "+partial+" to "+realfile)
            return self.tagman.delfromtag(partial,realfile)
        else:
            fullpath=self._full_path(path)
        printdbg(2,"in unlink real:"+fullpath)
        return os.unlink(fullpath)

    def symlink(self, name, target):
        printdbg(2,"in symlink :"+name)
        print name
        print self._full_path(target)
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        printdbg(2,"in rename :"+old+" "+new)
        oldfile=""
        #########molto test
        ######### fine molto test
        #rename tag
        if old.find(self.tagroot)>0:
            printdbg(2,"in tag rename"+old)
            old=old.replace(self.tagroot, "", 1)
            new=new.replace(self.tagroot, "", 1)
            return self.tagman.renametag(old,new)
        #rename file (mettere nel tag)
        if new.find(self.tagroot)>0:
            printdbg(2,"in rename to tag is add tag "+new+" to "+old)
            partial=new.replace(self.tagroot, "", 1)
            realfile=old.replace(self.fileroot,"",1)
            printdbg(2,"in rename to tag is add tag "+partial+" to "+realfile)
            if os.path.isdir(self._full_path(old)):
                printdbg(2,"giving tag "+partial+" to "+old)
                #raise FuseOSError(errno.EPERM)
            return self.tagman.add2tag(partial,realfile)
        printdbg(2,"rename standard"+ self._full_path(old))
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        printdbg(2,"in link :"+target)
        printdbg(1, path)
        print self._full_path(target)
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        printdbg(2,"in link :"+path)
        return os.utime(self._full_path(path), times)

    # File methods
    # ============


    def open(self, path, flags):
        printdbg(2,"in open :"+path)
        path=self.path2tagfile(path)
        full_path = self._full_path(path)
        printdbg(2,"in open full_path:"+full_path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        printdbg(2,"in create :"+path)
        full_path = self._full_path(path)
        printdbg(2,"in create realpath:"+path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        printdbg(2,"in read :"+path)
        path=self.path2tagfile(path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        printdbg(2,"in write :"+path)
        path=self.path2tagfile(path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        printdbg(2,"in truncate :"+path)
        path=self.path2tagfile(path)
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        path=self.path2tagfile(path)
        printdbg(2,"in flush :"+path)
        return os.fsync(fh)

    def release(self, path, fh):
        path=self.path2tagfile(path)
        printdbg(2,"in release :"+path)
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        path=self.path2tagfile(path)
        printdbg(2,"in fsync :"+path)
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(gluedfs(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
