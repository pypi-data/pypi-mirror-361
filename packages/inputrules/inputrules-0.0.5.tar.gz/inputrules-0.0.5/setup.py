from setuptools import setup, find_packages

setup(
    name="inputrules",
    version="0.0.5",
    packages=find_packages(),
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    description="A robust Python library for validating and sanitizing input data with predefined rules and filters",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Alvaro De Leon",
    author_email="info@alvarodeleon.com",
    url="https://github.com/alvarodeleon/inputrules",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
    ],
    keywords="validation, sanitization, input, forms, json, security, filters",
    python_requires=">=3.6",
) 


