from setuptools import setup, find_packages

setup(
    name="Dictionary107",
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "Dictionary107": ["etlex.txt"],
    },
    install_requires=[],
    author="",
    description="",
    python_requires=">=3.7",
)
