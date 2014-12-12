import os

from setuptools import setup, find_packages
from distutils.command.build_py import build_py as _build_py
from setuptools.command.develop import develop as _develop
from babel.messages.frontend import compile_catalog

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'colander',
    'colanderalchemy',
    'deform==2.0a2',
    'psycopg2',
    'geoalchemy2',
    'shapely',
    'pyproj',
    'lingua>=2.4',
    'babel',
    'webhelpers',
    'pyramid_beaker']


class compile_catalog_main(compile_catalog):
    """ Command which compiles the i18n files of c2cgeoform.
    """
    def finalize_options(self):
        self.directory = 'c2cgeoform/locale'
        self.domain = 'c2cgeoform'


class compile_catalog_pully(compile_catalog):
    """ Command which compiles the i18n files of the sample project.
    """
    def finalize_options(self):
        self.directory = 'c2cgeoform/pully/locale'
        self.domain = 'pully'


class build_py(_build_py):
    def run(self):
        self.run_command('compile_catalog_main')
        self.run_command('compile_catalog_pully')
        _build_py.finalize_options(self)
        _build_py.run(self)


class develop(_develop):
    def run(self):
        self.run_command('compile_catalog_main')
        self.run_command('compile_catalog_pully')
        _develop.run(self)

# overwrite the existing `build_py` and `develop` targets
cmdclass = {
    'build_py': build_py,
    'develop': develop,
    'compile_catalog_main': compile_catalog_main,
    'compile_catalog_pully': compile_catalog_pully
}

setup(name='c2cgeoform',
      version='0.0',
      description='c2cgeoform',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      package_data={'c2cgeoform': [
          'locale/*/LC_MESSAGES/*.mo', 'pully/locale/*/LC_MESSAGES/*.mo']},
      zip_safe=False,
      test_suite='c2cgeoform',
      install_requires=requires,
      cmdclass=cmdclass,
      entry_points="""\
      [paste.app_factory]
      main = c2cgeoform:main
      [console_scripts]
      initialize_c2cgeoform_db = c2cgeoform.scripts.initializedb:main
      """,
      )
