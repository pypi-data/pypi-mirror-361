from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Directly list dependencies instead of reading requirements.txt
requirements = [
    "attrs==23.2.0",
    "colorama==0.4.6",
    "iniconfig==2.0.0",
    "jsonschema==4.22.0",
    "jsonschema-specifications==2023.12.1",
    "numpy==1.26.3",
    "packaging==23.2",
    "pandas==2.2.0",
    "plotly==5.18.0",
    "pluggy==1.5.0",
    "polars==0.20.7",
    "pyarrow==15.0.0",
    "python-dateutil==2.8.2",
    "pytz==2024.1",
    "referencing==0.35.1",
    "rpds-py==0.18.0",
    "six==1.16.0",
    "tenacity==8.2.3",
    "tzdata==2023.4",
]

setup(
    name="petri-net-core",
    version="0.1.0",
    author="lhcnetop",
    author_email="lhcneto@gmail.com",
    description="Core Petri net simulation and analysis framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lhcnetop/petri_net",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
) 