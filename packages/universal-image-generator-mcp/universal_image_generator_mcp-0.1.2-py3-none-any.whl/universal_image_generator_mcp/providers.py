import os
import logging
import sys

from .base_provider import ImageProvider
from .gemini_provider import GeminiProvider
from .zhipuai_provider import ZhipuAIProvider
from .bailian_provider import BailianProvider

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


def create_provider(provider_name: str) -> ImageProvider:
    """Factory function to create image providers.
    
    Args:
        provider_name: Name of the provider ('gemini', 'zhipuai', or 'bailian')
        
    Returns:
        ImageProvider instance
        
    Raises:
        ValueError: If provider_name is not supported
    """
    provider_name = provider_name.lower()
    
    if provider_name == "gemini":
        return GeminiProvider()
    elif provider_name in ["zhipuai", "cogview", "cogview-4", "zhipu"]:
        return ZhipuAIProvider()
    elif provider_name in ["bailian", "dashscope", "alibaba"]:
        return BailianProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}. Supported providers: gemini, zhipuai, bailian")


def get_provider_from_env() -> ImageProvider:
    """Get the image provider based on environment variable.
    
    Returns:
        ImageProvider instance based on IMAGE_PROVIDER env var
        
    Raises:
        ValueError: If IMAGE_PROVIDER is not set or unsupported
    """
    provider_name = os.environ.get("IMAGE_PROVIDER")
    if not provider_name:
        raise ValueError("IMAGE_PROVIDER environment variable not set. Set to 'gemini', 'zhipuai', or 'bailian'")
    
    return create_provider(provider_name) 