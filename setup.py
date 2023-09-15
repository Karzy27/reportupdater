from setuptools import setup

setup(
    name="reportupdater",
    version="0.1.0",
    description="reportupdater CLI",
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
            'enrich= enrich:entrypoint',
        ]
    },
    packages=["enrich"]
)