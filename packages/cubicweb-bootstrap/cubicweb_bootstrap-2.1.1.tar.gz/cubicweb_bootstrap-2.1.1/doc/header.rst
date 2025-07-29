.. -*- coding: utf-8 -*-

Header
=======

Breadcrumbs
------------

Breadcrumbs separator must be set by HTML ::

  .breadcrumb > li + li:before {
    color: #CCCCCC;
    content: "/ ";
    padding: 0 5px;
  }