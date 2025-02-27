from setuptools import setup, find_packages

setup(
    name="cloudpilot",
    version="1.0.0",
    description="CloudPilot - AI-Driven Infrastructure Optimization",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "kubernetes",
        "torch",
        "scikit-learn",
        "PyYAML",
        "prometheus-api-client",
    ],
    entry_points={
        "console_scripts": [
            "cloudpilot=cli:main",
        ],
    },
)
