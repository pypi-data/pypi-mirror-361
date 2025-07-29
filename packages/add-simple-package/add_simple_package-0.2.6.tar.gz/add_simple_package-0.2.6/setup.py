from setuptools import setup, find_packages
from pathlib import Path

readme = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name='add_simple_package',
    version='0.2.6',
    description='hello world de publication',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='cbi',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
     install_requires=[
        'numpy',
    ],
    python_requires='>=3.6',
)
