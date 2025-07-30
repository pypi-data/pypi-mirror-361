import os
import json
import hashlib
from datetime import datetime
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class PufRepo:
    def __init__(self, mongodb_uri: Optional[str] = None):
        """Initialize PUF repository."""
        self.puf_dir = ".puf"
        self.objects_dir = os.path.join(self.puf_dir, "objects")
        self.refs_dir = os.path.join(self.puf_dir, "refs")
        self.config_file = os.path.join(self.puf_dir, "config.json")
        
        # MongoDB setup
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client.puf_db
        self.models = self.db.models
        self.users = self.db.users
        self.remotes = self.db.remotes  # Add remotes collection

    def init(self, user_info: Dict[str, str]) -> None:
        """Initialize a new PUF repository with user information."""
        if os.path.exists(self.puf_dir):
            raise Exception("Repository already initialized")

        os.makedirs(self.puf_dir)
        os.makedirs(self.objects_dir)
        os.makedirs(self.refs_dir)

        # Save user info to MongoDB
        user_id = self.users.insert_one({
            "name": user_info.get("name", ""),
            "email": user_info.get("email", ""),
            "created_at": datetime.utcnow()
        }).inserted_id

        # Create config
        config = {
            "user_id": str(user_id),
            "remote": "http://localhost:8000",
            "created_at": datetime.utcnow().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def add_model(self, model_path: str, metadata: Dict[str, Any]) -> str:
        """Add a model file to version control."""
        if not os.path.exists(model_path):
            raise Exception(f"Model file {model_path} does not exist")

        # Calculate file hash
        file_hash = self._get_file_hash(model_path)
        
        # Copy file to objects
        object_path = os.path.join(self.objects_dir, file_hash)
        if not os.path.exists(object_path):
            shutil.copy2(model_path, object_path)

        # Save model info to MongoDB
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        model_info = {
            "hash": file_hash,
            "filename": os.path.basename(model_path),
            "user_id": config["user_id"],
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "size_bytes": os.path.getsize(model_path)
        }

        self.models.insert_one(model_info)
        return file_hash

    def get_model_versions(self, model_name: str) -> list:
        """Get all versions of a model."""
        return list(self.models.find(
            {"filename": model_name},
            {"hash": 1, "metadata": 1, "created_at": 1}
        ).sort("created_at", -1))

    def get_user_models(self, user_id: str) -> list:
        """Get all models for a user."""
        return list(self.models.find(
            {"user_id": user_id},
            {"hash": 1, "filename": 1, "metadata": 1, "created_at": 1}
        ).sort("created_at", -1))

    @staticmethod
    def _get_file_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def close(self):
        """Close MongoDB connection."""
        self.client.close()

    def compare_versions(self, version1: str, version2: str) -> dict:
        """Compare two model versions and return their differences."""
        model1 = self.models.find_one({"metadata.version": version1})
        model2 = self.models.find_one({"metadata.version": version2})

        if not model1 or not model2:
            raise ValueError(f"One or both versions not found: {version1}, {version2}")

        # Basic comparison
        comparison = {
            'metrics': [],
            'performance': {}
        }

        # Example metrics to compare (you can expand this)
        metrics_to_compare = [
            {'name': 'Size', 'key': 'size_bytes'},
            {'name': 'Accuracy', 'key': 'metadata.accuracy'},
            {'name': 'Parameters', 'key': 'metadata.parameters'}
        ]

        for metric in metrics_to_compare:
            value1 = self._safe_get(model1, metric['key'], 0)
            value2 = self._safe_get(model2, metric['key'], 0)

            comparison['metrics'].append({
                'name': metric['name'],
                'value1': value1,
                'value2': value2,
                'difference': (value2 - value1) / max(value1, 1) if value1 or value2 else 0
            })

        return comparison

    def get_version_info(self, version: str) -> dict:
        """Get detailed information about a specific model version."""
        model = self.models.find_one({"metadata.version": version})

        if not model:
            raise ValueError(f"Version {version} not found")

        return {
            'version': version,
            'filename': model.get('filename', 'Unknown'),
            'hash': model.get('hash', 'N/A'),
            'size_bytes': model.get('size_bytes', 0),
            'created_at': model.get('created_at', 'Unknown'),
            'metadata': model.get('metadata', {})
        }

    def _safe_get(self, obj: dict, key: str, default=None):
        """Safely get nested dictionary values."""
        keys = key.split('.')
        for k in keys:
            if isinstance(obj, dict):
                obj = obj.get(k, {})
            else:
                return default
        return obj if obj != {} else default

    def add_remote(self, name: str, url: str):
        """Add a new remote repository."""
        # Validate URL
        if not url.startswith(('http://', 'https://', 'git://')):
            raise ValueError("Invalid remote URL. Must start with http://, https://, or git://")
        
        # Store remote in MongoDB
        remote_config = {
            'name': name,
            'url': url,
            'created_at': datetime.utcnow()
        }
        
        # Check if remote with same name already exists
        existing_remote = self.remotes.find_one({'name': name})
        if existing_remote:
            self.remotes.replace_one({'name': name}, remote_config)
        else:
            self.remotes.insert_one(remote_config)
        
        # Save to local config file
        config_path = Path.home() / '.puf' / 'config'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'a') as f:
            f.write(f"remote.{name}.url {url}\n")

    def list_remotes(self) -> dict:
        """List all configured remotes."""
        remotes = {}
        for remote in self.remotes.find():
            remotes[remote['name']] = remote['url']
        return remotes

    def remove_remote(self, name: str):
        """Remove a remote repository."""
        result = self.remotes.delete_one({'name': name})
        
        if result.deleted_count == 0:
            raise ValueError(f"Remote '{name}' not found")
        
        # Remove from local config file
        config_path = Path.home() / '.puf' / 'config'
        if config_path.exists():
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            with open(config_path, 'w') as f:
                for line in lines:
                    if not line.startswith(f"remote.{name}.url"):
                        f.write(line)

    def sync_with_remote(self, remote_name: str):
        """Synchronize local repository with a remote."""
        remote = self.remotes.find_one({'name': remote_name})
        if not remote:
            raise ValueError(f"Remote '{remote_name}' not found")
        
        # Placeholder for actual sync logic
        # This would involve:
        # 1. Authenticating with remote
        # 2. Fetching model metadata
        # 3. Pulling/pushing models
        print(f"Syncing with remote: {remote['url']}")
        # Actual implementation would depend on your backend API
