from setuptools import setup, find_packages

setup(
    name="mltt-resolver",
    version="0.1.0.0.1",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        'test': [
            'pytest>=8.3.4',
            'hypothesis>=6.122.3',
        ],
    },
    author="ytfh44",
    author_email="3118918283@qq.com",
    description="A Martin-Löf Type Theory implementation in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ytfh44/mltt-resolver",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 