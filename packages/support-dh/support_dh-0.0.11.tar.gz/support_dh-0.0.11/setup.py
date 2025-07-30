import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="support-dh",
    version="0.0.11",
    author="astatine",
    author_email="astatine.147@gmail.com", 
    description="decorate text, etc", 
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/astatinegithub/support-dh.git",
    install_requires=[ 
    "setuptools>=63.4.1", 
    ],
    include_package_data=True,
    packages = setuptools.find_packages(include=['support_dh', 'support_dh.*']),
    python_requires=">=3.9.13", 
)