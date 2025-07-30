from setuptools import setup, find_packages

setup(
    name="skylos",
    version="2.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "inquirer>=3.0.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    entry_points={
        "console_scripts": [
            "skylos=skylos.cli:main",
        ],
    },
)