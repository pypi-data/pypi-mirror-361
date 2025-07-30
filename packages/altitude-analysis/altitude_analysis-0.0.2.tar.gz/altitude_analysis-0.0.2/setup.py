from setuptools import setup, find_packages

setup(
    name='altitude-analysis',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0',
        'requests>=2.25',
        'scikit-learn>=1.0',
        'numpy>=1.20'
    ],
    entry_points={
        'console_scripts': [
            'altitude-analysis = src:main'
        ]
    },
    author='tokifyko',
    description='Advanced aircraft altitude analysis with multiple noise detection methods',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering'
    ],
    python_requires='>=3.8',
)