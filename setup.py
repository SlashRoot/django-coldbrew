from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')
CHANGES = read('CHANGES.rst')

setup(
    name = "django-coldbrew",
    packages = find_packages(),
    version = "0.5",
    author = "slashRoot Tech Group",
    author_email = "info@slashrootcafe.com",
    url = "https://github.com/SlashRoot/django-coldbrew",
    description = "Django Template Tags to compile CoffeeScript inline or from a file.",
    long_description = "\n\n".join([README, CHANGES]),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = ["coffeescript"],
)
