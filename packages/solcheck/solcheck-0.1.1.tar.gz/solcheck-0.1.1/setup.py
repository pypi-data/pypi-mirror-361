from setuptools import setup, find_packages

setup(
    name="solcheck",                         # 🔹 Name on PyPI
    version="0.1.1",                            # 🔹 Semantic version
    author="Your Name",
    author_email="you@example.com",
    description="A smart contract auditing tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/faizqowy/solcheck",  # Optional: GitHub repo
    packages=find_packages(),                   # Finds audit_tools/
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "slither-analyzer"
    ],
)
