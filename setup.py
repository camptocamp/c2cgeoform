import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'babel',
    'deform>=2.0.4',
    'lingua>=2.4',
    'pyramid',
    'pyramid_beaker',
    'pyramid_chameleon',
    'pyramid_jinja2'
]

setup(
    name='c2cgeoform',
    version='2.0',
    description='c2cgeoform',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Camptocamp',
    author_email='info@camptocamp.com',
    url='https://github.com/camptocamp/c2cgeoform',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='c2cgeoform',
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main=c2cgeoform:main',
        ],
        'pyramid.scaffold': [
            'c2cgeoform=c2cgeoform.scaffolds:C2cgeoformTemplate',
        ],
    },
)
