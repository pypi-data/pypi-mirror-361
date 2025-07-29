"""bootstrap implementation of reledit

:organization: Logilab
:copyright: 2013-2022 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb_web.views.reledit import AutoClickAndEditFormView

AutoClickAndEditFormView._addzone = ' <span class="glyphicon glyphicon-plus"></span>'
AutoClickAndEditFormView._deletezone = (
    ' <span class="glyphicon glyphicon-remove"></span>'
)
AutoClickAndEditFormView._editzone = ' <span class="glyphicon glyphicon-pencil"></span>'

try:
    from cubicweb_inlinedit.views import reledit
except ImportError:
    pass
else:
    reledit.ReleditRelationFormHandler._addzone = (
        ' <span class="glyphicon glyphicon-plus"></span>'
    )
    reledit.ReleditFormHandler._editzone = (
        ' <span class="glyphicon glyphicon-pencil"></span>'
    )
    reledit.ReleditEntityFormHandler._deletezone = (
        ' <span class="glyphicon glyphicon-remove"></span>'
    )
