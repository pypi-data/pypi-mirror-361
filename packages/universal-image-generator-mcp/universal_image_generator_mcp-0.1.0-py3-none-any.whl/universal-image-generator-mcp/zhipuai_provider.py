import os
import logging
import sys
from typing import Optional, Tuple
import PIL.Image

from zhipuai import ZhipuAI

from .base_provider import ImageProvider
from .utils import save_image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class ZhipuAIProvider(ImageProvider):
    """ZHIPU AI provider supporting CogView-4 (image generation) and GLM-4 (translation)."""
    
    def __init__(self):
        self.api_key = os.environ.get("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("ZHIPU_API_KEY environment variable not set")
        self.client = ZhipuAI(api_key=self.api_key)
    
    def get_name(self) -> str:
        return "zhipuai"
    
    def supports_generation(self) -> bool:
        return True
    
    def supports_transformation(self) -> bool:
        return False  # CogView-4 doesn't support image transformation
    
    async def generate_image(self, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Generate image using CogView-4."""
        model = kwargs.get('model', 'cogview-4-250304')
        quality = kwargs.get('quality', 'standard')
        
        try:
            # Call ZHIPU API for image generation
            response = self.client.images.generations(
                model=model,
                prompt=prompt,
                quality=quality
            )
            
            # Get the image URL from response
            if not response.data or not response.data[0].url:
                raise ValueError("No image URL found in CogView response")
            
            image_url = response.data[0].url
            logger.info(f"Generated image URL: {image_url}")
            
            # Download the image
            import urllib.request
            import urllib.error
            
            try:
                with urllib.request.urlopen(image_url) as response:
                    if response.status != 200:
                        raise ValueError(f"Failed to download image from URL: {image_url}")
                    image_bytes = response.read()
            except urllib.error.URLError as e:
                raise ValueError(f"Failed to download image from URL {image_url}: {e}")
            
            # Generate filename and save image
            filename = await self.convert_prompt_to_filename(prompt)
            saved_path = await save_image(image_bytes, filename)
            
            return image_bytes, saved_path, image_url
            
        except Exception as e:
            logger.error(f"Error generating image with CogView: {str(e)}")
            raise
    
    async def transform_image(self, image: PIL.Image.Image, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """CogView doesn't support image transformation."""
        raise NotImplementedError("CogView-4 does not support image transformation")
    
    async def translate_text(self, text: str, target_language: str = "chinese") -> str:
        """Translate text using GLM-4 model.
        
        Args:
            text: Text to translate
            target_language: Target language ("chinese" or "english")
            
        Returns:
            Translated text
        """
        try:
            if target_language.lower() == "chinese":
                system_prompt = "你是一个专业的翻译助手。请将用户输入的文本准确翻译成中文，保持原意不变。只返回翻译结果，不要添加任何解释。"
                user_prompt = f"请将以下文本翻译成中文：{text}"
            else:
                system_prompt = "You are a professional translation assistant. Please accurately translate the user's input text into English while preserving the original meaning. Return only the translation result without any explanations."
                user_prompt = f"Please translate the following text into English: {text}"
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent translation
                max_tokens=1000
            )
            
            # Handle the response properly with safe attribute access
            try:
                choices = getattr(response, 'choices', None)
                if choices and len(choices) > 0:
                    choice = choices[0]
                    message = getattr(choice, 'message', None)
                    if message:
                        content = getattr(message, 'content', None)
                        if content:
                            translated_text = content.strip()
                            logger.info(f"GLM-4 translation: '{text}' -> '{translated_text}'")
                            return translated_text
            except Exception as e:
                logger.warning(f"Error parsing GLM-4 response: {e}")
            
            logger.warning("No translation result from GLM-4, returning original text")
            return text
                
        except Exception as e:
            logger.error(f"Error translating with GLM-4: {str(e)}")
            return text

    async def convert_prompt_to_filename(self, prompt: str) -> str:
        """Generate simple filename for ZHIPU images."""
        import uuid
        import re
        
        # Clean prompt for filename
        clean_prompt = re.sub(r'[^\w\s-]', '', prompt)
        clean_prompt = re.sub(r'[\s-]+', '_', clean_prompt)
        truncated = clean_prompt[:20]
        
        return f"zhipuai_{truncated}_{str(uuid.uuid4())[:8]}" 