from setuptools import setup, find_packages

setup(
    name='stackl-cli',
    version='0.0.1-alpha5',
    py_modules=['stackl', 'commands', 'context'],
    packages=find_packages(),
    install_requires=[
        'stackl-client==1.0.2', 'pyYAML==5.3', 'Click==7.0', 'tabulate==0.8.6'
    ],
    entry_points='''
        [console_scripts]
        stackl=stackl:cli
    ''',
)
