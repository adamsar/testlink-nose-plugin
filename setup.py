import os
from setuptools import setup, find_packages

try:
    README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except Exception as e:
    README = "Readme unavailable"

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

test_requires = [
    "mock"
    ]
requires = [
    'testlink-python-api'
    ]
setup(
    name='testlink-nose',
    version='0.1',
    packages=['testlink_nose'],
    package_dir = {'testlink_nose': 'src/testlink_nose'},
    include_package_data=True,
    license='BSD License',  # example license
    description="""
    A nose plugin to be update testlink with proper test information
    """,
    long_description=README,
    url='https://github.com/adamsar',
    author='Andrew Adams',
    author_email='adamsar@gmail.com',
    install_requires=requires,
    test_requires=test_requires,
    dependency_links = ['https://github.com/adamsar/testlink-python-api/tarball/master#egg=testlink-python-api-0.1'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
