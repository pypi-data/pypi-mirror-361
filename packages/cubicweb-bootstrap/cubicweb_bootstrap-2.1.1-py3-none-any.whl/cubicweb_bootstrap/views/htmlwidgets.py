"""bootstrap implementation of htmlwidgets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb_web import htmlwidgets
from cubicweb_web.component import Separator


@monkeypatch(Separator)
def render(self, w):
    w('<li class="divider"></li>')


def bwcompatible_render_item(w, item):
    if hasattr(item, "render"):
        if getattr(item, "newstyle", False):
            if isinstance(item, Separator):
                item.render(w)
            else:
                w("<li>")
                item.render(w)
                w("</li>")
        else:
            item.render(w)  # XXX displays <li> by itself
    else:
        w("<li>%s</li>" % item)


@monkeypatch(htmlwidgets.BoxMenu)
def _render(self):
    tag = "li" if self.isitem else "div"
    self.w('<%s class="dropdown">', tag)
    self.w(
        '<a class="dropdown-toggle" data-toggle="dropdown" href="#">'
        "%s&nbsp;"
        '<span class="caret"></span>'
        "</a>",
        self.label,
        escape=False,
    )
    self.w('<ul class="dropdown-menu">')
    for item in self.items:
        bwcompatible_render_item(self.w, item)
    self.w("</ul>")
    self.w("</%s>", tag)
