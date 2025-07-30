from .core import PythonLibInstaller
import logging
__all__ = ["PythonLibInstaller"]
logging.basicConfig(
    filename='pipmanage.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

