from setuptools import setup, find_packages

setup(
    name='twlog',
    version='0.51.0',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests',
    ],
    extras_require={
        'dev': [
            'jupyter',
        ],
    },
    entry_points={
        'console_scripts': [
            'my_command = twlog.module:main_func',
        ],
    },
    # ... 他のメタデータ ...
)
