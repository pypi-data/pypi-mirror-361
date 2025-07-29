import os
import logging
import sys
from typing import Optional, List, Any, Tuple
import PIL.Image

from google import genai
from google.genai import types

from .base_provider import ImageProvider
from .utils import save_image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class GeminiProvider(ImageProvider):
    """Google Gemini image generation provider."""
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=self.api_key)
    
    def get_name(self) -> str:
        return "gemini"
    
    def supports_generation(self) -> bool:
        return True
    
    def supports_transformation(self) -> bool:
        return True
    
    async def _call_gemini(
        self, 
        contents: List[Any], 
        model: str = "gemini-2.0-flash", 
        config: Optional[types.GenerateContentConfig] = None, 
        text_only: bool = False
    ) -> bytes | str:
        """Internal method to call Gemini API."""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            
            logger.info(f"Response received from Gemini API using model {model}")
            
            # Check if response has candidates
            if not response.candidates or not response.candidates[0] or not response.candidates[0].content:
                raise ValueError("No valid response received from Gemini API")
            
            # For text-only calls, extract just the text
            if text_only:
                if not response.candidates[0].content.parts or not response.candidates[0].content.parts[0]:
                    raise ValueError("No text content found in Gemini response")
                text_content = response.candidates[0].content.parts[0].text
                if text_content is None:
                    raise ValueError("Text content is None in Gemini response")
                return text_content.strip()
            
            # Return the image data
            if not response.candidates[0].content.parts:
                raise ValueError("No content parts found in Gemini response")
                
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None and part.inline_data.data is not None:
                    return part.inline_data.data
                
            raise ValueError("No image data found in Gemini response")

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    async def generate_image(self, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Generate image using Gemini."""
        model = kwargs.get('model', 'gemini-2.0-flash-preview-image-generation')
        
        # Call Gemini for image generation
        response = await self._call_gemini(
            [prompt],
            model=model,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        if not isinstance(response, bytes):
            raise ValueError("Expected bytes response from Gemini for image generation")
        
        # Generate filename and save image
        filename = await self.convert_prompt_to_filename(prompt)
        saved_path = await save_image(response, filename)
        
        # Gemini doesn't provide a remote URL, so return None
        return response, saved_path, None
    
    async def transform_image(self, image: PIL.Image.Image, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Transform image using Gemini."""
        model = kwargs.get('model', 'gemini-2.0-flash-preview-image-generation')
        
        # Call Gemini for image transformation
        response = await self._call_gemini(
            [prompt, image],
            model=model,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        if not isinstance(response, bytes):
            raise ValueError("Expected bytes response from Gemini for image transformation")
        
        # Generate filename and save image
        filename = await self.convert_prompt_to_filename(prompt)
        saved_path = await save_image(response, filename)
        
        # Gemini doesn't provide a remote URL, so return None
        return response, saved_path, None
    
    async def convert_prompt_to_filename(self, prompt: str) -> str:
        """Generate filename using Gemini."""
        try:
            filename_prompt = f"""
            Based on this image description: "{prompt}"
            
            Generate a short, descriptive file name suitable for the requested image.
            The filename should:
            - Be concise (maximum 5 words)
            - Use underscores between words
            - Not include any file extension
            - Only return the filename, nothing else
            """
            
            response = await self._call_gemini([filename_prompt], text_only=True)
            
            if isinstance(response, str):
                return response
            else:
                raise ValueError("Expected string response from Gemini for filename generation")
                
        except Exception as e:
            logger.error(f"Error generating filename with Gemini: {str(e)}")
            # Fallback to simple filename
            import uuid
            truncated_text = prompt[:12].strip()
            return f"image_{truncated_text}_{str(uuid.uuid4())[:8]}" 