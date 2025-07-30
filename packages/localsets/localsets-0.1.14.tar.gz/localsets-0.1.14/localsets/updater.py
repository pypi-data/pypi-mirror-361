"""
Data updater for Pokemon random battle data.
"""

import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import time

from .formats import FORMATS

logger = logging.getLogger(__name__)


class DataUpdater:
    """
    Handles updating Pokemon random battle data from GitHub.
    """
    
    def __init__(self, cache_dir: Path):
        """
        Initialize DataUpdater.
        
        Args:
            cache_dir: Directory to store cached data
        """
        self.cache_dir = cache_dir
        self.github_raw_base = "https://raw.githubusercontent.com/pkmn/randbats/main/data"
        self.github_api_base = "https://api.github.com/repos/pkmn/randbats/contents/data"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'localsets/0.1.0'
        })
    
    def update_formats(self, formats: List[str]) -> List[str]:
        """
        Update data for specified formats.
        
        Args:
            formats: List of format names to update
            
        Returns:
            List of successfully updated formats
        """
        updated_formats = []
        
        for format_name in formats:
            if format_name not in FORMATS:
                logger.warning(f"Unknown format: {format_name}")
                continue
            
            try:
                if self._update_format(format_name):
                    updated_formats.append(format_name)
                    logger.info(f"Updated {format_name}")
                else:
                    logger.warning(f"No update needed for {format_name}")
                    
            except Exception as e:
                logger.error(f"Failed to update {format_name}: {e}")
        
        return updated_formats
    
    def _update_format(self, format_name: str) -> bool:
        """
        Update a single format.
        
        Args:
            format_name: Format name to update
            
        Returns:
            True if updated, False if no update needed
        """
        # Get current metadata
        current_metadata = self._get_current_metadata(format_name)
        if current_metadata is None:
            logger.warning(f"No current metadata for {format_name}")
            return False
        
        # Get remote metadata
        remote_metadata = self._get_remote_metadata(format_name)
        if remote_metadata is None:
            logger.warning(f"Failed to get remote metadata for {format_name}")
            return False
        
        # Check if update is needed
        if self._is_update_needed(current_metadata, remote_metadata):
            # Download new data
            if self._download_format_data(format_name):
                # Download stats data
                self._download_format_stats(format_name)
                # Save new metadata
                self._save_metadata(format_name, remote_metadata)
                return True
        
        return False
    
    def _get_current_metadata(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get current metadata for a format."""
        metadata_file = self.cache_dir / f"{format_name}_metadata.json"
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read metadata for {format_name}: {e}")
            return None
    
    def _get_remote_metadata(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get remote metadata for a format."""
        try:
            url = f"{self.github_api_base}/{format_name}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get remote metadata for {format_name}: {e}")
            return None
    
    def _is_update_needed(self, current: Dict[str, Any], remote: Dict[str, Any]) -> bool:
        """Check if update is needed based on metadata."""
        # Compare SHA
        current_sha = current.get('sha')
        remote_sha = remote.get('sha')
        
        if current_sha != remote_sha:
            return True
        
        # Compare timestamps if available
        current_updated = current.get('updated_at')
        remote_updated = remote.get('updated_at')
        
        if current_updated and remote_updated:
            try:
                current_time = datetime.fromisoformat(current_updated.replace('Z', '+00:00'))
                remote_time = datetime.fromisoformat(remote_updated.replace('Z', '+00:00'))
                return remote_time > current_time
            except Exception:
                pass
        
        return False
    
    def _download_format_data(self, format_name: str) -> bool:
        """Download format data from GitHub."""
        try:
            url = f"{self.github_raw_base}/{format_name}.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Validate JSON
            data = response.json()
            
            # Save to cache
            cache_file = self.cache_dir / f"{format_name}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download data for {format_name}: {e}")
            return False
    
    def _download_format_stats(self, format_name: str) -> bool:
        """Download format stats data from GitHub."""
        try:
            url = f"{self.github_raw_base}/stats/{format_name}.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Validate JSON
            stats_data = response.json()
            
            # Save to cache
            stats_file = self.cache_dir / f"{format_name}_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Downloaded stats for {format_name}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to download stats for {format_name}: {e}")
            return False
    
    def _save_metadata(self, format_name: str, metadata: Dict[str, Any]):
        """Save metadata for a format."""
        try:
            metadata_file = self.cache_dir / f"{format_name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata for {format_name}: {e}")
    
    def force_update(self, formats: List[str]) -> List[str]:
        """
        Force update of formats regardless of metadata.
        
        Args:
            formats: List of format names to update
            
        Returns:
            List of successfully updated formats
        """
        updated_formats = []
        
        for format_name in formats:
            if format_name not in FORMATS:
                continue
            
            try:
                if self._download_format_data(format_name):
                    # Download stats data
                    self._download_format_stats(format_name)
                    # Get and save metadata
                    metadata = self._get_remote_metadata(format_name)
                    if metadata:
                        self._save_metadata(format_name, metadata)
                    updated_formats.append(format_name)
                    logger.info(f"Force updated {format_name}")
                    
            except Exception as e:
                logger.error(f"Failed to force update {format_name}: {e}")
        
        return updated_formats
    
    def get_update_status(self, format_name: str) -> Dict[str, Any]:
        """
        Get update status for a format.
        
        Args:
            format_name: Format name to check
            
        Returns:
            Dictionary with update status information
        """
        if format_name not in FORMATS:
            return {"error": f"Unknown format: {format_name}"}
        
        try:
            # Check current metadata
            current_metadata = self._get_current_metadata(format_name)
            if not current_metadata:
                return {
                    "format": format_name,
                    "status": "not_cached",
                    "last_update": None,
                    "sha": None
                }
            
            # Check remote metadata
            remote_metadata = self._get_remote_metadata(format_name)
            if not remote_metadata:
                return {
                    "format": format_name,
                    "status": "remote_unavailable",
                    "last_update": current_metadata.get("updated_at"),
                    "sha": current_metadata.get("sha")
                }
            
            # Compare
            current_sha = current_metadata.get("sha")
            remote_sha = remote_metadata.get("remote_sha")
            
            if current_sha == remote_sha:
                status = "up_to_date"
            else:
                status = "update_available"
            
            return {
                "format": format_name,
                "status": status,
                "last_update": current_metadata.get("updated_at"),
                "current_sha": current_sha,
                "remote_sha": remote_sha
            }
            
        except Exception as e:
            return {
                "format": format_name,
                "status": "error",
                "error": str(e)
            }
    
    def cleanup_old_data(self, keep_formats: Optional[List[str]] = None):
        """
        Clean up old cached data files.
        
        Args:
            keep_formats: List of formats to keep. If None, keeps all loaded formats.
        """
        if keep_formats is None:
            keep_formats = FORMATS
        
        try:
            # Get all files in cache directory
            cache_files = list(self.cache_dir.glob("*.json"))
            
            for file_path in cache_files:
                # Extract format name from filename
                filename = file_path.stem
                
                # Handle different file types
                if filename.endswith("_metadata"):
                    format_name = filename[:-9]  # Remove "_metadata"
                elif filename.endswith("_stats"):
                    format_name = filename[:-6]  # Remove "_stats"
                else:
                    format_name = filename
                
                # Check if format should be kept
                if format_name not in keep_formats:
                    try:
                        file_path.unlink()
                        logger.debug(f"Cleaned up {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up {file_path.name}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

__all__ = ['DataUpdater'] 