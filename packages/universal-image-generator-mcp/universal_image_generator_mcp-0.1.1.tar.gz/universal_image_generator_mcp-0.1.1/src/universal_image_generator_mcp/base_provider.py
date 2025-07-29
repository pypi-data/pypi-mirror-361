import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import PIL.Image

logger = logging.getLogger(__name__)


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the provider."""
        pass
    
    @abstractmethod
    def supports_generation(self) -> bool:
        """Return True if the provider supports text-to-image generation."""
        pass
    
    @abstractmethod
    def supports_transformation(self) -> bool:
        """Return True if the provider supports image transformation/editing."""
        pass
    
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Generate an image from text prompt.
        
        Args:
            prompt: Text description for image generation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple of (image_bytes, saved_image_path, remote_image_url)
            remote_image_url is None if provider doesn't provide a remote URL
        """
        pass
    
    @abstractmethod
    async def transform_image(self, image: PIL.Image.Image, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Transform an existing image based on text prompt.
        
        Args:
            image: Source image to transform
            prompt: Text description for transformation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple of (image_bytes, saved_image_path, remote_image_url)
            remote_image_url is None if provider doesn't provide a remote URL
            
        Raises:
            NotImplementedError: If provider doesn't support transformation
        """
        pass
    
    @abstractmethod
    async def convert_prompt_to_filename(self, prompt: str) -> str:
        """Convert a prompt to a suitable filename."""
        pass
    
    async def translate_text(self, text: str, target_language: str = "english") -> str:
        """Translate text using the provider's capabilities.
        
        Args:
            text: Text to translate
            target_language: Target language ("chinese" or "english")
            
        Returns:
            Translated text (default implementation returns original text)
        """
        # Default implementation - providers can override this
        return text 