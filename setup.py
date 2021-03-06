"""
NAME:
    setup.py
  
SYNOPSIS:
    python setup.py [options] [command]
    
DESCRIPTION:
    Using distutils "setup", build, install, or make tarball of the package.
    
OPTIONS:
    See Distutils documentation for details on options and commands.
    Common commands:
    build               build the package, in preparation for install
    install             install module(s)/package(s) [runs build if needed]
    install_data        install datafiles (e.g., in a share dir)   
    install_scripts     install executable scripts (e.g., in a bin dir)   
    sdist               make a source distribution
    bdist               make a binary distribution
    clean               remove build temporaries

EXAMPLES:
    cd mydir
    (cp myfile-0.1.tar.gz here)
    gzip -cd myfile-0.1.tar.gz | tar xvf -
    cd myfile-0.1
    python setup.py build
    python setup.py install
    python setup.py sdist
"""
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import os,sys,re,string,getopt,shutil,subprocess,glob
from distutils.core import setup,Extension
from metagen.version import __version__

modname='setup'
debug_p=0

pkgname='metagen'
#version=string.strip(open("VERSION").readline())
version = __version__
exec_prefix=sys.exec_prefix
description = "Metadata.xml Generator for Ebuilds"
author = "Rob Cakebread"
author_email = "pythonhead@gentoo.org"
url=""
license = "GPL-2"

packages=['metagen']
package_data={"metagen" : ["test_cli"]}
data_files=[("share/doc/%s-%s" % ("metagen", version), glob.glob("docs/*"))]

#===utilities==========================
def debug(ftn,txt):
    if debug_p:
        sys.stdout.write("%s.%s:%s\n" % (modname,ftn,txt))
        sys.stdout.flush()

def fatal(ftn,txt):
    msg="%s.%s:FATAL:%s\n" % (modname,ftn,txt)
    raise SystemExit(msg)
    
def usage():
    print(__doc__)

#=============================
def main():
    setup (#---meta-data---
           name = pkgname,
           version = version,
           description = description,
           author = author,
           author_email = author_email,
           url=url,
           license = license,

           #---scripts,modules and packages---
           packages = packages,
           data_files = data_files,
           )
#==============================
if __name__ == '__main__':
    opts,pargs=getopt.getopt(sys.argv[1:],'hv',
                 ['help','version','exec-prefix'])
    for opt in opts:
        if opt[0]=='-h' or opt[0]=='--help':
            usage()
            sys.exit(0)
        elif opt[0]=='-v' or opt[0]=='--version':
            print(modname+": version="+version)
        elif opt[0]=='--exec-prefix':
            exec_prefix=opt[1]

    for arg in pargs:
        if arg=='test':
            do_test()
            sys.exit(0)
        elif arg=='doc':
            do_doc()
            sys.exit(0)
        else:
            pass

    main()

