"""bootstrap html helpers

:organization: Logilab
:copyright: 2013-2022 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"


class DropDownBox:
    ul_template = """
    <a class="dropdown-toggle %(klass)s" data-toggle="dropdown" href="#">
    %(title)s<span class="caret"></span></a>
    <ul class="dropdown-menu" role="menu">%(actions)s</ul>"""

    li_template = "<li>%(link)s<li>"

    def __init__(self, title, actions, klass=""):
        self.title = title
        self.actions = actions
        self.klass = klass

    def render(self, w):
        if not len(self.actions):
            return ""
        w(
            self.ul_template
            % {
                "title": self.title,
                "klass": self.klass,
                "actions": "".join(self.render_items()),
            }
        )

    def render_items(self):
        for item in self.actions:
            yield self.li_template % {"link": self._item_value(item)}

    def _item_value(self, item):
        return item
