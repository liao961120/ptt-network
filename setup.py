import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

packages = [
    "pttnet",
]

setuptools.setup(
    name="pttnet", # Replace with your own username
    version="0.0.1",
    author="Yongfu Liao",
    author_email="liao961120@gmail.com",
    description="PTT Comments as Social Network Data",
    long_description="PTT Comments as Social Network Data",
    long_description_content_type="text/markdown",
    url="https://github.com/liao961120/ptt-network",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

#%%
import setuptools
setuptools.find_packages()