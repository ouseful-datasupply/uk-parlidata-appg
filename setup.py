from setuptools import setup

setup(
    name="appg",
    version='0.0.1',
    packages=['appg'],
    install_requires=[
        'Click',
        'requests',
        'lxml',
        'pandas',
        'beautifulsoup4',
        'html5lib', 
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        appg=appg.cli:webscrape
    ''',
)