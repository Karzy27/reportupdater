from setuptools import setup

setup(
    name="infoCompany",
    version="0.1.0",
    description="InfoCompany CLI",
    classifiers=["Programming Language :: Python :: 3.11"],
    install_requires=[
        "requests",
    ],
    extras_require={
        "TEST": [
            "pytest"
        ]
    },
    entry_points={
        'console_scripts': [
            'enrich= infoCompany:entrypoint',
        ]
    },
    packages=["infoCompany"]
)