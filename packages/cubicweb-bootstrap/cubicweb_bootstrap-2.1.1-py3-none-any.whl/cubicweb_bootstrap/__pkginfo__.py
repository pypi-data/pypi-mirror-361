# pylint: disable=W0622
"""cubicweb-bootstrap application packaging information"""

modname = "bootstrap"
distname = "cubicweb-bootstrap"

numversion = (2, 1, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = ""
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/%s" % distname

__depends__ = {
    "cubicweb": ">= 4.5.2, < 6.0.0",
    "cubicweb-web": ">= 1.0.0, < 2.0.0",
}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: JavaScript",
]
