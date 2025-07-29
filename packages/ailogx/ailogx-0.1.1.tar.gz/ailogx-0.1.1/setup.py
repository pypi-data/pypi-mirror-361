from setuptools import setup, find_packages

setup(
    name="ailogx",
    version="0.1.1",
    description="LLM-optimized structured logging and summarization for large-scale debugging.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kunwar Vikrant",
    author_email="kunwar.vikrant3@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "tiktoken",
        "requests",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "ailogwise-summarize=ailogwise.summarize:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
