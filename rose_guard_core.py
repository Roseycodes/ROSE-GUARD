import hashlib
import bcrypt
import argon2
import time
import itertools
import string
import csv
import os
import sys
import yaml
import psutil
from typing import List, Dict, Callable, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
from logging_config import configure_logging
import threading

logger = configure_logging()

@dataclass
class AttackResult:
    """Results from a password attack attempt"""
    success: bool
    password: Optional[str]
    attempts: int
    time_taken: float
    hash_type: str
    attack_type: str

class SecurityConfig:
    """Configuration manager for ROSE GUARD"""
    
    DEFAULT_CONFIG = {
        'wordlist': 'wordlists/demo_wordlist.txt',
        'brute_force': {
            'max_length': 4,
            'charset': 'abcdefghijklmnopqrstuvwxyz0123456789',
            'timeout': 300  # 5 minutes
        },
        'hashing': {
            'bcrypt_rounds': 4,  # Low for demo, high for production
            'argon2_time_cost': 1
        },
        'performance': {
            'batch_size': 1000,
            'progress_update_interval': 100
        },
        'security': {
            'require_ethics_consent': True,
            'mask_passwords_in_logs': True,
            'demo_mode': True
        }
    }
    
    @classmethod
    def load_config(cls, config_path: str = "config.yaml") -> Dict:
        """Load configuration from YAML file or use defaults"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
            # Deep merge with defaults
            return cls._deep_merge(cls.DEFAULT_CONFIG.copy(), user_config)
        return cls.DEFAULT_CONFIG
    
    @staticmethod
    def _deep_merge(base: Dict, update: Dict) -> Dict:
        """Recursively merge dictionaries"""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                base[key] = SecurityConfig._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

class PasswordHashSimulator:
    """ROSE GUARD: Enhanced password hashing simulator"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    @staticmethod
    def md5_hash(password: str) -> str:
        """Generate MD5 hash (insecure - for demonstration only)"""
        return hashlib.md5(password.encode()).hexdigest()
    
    @staticmethod
    def sha256_hash(password: str) -> str:
        """Generate SHA-256 hash"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def bcrypt_hash(self, password: str, rounds: Optional[int] = None) -> bytes:
        """Generate bcrypt hash with configurable work factor"""
        if rounds is None:
            rounds = self.config['hashing']['bcrypt_rounds']
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds))
    
    def argon2_hash(self, password: str) -> str:
        """Generate Argon2 hash (modern recommended algorithm)"""
        ph = argon2.PasswordHasher(
            time_cost=self.config['hashing']['argon2_time_cost']
        )
        return ph.hash(password)
    
    def get_hash_function(self, hash_type: str) -> Callable:
        """Get the appropriate hash function based on type"""
        hash_type = hash_type.lower().replace('-', '').replace('_', '')  # Normalize hash type name
        hash_functions = {
            'md5': self.md5_hash,
            'sha256': self.sha256_hash,
            'bcrypt': self.bcrypt_hash,
            'argon2': self.argon2_hash
        }
        if hash_type not in hash_functions:
            raise ValueError(f"Unsupported hash type: {hash_type}. Available types: {list(hash_functions.keys())}")
        return hash_functions[hash_type]

    def verify_hash(self, password: str, hashed: str, hash_type: str) -> bool:
        """Verify a password against its hash"""
        try:
            hash_type = hash_type.lower().replace('-', '').replace('_', '')
            if hash_type in ['md5', 'sha256']:
                # For simple hashes, just compare the hash values
                hash_func = self.get_hash_function(hash_type)
                return hash_func(password) == hashed
            elif hash_type == 'bcrypt':
                # bcrypt has its own verification
                if isinstance(hashed, str):
                    hashed = hashed.encode()
                return bcrypt.checkpw(password.encode(), hashed)
            elif hash_type == 'argon2':
                # Argon2 has its own verification
                ph = argon2.PasswordHasher()
                return ph.verify(hashed, password)
            else:
                raise ValueError(f"Unsupported hash type: {hash_type}")
        except Exception as e:
            print(f"⚠️ Error verifying hash: {str(e)}")
            return False
    
    def benchmark_hashes(self, password: str, iterations: int = 100) -> Dict[str, float]:
        """Benchmark all hash algorithms for speed comparison"""
        results = {}
        
        # MD5
        start = time.time()
        for _ in range(iterations):
            self.md5_hash(password)
        results['md5'] = (time.time() - start) / iterations
        
        # SHA-256
        start = time.time()
        for _ in range(iterations):
            self.sha256_hash(password)
        results['sha256'] = (time.time() - start) / iterations
        
        # bcrypt
        start = time.time()
        for _ in range(iterations):
            self.bcrypt_hash(password)
        results['bcrypt'] = (time.time() - start) / iterations
        
        return results

class AttackEngine:
    """ROSE GUARD: Enhanced attack simulation engine with progress tracking"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.results: List[AttackResult] = []
        # Use threading.Event for robust cross-thread cancellation
        self.stop_event = threading.Event()
    
    def stop_attacks(self):
        """Gracefully stop ongoing attacks"""
        self.stop_event.set()
        logger.info("AttackEngine: stop requested")

    def reset_stop(self):
        """Reset the stop flag so a new attack can start"""
        self.stop_event.clear()
        logger.debug("AttackEngine: stop flag reset")
    
    def dictionary_attack(self, target_hash: str, wordlist_path: str, 
                         hash_fn: Optional[Callable] = None, hash_type: str = "md5", 
                         use_rules: bool = True,
                         progress_callback: Optional[Callable] = None) -> AttackResult:
        """Perform dictionary attack with progress tracking"""
        if hash_fn is None:
            # Use PasswordHashSimulator to get appropriate hash function
            hash_fn = PasswordHashSimulator(self.config).get_hash_function(hash_type)
        start_time = time.time()
        attempts = 0
        
        try:
            # Count total words for progress tracking
            total_words = self._count_lines(wordlist_path)
            current_progress = 0
            
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if self.stop_event.is_set():
                        return AttackResult(False, None, attempts, 
                                          time.time() - start_time, hash_type, "dictionary")
                    
                    word = line.strip()
                    if not word:
                        continue
                    
                    # Test original word
                    attempts += 1
                    current_progress += 1
                    
                    if progress_callback and attempts % self.config['performance']['progress_update_interval'] == 0:
                        progress_callback(current_progress, total_words, "dictionary")
                    
                    if hash_fn(word) == target_hash:
                        return AttackResult(True, word, attempts, 
                                          time.time() - start_time, hash_type, "dictionary")
                    
                    # Apply mutation rules if enabled
                    if use_rules:
                        for mutated in self._apply_mutation_rules(word):
                            if self.stop_event.is_set():
                                return AttackResult(False, None, attempts, 
                                                      time.time() - start_time, hash_type, "dictionary")

                            attempts += 1
                            if hash_fn(mutated) == target_hash:
                                return AttackResult(True, mutated, attempts,
                                                  time.time() - start_time, hash_type, "dictionary_rules")
        
        except FileNotFoundError:
            print(f"ROSE GUARD: Wordlist not found: {wordlist_path}")
        
        return AttackResult(False, None, attempts, time.time() - start_time, 
                          hash_type, "dictionary_rules" if use_rules else "dictionary")
    
    def _count_lines(self, filepath: str) -> int:
        """Count lines in file for progress tracking"""
        try:
            if not os.path.exists(filepath):
                print(f"⚠️  Warning: File not found: {filepath}")
                return 0
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                count = sum(1 for line in f if line.strip())  # Only count non-empty lines
                if count == 0:
                    print(f"⚠️  Warning: No valid lines found in {filepath}")
                return count
        except Exception as e:
            print(f"⚠️  Error reading file {filepath}: {str(e)}")
            return 0
    
    def _apply_mutation_rules(self, word: str) -> List[str]:
        """Apply comprehensive password mutation rules"""
        mutations = set()  # Use set for automatic deduplication
        
        # Common substitutions and patterns from real-world passwords
        substitutions = {
            'a': '@4',
            'e': '3',
            'i': '1!',
            'o': '0',
            's': '$5',
            'l': '1',
            't': '7'
        }
        
        # Add base mutations
        word_lower = word.lower()
        mutations.update([
            word_lower,
            word.capitalize(),
            word.upper(),
            word_lower + '1',
            word_lower + '123',
            word_lower + '!',
            word.capitalize() + '1',
            word.capitalize() + '!',
            word_lower + '2024',
            word_lower + '2025',
        ])
        
        # Smart substitutions (only if beneficial)
        if any(c in word_lower for c in substitutions):
            # Build substitution combinations dynamically
            chars_to_sub = []
            for i, c in enumerate(word_lower):
                if c in substitutions:
                    chars_to_sub.append((i, c))
            
            # Apply substitutions one at a time (more common in real passwords)
            for pos, char in chars_to_sub:
                for sub in substitutions[char]:
                    mutated = list(word_lower)
                    mutated[pos] = sub
                    mutations.add(''.join(mutated))
        
        return list(set(mutations))  # Remove duplicates
    
    def brute_force_attack(self, target_hash: str, hash_fn: Callable, 
                          hash_type: str, max_length: Optional[int] = None,
                          charset: Optional[str] = None,
                          progress_callback: Optional[Callable] = None) -> AttackResult:
        """Perform brute-force attack with progress tracking"""
        if max_length is None:
            max_length = self.config['brute_force']['max_length']
        if charset is None:
            charset = self.config['brute_force']['charset']
            
        start_time = time.time()
        attempts = 0
        timeout = self.config['brute_force']['timeout']
        total_combinations_all = sum(len(charset) ** i for i in range(1, max_length + 1))
        current_combination = 0
        
        for length in range(1, max_length + 1):
            for combo in itertools.product(charset, repeat=length):
                if self.stop_event.is_set():
                    return AttackResult(False, None, attempts, 
                                      time.time() - start_time, hash_type, "brute_force")
                
                # Check timeout only periodically to improve performance
                if attempts % 1000 == 0 and (time.time() - start_time) > timeout:
                    return AttackResult(False, None, attempts, 
                                      time.time() - start_time, hash_type, "brute_force")
                
                guess = ''.join(combo)
                attempts += 1
                current_combination += 1
                
                if progress_callback and attempts % 10 == 0:
                    progress_callback(current_combination, total_combinations_all, "brute_force")
                
                if time.time() - start_time > self.config['brute_force']['timeout']:
                    return AttackResult(False, None, attempts, 
                                      time.time() - start_time, hash_type, "brute_force")
                
                if hash_fn(guess) == target_hash:
                    return AttackResult(True, guess, attempts, 
                                      time.time() - start_time, hash_type, "brute_force")
        
        return AttackResult(False, None, attempts, time.time() - start_time,
                          hash_type, "brute_force")
    
    def hybrid_attack(self, target_hash: str, wordlist_path: str,
                     hash_fn: Callable, hash_type: str,
                     max_suffix_length: int = 3,
                     progress_callback: Optional[Callable] = None) -> AttackResult:
        """Enhanced hybrid attack with progress tracking"""
        start_time = time.time()
        attempts = 0
        
        # Optimize character set to common password suffixes
        numbers = string.digits
        special = "!@#$%^&*"
        common_suffixes = ['1', '123', '!', '#', '@'] + [str(y) for y in range(2020, 2026)]
        
        try:
            # Pre-calculate total operations for better progress reporting
            total_words = self._count_lines(wordlist_path)
            suffix_combinations = len(common_suffixes) + sum(
                (len(numbers + special) ** i) for i in range(1, max_suffix_length + 1)
            )
            total_operations = total_words * (1 + suffix_combinations)
            current_operation = 0
            
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if self.stop_event.is_set():
                        return AttackResult(False, None, attempts, 
                                          time.time() - start_time, hash_type, "hybrid")
                    
                    base_word = line.strip()
                    if not base_word:
                        continue
                    
                    # Test base word
                    attempts += 1
                    current_operation += 1
                    if progress_callback and current_operation % 100 == 0:
                        progress_callback(current_operation, total_operations, "hybrid")
                    
                    if hash_fn(base_word) == target_hash:
                        return AttackResult(True, base_word, attempts,
                                          time.time() - start_time, hash_type, "hybrid")
                    
                    # First try common suffixes
                    for suffix in common_suffixes:
                        if self.stop_event.is_set():
                            return AttackResult(False, None, attempts, 
                                              time.time() - start_time, hash_type, "hybrid")
                        
                        guess = base_word + suffix
                        attempts += 1
                        current_operation += 1
                        
                        if hash_fn(guess) == target_hash:
                            return AttackResult(True, guess, attempts,
                                              time.time() - start_time, hash_type, "hybrid")
                    
                    # Then try combinations of numbers and special characters
                    charset = numbers + special
                    for length in range(1, max_suffix_length + 1):
                        for suffix in itertools.product(charset, repeat=length):
                            if self.stop_event.is_set():
                                return AttackResult(False, None, attempts, 
                                                  time.time() - start_time, hash_type, "hybrid")
                            
                            guess = base_word + ''.join(suffix)
                            attempts += 1
                            current_operation += 1
                            
                            if hash_fn(guess) == target_hash:
                                return AttackResult(True, guess, attempts,
                                                  time.time() - start_time, hash_type, "hybrid")
        
        except FileNotFoundError:
            print(f"ROSE GUARD: Wordlist not found: {wordlist_path}")
        
        return AttackResult(False, None, attempts, time.time() - start_time,
                          hash_type, "hybrid")

class MetricsCollector:
    """ROSE GUARD: Enhanced metrics collection and analysis with memory tracking"""
    
    def __init__(self):
        self.results: List[AttackResult] = []
        self.attack_history: List[Dict] = []
        self.performance_stats: Dict = {}
        self.active_timers: Dict[str, float] = {}  # Track active timers
        self.memory_snapshots: Dict[str, List[float]] = {}
    
    def add_result(self, result: AttackResult):
        """Add a new attack result to metrics"""
        self.results.append(result)
        self.attack_history.append({
            'timestamp': datetime.now(),
            'hash_type': result.hash_type,
            'attack_type': result.attack_type,
            'success': result.success,
            'attempts': result.attempts,
            'time_taken': result.time_taken,
            'password_found': result.password if result.password else "Not found",
            'attempts_per_second': result.attempts / result.time_taken if result.time_taken > 0 else 0
        })
    
    def calculate_comprehensive_metrics(self) -> Dict:
        """Calculate comprehensive security metrics with enhanced analysis"""
        if not self.results:
            return {}
        
        successful_attacks = [r for r in self.results if r.success]
        
        metrics = {
            'total_attacks': len(self.results),
            'successful_attacks': len(successful_attacks),
            'success_rate': len(successful_attacks) / len(self.results) * 100,
            'total_attempts': sum(r.attempts for r in self.results),
            'total_time': sum(r.time_taken for r in self.results),
        }
        
        # Enhanced metrics by hash type
        hash_types = set(r.hash_type for r in self.results)
        for hash_type in hash_types:
            hash_attacks = [r for r in self.results if r.hash_type == hash_type]
            hash_success = [r for r in hash_attacks if r.success]
            if hash_attacks:
                metrics[f'{hash_type}_success_rate'] = len(hash_success) / len(hash_attacks) * 100
                metrics[f'{hash_type}_avg_time'] = sum(r.time_taken for r in hash_attacks) / len(hash_attacks)
        
        # Enhanced metrics by attack type
        attack_types = set(r.attack_type for r in self.results)
        for attack_type in attack_types:
            type_attacks = [r for r in self.results if r.attack_type == attack_type]
            type_success = [r for r in type_attacks if r.success]
            if type_attacks:
                metrics[f'{attack_type}_success_rate'] = len(type_success) / len(type_attacks) * 100
                metrics[f'{attack_type}_efficiency'] = len(type_success) / sum(r.attempts for r in type_attacks) * 1000 if type_attacks else 0
        
        # Performance metrics
        if successful_attacks:
            metrics['avg_time_to_crack'] = sum(r.time_taken for r in successful_attacks) / len(successful_attacks)
            metrics['fastest_crack'] = min(r.time_taken for r in successful_attacks)
            metrics['slowest_crack'] = max(r.time_taken for r in successful_attacks)
        
        # Attempts per second
        total_time = metrics['total_time']
        if total_time > 0:
            metrics['overall_attempts_per_second'] = metrics['total_attempts'] / total_time
        
        # Security effectiveness score
        if metrics['total_attempts'] > 0:
            metrics['security_effectiveness'] = (1 - (len(successful_attacks) / metrics['total_attempts'])) * 100
        
        return metrics
    
    def start_timer(self, name: str, track_memory: bool = True) -> None:
        """Start a named performance timer with optional memory tracking"""
        if name in self.active_timers:
            print(f"⚠️  Warning: Timer '{name}' is already running")
            return
            
        self.active_timers[name] = time.time()
        if track_memory:
            self.memory_snapshots[name] = [psutil.Process().memory_info().rss / (1024 * 1024)]  # MB

    def stop_timer(self, name: str) -> Optional[Dict]:
        """Stop a named timer and return timing and memory metrics"""
        if name not in self.active_timers:
            print(f"⚠️  Warning: Timer '{name}' was never started")
            return None

        end_time = time.time()
        duration = end_time - self.active_timers[name]
        
        metrics = {'duration': duration}
        
        if name in self.memory_snapshots:
            final_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
            initial_memory = self.memory_snapshots[name][0]
            metrics.update({
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_change_mb': final_memory - initial_memory
            })
        
        # Cleanup
        del self.active_timers[name]
        if name in self.memory_snapshots:
            del self.memory_snapshots[name]
            
        return metrics

    def export_to_csv(self, filename: str = "rose_guard_enhanced_results.csv"):
        """Export enhanced results to CSV with additional metrics"""
        if not self.attack_history:
            print("⚠️  Warning: No data to export")
            return
        
        # Check for any lingering timers
        for timer in list(self.active_timers.keys()):
            print(f"⚠️  Warning: Timer '{timer}' was never stopped")
            self.stop_timer(timer)
        
        try:
            import pandas as pd
            df = pd.DataFrame(self.attack_history)
            
            # Add performance metrics
            metrics = self.calculate_comprehensive_metrics()
            metrics_df = pd.DataFrame([metrics])
            
            # Export both to separate sheets in Excel
            with pd.ExcelWriter(filename.replace('.csv', '.xlsx')) as writer:
                df.to_excel(writer, sheet_name='Attack History', index=False)
                metrics_df.to_excel(writer, sheet_name='Performance Metrics', index=False)
            
            print(f"✅ Results exported to {filename.replace('.csv', '.xlsx')}")
            
        except ImportError:
            # Fallback to basic CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.attack_history[0].keys())
                writer.writeheader()
                writer.writerows(self.attack_history)
            print(f"ROSE GUARD: Enhanced results exported to {filename} (using standard CSV)")
    
    def generate_security_report(self):
        """Generate comprehensive security assessment report"""
        metrics = self.calculate_comprehensive_metrics()
        
        print("\n" + "="*80)
        print("🔐 ROSE GUARD: ENHANCED SECURITY ASSESSMENT REPORT")
        print("="*80)
        print("COMPREHENSIVE SECURITY METRICS")
        print("="*80)
        
        print(f"\n📊 Overall Performance Metrics:")
        print(f"   Total attacks performed: {metrics.get('total_attacks', 0):,}")
        print(f"   Successful cracks: {metrics.get('successful_attacks', 0):,}")
        print(f"   Success rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"   Total attempts: {metrics.get('total_attempts', 0):,}")
        print(f"   Total time invested: {metrics.get('total_time', 0):.2f}s")
        
        if 'overall_attempts_per_second' in metrics:
            print(f"   Attempts per second: {metrics['overall_attempts_per_second']:,.0f}")
        
        print(f"\n⏱️  Timing Analysis:")
        if 'avg_time_to_crack' in metrics:
            print(f"   Average time to crack: {metrics['avg_time_to_crack']:.2f}s")
            print(f"   Fastest crack: {metrics.get('fastest_crack', 0):.2f}s")
            print(f"   Slowest crack: {metrics.get('slowest_crack', 0):.2f}s")
        
        print(f"\n🛡️  Security Effectiveness:")
        if 'security_effectiveness' in metrics:
            print(f"   Security effectiveness score: {metrics['security_effectiveness']:.1f}%")
        
        print(f"\n🔍 Detailed Attack Results:")
        for result in self.results:
            status = "✅ CRACKED" if result.success else "❌ FAILED"
            password_display = f"'{result.password}'" if result.password else "Not found"
            efficiency = result.attempts / result.time_taken if result.time_taken > 0 else 0
            print(f"   {status} | {result.hash_type:8} | {result.attack_type:18} | "
                  f"{result.attempts:8,} attempts | {result.time_taken:7.2f}s | "
                  f"{efficiency:7.0f} att/s | {password_display}")