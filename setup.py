import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = f.read().splitlines()

setup(name='c2cgeoform',
      version='1.1.4',
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
      [paste.app_factory]
      main = c2cgeoform:main
      [console_scripts]
      initialize_c2cgeoform_db = c2cgeoform.scripts.initializedb:main
      """,
      )
