Release 0.5.0
===================

What's new in 0.5.0

Clean up
--------

A huge clean up has been done on the HTML.

The following CSS classes and IDs have been removed ::

 <div class="mainInfo">
 <div class="boxBody">
 <tr class="entityfield">

The following classes and IDs have been renamed ::

 <div class="primary_entities"> -> <table class=".cw-table-primary-entity" >


CubicWeb compatibility stylesheets
----------------------------------

As long as cubicweb-bootstrap does not provide exhaustive Bootstrap
coverage of CubicWeb HTML, we need some CSS roles to compensate this
lack (e.g. we cannot add the `form-control` class on all CW-generated
inputs).

Those rules have been moved into `cubes.bootstrap.cw_compat.css` which
should shrink to an empty file at the end of this process.

If you want to contribute to the bootstrapification of CW, desactivate
the inclusion of `cubes.bootstrap.cw_compat.css` by setting the
all-in-one option `cw_compatibility` to `False`.
