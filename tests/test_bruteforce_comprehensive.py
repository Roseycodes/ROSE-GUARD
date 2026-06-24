import pytest
import time
from rose_guard_core import AttackEngine, PasswordHashSimulator, SecurityConfig

@pytest.fixture
def engine():
    config = SecurityConfig.DEFAULT_CONFIG.copy()
    config['brute_force']['max_length'] = 3
    config['brute_force']['charset'] = 'abc123'  # Simplified charset for testing
    config['brute_force']['timeout'] = 10
    return AttackEngine(config)

@pytest.fixture
def sim():
    config = SecurityConfig.DEFAULT_CONFIG.copy()
    return PasswordHashSimulator(config)

def test_simple_password(engine, sim):
    """Test finding a simple password"""
    target = sim.md5_hash('a1')
    result = engine.brute_force_attack(target, sim.md5_hash, 'md5', max_length=2)
    assert result.success is True
    assert result.password == 'a1'

def test_max_length_respected(engine, sim):
    """Test that max_length parameter is respected"""
    target = sim.md5_hash('abc123')  # Longer than max_length
    result = engine.brute_force_attack(target, sim.md5_hash, 'md5', max_length=2)
    assert result.success is False

def test_charset_respected(engine, sim):
    """Test that charset parameter is respected"""
    target = sim.md5_hash('x')  # Not in charset
    result = engine.brute_force_attack(target, sim.md5_hash, 'md5', charset='abc123')
    assert result.success is False

def test_progress_callback(engine, sim):
    """Test that progress callback is called"""
    calls = []
    def callback(current, total, attack_type):
        calls.append((current, total, attack_type))
    
    target = sim.md5_hash('c3')
    result = engine.brute_force_attack(target, sim.md5_hash, 'md5', 
                                     progress_callback=callback)
    assert len(calls) > 0
    assert calls[0][2] == 'brute_force'

def test_timeout_functionality(engine, sim):
    """Test that timeout works"""
    engine.config['brute_force']['timeout'] = 0.1  # Very short timeout
    target = sim.md5_hash('abc123')  # Will take longer than timeout
    start = time.time()
    result = engine.brute_force_attack(target, sim.md5_hash, 'md5')
    duration = time.time() - start
    assert duration < 0.5  # Should stop due to timeout
    assert result.success is False