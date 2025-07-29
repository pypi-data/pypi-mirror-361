# copyright 2013-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.
"""bootstrap implementation of forms"""

__docformat__ = "restructuredtext en"


from cubicweb_web.views.forms import FieldsForm
from cubicweb_web.views.autoform import AutomaticEntityForm

# Forms
FieldsForm.needs_js += ("cubes.bootstrap.edition.js",)
FieldsForm.needs_css = ()
FieldsForm.cssclass = AutomaticEntityForm.cssclass = "form-horizontal"
