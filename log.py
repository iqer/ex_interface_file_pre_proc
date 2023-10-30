import logging
from logging import handlers

logger = logging.getLogger("test")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
)

# 自动分割日志文件
# logging.handlers.RotatingFileHandler -> 按照大小自动分割日志文件，一旦达到指定的大小重新生成文件
# logging.handlers.TimedRotatingFileHandler -> 按照时间自动分割日志文件
time_rotating_file_handler = handlers.TimedRotatingFileHandler(
    filename='ex_file_proc.log', when="D"
)
time_rotating_file_handler.setLevel(logging.INFO)
time_rotating_file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(time_rotating_file_handler)
