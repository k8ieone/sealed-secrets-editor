import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sedit",
    version="0.0.1",
    author="k8ieone",
    author_email="k8ie@firemail.cc",
    description="Easily edit sealed-secrets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/k8ieone/sealed-secrets-editor",
    project_urls={
        "Bug Tracker": "https://github.com/k8ieone/sealed-secrets-editor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=["sedit"]),
    entry_points={
        "console_scripts": [
            "sedit = sedit.main:main"
        ]
    },
    install_requires=["PyYAML"],
    python_requires=">=3.6"
)
