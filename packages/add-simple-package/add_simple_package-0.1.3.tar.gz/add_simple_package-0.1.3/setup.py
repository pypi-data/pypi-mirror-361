from setuptools import setup, find_packages
from pathlib import Path

readme = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name='add_simple_package',
    version='0.1.3',
    description='Un petit package pour additionner deux nombres',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='cbi',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
