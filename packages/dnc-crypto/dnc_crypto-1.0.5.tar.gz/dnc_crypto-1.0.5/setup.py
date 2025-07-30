import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dnc_crypto",
    version="1.0.5",
    author="Mohammadmoein Pisodeh",
    author_email="mmoeinp3@gmail.com",
    description="An innovative, multi-layered dynamic network cipher.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/your_username/dnc_crypto",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'cryptography',
        'networkx',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    python_requires='>=3.7',
)