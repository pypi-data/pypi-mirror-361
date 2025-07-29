# pylint: disable-msg=W0622
"""cubicweb-blog packaging information"""

modname = "blog"
distname = f"cubicweb-{modname}"

numversion = (3, 1, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
description = "blogging component for the CubicWeb framework"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"
mailinglist = "mailto://cubicweb@lists.logilab.org"
author = "Logilab"
author_email = "contact@logilab.fr"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.5.2, < 6.0.0",
    "cubicweb-web": ">= 1.4.2, < 2.0.0",
    "cubicweb-sioc": ">= 1.0.0, < 2.0.0",
}
__recommends__ = {
    "cubicweb-tag": None,
    "cubicweb-preview": None,
    "cubicweb-comment": ">= 1.6.3",
    "cubicweb-seo": None,
    "feedparser": None,
    "rdflib": None,
}
