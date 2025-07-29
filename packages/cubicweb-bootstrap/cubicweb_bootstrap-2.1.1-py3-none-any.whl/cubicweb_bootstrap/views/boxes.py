"""bootstrap implementation of boxes

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.utils import wrap_on_write
from cubicweb_web.views import boxes

from cubicweb_bootstrap import CW_325

boxes.SearchBox.formdef = (
    '<form action="%(action)s" id="search_box" class="navbar-form" role="search">\n'
    '  <input id="norql" type="text" accesskey="q" tabindex="%(tabindex1)s"'
    '    title="search text" value="%(value)s" name="rql"'
    '    class="search-query form-control" placeholder="%(searchlabel)s"/>\n'
    '  <input type="hidden" name="__fromsearchbox" value="1" />\n'
    '  <input type="hidden" name="subvid" value="tsearch" />\n'
    "</form>\n"
)


@monkeypatch(boxes.SearchBox)
def render_body(self, w):
    # Don't display search box title, just display the search box body
    if self._cw.form.pop("__fromsearchbox", None):
        rql = self._cw.form.get("rql", "")
    else:
        rql = ""
    w(
        self.formdef
        % {
            "action": self._cw.build_url("view"),
            "tabindex1": self._cw.next_tabindex() if not CW_325 else "",
            "value": xml_escape(rql),
            "searchlabel": self._cw._("Search"),
        }
    )


@monkeypatch(boxes.ContextualBoxLayout)
def render(self, w):
    if self.init_rendering():
        view = self.cw_extra_kwargs["view"]
        w(
            '<div class="panel panel-default %s %s" id="%s">'
            % (self.cssclass, view.cssclass, view.domid)
        )
        with wrap_on_write(
            w, '<div class="panel-heading"><div class="panel-title">', "</div></div>"
        ) as wow:
            view.render_title(wow)
        w('<div class="panel-body">')
        view.render_body(w)
        # We dissapear the boxFooter CSS place holder, as shadows
        # or effect will be made with CSS
        w("</div></div>\n")
