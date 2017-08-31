#!/usr/bin/python

from __future__ import print_function
from __future__ import absolute_import
import sys

import jaxml
from portage.output import red


class MyMetadata(jaxml.XML_document):

    """Create Gentoo Linux metadata.xml"""

    def __init__(self):
        jaxml.XML_document.__init__(self, "1.0", "UTF-8")
        self._indentstring("\t")
        self._text('<!DOCTYPE pkgmetadata SYSTEM ' +
                   '"http://www.gentoo.org/dtd/metadata.dtd">')
        self.pkgmetadata()

    def set_maintainer(self, emails, names, descs, types):
        """Set maintainer(s)'s email, name, desc"""
        if len(types) != len(emails):
            if len(types) != 1:
                print(red("!!! Nbr maintainer types != nbr emails"))
                sys.exit(1)
            types = [types[0] for _ in emails]

        i = 0
        for e in emails:
            self._push("maintainer_level")
            self.maintainer(type=types[i]).email(e)
            if names:
                if len(names) > len(emails):
                    print(red("!!! Nbr names > nbr emails"))
                    sys.exit(1)
                if i <= len(names) -1:
                    self.name(names[i])
            if descs:
                if len(descs) > len(emails):
                    print(red("!!! Nbr descs > nbr emails"))
                    sys.exit(1)
                if i <= len(descs) -1:
                    self.description(descs[i])
            self._pop("maintainer_level")
            i += 1

    def set_longdescription(self, longdesc):
        """Set package's long description."""
        self.longdescription(longdesc)

def do_tests():
    from . import meta_unittest
    fails = 0
    for func in dir(meta_unittest):
        if func[0:4] == "test":
            try:
                exec("print meta_unittest.%s.__name__ + ':'," % func)
                exec("print meta_unittest.%s.__doc__" % func)
                exec("print meta_unittest.%s()" % func)
            except:
                fails += 1
                print("Test %s failed:" % func)
                print(sys.exc_info()[0], sys.exc_info()[1])
    print("%s tests failed." % fails)

if __name__ == "__main__":
    do_tests()
