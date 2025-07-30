from setuptools import setup, find_packages

setup(
    name="puf-cli",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "pyyaml>=5.4.0",
        "pymongo>=4.0.0",
        "python-dotenv>=0.19.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "pydantic>=2.0.0",
        "passlib>=1.7.4",
        "python-jose>=3.3.0",
        "bcrypt>=3.2.0",
        "aiofiles>=0.8.0",
        "motor>=2.5.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0"
    ],
    extras_require={
        'tensorflow': ['tensorflow>=2.8.0'],
        'torch': ['torch>=1.10.0'],
        'sklearn': ['scikit-learn>=0.24.0'],
        'all': [
            'tensorflow>=2.8.0',
            'torch>=1.10.0',
            'scikit-learn>=0.24.0'
        ]
    },
    entry_points={
        "console_scripts": [
            "puf=puf.cli:cli",
        ],
    },
    author="Pooja Patel",
    author_email="poojapatel013@gmail.com",
    description="Python Universal Framework for Model Version Control - A comprehensive tool for managing ML models",
    long_description="""# PUF - Python Universal Framework for Model Version Control

PUF is a comprehensive tool for managing machine learning models, offering version control, performance tracking,
and easy deployment capabilities. It supports various ML frameworks including TensorFlow, PyTorch, and scikit-learn.

## Features
- Model version control
- Performance metrics tracking
- Easy model deployment
- Framework agnostic
- Web interface for visualization
- CLI for easy management
""",
    long_description_content_type="text/markdown",
    url="https://github.com/PoojasPatel013/puf",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Version Control",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False
)
