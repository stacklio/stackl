from setuptools import setup, find_packages

__version__ = "0.3.1"

setup(
    name='stackl-cli',
    version=__version__,
    py_modules=['stackl', 'commands', 'context'],
    packages=find_packages(),
    install_requires=[
        f'stackl-client==0.3.0', 'pyYAML==5.3', 'Click==7.0',
        'mergedeep==1.3.0', 'tabulate==0.8.6', 'glom==19.10.0'
    ],
    entry_points='''
        [console_scripts]
        stackl=stackl:cli
    ''',
)
