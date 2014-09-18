Updating the messages

Extract messages from the templates:

    ./.build/venv/bin/pot-create -c lingua.cfg -o c2cgeoform/pully/locale/pully.pot c2cgeoform/pully

Update catalog files:

    cd c2cgeoform/pully/locale/
    msgmerge --update fr/LC_MESSAGES/pully.po pully.pot

Compile translations to *.mo files:

    make install

Or:

    msgfmt c2cgeoform/pully/locale/fr/LC_MESSAGES/pully.po --output-file=c2cgeoform/pully/locale/fr/LC_MESSAGES/pully.mo