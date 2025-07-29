from setuptools import setup, find_packages

setup(
    name="R-AScan",
    version="0.0.5",
    description="Rusher Automatic Scan",
    author="HarshXor",
    author_email="harshxor@incrustwerush.org",
    python_requires=">=3.10",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.1",
        "colorama>=0.4.6",
        "beautifulsoup4>=4.12.3",
        "pandas>=1.3.5",
        "scikit-learn>=1.1.3",
        "numpy>=1.21.0"
    ],
    entry_points={
        "console_scripts": [
            "R-AScan=rascan.app:main",
        ],
    },
    package_data={
        "rascan.resources": ["*.*"],
        "rascan.module": ["*.*"],
        "rascan.scanners": ["*.*"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
