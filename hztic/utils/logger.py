import logging
import os

def setup_logger(name, log_file="app.log", level=logging.INFO):
    """设置日志记录器"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, log_file)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 创建文件日志处理器
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    
    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器到日志记录器
    if not logger.handlers:  # 避免重复添加
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger