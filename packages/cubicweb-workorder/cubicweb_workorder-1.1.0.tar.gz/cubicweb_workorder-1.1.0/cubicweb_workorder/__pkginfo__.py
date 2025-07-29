# pylint: disable-msg=W0622
"""cubicweb-workorder application packaging information"""

modname = "workorder"
distname = "cubicweb-%s" % modname

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
description = "workorder component for the CubicWeb framework"
web = "http://www.cubicweb.org/project/%s" % distname
author = "Logilab"
author_email = "contact@logilab.fr"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">=4.5.2,<5.0.0",
    "cubicweb-web": ">=1.4.2,<2.0.0",
    "cubicweb-iprogress": ">=1.0.0,<2.0.0",
}
