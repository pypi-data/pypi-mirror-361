Génération de la documentation
==============================

Sphinx
______

Sphinx est un générateur de documentation qui permet de convertir des
fichiers au format reStructuredText en HTML, PDF, EPUB, etc.

Pour rengréner la documentation sous format HTML utilisez la commande
::

   make html

Note : ce paquet contient la documentation au format HTML généré avec Sphinx
dans le répertoire `doc/_build/html`.


PDF
---

L'utilitaire `rst2pdf` permet de générer la documentation sous format PDF ::

   rst2pdf index_odt.rst -o bootstrap.pdf

ODT
---

L'utilitaire `rst2odt` permet de générer la documentation sous format ODT ::

   rst2odt index_odt.rst bootstrap.odt

Il convient de régénérer la table de matière afin de mettre à jour
l'index des pages.
