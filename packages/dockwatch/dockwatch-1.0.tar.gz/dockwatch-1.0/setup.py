from setuptools import setup, find_packages

setup(
    name="dockwatch",
    version="1.0.0",
    description="Docker container monitoring and image analysis CLI tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Saimon Bhuiyan",
    author_email="bsse1402@iit.du.ac.bd",
    packages=find_packages(),
    install_requires=[
        "docker",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "dockwatch = dockwatch.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Ubuntu",
        "Intended Audience :: Students",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
