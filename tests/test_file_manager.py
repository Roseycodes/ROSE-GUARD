import os
from file_manager import FileManager

def test_save_simple_report(tmp_path):
    filename = tmp_path / "report.html"
    metrics = {'total_attacks': 2, 'successful_attacks': 0, 'total_attempts': 150, 'overall_attempts_per_second': 120.5}
    output_text = "Test output"
    ok, err = FileManager._save_simple_report(str(filename), metrics, output_text, 'Oct 5, 2025')
    assert ok is True
    assert err is None
    assert os.path.exists(str(filename))
    content = open(str(filename), 'r', encoding='utf-8').read()
    assert 'ROSE GUARD Security Report' in content
    assert 'Test output' in content
