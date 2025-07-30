from setuptools import setup, find_packages

setup(
    name="moodylang",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "moodylang = moody.cli:main"
        ],
    },
    author="Your Name",
    description="A polite emotional programming language interpreter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)