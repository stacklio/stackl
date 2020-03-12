from setuptools import setup, find_packages

setup(
    name='stackl-cli',
    version='0.0.1-alpha2',
    py_modules=['stackl', 'commands', 'context'],
    packages=find_packages(),
    install_requires=[
        'stackl-client',
        'pyYAML',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        stackl=stackl:cli
    ''',
)
