from setuptools import setup, find_packages

setup(
    name="MiraAiSystems",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "google-generativeai",
    ],
    author="MoonTech",
    description="An AI system to translate text using Gemini AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
