"""
模型获取模块

提供 LLM 和 embedding model 的统一接口，支持 API 模型获取。
"""

from .base import (
    BaseLLMProvider,
    BaseEmbeddingProvider,
    ModelConfig,
    ProviderType
)
from .api_providers import (
    OpenAILLMProvider,
    OpenAIEmbeddingProvider,
    OpenAIProvider,
    create_openai_provider
)
from .factory import (
    ModelFactory,
    create_llm_provider,
    create_embedding_provider,
    create_openai_providers
)
from .utils import setup_model_logging

__all__ = [
    # 基础接口
    'BaseLLMProvider',
    'BaseEmbeddingProvider',
    'ModelConfig',
    'ProviderType',
    
    # API 提供商
    'OpenAILLMProvider',
    'OpenAIEmbeddingProvider',
    'OpenAIProvider',
    'create_openai_provider',
    
    # 工厂方法
    'ModelFactory',
    'create_llm_provider',
    'create_embedding_provider',
    'create_openai_providers',
    
    # 工具函数
    'setup_model_logging',
] 