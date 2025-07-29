"""bootstrap implementation of base components

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: https://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb_web import component

from cubicweb_bootstrap import monkeypatch_default_value

monkeypatch_default_value(component.CtxComponent.render_items, "klass", "list-unstyled")
