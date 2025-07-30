from setuptools import setup, find_packages

setup(
    name="bngmodule",
    version="1.1",
    packages=find_packages(),
    install_requires=["pyttsx3","psutil"],
    author="saleh",
    description="A library for simple sockets and making malware very, very easy",
    url="https://github.com/salehbngpy",
)
