Updating the messages

Extract messages from the templates:

    ./.build/venv/bin/pot-create -c lingua.cfg -o c2cgeoform/locale/c2cgeoform.pot c2cgeoform/ext/deform_ext.py c2cgeoform/templates/ c2cgeoform/views.py

Update catalog files:

    cd c2cgeoform/locale/
    msgmerge --update fr/LC_MESSAGES/c2cgeoform.po c2cgeoform.pot
    msgmerge --update de/LC_MESSAGES/c2cgeoform.po c2cgeoform.pot

Compile translations to \*.mo files:

    make compile-catalog

Or:

    msgfmt c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po --output-file=c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.mo
    msgfmt c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po --output-file=c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.mo
