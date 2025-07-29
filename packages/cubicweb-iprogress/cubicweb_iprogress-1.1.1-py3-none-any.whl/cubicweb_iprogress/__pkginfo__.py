# pylint: disable=W0622
"""cubicweb-iprogress application packaging information"""

modname = "iprogress"
distname = "cubicweb-iprogress"

numversion = (1, 1, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "some adapters and view for stuff progressing to reach a milestone"
web = "http://www.cubicweb.org/project/%s" % distname
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">=4.5.2,<6.0.0",
    "cubicweb-web": ">=1.4.2,<2.0.0",
}
__recommends__ = {}
