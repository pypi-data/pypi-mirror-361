"""
模型工厂类，提供便利的模型提供商创建方法
"""

from typing import Optional, Union, Dict, Any

from .base import (
    BaseLLMProvider, 
    BaseEmbeddingProvider, 
    ModelConfig, 
    ProviderType
)
from .api_providers import (
    OpenAILLMProvider,
    OpenAIEmbeddingProvider,
    OpenAIProvider
)


class ModelFactory:
    """模型提供商工厂类"""
    
    @staticmethod
    def create_llm_provider(
        provider_type: Union[str, ProviderType],
        model_name: str,
        **config_kwargs
    ) -> BaseLLMProvider:
        """
        创建 LLM 提供商
        
        Args:
            provider_type: 提供商类型 ("api" 或 ProviderType 枚举)
            model_name: 模型名称
            **config_kwargs: 配置参数
            
        Returns:
            LLM 提供商实例
            
        Raises:
            ValueError: 不支持的提供商类型
        """
        # 转换字符串类型到枚举
        if isinstance(provider_type, str):
            provider_type = ProviderType(provider_type.lower())
        
        # 创建配置
        config = ModelConfig(
            provider_type=provider_type,
            model_name=model_name,
            **config_kwargs
        )
        
        # 根据类型创建提供商
        if provider_type == ProviderType.API:
            return OpenAILLMProvider(config)
        else:
            raise ValueError(f"不支持的提供商类型: {provider_type}")
    
    @staticmethod
    def create_embedding_provider(
        provider_type: Union[str, ProviderType],
        model_name: str,
        **config_kwargs
    ) -> BaseEmbeddingProvider:
        """
        创建 Embedding 提供商
        
        Args:
            provider_type: 提供商类型 ("api" 或 ProviderType 枚举)
            model_name: 模型名称
            **config_kwargs: 配置参数
            
        Returns:
            Embedding 提供商实例
            
        Raises:
            ValueError: 不支持的提供商类型
        """
        # 转换字符串类型到枚举
        if isinstance(provider_type, str):
            provider_type = ProviderType(provider_type.lower())
        
        # 创建配置
        config = ModelConfig(
            provider_type=provider_type,
            model_name=model_name,
            **config_kwargs
        )
        
        # 根据类型创建提供商
        if provider_type == ProviderType.API:
            return OpenAIEmbeddingProvider(config)
        else:
            raise ValueError(f"不支持的提供商类型: {provider_type}")
    
    @staticmethod
    def create_unified_provider(
        provider_type: Union[str, ProviderType],
        llm_model: str,
        embedding_model: str,
        **config_kwargs
    ) -> OpenAIProvider:
        """
        创建统一提供商（同时支持 LLM 和 Embedding）
        
        Args:
            provider_type: 提供商类型
            llm_model: LLM 模型名称
            embedding_model: Embedding 模型名称
            **config_kwargs: 配置参数
            
        Returns:
            统一提供商实例
            
        Raises:
            ValueError: 不支持的提供商类型
        """
        # 转换字符串类型到枚举
        if isinstance(provider_type, str):
            provider_type = ProviderType(provider_type.lower())
        
        if provider_type == ProviderType.API:
            return OpenAIProvider(
                llm_model=llm_model,
                embedding_model=embedding_model,
                **config_kwargs
            )
        else:
            raise ValueError(f"统一提供商目前仅支持 API 类型，不支持: {provider_type}")


# 便利函数

def create_llm_provider(
    provider_type: Union[str, ProviderType] = "api",
    model_name: str = "qwen-plus",
    **kwargs
) -> BaseLLMProvider:
    """
    创建 LLM 提供商的便利函数
    
    Args:
        provider_type: 提供商类型，默认为 "api"
        model_name: 模型名称，默认为 "qwen-plus"
        **kwargs: 其他配置参数
        
    Returns:
        LLM 提供商实例
    """
    return ModelFactory.create_llm_provider(provider_type, model_name, **kwargs)


def create_embedding_provider(
    provider_type: Union[str, ProviderType] = "api",
    model_name: str = "text-embedding-v3",
    **kwargs
) -> BaseEmbeddingProvider:
    """
    创建 Embedding 提供商的便利函数
    
    Args:
        provider_type: 提供商类型，默认为 "api"
        model_name: 模型名称，默认为 "text-embedding-3-small"
        **kwargs: 其他配置参数
        
    Returns:
        Embedding 提供商实例
    """
    return ModelFactory.create_embedding_provider(provider_type, model_name, **kwargs)


def create_openai_providers(
    api_key: str,
    base_url: Optional[str] = None,
    llm_model: str = "qwen-plus",
    embedding_model: str = "text-embedding-v3",
    **kwargs
) -> OpenAIProvider:
    """
    创建 OpenAI 提供商的便利函数
    
    Args:
        api_key: API 密钥
        base_url: API 基础 URL
        llm_model: LLM 模型名称
        embedding_model: Embedding 模型名称
        **kwargs: 其他配置参数
        
    Returns:
        OpenAI 提供商实例
    """
    return OpenAIProvider(
        api_key=api_key,
        base_url=base_url,
        llm_model=llm_model,
        embedding_model=embedding_model,
        **kwargs
    ) 