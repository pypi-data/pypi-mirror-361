from setuptools import setup, find_packages
install_requires=[
"pandas",
"numpy",
"matplotlib",
"matplotlib-venn",
"tqdm"

            ]


setup(
    name="cellblender",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    author="Amirhossein Sakhteman",
    author_email="amirhossein.sakhteman@tume.de",
    description="Tools for selection of cell lines",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)
