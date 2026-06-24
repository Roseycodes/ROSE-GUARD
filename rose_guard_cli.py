#!/usr/bin/env python3
"""
ROSE GUARD Enhanced CLI
Interactive command-line interface for password security testing
"""

import signal
import sys
import os
import time
from typing import Optional, Dict, Any

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("⚠️  Install tqdm for progress bars: pip install tqdm")

from rose_guard_core import (
    SecurityConfig, PasswordHashSimulator, 
    AttackEngine, MetricsCollector, AttackResult
)

class InteractiveCLI:
    """Enhanced interactive CLI for ROSE GUARD"""
    
    def __init__(self):
        self.config = SecurityConfig.load_config()
        self.simulator = PasswordHashSimulator(self.config)
        self.engine = AttackEngine(self.config)
        self.metrics = MetricsCollector()
        self.current_target = None
        self.current_hash_type = None
        
        # Setup signal handling for graceful interruption
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Received interrupt signal - stopping attacks...")
        self.engine.stop_attacks()
        time.sleep(1)  # Give threads time to clean up
        print("✅ Attacks stopped safely. Partial results preserved.")
        self._show_results_menu()
    
    def _display_ethics_warning(self):
        """Display enhanced ethics warning"""
        print("🔐" + "="*70)
        print("ROSE GUARD: ROBUST OFFENSIVE SECURITY EVALUATOR GUARD")
        print("ENHANCED INTERACTIVE SECURITY TESTING PLATFORM")
        print("="*70)
        print("🚨 IMPORTANT: AUTHORIZED SECURITY TESTING ONLY")
        print("="*70)
        print("THIS TOOL IS DESIGNED FOR:")
        print("  ✅ Authorized penetration testing & security research")
        print("  ✅ Educational purposes in controlled environments")
        print("  ✅ Testing YOUR OWN systems with explicit permission")
        print("  ✅ Improving organizational security posture")
        print("")
        print("🚫 STRICTLY PROHIBITED:")
        print("  ❌ Unauthorized testing of any systems")
        print("  ❌ Malicious or criminal activities")
        print("  ❌ Testing without explicit written permission")
        print("="*70)
        
        if self.config['security']['require_ethics_consent']:
            response = input("Do you agree to use ROSE GUARD ethically and legally? (yes/NO): ")
            if response.lower() != 'yes':
                print("❌ Ethics consent not provided. Exiting.")
                sys.exit(1)
    
    def _progress_callback(self, current: int, total: int, attack_type: str):
        """Progress callback for attacks"""
        if TQDM_AVAILABLE:
            return  # tqdm handles this
        
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"   Progress: {current:,}/{total:,} ({percentage:.1f}%) - {attack_type}", end='\r')
    
    def _create_sample_wordlist(self):
        """Create enhanced sample wordlist"""
        wordlist_dir = "wordlists"
        os.makedirs(wordlist_dir, exist_ok=True)
        
        wordlist_path = os.path.join(wordlist_dir, "demo_wordlist.txt")
        
        enhanced_passwords = [
            # Common weak passwords
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master",
            "hello", "freedom", "whatever", "computer", "internet",
            
            # Common patterns
            "Password1", "P@ssw0rd", "Welcome123", "Admin123", "Guest1",
            "Summer2024", "Winter2025", "Spring123", "Fall2024",
            "Company123", "Secure2024", "TempPass123",
            
            # Short passwords for brute-force demo
            "cat", "dog", "boy", "girl", "man", "woman", "sun", "moon",
            
            # Number sequences
            "123", "1234", "12345", "123456", "1234567", "12345678",
            
            # Keyboard patterns
            "qwerty", "asdfgh", "zxcvbn", "qazwsx", "1qaz2wsx"
        ]
        
        with open(wordlist_path, 'w') as f:
            for pwd in enhanced_passwords:
                f.write(pwd + '\n')
        
        print(f"✅ Created enhanced wordlist: {wordlist_path}")
        return wordlist_path
    
    def main_menu(self):
        """Main interactive menu"""
        self._display_ethics_warning()
        
        while True:
            print("\n" + "="*60)
            print("🎯 ROSE GUARD - ENHANCED INTERACTIVE MENU")
            print("="*60)
            print("1. 🔐 Hash a password (create test target)")
            print("2. 🎯 Run targeted attack on hash")
            print("3. 🚀 Run comprehensive security assessment")
            print("4. 📊 View current results & metrics")
            print("5. 💾 Export results to file")
            print("6. ⚙️  Show configuration")
            print("7. 🏃 Run quick demonstration")
            print("8. 🚪 Exit")
            print("="*60)
            
            choice = input("Select option [1-8]: ").strip()
            
            if choice == '1':
                self._hash_password_menu()
            elif choice == '2':
                self._targeted_attack_menu()
            elif choice == '3':
                self._comprehensive_assessment_menu()
            elif choice == '4':
                self._show_results_menu()
            elif choice == '5':
                self._export_menu()
            elif choice == '6':
                self._show_configuration()
            elif choice == '7':
                self._run_demonstration()
            elif choice == '8':
                print("👋 Thank you for using ROSE GUARD!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def _hash_password_menu(self):
        """Menu for hashing passwords"""
        print("\n🔐 Password Hashing Utility")
        print("-" * 40)
        
        password = input("Enter password to hash: ").strip()
        if not password:
            print("❌ No password entered.")
            return
        
        print("\nAvailable hash algorithms:")
        print("1. MD5 (Insecure - demonstration only)")
        print("2. SHA-256 (Fast but not for passwords)")
        print("3. bcrypt (Recommended for passwords)")
        print("4. Argon2 (Modern recommended)")
        
        algo_choice = input("Select algorithm [1-4]: ").strip()
        
        hash_result = None
        algo_name = ""
        
        if algo_choice == '1':
            hash_result = self.simulator.md5_hash(password)
            algo_name = "MD5"
        elif algo_choice == '2':
            hash_result = self.simulator.sha256_hash(password)
            algo_name = "SHA-256"
        elif algo_choice == '3':
            hash_result = self.simulator.bcrypt_hash(password)
            algo_name = "bcrypt"
        elif algo_choice == '4':
            hash_result = self.simulator.argon2_hash(password)
            algo_name = "Argon2"
        else:
            print("❌ Invalid algorithm choice.")
            return
        
        print(f"\n✅ {algo_name} Hash created:")
        print(f"📦 Hash: {hash_result}")
        print(f"📝 Password length: {len(password)} characters")
        
        # Ask if user wants to attack this hash immediately
        use_for_attack = input("\n🎯 Use this hash for immediate attack? (y/N): ").strip().lower()
        if use_for_attack == 'y':
            self.current_target = hash_result
            self.current_hash_type = algo_name.lower()
            print(f"✅ Target set: {algo_name} hash")
            self._targeted_attack_menu()
    
    def _targeted_attack_menu(self):
        """Menu for targeted attacks on specific hashes"""
        if not self.current_target:
            print("\n❌ No target hash set. Please create a hash first.")
            return
        
        print(f"\n🎯 Targeted Attack Menu")
        print(f"-" * 40)
        print(f"Target: {self.current_hash_type.upper()} hash")
        print(f"Hash: {self.current_target[:50]}..." if len(str(self.current_target)) > 50 else f"Hash: {self.current_target}")
        
        while True:
            print(f"\nAttack Methods:")
            print("1. 📚 Dictionary attack (basic)")
            print("2. 🔄 Dictionary attack with mutation rules")
            print("3. ⚡ Hybrid attack (dictionary + suffixes)")
            print("4. 💥 Brute-force attack (short passwords)")
            print("5. 🎯 Sequential multi-method attack")
            print("6. 🔙 Back to main menu")
            
            attack_choice = input("Select attack [1-6]: ").strip()
            
            if attack_choice == '6':
                break
            
            # Get appropriate hash function
            hash_fn = getattr(self.simulator, f"{self.current_hash_type}_hash")
            wordlist_path = self.config['wordlist']
            
            # Ensure wordlist exists
            if not os.path.exists(wordlist_path):
                print(f"📁 Creating sample wordlist...")
                wordlist_path = self._create_sample_wordlist()
            
            result = None
            
            if attack_choice == '1':
                print("🚀 Starting dictionary attack...")
                result = self.engine.dictionary_attack(
                    self.current_target, wordlist_path, hash_fn, 
                    self.current_hash_type, use_rules=False,
                    progress_callback=self._progress_callback
                )
                
            elif attack_choice == '2':
                print("🚀 Starting dictionary attack with mutation rules...")
                result = self.engine.dictionary_attack(
                    self.current_target, wordlist_path, hash_fn,
                    self.current_hash_type, use_rules=True,
                    progress_callback=self._progress_callback
                )
                
            elif attack_choice == '3':
                print("🚀 Starting hybrid attack...")
                result = self.engine.hybrid_attack(
                    self.current_target, wordlist_path, hash_fn,
                    self.current_hash_type, progress_callback=self._progress_callback
                )
                
            elif attack_choice == '4':
                print("🚀 Starting brute-force attack...")
                max_len = input(f"Max length [{self.config['brute_force']['max_length']}]: ").strip()
                max_len = int(max_len) if max_len else self.config['brute_force']['max_length']
                
                result = self.engine.brute_force_attack(
                    self.current_target, hash_fn, self.current_hash_type,
                    max_length=max_len, progress_callback=self._progress_callback
                )
                
            elif attack_choice == '5':
                print("🚀 Starting sequential multi-method attack...")
                result = self._run_sequential_attack()
                
            else:
                print("❌ Invalid attack choice.")
                continue
            
            if result:
                self.metrics.add_result(result)
                self._display_attack_result(result)
    
    def _run_sequential_attack(self) -> AttackResult:
        """Run attacks in sequence until password is found"""
        hash_fn = getattr(self.simulator, f"{self.current_hash_type}_hash")
        wordlist_path = self.config['wordlist']
        
        attacks = [
            ("Dictionary", lambda: self.engine.dictionary_attack(
                self.current_target, wordlist_path, hash_fn,
                self.current_hash_type, use_rules=False
            )),
            ("Dictionary with Rules", lambda: self.engine.dictionary_attack(
                self.current_target, wordlist_path, hash_fn,
                self.current_hash_type, use_rules=True
            )),
            ("Hybrid", lambda: self.engine.hybrid_attack(
                self.current_target, wordlist_path, hash_fn, self.current_hash_type
            ))
        ]
        
        for attack_name, attack_func in attacks:
            print(f"🎯 Running {attack_name}...")
            result = attack_func()
            if result.success:
                print(f"✅ Password found with {attack_name}!")
                return result
            else:
                print(f"❌ {attack_name} failed ({result.attempts:,} attempts)")
        
        # If all else fails, try brute force for very short passwords
        print("🎯 Trying brute-force for short passwords...")
        return self.engine.brute_force_attack(
            self.current_target, hash_fn, self.current_hash_type, max_length=3
        )
    
    def _display_attack_result(self, result: AttackResult):
        """Display attack results in a formatted way"""
        print("\n" + "="*50)
        print("📊 ATTACK RESULTS")
        print("="*50)
        
        if result.success:
            print(f"✅ SUCCESS: Password cracked!")
            print(f"🔑 Password: {result.password}")
        else:
            print(f"❌ FAILED: Password not cracked")
        
        print(f"📈 Attempts: {result.attempts:,}")
        print(f"⏱️  Time: {result.time_taken:.2f}s")
        print(f"⚡ Speed: {result.attempts/result.time_taken:,.0f} attempts/second")
        print(f"🎯 Method: {result.attack_type}")
        print(f"🔒 Hash type: {result.hash_type}")
        print("="*50)
    
    def _comprehensive_assessment_menu(self):
        """Run comprehensive security assessment"""
        print("\n🔍 Comprehensive Security Assessment")
        print("="*50)
        
        # Test passwords of varying strength
        test_passwords = [
            "password",          # Very weak
            "Password1",         # Weak  
            "P@ssw0rd",          # Moderate
            "SecurePass123!",    # Strong
            "xK8@3p#L",          # Random, short but complex
        ]
        
        print("Testing passwords of varying strength:")
        for pwd in test_passwords:
            print(f"  • '{pwd}'")
        
        input("\nPress Enter to start assessment...")
        
        # Create test hashes and run attacks
        hashes = {}
        for pwd in test_passwords:
            hashes[pwd] = {
                'md5': self.simulator.md5_hash(pwd),
                'sha256': self.simulator.sha256_hash(pwd),
                'bcrypt': self.simulator.bcrypt_hash(pwd),
            }
        
        wordlist_path = self.config['wordlist']
        if not os.path.exists(wordlist_path):
            wordlist_path = self._create_sample_wordlist()
        
        total_tests = len(test_passwords) * 3  # 3 hash types per password
        current_test = 0
        
        for plaintext, hash_dict in hashes.items():
            print(f"\n🔍 Testing: '{plaintext}'")
            print("-" * 40)
            
            for hash_name, target_hash in hash_dict.items():
                current_test += 1
                print(f"  [{current_test}/{total_tests}] {hash_name.upper()}: ", end="", flush=True)
                
                hash_fn = getattr(self.simulator, f"{hash_name}_hash")
                
                # Try dictionary attack with rules
                result = self.engine.dictionary_attack(
                    target_hash, wordlist_path, hash_fn, hash_name, use_rules=True
                )
                
                if not result.success and len(plaintext) <= 6:
                    # Try brute force for short passwords
                    result = self.engine.brute_force_attack(
                        target_hash, hash_fn, hash_name, max_length=len(plaintext)
                    )
                
                self.metrics.add_result(result)
                
                status = "✅ CRACKED" if result.success else "❌ SECURE"
                print(f"{status} ({result.attempts:,} attempts, {result.time_taken:.2f}s)")
        
        print(f"\n🎉 Assessment complete! Run 'View results' for detailed analysis.")
    
    def _show_results_menu(self):
        """Display results and metrics"""
        if not self.metrics.results:
            print("\n❌ No results available. Run some attacks first.")
            return
        
        print("\n📊 Results & Analytics Menu")
        print("="*50)
        print("1. 📈 Quick summary")
        print("2. 📋 Detailed report")
        print("3. 🔍 Security insights")
        print("4. 🎯 Compare hash algorithms")
        print("5. 🔙 Back to main menu")
        
        choice = input("Select option [1-5]: ").strip()
        
        if choice == '1':
            self.metrics.generate_security_report()
        elif choice == '2':
            self._show_detailed_results()
        elif choice == '3':
            self._show_security_insights()
        elif choice == '4':
            self._compare_algorithms()
        elif choice == '5':
            return
        else:
            print("❌ Invalid option.")
    
    def _show_detailed_results(self):
        """Show detailed attack results"""
        print("\n📋 Detailed Attack History")
        print("="*80)
        for i, result in enumerate(self.metrics.results, 1):
            status = "CRACKED" if result.success else "FAILED"
            print(f"{i:2d}. {status:8} {result.hash_type:8} {result.attack_type:18} "
                  f"{result.attempts:8,} attempts {result.time_taken:7.2f}s")
    
    def _show_security_insights(self):
        """Provide security insights based on results"""
        metrics = self.metrics.calculate_comprehensive_metrics()
        
        print("\n🔍 Security Insights")
        print("="*50)
        
        if metrics.get('success_rate', 0) > 50:
            print("🚨 HIGH RISK: Over 50% of test passwords were cracked!")
            print("💡 Recommendation: Implement stronger password policies")
        elif metrics.get('success_rate', 0) > 20:
            print("⚠️  MEDIUM RISK: Significant number of passwords cracked")
            print("💡 Recommendation: Review password complexity requirements")
        else:
            print("✅ LOW RISK: Good password security demonstrated")
        
        # Algorithm-specific insights
        for algo in ['md5', 'sha256', 'bcrypt']:
            algo_key = f'{algo}_success_rate'
            if algo_key in metrics:
                success_rate = metrics[algo_key]
                if success_rate > 0:
                    print(f"\n🔒 {algo.upper()} analysis:")
                    print(f"   Crack success rate: {success_rate:.1f}%")
    
    def _compare_algorithms(self):
        """Compare hash algorithm performance"""
        print("\n⚡ Hash Algorithm Performance Comparison")
        print("="*50)
        
        test_password = "ROSE_GUARD_Performance_Test_2024"
        iterations = 100
        
        benchmarks = self.simulator.benchmark_hashes(test_password, iterations)
        
        print(f"Results ({iterations} iterations):")
        for algo, avg_time in benchmarks.items():
            hashes_per_second = 1 / avg_time if avg_time > 0 else float('inf')
            print(f"  {algo:8}: {avg_time*1000:7.2f} ms/hash = {hashes_per_second:8,.0f} hashes/sec")
        
        # Security implications
        print(f"\n🔒 Security Implications:")
        fastest = min(benchmarks, key=benchmarks.get)
        slowest = max(benchmarks, key=benchmarks.get)
        print(f"  Fastest: {fastest.upper()} - vulnerable to brute force")
        print(f"  Slowest: {slowest.upper()} - resistant to attacks")
    
    def _export_menu(self):
        """Handle results export"""
        if not self.metrics.results:
            print("❌ No results to export.")
            return
        
        filename = input("Export filename [rose_guard_results.csv]: ").strip()
        filename = filename or "rose_guard_results.csv"
        
        self.metrics.export_to_csv(filename)
        
        # Offer to show the file location
        file_path = os.path.abspath(filename)
        print(f"✅ Results exported to: {file_path}")
    
    def _show_configuration(self):
        """Display current configuration"""
        print("\n⚙️  Current Configuration")
        print("="*50)
        
        for category, settings in self.config.items():
            print(f"\n{category.upper()}:")
            for key, value in settings.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for subkey, subvalue in value.items():
                        print(f"    {subkey}: {subvalue}")
                else:
                    print(f"  {key}: {value}")
    
    def _run_demonstration(self):
        """Run a quick demonstration"""
        print("\n🏃 Running Quick Demonstration")
        print("="*50)
        print("This will demonstrate ROSE GUARD capabilities with sample data...")
        
        # Set a demo target
        demo_password = "Summer2024"
        self.current_target = self.simulator.md5_hash(demo_password)
        self.current_hash_type = "md5"
        
        print(f"🎯 Demo target: MD5 hash of '{demo_password}'")
        print("🚀 Running dictionary attack with rules...")
        
        hash_fn = self.simulator.md5_hash
        wordlist_path = self.config['wordlist']
        
        if not os.path.exists(wordlist_path):
            wordlist_path = self._create_sample_wordlist()
        
        result = self.engine.dictionary_attack(
            self.current_target, wordlist_path, hash_fn,
            self.current_hash_type, use_rules=True
        )
        
        self.metrics.add_result(result)
        self._display_attack_result(result)
        
        if result.success:
            print("🎉 Demonstration completed successfully!")
        else:
            print("💡 Demonstration completed - password was secure against this attack.")

def main():
    """Main entry point for enhanced CLI"""
    try:
        cli = InteractiveCLI()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 ROSE GUARD closed gracefully.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please report this issue.")

if __name__ == "__main__":
    main()