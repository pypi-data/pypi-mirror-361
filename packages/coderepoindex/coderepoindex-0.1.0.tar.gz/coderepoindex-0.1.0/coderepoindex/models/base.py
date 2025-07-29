"""
模型提供商的基础接口和抽象类
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Iterator, Union

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """提供商类型枚举"""
    API = "api"


@dataclass
class ModelConfig:
    """模型配置类"""
    provider_type: ProviderType
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[float] = None
    extra_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """配置验证"""
        if self.provider_type == ProviderType.API and not self.api_key:
            raise ValueError("API 提供商必须提供 api_key")


class BaseLLMProvider(ABC):
    """LLM 提供商基础抽象类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> Optional[str]:
        """
        获取聊天补全响应
        
        Args:
            messages: 消息列表，每个消息包含 role 和 content
            **kwargs: 额外参数
            
        Returns:
            模型响应内容
        """
        pass
    
    @abstractmethod
    def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> Iterator[str]:
        """
        获取流式聊天补全响应
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Yields:
            模型响应的流式片段
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name


class BaseEmbeddingProvider(ABC):
    """Embedding 提供商基础抽象类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @abstractmethod
    def get_embedding(
        self,
        text: str,
        **kwargs: Any
    ) -> List[float]:
        """
        获取文本的 embedding 向量
        
        Args:
            text: 输入文本
            **kwargs: 额外参数
            
        Returns:
            embedding 向量
        """
        pass
    
    @abstractmethod
    def get_embeddings_batch(
        self,
        texts: List[str],
        **kwargs: Any
    ) -> List[List[float]]:
        """
        批量获取文本的 embedding 向量
        
        Args:
            texts: 输入文本列表
            **kwargs: 额外参数
            
        Returns:
            embedding 向量列表
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name
    
    @abstractmethod
    def get_max_input_length(self) -> int:
        """获取最大输入长度"""
        pass


class ModelProvider(ABC):
    """通用模型提供商接口（同时支持 LLM 和 Embedding）"""
    
    @abstractmethod
    def get_llm_provider(self) -> Optional[BaseLLMProvider]:
        """获取 LLM 提供商"""
        pass
    
    @abstractmethod
    def get_embedding_provider(self) -> Optional[BaseEmbeddingProvider]:
        """获取 Embedding 提供商"""
        pass 