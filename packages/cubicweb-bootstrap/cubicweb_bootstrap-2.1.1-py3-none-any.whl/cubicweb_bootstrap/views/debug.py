"""bootstrap implementation of base debug views

:organization: Logilab
:copyright: 2013-2022 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from time import strftime, localtime

from logilab.common.decorators import monkeypatch

from logilab.mtconverter import xml_escape

from cubicweb import BadConnectionId
from cubicweb_web.views import debug


def dict_to_html(w, dict):
    # XHTML doesn't allow emtpy <ul> nodes
    if dict:
        w("<dl>")
        for key in sorted(dict):
            w(
                "<dt>%s</dt><dd>%s</dd>"
                % (xml_escape(str(key)), xml_escape(repr(dict[key])))
            )
        w("</dl>")


@monkeypatch(debug.ProcessInformationView)
def call(self, **kwargs):
    req = self._cw
    dtformat = req.property_value("ui.datetime-format")
    _ = req._
    repo = req.cnx.repo
    # generic instance information
    self.w("<h2>%s</h2>", _("Instance"))
    self.w('<table class="table table-striped table-condensed">')
    for key, value in (
        (_("config type"), self._cw.vreg.config.name),
        (_("config mode"), self._cw.vreg.config.mode),
        (_("instance home"), self._cw.vreg.config.apphome),
    ):
        self.w("<tr><th>%s</th><td>%s</td></tr>", key, value)
    self.w("</table>")
    vcconf = repo.get_versions()
    self.w("<h3>%s</h3>", _("versions configuration"))
    self.w('<table class="table table-striped table-condensed">')
    self.w(
        "<tr><th>%s</th><td>%s</td></tr>",
        "CubicWeb",
        vcconf.get("cubicweb", _("no version information")),
    )
    for cube in sorted(self._cw.vreg.config.cubes()):
        cubeversion = vcconf.get(cube, _("no version information"))
        self.w("<tr><th>%s</th><td>%s</td></tr>", cube, cubeversion)
    self.w("</table>")
    # repository information
    self.w("<h2>%s</h2>", _("Repository"))
    self.w("<h3>%s</h3>", _("resources usage"))
    self.w('<table class="table table-striped table-condensed">')
    stats = self._cw.call_service("repo_stats")
    for element in sorted(stats):
        self.w(
            "<tr><th>%s</th><td>%s %s</td></tr>",
            element,
            xml_escape(str(stats[element])),
            element.endswith("percent") and "%" or "",
        )
    self.w("</table>")
    # web server information
    self.w("<h2>%s</h2>", _("Web server"))
    self.w('<table class="table table-striped table-condensed">')
    self.w("<tr><th>%s</th><td>%s</td></tr>", _("base url"), req.base_url())
    self.w("<tr><th>%s</th><td>%s</td></tr>", _("data directory url"), req.datadir_url)
    self.w("</table>")
    from cubicweb_web.application import SESSION_MANAGER

    if SESSION_MANAGER is not None and req.user.is_in_group("managers"):
        sessions = SESSION_MANAGER.current_sessions()
        self.w("<h3>%s</h3>", _("opened web sessions"))
        if sessions:
            self.w("<ul>")
            for session in sessions:
                if hasattr(session, "cnx"):
                    # cubicweb < 3.19
                    if not session.cnx:
                        self.w("<li>%s (NO CNX)</li>", session.sessionid)
                        continue
                    try:
                        last_usage_time = session.cnx.check()
                    except BadConnectionId:
                        self.w("<li>%s (INVALID)</li>", session.sessionid)
                        continue
                else:
                    # cubicweb >= 3.19
                    last_usage_time = session.mtime
                self.w(
                    "<li>%s (%s: %s)<br/>",
                    session.sessionid,
                    _("last usage"),
                    strftime(dtformat, localtime(last_usage_time)),
                )
                dict_to_html(self.w, session.data)
                self.w("</li>")
            self.w("</ul>")
        else:
            self.w("<p>%s</p>", _("no web sessions found"))


@monkeypatch(debug.RegistryView)
def call(self, **kwargs):  # noqa: F811
    self.w("<h2>%s</h2>", self._cw._("Registry's content"))
    keys = sorted(self._cw.vreg)
    url = xml_escape(self._cw.url())
    self.w(
        "<p>%s</p>\n",
        " - ".join(f'<a href="{url}#{key}">{key}</a>' for key in keys),
        escape=False,
    )
    for key in keys:
        if key in ("boxes", "contentnavigation"):  # those are bw compat registries
            continue
        self.w('<h3 id="%s">%s</h3>', key, key)
        if self._cw.vreg[key]:
            values = sorted(self._cw.vreg[key].items())
            self.wview(
                "pyvaltable",
                pyvalue=[(key, xml_escape(repr(val))) for key, val in values],
            )
        else:
            self.w("<p>Empty</p>\n")
