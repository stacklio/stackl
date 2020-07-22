from setuptools import setup, find_packages

setup(
    name='stackl-cli',
    version='0.2.0rc1',
    py_modules=['stackl', 'commands', 'context'],
    packages=find_packages(),
    install_requires=[
        'stackl-client==0.2.0rc2', 'pyYAML==5.3', 'Click==7.0',
        'mergedeep==1.3.0', 'tabulate==0.8.6', 'glom==19.10.0'
    ],
    entry_points='''
        [console_scripts]
        stackl=stackl:cli
    ''',
)
