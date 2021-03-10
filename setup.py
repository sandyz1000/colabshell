from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()


if __name__ == "__main__":
    setup(
        name="colabshell",
        scripts=["scripts/colabshell"],
        version="0.1.0",
        description="ColabShell - Run shell on Colab/Kaggle notebook!",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Sandip Dey",
        author_email="sandip.dey1988@yahoo.com",
        url="https://github.com/sandyz1000/colabshell",
        license="MIT License",
        packages=find_packages(),
        include_package_data=True,
        install_requires=["pyngrok>=5.0.0"],
        platforms=["linux", "unix"],
        python_requires=">3.5.2",
    )
