from setuptools import setup, find_packages

setup(
    name="assher",
    version="0.2.0",
    author="Oleg Marin",
    author_email="wWolfovich@gmail.com",
    description="Async SSH/SFTP massive runner",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wWolfovich/aioqs",
    packages=find_packages(),
    install_requires=[
        "asyncssh>=1.12.0",
        "aioqs>=0.5.5",
        ]
    keywords="AIO async SSH SFTP aioqs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
        "Operating System :: OS Independent",
    ],
)

