from setuptools import setup, find_packages

setup(
    name='stackli',
    version='0.1',
    py_modules=['stackli'],
    install_requires=[
        'stackl-client',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        stackli=stackli:cli
    ''',
)
