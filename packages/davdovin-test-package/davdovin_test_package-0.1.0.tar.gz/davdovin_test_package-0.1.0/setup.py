from setuptools import setup, find_packages

setup(
    name="davdovin_test_package",
    version="0.1.0",
    author="Danil Vdovin",
    author_email="davdovin32@gmail.com",
    description="Простой пример пакета",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
