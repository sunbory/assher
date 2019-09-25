from setuptools import setup, find_packages

<<<<<<< HEAD
with open("README.md", "r") as rf:
=======
with open("README.md", "rt", encoding="utf8") as rf:
>>>>>>> 1b55c8e1c577263886fb95ccb474df80a233a623
    long_description = rf.read()
    
setup(
    name="assher",
    version="0.7",
    author="Oleg Marin",
    author_email="wWolfovich@gmail.com",
    description="Async SSH/SFTP massive runner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wWolfovich/aioqs",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "asyncssh>=1.12.0",
        "aioqs>=0.5.5",
        ],
    keywords="AIO async SSH SFTP aioqs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
        "Operating System :: OS Independent",
    ],
)

