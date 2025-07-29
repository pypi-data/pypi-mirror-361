import os.path as osp
from setuptools import setup, find_packages


cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'readme.rst')).read()
CHANGELOG = open(osp.join(cdir, 'changelog.rst')).read()

version_fpath = osp.join(cdir, 'morphi', 'version.py')
version_globals = {}
with open(version_fpath) as fo:
    exec(fo.read(), version_globals)

install_requires = [
    'Babel',
    'pytz',
    'speaklater',
    'tomli',
]
develop_requires = testing_requires = [
    'flake8',
    'pytest',
    'pytest-cov',
    'tox'
]

setup(
    name="morphi",
    version=version_globals['VERSION'],
    setup_requires=['Babel'],
    description="i18n services for libraries and applications",
    long_description='\n\n'.join((README, CHANGELOG)),
    author="Level 12 Developers",
    author_email="devteam@level12.io",
    url='https://github.com/level12/morphi',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license='BSD',
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
    entry_points = """
    [distutils.commands]
    compile_catalog = babel.messages.frontend:compile_catalog
    extract_messages = babel.messages.frontend:extract_messages
    init_catalog = babel.messages.frontend:init_catalog
    update_catalog = babel.messages.frontend:update_catalog
    compile_json = morphi.messages.frontend:CompileJson
    """,
    extras_require={
        'develop': develop_requires,
        'tests': testing_requires
    },
)
