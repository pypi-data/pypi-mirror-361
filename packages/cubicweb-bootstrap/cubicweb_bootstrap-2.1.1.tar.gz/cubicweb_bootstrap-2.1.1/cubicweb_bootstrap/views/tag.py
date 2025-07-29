"""bootstrap implementation of tag cube

:organization: Logilab
:copyright: 2015 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

try:
    from cubicweb_tag.views import SimilarityBox
except ImportError:
    pass
else:
    from logilab.common.decorators import monkeypatch
    from cubicweb_web import tags

    @monkeypatch(SimilarityBox)
    def render_body(self, w):
        # bs customization begins
        self._cw.view("list", self.cw_rset, w=w, klass="list-unstyled")
        # bs customization ends
        rql = self.rql % "" % {"x": self.entity.eid}
        title = self._cw._("entities similar to %s") % self.entity.dc_title()
        url = self._cw.build_url("view", rql=rql, vtitle=title)
        w("<div>[%s]</div>" % tags.a(self._cw._("see all"), href=url))
