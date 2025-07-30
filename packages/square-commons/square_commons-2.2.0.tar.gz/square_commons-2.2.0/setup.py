from setuptools import find_packages, setup

package_name = "square_commons"

setup(
    name=package_name,
    version="2.2.0",
    packages=find_packages(),
    install_requires=[
        "configparser>=6.0.0",
        "requests>=2.32.3",
        "pytest>=8.3.3",
        "pytest-mock>=3.14.0",
    ],
    extras_require={},
    author="thePmSquare",
    author_email="thepmsquare@gmail.com",
    description="helper module containing common functions for all my python modules.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url=f"https://github.com/thepmsquare/{package_name}",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
