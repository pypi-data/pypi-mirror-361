from setuptools import setup, find_packages

setup(
    name="distributed-pg-lock",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "sqlalchemy>=1.4",
        "tenacity>=8.0"
    ],
    extras_require={
        "test": ["pytest", "psycopg2-binary"]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={},
)