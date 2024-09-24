import PyInstaller.__main__
import os

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.dirname(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=DictationApp',
    '--windowed',
    f'--add-data={os.path.join(project_root, "MyIcon.icns")}:.',  # Ensure correct path formatting
    f'--icon={os.path.join(project_root, "MyIcon.icns")}',       # Ensure the icon path is correctly formatted
    '--hidden-import=pyaudio',
    '--hidden-import=pynput',
    '--hidden-import=openai',
    '--hidden-import=dotenv',
    '--hidden-import=sqlalchemy',
    '--hidden-import=sqlalchemy.sql.default_comparator',
    '--hidden-import=sqlalchemy.ext.declarative',
    '--hidden-import=sqlalchemy.orm',
    '--hidden-import=sqlalchemy.pool',
    '--hidden-import=src.utils.text_inserter',
    '--collect-all=openai',
])