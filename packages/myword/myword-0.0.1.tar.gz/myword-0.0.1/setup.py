from setuptools import setup, find_packages

setup(
    name="myword",
    version="0.0.1",
    description="Myanmar (Burmese) Syllable, Word, and Phrase",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ye Kyaw Thu",
    author_email="yekyaw.thu@nectec.or.th",
    url="https://github.com/ye-kyaw-thu/myWord", 
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "cached_path",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)