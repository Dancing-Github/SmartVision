from pathlib import Path

from loguru import logger

# 定义日志文件路径
log_directory = Path.cwd()
log_filename = Path('myLogger.log')
log_filepath = log_directory / log_filename
logger.add(log_filepath)
