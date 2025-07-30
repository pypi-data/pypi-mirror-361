from setuptools import setup, find_packages

setup(
    name="datacmp",
    version="2.0.0",
    author="Moustafa Mohamed",
    author_email="moustafa.mh.mohamed@gmail.com",
    description="A powerful and configurable library for exploratory data analysis (EDA) and data cleaning for machine learning workflows.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MoustafaMohamed01/datacmp",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "tabulate>=0.8.0",
        "PyYAML>=6.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
