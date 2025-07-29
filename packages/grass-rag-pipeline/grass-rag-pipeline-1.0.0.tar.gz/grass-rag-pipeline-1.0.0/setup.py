from setuptools import setup, find_packages

def read_requirements():
    try:
        with open("requirements.txt", "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "torch>=2.0.0",
            "transformers>=4.30.0", 
            "sentence-transformers>=2.2.0",
            "lancedb>=0.3.0",
            "loguru>=0.7.0",
            "requests>=2.28.0",
            "numpy>=1.21.0"
        ]

setup(
    name="grass-rag-pipeline",
    version="1.0.0",
    author="Sachin NK",
    author_email="snkodikara52@gmail.com",
    description="High-performance RAG pipeline for GRASS GIS command generation",
    long_description="GRASS GIS RAG Pipeline - High-performance chatbot for GRASS GIS commands",
    long_description_content_type="text/markdown",
    url="https://github.com/Sachin-NK/grass-rag-pipeline",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "grass-rag=grass_rag.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)