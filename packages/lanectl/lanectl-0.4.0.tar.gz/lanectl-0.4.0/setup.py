from setuptools import setup, find_packages
# we go dumm
setup(
    name="lanectl",
    version="0.4.0",
    description="embed scripting engine by Infrared LLC.",
    author="infrared",
    author_email="faneorg.official@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/infraredhuh/lanectl",
    package_data={"lanectl": ["py.typed"]},
    install_requires=[
        "discord.py",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
