"""
API 模型提供商实现
"""

import openai
from typing import List, Dict, Any, Optional, Iterator

from .base import BaseLLMProvider, BaseEmbeddingProvider, ModelConfig, ProviderType
from .utils import retry_with_exponential_backoff, truncate_text, validate_api_key


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI LLM 提供商"""
    
    DEFAULT_CHAT_MODEL = "qwen-plus"
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        validate_api_key(config.api_key)
        
        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout or 30.0
        )
        
        # 设置默认参数
        self.default_params = {
            'temperature': config.temperature or 0.7,
            'max_tokens': config.max_tokens or 2048,
            **(config.extra_params or {})
        }
    
    @retry_with_exponential_backoff(
        allowed_exceptions=[openai.RateLimitError, openai.APITimeoutError, openai.APIError]
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> Optional[str]:
        """
        获取聊天补全响应
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Returns:
            模型响应内容
        """
        # 合并参数
        params = {**self.default_params, **kwargs}
        params.pop('stream', None)  # 确保非流式
        
        self.logger.info(f"正在请求聊天补全: {self.config.model_name}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                **params
            )
            
            if response.choices:
                return response.choices[0].message.content
            
            self.logger.warning("API 调用成功，但未返回任何 choices。")
            return None
            
        except Exception as e:
            self.logger.error(f"聊天补全请求失败: {e}")
            raise
    
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
        # 合并参数
        params = {**self.default_params, **kwargs}
        params['stream'] = True
        
        self.logger.info(f"正在请求流式聊天补全: {self.config.model_name}")
        
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                **params
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"流式聊天补全请求失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        try:
            # 发送一个简单的测试请求
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            self.logger.warning(f"提供商不可用: {e}")
            return False


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embedding 提供商"""
    
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
    # text-embedding-3-small 的官方 token 限制是 8191
    # 使用保守的字符数限制以避免超限
    MAX_EMBEDDING_INPUT_CHARS = 5120
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        validate_api_key(config.api_key)
        
        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout or 30.0
        )
    
    @retry_with_exponential_backoff(
        allowed_exceptions=[openai.RateLimitError, openai.APITimeoutError, openai.APIError]
    )
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
        if not text.strip():
            raise ValueError("用于 embedding 的输入文本不能为空。")
        
        # 检查并截断文本长度
        if len(text) > self.MAX_EMBEDDING_INPUT_CHARS:
            self.logger.warning(
                f"输入文本长度 ({len(text)}) 超过了 {self.MAX_EMBEDDING_INPUT_CHARS} 个字符的限制。"
                "将自动截断文本。"
            )
            text = truncate_text(text, self.MAX_EMBEDDING_INPUT_CHARS)
        
        self.logger.info(f"正在请求 embedding: {self.config.model_name}")
        
        try:
            response = self.client.embeddings.create(
                model=self.config.model_name,
                input=text,
                **kwargs
            )
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Embedding 请求失败: {e}")
            raise
    
    @retry_with_exponential_backoff(
        allowed_exceptions=[openai.RateLimitError, openai.APITimeoutError, openai.APIError]
    )
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
        if not texts:
            return []
        
        # 过滤空文本并截断长文本
        processed_texts = []
        for text in texts:
            if not text.strip():
                self.logger.warning("跳过空文本")
                processed_texts.append("")  # 保持索引一致性
                continue
            
            if len(text) > self.MAX_EMBEDDING_INPUT_CHARS:
                text = truncate_text(text, self.MAX_EMBEDDING_INPUT_CHARS)
            
            processed_texts.append(text)
        
        self.logger.info(f"正在批量请求 embedding: {self.config.model_name}, 文本数量: {len(processed_texts)}")
        
        try:
            response = self.client.embeddings.create(
                model=self.config.model_name,
                input=processed_texts,
                **kwargs
            )
            
            # 按顺序返回 embeddings
            embeddings = []
            for i, data in enumerate(response.data):
                embeddings.append(data.embedding)
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"批量 Embedding 请求失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        try:
            # 发送一个简单的测试请求
            response = self.client.embeddings.create(
                model=self.config.model_name,
                input="test"
            )
            return True
        except Exception as e:
            self.logger.warning(f"提供商不可用: {e}")
            return False
    
    def get_max_input_length(self) -> int:
        """获取最大输入长度"""
        return self.MAX_EMBEDDING_INPUT_CHARS


class OpenAIProvider:
    """OpenAI 统一提供商（同时支持 LLM 和 Embedding）"""
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        llm_model: str = OpenAILLMProvider.DEFAULT_CHAT_MODEL,
        embedding_model: str = OpenAIEmbeddingProvider.DEFAULT_EMBEDDING_MODEL,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """
        初始化 OpenAI 提供商
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            llm_model: LLM 模型名称
            embedding_model: Embedding 模型名称
            timeout: 请求超时时间
            **kwargs: 其他配置参数
        """
        # 创建 LLM 配置
        llm_config = ModelConfig(
            provider_type=ProviderType.API,
            model_name=llm_model,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            extra_params=kwargs
        )
        
        # 创建 Embedding 配置
        embedding_config = ModelConfig(
            provider_type=ProviderType.API,
            model_name=embedding_model,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            extra_params=kwargs
        )
        
        # 初始化提供商
        self.llm_provider = OpenAILLMProvider(llm_config)
        self.embedding_provider = OpenAIEmbeddingProvider(embedding_config)
    
    def get_llm_provider(self) -> OpenAILLMProvider:
        """获取 LLM 提供商"""
        return self.llm_provider
    
    def get_embedding_provider(self) -> OpenAIEmbeddingProvider:
        """获取 Embedding 提供商"""
        return self.embedding_provider


def create_openai_provider(
    api_key: str,
    base_url: Optional[str] = None,
    llm_model: Optional[str] = None,
    embedding_model: Optional[str] = None,
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
        llm_model=llm_model or OpenAILLMProvider.DEFAULT_CHAT_MODEL,
        embedding_model=embedding_model or OpenAIEmbeddingProvider.DEFAULT_EMBEDDING_MODEL,
        **kwargs
    ) 