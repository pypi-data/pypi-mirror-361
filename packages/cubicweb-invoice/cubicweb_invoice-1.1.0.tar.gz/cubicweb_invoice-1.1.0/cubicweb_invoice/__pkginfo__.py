# pylint: disable=W0622
"""cubicweb-invoice application packaging information"""


modname = 'cubicweb_invoice'
distname = 'cubicweb-invoice'

numversion = (1, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'Logilab'
author_email = 'contact@logilab.fr'
description = 'invoice component for the CubicWeb framework'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>=4.5.2,<6.0.0',
    'cubicweb_web': '>=1.4.2,<2.0.0',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python :: 3',
    'Programming Language :: JavaScript',
]
