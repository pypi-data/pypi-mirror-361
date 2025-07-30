import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="saz",
    version="0.0.11",  # 🔁 MUST BUMP VERSION for PyPI upload
    packages=["saz"],
    license="MIT",
    description="Tools for CSV cleaning and reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Saman Siadati",
    author_email="siadatisaman@gmail.com",
    url="https://github.com/samansiadati/saz",
    project_urls={
        "Bug Tracker": "https://github.com/samansiadati/saz/issues",
    },
    install_requires=["pandas"],
    keywords=["pandas", "csv", "data cleaning", "reporting", "saz"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)