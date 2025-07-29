"""
:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from logilab.common.decorators import monkeypatch

from cubicweb.schema import display_name
from cubicweb_web import view as cwview
from cubicweb_web.views.basetemplates import HTMLHeader

# do not wrap cell_calls with <div class="section">

cwview.View.add_div_section = False


@monkeypatch(cwview.View)
def field(self, label, value, row=True, show_label=True, w=None, tr=True, table=False):
    """read-only field"""
    if w is None:
        w = self.w
    w("<tr>")
    if show_label and label:
        if tr:
            label = display_name(self._cw, label)
        w("<th>%s</th>" % label)
    if not (show_label and label):
        w('<td colspan="2">%s</td>' % value)
    else:
        w("<td>%s</td>" % value)
    w("</tr>")


class BSHTMLHeader(HTMLHeader):
    def stylesheets(self):
        super().stylesheets()
        # add cw compatibility stylesheets
        if self._cw.vreg.config["cw_compatibility"]:
            for css in self._cw.uiprops["CW_COMPAT_STYLESHEETS"]:
                self._cw.add_css(css, localfile=False)


def registration_callback(vreg):
    components = ((BSHTMLHeader, HTMLHeader),)
    vreg.register_all(globals().values(), __name__, [new for (new, old) in components])
    for new, old in components:
        vreg.register_and_replace(new, old)
