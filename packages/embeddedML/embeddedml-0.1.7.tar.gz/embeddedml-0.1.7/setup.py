from setuptools import setup, find_packages

setup(
    name="embeddedML",
    version="0.1.7",
    description="Optimized Machine Learning Library for Embedded Systems",
    author="Halil Hüseyin Çalışkan",
    author_email="caliskanhalil815@gmail.com",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy==1.26.4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
