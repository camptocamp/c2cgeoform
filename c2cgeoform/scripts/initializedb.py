import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import Base
from ..settings import apply_local_settings


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    """
    Function called when the "initialize_c2cgeoform_db" script is run. It
    creates in the database the tables declared in the model of the test
    application ("pully").
    """
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    apply_local_settings(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')

    # FIXME this is needed for now so the "Pully" model is in the
    # metadata object when create_all is called.
    from ..pully.model import ExcavationPermission  # flake8: noqa
    
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
