from loguru import logger
import sys
import os

# 定义日志格式，包含可点击的文件路径和行号
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <4}</level> | <cyan>using_function:{function}</cyan> | <cyan>{file}:{line}</cyan> | <level>{message}</level>"

def setup_logger(log_level="INFO", log_file=None):
    """
    配置日志工具
    
    Args:
        log_level: 日志级别，默认为INFO
        log_file: 日志文件路径，默认为None（仅控制台输出）
    
    Returns:
        配置好的logger实例
    """
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台处理器，使用自定义格式
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=log_level,
        diagnose=True,  # 启用诊断信息
        backtrace=True,  # 启用回溯
    )
    
    # 如果提供了日志文件路径，添加文件处理器
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logger.add(
            log_file,
            format=LOG_FORMAT,
            level=log_level,
            rotation="10 MB",  # 日志文件达到10MB时轮转
            retention="1 month",  # 保留1个月的日志
        )
    
    return logger

# 默认导出配置好的logger实例
logger = setup_logger()

# 使用示例
if __name__ == "__main__":
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志") 