from setuptools import setup, find_packages

setup(
    name="azerbaijani_stopwords",
    version="0.1.0",
    author="Cafarli",
    description="A lightweight Python package providing Azerbaijani stopwords for NLP tasks.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
