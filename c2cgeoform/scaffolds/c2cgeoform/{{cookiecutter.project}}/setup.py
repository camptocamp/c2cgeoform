import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.txt")) as f:
    README = f.read()

setup(
    name="{{cookiecutter.project}}",
    version="0.0",
    description="{{cookiecutter.project}}",
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="",
    author_email="",
    url="",
    keywords="web wsgi bfg pylons pyramid",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="{{cookiecutter.package}}",
    entry_points="""\
      [paste.app_factory]
      main = {{cookiecutter.package}}:main
      [console_scripts]
      initialize_{{cookiecutter.package}}_db = {{cookiecutter.package}}.scripts.initializedb:main
      """,
)
