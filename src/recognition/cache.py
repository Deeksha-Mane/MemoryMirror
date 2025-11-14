"""Recognition caching system for Memory Mirror application."""

import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import hashlib
import numpy as np

from src.recognition.recognizer import RecognitionResult

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry for recognition results."""
    result: RecognitionResult
    timestamp: datetime
    frame_hash: str
    hit_count: int = 0
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry is expired."""
        return (datetime.now() - self.timestamp).total_seconds() > ttl_seconds

class RecognitionCache:
    """Caches recognition results for performance optimization."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 30):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # For LRU eviction
        self.lock = threading.RLock()
        
        # Performance tracking
        self.hit_count = 0
        self.miss_count = 0
        self.total_requests = 0
        
        # Cleanup thread
        self.cleanup_interval = 60  # seconds
        self.last_cleanup = datetime.now()
    
    def get(self, frame_hash: str) -> Optional[RecognitionResult]:
        """Get cached recognition result."""
        with self.lock:
            self.total_requests += 1
            
            if frame_hash not in self.cache:
                self.miss_count += 1
                return None
            
            entry = self.cache[frame_hash]
            
            # Check if expired
            if entry.is_expired(self.ttl_seconds):
                self._remove_entry(frame_hash)
                self.miss_count += 1
                return None
            
            # Update access order (move to end for LRU)
            if frame_hash in self.access_order:
                self.access_order.remove(frame_hash)
            self.access_order.append(frame_hash)
            
            # Update hit count
            entry.hit_count += 1
            self.hit_count += 1
            
            logger.debug(f"Cache hit for frame hash: {frame_hash[:8]}...")
            return entry.result
    
    def put(self, frame_hash: str, result: RecognitionResult) -> None:
        """Store recognition result in cache."""
        with self.lock:
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Create new cache entry
            entry = CacheEntry(
                result=result,
                timestamp=datetime.now(),
                frame_hash=frame_hash
            )
            
            # Store in cache
            self.cache[frame_hash] = entry
            
            # Update access order
            if frame_hash in self.access_order:
                self.access_order.remove(frame_hash)
            self.access_order.append(frame_hash)
            
            logger.debug(f"Cached result for frame hash: {frame_hash[:8]}...")
            
            # Periodic cleanup
            self._maybe_cleanup()
    
    def invalidate(self, person_id: str = None) -> None:
        """Invalidate cache entries."""
        with self.lock:
            if person_id is None:
                # Clear all cache
                self.cache.clear()
                self.access_order.clear()
                logger.info("Cache cleared completely")
            else:
                # Remove entries for specific person
                keys_to_remove = []
                for key, entry in self.cache.items():
                    if entry.result.person_id == person_id:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    self._remove_entry(key)
                
                logger.info(f"Cache invalidated for person: {person_id}")
    
    def get_stats(self) -> Dict:
        """Get cache performance statistics."""
        with self.lock:
            hit_rate = (self.hit_count / self.total_requests * 100) if self.total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'total_requests': self.total_requests,
                'hit_rate_percent': round(hit_rate, 2),
                'ttl_seconds': self.ttl_seconds,
                'oldest_entry': self._get_oldest_entry_age(),
                'most_accessed': self._get_most_accessed_entry()
            }
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.access_order:
            return
        
        # Remove oldest entry
        lru_key = self.access_order[0]
        self._remove_entry(lru_key)
        
        logger.debug(f"Evicted LRU entry: {lru_key[:8]}...")
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache and access order."""
        if key in self.cache:
            del self.cache[key]
        
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _maybe_cleanup(self) -> None:
        """Perform cleanup if enough time has passed."""
        now = datetime.now()
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self._cleanup_expired()
            self.last_cleanup = now
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        expired_keys = []
        
        for key, entry in self.cache.items():
            if entry.is_expired(self.ttl_seconds):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _get_oldest_entry_age(self) -> Optional[int]:
        """Get age of oldest entry in seconds."""
        if not self.cache:
            return None
        
        oldest_time = min(entry.timestamp for entry in self.cache.values())
        return int((datetime.now() - oldest_time).total_seconds())
    
    def _get_most_accessed_entry(self) -> Optional[Dict]:
        """Get information about most accessed entry."""
        if not self.cache:
            return None
        
        most_accessed = max(self.cache.values(), key=lambda e: e.hit_count)
        
        return {
            'person_id': most_accessed.result.person_id,
            'hit_count': most_accessed.hit_count,
            'confidence': most_accessed.result.confidence
        }

class FrameHasher:
    """Utility class for generating frame hashes."""
    
    @staticmethod
    def hash_frame(frame: np.ndarray, face_coords: Dict = None) -> str:
        """Generate hash for a video frame or face region."""
        try:
            if frame is None:
                return ""
            
            # If face coordinates provided, extract face region
            if face_coords:
                x, y, w, h = face_coords['x'], face_coords['y'], face_coords['width'], face_coords['height']
                face_region = frame[y:y+h, x:x+w]
                hash_input = face_region
            else:
                hash_input = frame
            
            # Resize to standard size for consistent hashing
            import cv2
            resized = cv2.resize(hash_input, (64, 64))
            
            # Convert to grayscale
            if len(resized.shape) == 3:
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            else:
                gray = resized
            
            # Generate hash
            frame_bytes = gray.tobytes()
            hash_obj = hashlib.md5(frame_bytes)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Error hashing frame: {e}")
            return ""
    
    @staticmethod
    def hash_face_features(face_coords: Dict, frame_shape: Tuple[int, int]) -> str:
        """Generate hash based on face features and position."""
        try:
            # Create feature string
            feature_str = f"{face_coords['x']}_{face_coords['y']}_{face_coords['width']}_{face_coords['height']}_{frame_shape[0]}_{frame_shape[1]}"
            
            # Generate hash
            hash_obj = hashlib.md5(feature_str.encode())
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Error hashing face features: {e}")
            return ""

class PerformanceOptimizer:
    """Performance optimization utilities."""
    
    def __init__(self):
        self.frame_skip_count = 0
        self.max_frame_skip = 2  # Process every 3rd frame
        self.last_process_time = datetime.now()
        self.target_fps = 10  # Target processing FPS
        self.min_process_interval = 1.0 / self.target_fps
    
    def should_process_frame(self) -> bool:
        """Determine if current frame should be processed."""
        try:
            current_time = datetime.now()
            time_since_last = (current_time - self.last_process_time).total_seconds()
            
            # Check time-based throttling
            if time_since_last < self.min_process_interval:
                return False
            
            # Check frame skipping
            self.frame_skip_count += 1
            if self.frame_skip_count <= self.max_frame_skip:
                return False
            
            # Reset counters
            self.frame_skip_count = 0
            self.last_process_time = current_time
            
            return True
            
        except Exception as e:
            logger.error(f"Error in frame processing decision: {e}")
            return True  # Default to processing
    
    def optimize_frame_for_processing(self, frame: np.ndarray) -> np.ndarray:
        """Optimize frame for faster processing."""
        try:
            if frame is None:
                return None
            
            import cv2
            
            # Resize for faster processing
            height, width = frame.shape[:2]
            if width > 640:
                scale = 640 / width
                new_width = 640
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error optimizing frame: {e}")
            return frame
    
    def set_target_fps(self, fps: int) -> None:
        """Set target processing FPS."""
        self.target_fps = max(1, min(30, fps))
        self.min_process_interval = 1.0 / self.target_fps
        logger.info(f"Target processing FPS set to: {self.target_fps}")
    
    def set_frame_skip(self, skip_count: int) -> None:
        """Set number of frames to skip between processing."""
        self.max_frame_skip = max(0, min(10, skip_count))
        logger.info(f"Frame skip count set to: {self.max_frame_skip}")
    
    def get_performance_stats(self) -> Dict:
        """Get performance optimization statistics."""
        return {
            'target_fps': self.target_fps,
            'frame_skip_count': self.max_frame_skip,
            'min_process_interval': self.min_process_interval,
            'last_process_time': self.last_process_time.isoformat()
        }