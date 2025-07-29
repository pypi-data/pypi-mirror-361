import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    setuptools.setup(
        name="atriumsports_sdk",
        version="2.1.1",
        author="Atrium Sports",
        author_email="python_dev@atriumsports.com",
        description="Python module for integration to Atrium Sports APIs",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.7",
        install_requires=[
            "requests",
            "paho-mqtt>=2.1.0",
            "python-dateutil>=2.8.2",
            "setuptools>=80.9.0",
            "urllib3>=2.1.0,<3.0.0",
            "pydantic>=2",
            "typing-extensions>=4.7.1",
            "aenum>=3.1.11",
            "pyjwt>=2.8.0",
        ],
    )
