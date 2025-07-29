from setuptools import setup, Extension
import sys
import pybind11

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

ext_modules = [
    Extension(
        'fex',
        sources=['fex.cpp', 'bindings.cpp'],
        include_dirs=[pybind11.get_include()],
        language='c++',
        extra_compile_args=['-O3', '-std=c++17'] if sys.platform != 'win32' else ['/O2', '/std:c++17'],
    ),
]

setup(
    name='fex-crypto',
    version='1.0b1',
    author='Bronio Int',
    author_email='bronio.int@example.com',
    description='FEX v1.0-beta: Fast Encryption eXchange (novel symmetric cipher)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BronioInt/fex',
    ext_modules=ext_modules,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    python_requires='>=3.6',
) 