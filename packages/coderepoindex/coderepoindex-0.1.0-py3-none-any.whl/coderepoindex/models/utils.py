"""
模型模块的通用工具函数
"""

import time
import logging
import random
from functools import wraps
from typing import List, Type, Optional, Any, Callable

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0,
    jitter: bool = True,
    allowed_exceptions: Optional[List[Type[Exception]]] = None
):
    """
    一个装饰器，用于在函数失败时使用指数退避策略进行重试。

    Args:
        max_retries (int): 最大重试次数。
        initial_delay (float): 初始等待时间（秒）。
        max_delay (float): 最大等待时间（秒）。
        factor (float): 每次重试后延迟时间的乘数。
        jitter (bool): 是否在等待时间中添加随机抖动以避免同时重试。
        allowed_exceptions (Optional[List[Type[Exception]]]): 仅在这些异常发生时重试。
                                                              如果为 None，则对所有 Exception 进行重试。
    """
    if allowed_exceptions is None:
        allowed_exceptions = [Exception]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except tuple(allowed_exceptions) as e:
                    last_exception = e
                    logger.warning(
                        f"在调用 {func.__name__} 时出现错误 (尝试 {i + 1}/{max_retries}): {e}"
                    )
                    
                    if i + 1 == max_retries:
                        logger.error(f"{func.__name__} 的所有 {max_retries} 次重试均失败。")
                        raise e

                    # 计算下一次的延迟
                    delay *= factor
                    if jitter:
                        # 添加随机抖动
                        sleep_time = delay + random.uniform(0, delay * 0.2)
                    else:
                        sleep_time = delay
                    
                    # 确保延迟时间不超过最大值
                    actual_sleep = min(sleep_time, max_delay)
                    
                    logger.info(f"将在 {actual_sleep:.2f} 秒后重试...")
                    time.sleep(actual_sleep)
                    
            # 理论上不应该到达这里，但为了类型安全
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后的后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    # 确保后缀不会使文本超出最大长度
    if len(suffix) >= max_length:
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def validate_api_key(api_key: Optional[str]) -> None:
    """
    验证 API key
    
    Args:
        api_key: API 密钥
        
    Raises:
        ValueError: 如果 API key 无效
    """
    if not api_key or not api_key.strip():
        raise ValueError("API key 不能为空")


def estimate_token_count(text: str, chars_per_token: float = 3.5) -> int:
    """
    估算文本的 token 数量
    
    Args:
        text: 输入文本
        chars_per_token: 每个 token 的平均字符数
        
    Returns:
        估算的 token 数量
    """
    return max(1, int(len(text) / chars_per_token))


def batch_texts(texts: List[str], max_batch_size: int = 100) -> List[List[str]]:
    """
    将文本列表分批处理
    
    Args:
        texts: 文本列表
        max_batch_size: 最大批处理大小
        
    Returns:
        分批后的文本列表
    """
    if max_batch_size <= 0:
        raise ValueError("批处理大小必须大于 0")
    
    batches = []
    for i in range(0, len(texts), max_batch_size):
        batches.append(texts[i:i + max_batch_size])
    
    return batches


def setup_model_logging(level: int = logging.INFO) -> None:
    """
    设置模型模块的日志配置
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING) 