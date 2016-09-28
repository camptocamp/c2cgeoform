import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'deform==2.0a2',
    'pyramid_beaker',
    'lingua>=2.4']

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
      zip_safe=False,
      test_suite='c2cgeoform',
      install_requires=requires,
      entry_points="""\
      [pyramid.scaffold]
        c2cgeoform=c2cgeoform.scaffolds:C2cgeoformTemplate
      """,
      )
