# pylint: disable-msg=W0622
"""cubicweb-workcase application packaging information"""

modname = 'workcase'
distname = "cubicweb-%s" % modname

numversion = (1, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
description = "workcase component for the CubicWeb framework"
author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
           ]

__depends__ = {'cubicweb': '>= 4.5.2,<6.0.0'}
