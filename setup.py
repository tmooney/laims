from setuptools import setup, find_packages
import versioneer

setup(
    name='laims',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'click>=7.0',
        'SQLAlchemy==1.1.11',
        'logzero==1.3.1',
        'dataset==1.1.2',
        'psycopg2-binary==2.8.2',
        'Jinja2==2.10.1',
        'Crimson @ https://github.com/hall-lab/crimson/tarball/8d0791c129e0b7c138c5d26c82952a069c063c27'
    ],
    entry_points={
            'console_scripts': [
            'laims=laims.cli:cli',
            ]
        }
)
