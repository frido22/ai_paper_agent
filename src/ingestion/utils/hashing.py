import hashlib
import json
from typing import Dict

class Hasher:
    @staticmethod
    def hash_content(metadata: Dict[str, str]) -> str:
        """
        Create a hash of the metadata to uniquely identify a file.
        """
        # Convert metadata to JSON string with sorted keys for consistency
        content_str = json.dumps(metadata, sort_keys=True)
        # Create SHA-256 hash
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
