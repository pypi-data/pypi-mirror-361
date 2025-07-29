from setuptools import setup, find_packages

setup(
    name="raglab_easygenius",
    version="0.1.0",
    description="A RAG project using raglib, OCR, and Qdrant",
    author="Jay & Abhishek",
    packages=find_packages(),
    install_requires=[
        "raglib",
        "pytesseract",
        "Pillow",
        "qdrant-client",
        "sentence-transformers"
    ],
    entry_points={
        "console_scripts": [
            "myragproject=version:main"
        ]
    },
    python_requires=">=3.7",
)
