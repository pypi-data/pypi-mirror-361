from setuptools import setup, find_packages

setup(
    name="file_size_formatter",
    version="1.0.0",
    description="Convert bytes into human-readable file sizes (KB, MB, GB) with precision control.",
    author="Your Name",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
