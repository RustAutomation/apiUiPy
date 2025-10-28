import sys
import os

# Добавляем src в PYTHONPATH, чтобы pytest мог импортировать пакеты
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
