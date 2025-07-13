import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CacheManager:
    def __init__(self, cache_dir: str = "cache", max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age_hours = max_age_hours
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a unique cache key from input data"""
        # Sort the data to ensure consistent keys
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def get_cache_path(self, cache_key: str) -> str:
        """Get the full path for a cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data if it exists and is not expired"""
        cache_path = self.get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time > timedelta(hours=self.max_age_hours):
                # Remove expired cache
                os.remove(cache_path)
                return None
            
            return cached_data['data']
        
        except (json.JSONDecodeError, KeyError, ValueError):
            # Remove corrupted cache
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache data with timestamp"""
        cache_path = self.get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error caching data: {e}")
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries and return count of cleared items"""
        cleared_count = 0
        
        if not os.path.exists(self.cache_dir):
            return 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cache_time > timedelta(hours=self.max_age_hours):
                        os.remove(cache_path)
                        cleared_count += 1
                
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Remove corrupted cache
                    os.remove(cache_path)
                    cleared_count += 1
        
        return cleared_count
    
    def clear_all(self) -> int:
        """Clear all cache entries and return count of cleared items"""
        cleared_count = 0
        
        if not os.path.exists(self.cache_dir):
            return 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_path = os.path.join(self.cache_dir, filename)
                os.remove(cache_path)
                cleared_count += 1
        
        return cleared_count

# Global cache manager instance
cache_manager = CacheManager() 