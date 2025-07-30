from setuptools import setup, find_packages

setup(
    name="djmigrator",
    version="1.0.7",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Django>=4.2"],
    author="Umakaran",
    author_email="umakaranuma1126@gmail.com",
    description="Smart Django migration manager.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/djmigrator",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
