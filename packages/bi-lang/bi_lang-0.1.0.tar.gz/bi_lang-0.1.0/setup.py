from setuptools import setup, find_packages

setup(
    name="bi-lang",
    version="0.1.0",
    author="Roy Pery",
    description="Python interpreter for Tsoding's B language",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/royp/bi-lang",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    entry_points={
        "console_scripts": ["bi=bi.__main__:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
)
