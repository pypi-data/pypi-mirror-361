from setuptools import setup , find_packages

with open("README.md","r") as file:
    readme = file.read()

setup(
    name="Aiology",
    version="0.0.5",
    author="Seyed Moied Seyedi (Single Star)",
    packages=find_packages(),
    install_requires=[
        "requests","pypdf","arabic-reshaper","python-bidi","setuptools","chromadb==0.4.14","colorama"
    ],
    license="MIT",
    description="Ai library",
    long_description=readme,
    long_description_content_type="text/markdown"
)