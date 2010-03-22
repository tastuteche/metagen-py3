#!/usr/bin/python

from metagenerator import MyMetadata


def test1():
    """1 herd specified"""
    metadata = MyMetadata()
    metadata.set_herd(("python"))
    return metadata 
 
def test2():
    """No herd specified, 1 maintainer"""
    metadata = MyMetadata()
    metadata.set_herd([""])
    metadata.set_maintainer(["<pythonhead@gentoo.org>"], 
                            ["Rob Cakebread"], 
                            ["Maintainer description."]
                           )
    return metadata 
    
def test3():
    """1 herd, 1 maintainer"""
    metadata = MyMetadata()
    metadata.set_herd(["python"])
    metadata.set_maintainer(["<pythonhead@gentoo.org>"],
                            ["Rob Cakebread"],
                            ["Maintainer description."]
                           )
    return metadata 

def test4():
    """2 herds, 1 maintainer"""
    metadata = MyMetadata()
    metadata.set_herd(["python", "gnome"])
    metadata.set_maintainer(["pythonhead@gentoo.org"],
                            ["Rob Cakebread"],
                            ["Maintainer description."]
                           )
    return metadata 

def test5():
    """2 herds, 2 maintainers, longdesc"""
    metadata = MyMetadata()
    metadata.set_herd(["python", "gnome"])
    metadata.set_maintainer(["goofy@gentoo.org", "pythonhead@gentoo.org"],
                            ["Goo Fi", "Rob Cakebread"],
                            ["Maintainer one.", "Maintainer two"]
                           )
    metadata.set_longdescription("This packages does X Y and Z.")
    return metadata 

