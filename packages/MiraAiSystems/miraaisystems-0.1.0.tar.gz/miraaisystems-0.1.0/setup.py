from setuptools import setup, find_packages

setup(
    name="MiraAiSystems",                
    version="0.1.0",                     
    author="MoonTech",
    author_email="gammermood@gmail.com",      # Optional
    description="MoonTech’s AI Library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MoonTechYT/MiraAiSystems",  # Optional but pro
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
