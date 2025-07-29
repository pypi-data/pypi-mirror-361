from setuptools import setup, find_packages

setup(
    name='etiennevar',
    version='1.0.4',
    description='Outil en ligne de commande pour résumer et visualiser les fichiers VCF',
    author='Etienne Kabongo',
    author_email='etienne.ntumba.kabongo@umontreal.ca',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'etiennevar = etiennevar.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    python_requires='>=3.7',
)

