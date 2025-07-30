from setuptools import setup, find_packages

setup(
    name="ailogx",
    version="1.1.0",
    description="LLM-optimized structured logging and summarization for large-scale debugging.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kunwar Vikrant",
    author_email="kunwar.vikrant3@gmail.com",
    packages=find_packages(include=["ailogx", "ailogx.*"]),
    include_package_data=True,
    install_requires=[
        "tiktoken",
        "requests",
        "rich",
        "groq",
        "openai",
        "ollama",
    ],
    entry_points={
        "console_scripts": [
            "ailogx-summarize=ailogx.summarize:main"
        ]

    },
    license="Proprietary",
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
)
