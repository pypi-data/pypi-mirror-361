from setuptools import setup, find_packages
from pathlib import Path

VERSION = '1.0.10'
DESCRIPTION = 'A Python library for Creole text preprocessing'
LONG_DESCRIPTION = (Path(__file__).parent / "README.md").read_text()

setup(
    name='creolenltk',
    version=VERSION,
    packages=find_packages(exclude=('test*',)),
    package_data={
        'creolenltk.data': ['*.txt'],
        'creolenltk.pos': ['model-best/**', 'model-best/**/*'],
    },
    install_requires=[
        'beautifulsoup4>=4.9.3',
        'nltk>=3.6.2',
        'spacy>=3.7.2',
        'conllu',
    ],
    author='John Clayton',
    author_email='jclaytonblanc@gmail.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/bjclayton/CreoleNLTK.git',
    keywords=['python', 'nlp', 'creole', 'haitian creole',
              'natural language processing', 'text preprocessing'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license_files=('LICENSE',),
    python_requires='>=3.6',
)
