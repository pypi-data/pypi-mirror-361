# PUF - Python Universal Framework for Model Version Control

A comprehensive tool for managing machine learning models, offering version control, performance tracking,
and easy deployment capabilities. It supports various ML frameworks including TensorFlow, PyTorch, and scikit-learn.

## Features
- Git-like CLI for model version control
- GitHub-style web interface with analytics
- Upload and version control ML models
- Track model versions with timestamps
- List all available model versions
- Detailed model analytics and performance tracking
- Star/unstar models
- GitHub integration
- Branching and tagging support for model versions
- Remote repository support
- Performance metrics tracking
- Version comparison
- Model statistics and metrics visualization

## Components

1. Backend API (FastAPI)
2. Command Line Interface (CLI)
3. Web Interface (React)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Start the backend server:
```bash
python main.py
```

4. Start the frontend development server:
```bash
cd frontend
npm start
```

## Web Interface

The web interface provides a modern, GitHub-like experience:

1. Access the web interface at `http://localhost:3000`
2. Upload new models through the web form
3. View all model versions in a table format
4. Dark/light mode support

## API Endpoints

- `POST /models/upload`: Upload a new model version
  - Parameters:
    - `model_file`: The model file to upload
    - `version` (optional): Custom version string
    - `description` (optional): Version description

- `GET /models/versions`: List all model versions

- `GET /models/{version}`: Get information about a specific version

## Project Structure

```
puf/
├── src/              # Source code
│   ├── puf/         # Core package
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── core.py
│   └── frontend/    # Web interface
│       ├── static/
│       ├── templates/
│       └── app.py
├── setup.py         # Package configuration
└── requirements.txt # Dependencies
```

## Installation

```bash
# Install from PyPI
pip install puf-cli

# Or install from source
pip install .
```

## Usage

### CLI Commands
```bash
# Initialize a new repository
puf init

# Add a model
puf add model.h5

# Create a new commit
puf commit -m "Initial model version"

# Create a new branch
puf branch feature-branch

# Tag a version
puf tag v1.0

# Push to remote
puf push

# View model analytics
puf analytics model_name
```
    │   │   ├── ModelList.js
    │   │   ├── Navbar.js
    │   │   └── UploadModel.js
    │   └── App.js
    └── package.json
```
