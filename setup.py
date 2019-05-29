from setuptools import setup, find_packages
import versioneer

setup(
    name='laims',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'click==6.7',
        'SQLAlchemy==1.1.11',
        'Crimson>0.3.0',
        'logzero==1.3.1',
        'dataset==1.1.2',
        'psycopg2-binary==2.8.2',
        'Jinja2==2.10.1'
    ],
    dependency_links=['https://github.com/ernfrid/crimson/tarball/verifybamid#egg=Crimson-0.4.0'],
    entry_points={
            'console_scripts': [
            'laims=laims.cli:cli',
            ]
        }
)
