from setuptools import setup, find_packages

setup(
    name="csvchatbot",
    version="0.1.0",
    description="Chat with your CSV files using OpenAI and LangChain",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Parth Kher",
    author_email="kherparth32@gmail.com",
    url="https://github.com/yourusername/csvchatbot",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0",
        "python-dotenv"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
