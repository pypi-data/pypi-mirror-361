"""bootstrap implementation of baseviews

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb_web.views import baseviews

baseviews.ListView.listtag = "ul"


@monkeypatch(baseviews.ListView)
def call(self, klass="list-striped", title=None, subvid=None, listid=None, **kwargs):
    """display a list of entities by calling their <item_vid> view

    :param listid: the DOM id to use for the root element
    """
    if subvid is None and "subvid" in self._cw.form:
        subvid = self._cw.form.pop("subvid")  # consume it
    if listid:
        listid = ' id="%s"' % listid
    else:
        listid = ""
    if title:
        self.w('<div%s class="%s"><h4>%s</h4>\n', listid, klass or "", title)
        self.w('<%s class="%s">\n', self.listtag, klass or "")
    else:
        self.w('<%s%s class="%s">\n', self.listtag, listid, klass or "")
    for i in range(self.cw_rset.rowcount):
        self.cell_call(row=i, col=0, vid=subvid, klass=klass, **kwargs)
    self.w("</%s>\n", self.listtag)
    if title:
        self.w("</div>\n")


@monkeypatch(baseviews.ListView)
def cell_call(self, row, col=0, vid=None, klass=None, **kwargs):
    self.w('<li class="%s">', "odd" if row % 2 else "even")
    self.wview(self.item_vid, self.cw_rset, row=row, col=col, vid=vid, **kwargs)
    self.w("</li>\n")


@monkeypatch(baseviews.SameETypeListView)
def call(self, klass="list-striped", **kwargs):  # noqa: F811
    showtitle = kwargs.pop("showtitle", "vtitle" not in self._cw.form)
    if showtitle:
        self.w("<h1>%s</h1>", self.title)
    if klass:
        self.w('<ul class="%s">\n', klass)
    else:
        self.w("<ul>\n")
    for i in range(len(self.cw_rset)):
        self.w('<li class="%s">', "odd" if i % 2 else "even")
        self._cw.view(self.item_vid, self.cw_rset, row=i, col=0, w=self.w)
        self.w("</li>")
    self.w("</ul>\n")


@monkeypatch(baseviews.MetaDataView)
def cell_call(self, row, col):  # noqa: F811
    _ = self._cw._
    entity = self.cw_rset.get_entity(row, col)
    self.w('<p class="text-right"><small>')
    if self.show_eid:
        self.w("%s #%s - ", entity.dc_type(), entity.eid)
    if entity.modification_date != entity.creation_date:
        self.w("<span>%s</span> ", _("latest update on"))
        self.w(
            '<span class="value">%s</span>, ',
            self._cw.format_date(entity.modification_date),
        )
    # entities from external source may not have a creation date (eg ldap)
    if entity.creation_date:
        self.w("<span>%s</span> ", _("created on"))
        self.w(
            '<span class="value">%s</span>', self._cw.format_date(entity.creation_date)
        )
    if entity.creator:
        if entity.creation_date:
            self.w(" <span>%s</span> ", _("by"))
        else:
            self.w(" <span>%s</span> ", _("created_by"))
        self.w('<span class="value">%s</span>', entity.creator.name())
    if entity.cw_source:
        source = entity.cw_source[0]
        if source.name != "system":
            self.w(" (<span>%s</span>", _("cw_source"))
            self.w(' <span class="value">%s</span>)', source.name)
    self.w("</small></p>")
