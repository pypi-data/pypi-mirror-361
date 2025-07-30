from setuptools import setup, find_packages

setup(
    name="iLaplace",
    version="0.4.4",
    author="Mohammad H. Rostami",
    author_email="MHRo.R84@Gmail.com",
    description="High-precision numerical inverse Laplace transform calculation library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/iLaplace",
    packages=find_packages(include=["iLaplace", "iLaplace.*"]),
    python_requires=">=3.7",
    install_requires=[
        "mpmath>=1.2.1",
        "sympy>=1.10",
        "numpy>=1.20",
        "matplotlib>=3.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Science/Research",
    ],
    license="MIT",
    include_package_data=True,
    keywords="inverse laplace transform numerical analysis mathematics",
)
