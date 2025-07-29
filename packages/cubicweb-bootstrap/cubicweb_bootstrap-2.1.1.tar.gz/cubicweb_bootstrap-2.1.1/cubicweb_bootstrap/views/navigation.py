"""bootstrap implementation of navigation components

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from logilab.common.decorators import monkeypatch

from logilab.mtconverter import xml_escape

from cubicweb_web.view import View
from cubicweb_web.component import NavigationComponent

from cubicweb_web.views.navigation import (
    NextPrevNavigationComponent,
    SortedNavigation,
    PageNavigation,
    PageNavigationSelect,
)
from cubicweb_bootstrap import CW_323

__docformat__ = "restructuredtext en"

NavigationComponent.page_link_templ = '<li><a href="%s" title="%s">%s</a></li>'
NavigationComponent.selected_page_link_templ = (
    '<li class="active"><a href="%s" title="%s">%s</a></li>'
)
NavigationComponent.previous_page_link_templ = NavigationComponent.page_link_templ
NavigationComponent.next_page_link_templ = NavigationComponent.page_link_templ
NavigationComponent.no_previous_page_link = (
    '<li class="disabled"><a href="#">«</a></li>'
)
NavigationComponent.no_next_page_link = '<li class="disabled"><a href="#">»</a></li>'
NavigationComponent.no_content_prev_link = "«"
NavigationComponent.no_content_next_link = "»"


@monkeypatch(NavigationComponent)
def render_link_back_to_pagination(self, w):
    "allow to come back to the paginated view"
    req = self._cw
    params = dict(req.form)
    basepath = req.relative_path(includeparams=False)
    del params["__force_display"]
    url = self.page_url(basepath, params)
    w(
        '<ul class="pagination"><li>'
        '<span><a href="%s">%s</a></span>'
        "</li></ul>"
        % (xml_escape(url), req._("back to pagination (%s results)") % self.page_size)
    )


@monkeypatch(NavigationComponent)
def render_link_display_all(self, w):
    "make a link to see them all"
    req = self._cw
    params = dict(req.form)
    self.clean_params(params)
    basepath = req.relative_path(includeparams=False)
    params["__force_display"] = 1
    params["__fromnavigation"] = 1
    url = self.page_url(basepath, params)
    w(
        '<ul class="pagination pull-right"><li>'
        '<span><a href="%s">%s</a></span>'
        "</li></ul>" % (xml_escape(url), req._("show %s results") % len(self.cw_rset))
    )


@monkeypatch(SortedNavigation)
def write_links(self, basepath, params, blocklist):
    """Return HTML for the whole navigation: `blocklist` is a list of HTML
    snippets for each page, `basepath` and `params` will be necessary to
    build previous/next links.
    """
    self.w('<ul class="pagination">')
    self.w("%s&#160;", self.previous_link(basepath, params), escape=False)
    self.w("%s", "".join(blocklist), escape=False)
    self.w("&#160;%s", self.next_link(basepath, params), escape=False)
    self.w("</ul>")


@monkeypatch(PageNavigation)
def call(self):
    """displays a resultset by page"""
    params = dict(self._cw.form)
    self.clean_params(params)
    basepath = self._cw.relative_path(includeparams=False)
    self.w('<ul class="pagination">')
    self.w("%s&#160;", self.previous_link(basepath, params), escape=False)
    self.w("&#160;".join(self.iter_page_links(basepath, params)), escape=False)
    self.w("&#160;%s", self.next_link(basepath, params), escape=False)
    self.w("</ul>")


NextPrevNavigationComponent.prev_icon = "&#8592;"
NextPrevNavigationComponent.next_icon = "&#8594;"


@monkeypatch(NextPrevNavigationComponent)
# Should be better done, but this works
def render_body(self, w):
    w('<div class="prevnext row">')
    w('<ul class="pager">')
    self.prevnext(w)
    w("</ul>")
    w("</div>")
    # w(u'<div class="clear"></div>')


@monkeypatch(NextPrevNavigationComponent)
def prevnext_div(self, w, type, cssclass, url, title, content):
    csscls = {"prev": "previous", "next": "next"}
    w('<li class="%s">' % csscls[type])
    w(
        '<a href="{}" title="{}">{}</a>'.format(
            xml_escape(url), xml_escape(title), content
        )
    )
    w("</li>")
    self._cw.html_headers.add_raw(f'<link rel="{type}" href="{xml_escape(url)}" />')


def do_paginate(view, rset=None, w=None, show_all_option=True, page_size=None):
    """write pages index in w stream (default to view.w) and then limit the
    result set (default to view.rset) to the currently displayed page if we're
    not explicitly told to display everything (by setting __force_display in
    req.form)
    """
    req = view._cw
    if rset is None:
        rset = view.cw_rset
    if w is None:
        w = view.w
    nav = req.vreg["components"].select_or_none(
        "navigation", req, rset=rset, page_size=page_size, view=view
    )
    if nav:
        if w is None:
            w = view.w
        if req.form.get("__force_display"):
            # allow to come back to the paginated view
            params = dict(req.form)
            basepath = req.relative_path(includeparams=False)
            del params["__force_display"]
            url = nav.page_url(basepath, params)
            w(
                '<span><a href="%s">%s</a></span>\n'
                % (
                    xml_escape(url),
                    req._("back to pagination (%s results)") % nav.page_size,
                )
            )
        else:
            # get boundaries before component rendering
            start, stop = nav.page_boundaries()
            nav.render(w=w)
            params = dict(req.form)
            nav.clean_params(params)
            # make a link to see them all
            if show_all_option:
                basepath = req.relative_path(includeparams=False)
                params["__force_display"] = 1
                params["__fromnavigation"] = 1
                url = nav.page_url(basepath, params)
                w(
                    '<span><a href="%s">%s</a></span>\n'
                    % (xml_escape(url), req._("show %s results") % len(rset))
                )
            rset.limit(offset=start, limit=stop - start, inplace=True)  # noqa


def paginate(view, show_all_option=True, w=None, page_size=None, rset=None):
    """paginate results if the view is paginable"""
    if view.paginable:
        do_paginate(view, rset, w, show_all_option, page_size)


# monkey patch base View class to add a .paginate([...])
# method to be called to write pages index in the view and then limit the result
# set to the current page


if not CW_323:
    View.do_paginate = do_paginate
    View.paginate = paginate
View.handle_pagination = False


@monkeypatch(PageNavigationSelect)
def call(self):  # noqa: F811
    params = dict(self._cw.form)
    self.clean_params(params)
    basepath = self._cw.relative_path(includeparams=False)
    self.w('<ul class="pagination">')
    self.w(self.previous_link(basepath, params))
    start, stop = self.page_boundaries()
    self.w(
        '<li><span><a class="dropdown-toggle" data-toggle="dropdown" href="#">'
        '%s<span class="caret"></span></a>',
        self.index_display(start, stop - 1),
    )
    self.w('<ul class="dropdown-menu" role="menu">')
    for option in self.iter_page_links(basepath, params):
        self.w(option)
    self.w("</ul></span></li>")
    self.w("&#160;%s", self.next_link(basepath, params), escape=False)
    self.w("</ul>")


PageNavigationSelect.page_link_templ = '<li><a href="%s" title="%s">%s</a></li>'
PageNavigationSelect.selected_page_link_templ = (
    '<li class="disabled"><a href="%s" title="%s">%s</a></li>'
)
