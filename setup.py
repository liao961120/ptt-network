import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="liao961120", # Replace with your own username
    version="0.0.1",
    author="Yongfu Liao",
    author_email="liao961120@gmail.com",
    description="PTT Comments as Social Network Data",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/liao961120/ptt-network",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)