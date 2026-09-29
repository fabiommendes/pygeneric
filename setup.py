import sys
from setuptools import setup, find_packages

# Version
version = '1.0.0b0'

# Cython stuff
setup_kwargs = {'cmdclass': {}}
if 'PyPy' not in sys.version:
    try:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext
    except ImportError:
        import warnings
        warnings.warn(
            'Please install Cython to compile faster versions of pygeneric')
    else:
        try:
            setup_kwargs.update(ext_modules=cythonize('src/generic/*.pyx'))
            setup_kwargs['cmdclass']['build_ext'] = build_ext
        except ValueError:
            pass


setup(
    # Basic info
    name='pygeneric',
    version=version,
    author='Fábio Macêdo Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='http://github.com/fabiommendes/pygeneric/',
    description='Generalize functools.singledispatch to multiple arguments.',
    long_description=open('README.rst').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[],
    extras_require={'dev': ['pytest', 'manuel']},

    # Other configurations
    platforms='any',
    **setup_kwargs
)
