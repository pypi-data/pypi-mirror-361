# pylint: disable-msg=W0622
"""cubicweb-tag packaging information"""

modname = "tag"
distname = f"cubicweb-{modname}"

numversion = (3, 1, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
description = "tag component for the CubicWeb framework"
author = "Logilab"
author_email = "contact@logilab.fr"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.5.2, < 6.0.0",
    "cubicweb-web": ">= 1.0.0, < 2.0.0",
}
