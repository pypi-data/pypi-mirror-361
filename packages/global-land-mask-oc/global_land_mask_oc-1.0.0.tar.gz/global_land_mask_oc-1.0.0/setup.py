import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="global-land-mask-oc",
    version="1.0.0",
    author="feng qiao",
    author_email="qiaofengwy@163.coms",
    description="Global land mask for satellite ocean color remote sensing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fengqiaogh/global-land-mask-oc",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
