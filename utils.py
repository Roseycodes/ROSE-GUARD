import os
import webbrowser

def open_file(filepath):
    """Open a file using the system's default program."""
    try:
        os.startfile(filepath)  # Windows
    except AttributeError:
        try:
            webbrowser.open(f"file://{os.path.abspath(filepath)}")
        except:
            webbrowser.open(filepath)

def safe_write(filepath, content, encoding='utf-8'):
    """Safely write content to a file with proper encoding."""
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {str(e)}")
        return False

def ensure_directory_exists(filepath):
    """Ensure the directory for a file exists, creating it if necessary."""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)