"""bootstrap implementation of facets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb_web.views import facets

facets.FilterBox.bk_linkbox_template = '<div class="facet-action">%s</div>'
