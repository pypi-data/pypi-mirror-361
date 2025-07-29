from setuptools import setup, find_packages

setup(
    name="axisbot",
    version="0.1.0",
    description="Python библиотека для ботов AxisMessenger (официальный API)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AxisMessenger Team",
    author_email="support@axismessenger.app",
    url="https://github.com/axismessenger/axisbot",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
) 