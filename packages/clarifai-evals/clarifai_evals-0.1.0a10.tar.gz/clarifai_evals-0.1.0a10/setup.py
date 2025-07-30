import re

import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

with open("./clarifai_evals/__init__.py") as f:
  content = f.read()
_search_version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content)
assert _search_version
version = _search_version.group(1)

with open("requirements.txt", "r") as fh:
  install_requires = fh.read().split("\n")

if install_requires and install_requires[-1] == "":
  # Remove the last empty line
  install_requires = install_requires[:-1]

packages = setuptools.find_namespace_packages(include=["clarifai_evals*"])

setuptools.setup(
    name="clarifai_evals",
    version=f"{version}",
    author="Clarifai",
    author_email="support@clarifai.com",
    description=
    "Clarifai Evals is an SDK for evaluating AI models, providing a structured framework to benchmark model performance using predefined and custom evaluation templates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Clarifai/clarifai-evals",
    packages=packages,
    classifiers=[
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        # "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
    python_requires=">=3.9",
    install_requires=install_requires,
    include_package_data=True,
)
