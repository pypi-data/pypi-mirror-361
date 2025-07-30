from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neuron-memory",
    version="0.1.6",
    author="NeuronMemory Team",
    author_email="danushidk507@gmail.com",
    description="Advanced Memory Engine for LLMs and AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NeuronMemory/neuronmemory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "full": [
            "weaviate-client>=3.24.0",
            "pinecone-client>=2.2.0",
            "elasticsearch>=8.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neuron-memory=neuron_memory.cli:main",
        ],
    },
) 