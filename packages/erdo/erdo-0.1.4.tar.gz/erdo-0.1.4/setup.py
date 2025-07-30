from setuptools import find_packages, setup
import os

def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r') as f:
        return f.read().strip()

setup(
    name="erdo",
    version=get_version(),
    description="Erdo Agent SDK for building AI agents",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
    ],
    include_package_data=True,
)
