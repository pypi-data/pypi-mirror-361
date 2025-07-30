from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ollama-flow",
    version="0.1.0",
    author="Warren",
    author_email="warren@example.com",
    description="A Python library for the Ollama API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ollama-flow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="ollama, ai, llm, api, chat, generate, embed",
    project_urls={
        "Bug Reports": "https://github.com/your-username/ollama-flow/issues",
        "Source": "https://github.com/your-username/ollama-flow",
        "Documentation": "https://github.com/your-username/ollama-flow#readme",
    },
) 