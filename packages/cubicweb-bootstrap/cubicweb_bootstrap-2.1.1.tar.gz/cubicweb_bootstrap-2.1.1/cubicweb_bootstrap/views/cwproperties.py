"""bootstrap implementation of cwproperty view

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from cubicweb_web.views.cwproperties import SystemCWPropertiesForm, make_togglable_link


@monkeypatch(SystemCWPropertiesForm)
def wrap_main_form(self, group, label, form):
    label += ' <span class="caret"></span>'
    status = self._group_status(group)
    cssclass = "panel-body %s" % status if status else "panel-body"
    self.w(
        '<div class="panel panel-default">' '<div class="panel-heading">%s</div>\n',
        make_togglable_link("fieldset_" + group, label),
        escape=False,
    )
    self.w('<div class="%s" id="fieldset_%s">', cssclass, group)
    self.w(form)
    self.w("</div>")
    self.w("</div>")


@monkeypatch(SystemCWPropertiesForm)
def wrap_grouped_form(self, group, label, objects):
    label += ' <span class="caret"></span>'
    status = self._group_status(group)
    cssclass = "panel-body %s" % status if status else "panel-body"
    self.w(
        '<div class="panel panel-default">' '<div class="panel-heading">%s</div>\n',
        make_togglable_link("fieldset_" + group, label),
        escape=False,
    )
    self.w('<div class="%s" id="fieldset_%s">', cssclass, group)

    sorted_objects = sorted(
        (self._cw.__(f"{group}_{o}"), o, f) for o, f in objects.items()
    )
    for label, oid, form in sorted_objects:
        self.wrap_object_form(group, oid, label, form)
    self.w("</div>")
    self.w("</div>")
