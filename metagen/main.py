#!/usr/bin/python

"""

NAME     - metagen
SYNOPSIS - Adds metadata.xml to current directory
AUTHOR   - Rob Cakebread <cakebread@gmail.com>
AUTHOR   - Jesus Rivero <neurogeek@gentoo.org>
USE      - metagen --help
EXAMPLES - man metagen

"""

import re
import os
import sys
from argparse import ArgumentParser
from commands import getstatusoutput

from portage import config
from portage.output import red, blue

try:
    # portage <2.2.22
    # https://bugs.gentoo.org/show_bug.cgi?id=561908
    from repoman import herdbase
except ImportError:
    # portage >=2.2.22
    from repoman.checks.herds import herdbase

from metagen.version import __version__
from metagen import metagenerator

PORTDIR = config(local_config=False)["PORTDIR"]
HB = herdbase.make_herd_base(os.path.sep.join([PORTDIR, 'metadata', 'herds.xml']))

def parse_echangelog_variable(name, email):
    """Extract developer name and email from ECHANGELOG_USER variable"""
    try:
        e = os.environ["ECHANGELOG_USER"]
    except KeyError:
        print red("!!! Environmental variable ECHANGELOG_USER not set.")
        print red("!!! Set ECHANGELOG_USER or use -e and -n")
        sys.exit(1) 
    try:
        my_email = e[e.find("<") +1:e.find(">")]
    except:
        print red("!!! ECHANGELOG_USER not set properly")
        sys.exit(1) 
    try:
        my_name = e[0:e.find("<")-1]
    except:
        print red("!!! ECHANGELOG_USER not set properly")
        sys.exit(1) 
    if email:
        email = "%s,%s" % (my_email, email)
    else:
        email = my_email
    if name:
        name = "%s,%s" % (my_name, name)
    else:
        name = my_name
    return name, email

def generate_xml(options):
    """Returns metadata.xml text"""

    herds=[]
    metadata = metagenerator.MyMetadata()

    if options.herd:
        herds = options.herd.split(",")

    for herd in herds:
        if not HB.known_herd(herd):
            print red("!!! Error. Herd %s does not exist." % herd)
            sys.exit(1) 
            
    metadata.set_herd(herds)

    if options.echangelog:
        (options.name, options.email) = \
            parse_echangelog_variable(options.name, options.email)

    if options.email:
        names, descs = [], []
        if options.name:
            names = options.name.split(",")
        if options.desc:
            descs = options.desc.split(",")
        metadata.set_maintainer(options.email.split(","),
                                names,
                                descs
                                )

    if options.long:
        metadata.set_longdescription(options.long)

    return "%s" % metadata

def validate_xml(my_xml):
    """Test for valid XML"""
    #TODO validate against DTD
    #This just makes sure its valid XML of some sort.
    #Probably not necessary since repoman validates against DTD?
    re_escape_quotes = re.compile('"')
    s = re_escape_quotes.sub('\\"', my_xml)
    cmd = "echo \"%s\" | xmllint --valid - 2>&1 > /dev/null" % s
    return getstatusoutput(cmd)[0]


if __name__ == '__main__':
    parser = ArgumentParser(prog='metagen')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    maintainer = parser.add_argument_group(title='maintainer arguments')
    maintainer.add_argument("-H", action="store", dest="herd",
                         help="Name of herd. If not specified, It will be empty. " +
                         "This requires either the -e or -m option.")
    maintainer.add_argument("-e", action="store", dest="email",
                         help="Maintainer's email address")
    maintainer.add_argument("-n", action="store", dest="name",
                         help="Maintainer's name")
    maintainer.add_argument("-m", action="store_true", dest="echangelog",
                         default=False,
                         help="Use name and email address from ECHANGELOG_USER "+
                         "environmental variable. "+
                         "This is a shortcut for -e <email> -n <name>")
    maintainer.add_argument("-d", action="store", dest="desc",
                         help="Description of maintainership")

    package = parser.add_argument_group(title='package arguments')
    package.add_argument("-l", action="store", dest="long",
                         help="Long description of package.")

    operation = parser.add_argument_group(title='operation arguments')
    operation.add_argument("-o", action="store", dest="output",
                         help="Specify location of output file.")
    operation.add_argument("-f", action="store_true", dest="force", default=False,
                         help="Force overwrite of existing metadata.")
    operation.add_argument("-v", action="store_true", dest="verbose", default=True,
                         help="Verbose. Output of file to stdout. (default)")
    operation.add_argument("-q", action="store_false", dest="verbose",
                         help="Squelch output of file to stdout.")
    operation.add_argument("-Q", action="store_true", dest="no_write",
                         default=False,
                         help="Do not write file to disk.")

    options = parser.parse_args()

    if options.desc or options.name:
        if not options.email and not options.echangelog:
            print red("!!! No maintainer's email address specified.")
            print red("!!! Options -d and -n are only valid with -e or -m")
            sys.exit(1)
 
    if not options.herd and not options.email and not options.echangelog:
        print red("!!! You must specify at least a herd (-H) " +
                  "or maintainer's email address (-e)\n")
        sys.exit(1)

    txt = generate_xml(options)

    error_status = validate_xml(txt)
    if error_status < 0:
        print red("!!! Error - Invalid XML")
        print red("!!! Please report this bug with the options you used and the output:")
        print error_status
        print txt
        sys.exit(1)

    if options.verbose:
        print "\n%s" % txt

    out_file = "./metadata.xml"
    if options.output:
        out_file = options.output
    if not options.no_write and os.path.exists(out_file):
        if not options.force:
            print red("!!! File %s exists." % out_file)
            print red("!!! Use -f to force overwrite.")
            sys.exit(1)
    if not options.no_write:
        open("%s" % out_file, "w").writelines(txt)
        print blue("%s written") % out_file

