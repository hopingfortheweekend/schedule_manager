"""
简易日志工具：记录程序运行时的关键操作和错误。
日志写入 app.log 文件，同时在控制台输出。
"""
import logging
import os


def setup_logger(name="schedule_manager", log_file="app.log"):
    """配置并返回一个 logger 实例"""
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 格式：时间 - 级别 - 消息
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # 文件输出
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # 控制台输出
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


# 全局 logger，各模块直接 import 使用
logger = setup_logger()
