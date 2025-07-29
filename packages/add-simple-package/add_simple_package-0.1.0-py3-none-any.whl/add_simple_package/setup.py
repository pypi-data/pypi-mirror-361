from setuptools import setup, find_packages

setup(
    name='add_simple_package',
    version='0.1.0',
    description='Un petit package pour additionner deux nombres',
    author='cbi',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)

