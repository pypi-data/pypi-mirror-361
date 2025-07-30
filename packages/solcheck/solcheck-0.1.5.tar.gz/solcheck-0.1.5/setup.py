from setuptools import setup, find_packages

setup(
    name="solcheck",                    
    version="0.1.5",                            
    author="Faiz Qowy",
    author_email="faizislamicqowy@gmail.com",
    description="A smart contract auditing tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/faizqowy/solcheck", 
    packages=find_packages(),                   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "slither-analyzer",
        "py-solc-x"
    ],
)
