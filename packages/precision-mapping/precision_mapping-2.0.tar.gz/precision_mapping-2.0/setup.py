from setuptools import setup, find_packages

setup(
    name='precision_mapping',
    version='2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cortex_mapping = cortex_mapping.main:main',
            'hipp_mapping = hipp_mapping.main:main',
        ],
    },
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'nibabel',
    ],
    python_requires='>=3.6',
    package_data={
        'cortex_mapping': ['data/*'],
        'hipp_mapping': ['data/*'],
    },
)
