import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqlalchemy-awildtechno",
    version="0.0.1",
    author="Alex Weavers",
    author_email="ajdweavers@gmail.com",
    description="A distributed queue using SQLAlchemy and a database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/awildtechno/alchq",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['sqlalchemy']
)
