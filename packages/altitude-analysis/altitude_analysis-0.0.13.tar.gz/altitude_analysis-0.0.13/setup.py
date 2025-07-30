from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import platform
import os

# Platform-specific configuration
extra_compile_args = []
extra_link_args = []
include_dirs = []
library_dirs = []
libraries = ['curl', 'ssl', 'crypto', 'jansson']

if platform.system() == "Darwin":  # macOS
    # Get Homebrew prefix
    brew_prefix = os.popen('brew --prefix').read().strip()

    # Add paths for curl, openssl, jansson
    include_dirs.extend([
        f'{brew_prefix}/include',
        f'{brew_prefix}/opt/curl/include',
        f'{brew_prefix}/opt/openssl/include',
        f'{brew_prefix}/opt/jansson/include'
    ])

    library_dirs.extend([
        f'{brew_prefix}/lib',
        f'{brew_prefix}/opt/curl/lib',
        f'{brew_prefix}/opt/openssl/lib',
        f'{brew_prefix}/opt/jansson/lib'
    ])

    extra_compile_args.extend(['-O3', '-Wall', '-Wextra'])
elif platform.system() == "Windows":
    extra_compile_args = ["/O2"]
else:  # Linux
    extra_compile_args = ["-O3", "-Wall", "-Wextra"]

# Core C extension
core_extension = Extension(
    'altitude_analysis.core',
    sources=['src/altitude_analysis/core.c'],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    define_macros=[('NDEBUG', '1')],
)


# Custom build class
class CustomBuild(build_ext):
    def build_extensions(self):
        # Set compiler options before building
        for ext in self.extensions:
            ext.extra_compile_args = extra_compile_args
            ext.extra_link_args = extra_link_args
        super().build_extensions()


# Read long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='altitude_analysis',
    version='0.0.13',
    author='tokifyko',
    description='Advanced aircraft altitude analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://ya.com',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    ext_modules=[core_extension],
    cmdclass={'build_ext': CustomBuild},
    install_requires=[
        'pandas>=1.0',
        'requests>=2.25',
        'scikit-learn>=1.0',
        'numpy>=1.20',
        'pycurl>=7.45'  # For CURL integration
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'altitude-analysis = altitude_analysis:main'
        ]
    },
    zip_safe=False,
    setup_requires=['wheel', 'setuptools>=40.8.0'],
)
