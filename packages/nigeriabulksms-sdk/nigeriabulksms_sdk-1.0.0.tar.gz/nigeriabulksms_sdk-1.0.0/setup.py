from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nigeriabulksms-sdk",
    version="1.0.0",
    author="Timothy Dake",
    author_email="timdake4@gmail.com",
    description="A Python SDK for the NigeriaBulkSMS API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timothydake/nigeriabulksms-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/timothydake/nigeriabulksms-python-sdk/issues",
        "Documentation": "https://github.com/timothydake/nigeriabulksms-python-sdk#readme",
        "Source Code": "https://github.com/timothydake/nigeriabulksms-python-sdk",
    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="sms, bulk sms, nigeria, messaging, api, sdk, voice, tts",
    include_package_data=True,
    zip_safe=False,
)

