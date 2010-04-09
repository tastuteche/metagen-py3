#!/usr/bin/python


"""

NAME     - metagen

SYNOPSIS - Adds metadata.xml to current directory

AUTHOR   - Rob Cakebread <pythonhead@gentoo.org>

USE      - metagen --help

EXAMPLES - man metagen

"""

import sys
import re
import os
from optparse import OptionParser
from commands import getstatusoutput

from portage.output import red, blue

from metagen.version import __version__
from metagen import metagenerator


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

    metadata = metagenerator.MyMetadata()

    if options.herd:
        herds = options.herd.split(",")
    else:
        herds = ["no-herd"]
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
    #Probably not necessary since repoma validates against DTD?
    re_escape_quotes = re.compile('"')
    s = re_escape_quotes.sub('\\"', my_xml)
    cmd = "echo \"%s\" | xmllint --valid - 2>&1 > /dev/null" % s
    return getstatusoutput(cmd)[0]


if __name__ == '__main__':
    optParser = OptionParser(version=__version__)
    optParser.add_option("-H", action="store", dest="herd", type="string",
                         help="Name of herd. If not specified, " +
                         "'no-herd' will be inserted. " +
                         "This requires either the -e or -m option.")

    optParser.add_option("-e", action="store", dest="email", type="string",
                         help="Maintainer's email address")

    optParser.add_option("-n", action="store", dest="name", type="string",
                         help="Maintainer's name")

    optParser.add_option("-m", action="store_true", dest="echangelog", 
                         default=False,
                         help="Use name and email address from ECHANGELOG_USER "+
                         "environmental variable. "+
                         "This is a shortcut for -e <email> -n <name>")

    optParser.add_option("-d", action="store", dest="desc", type="string",
                         help="Description of maintainership")

    optParser.add_option("-l", action="store", dest="long", type="string",
                         help="Long description of package.")

    optParser.add_option("-o", action="store", dest="output", type="string",
                         help="Specify location of output file.")

    optParser.add_option("-f", action="store_true", dest="force", default=False,
                         help="Force overwrite of existing metadata.")

    optParser.add_option("-v", action="store_true", dest="verbose", default=True,
                         help="Verbose. Output of file to stdout. (default)")

    optParser.add_option("-q", action="store_false", dest="verbose",
                         help="Squelch output of file to stdout.")

    optParser.add_option("-Q", action="store_true", dest="no_write",
                         default=False,
                         help="Do not write file to disk.")

    (options, remainingArgs) = optParser.parse_args()

    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit(1)

    if options.desc or options.name:
        if not options.email and not options.echangelog:
            print red("!!! No maintainer's email address specified.")
            print red("!!! Options -d and -n are only valid with -e or -m")
            sys.exit(1)
 
    if options.herd == "no-herd" and not options.email and not options.echangelog:
        print red("!!! You must specify a maintainer if you have no-herd.")
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

