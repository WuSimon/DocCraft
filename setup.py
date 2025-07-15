from setuptools import setup, find_packages

setup(
    name='doccraft',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'doccraft = doccraft.cli:main',
        ],
    },
    # ... other metadata as needed ...
) 