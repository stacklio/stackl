from setuptools import setup, find_packages

setup(
    name='stackl-cli',
    version='0.0.1-alpha9',
    py_modules=['stackl', 'commands', 'context'],
    packages=find_packages(),
    install_requires=[
        'stackl-client==1.0.12', 'pyYAML==5.3', 'Click==7.0',
        'tabulate==0.8.6', 'glom==19.10.0'
    ],
    entry_points='''
        [console_scripts]
        stackl=stackl:cli
    ''',
)
