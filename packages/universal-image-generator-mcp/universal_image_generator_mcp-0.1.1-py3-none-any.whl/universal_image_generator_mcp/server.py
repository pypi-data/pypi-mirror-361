import base64
import binascii
import os
import logging
import sys
import uuid
from io import BytesIO
from typing import Optional, Any, Union, List, Tuple

import PIL.Image
from mcp.server.fastmcp import FastMCP

from .prompts import (
    get_image_generation_prompt, 
    get_image_transformation_prompt, 
    get_translate_prompt,
    get_chinese_image_generation_prompt
)
from .base_provider import ImageProvider
from .providers import get_provider_from_env
from .utils import save_image


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("universal_image_generator_mcp")

# Global provider variable - will be initialized when needed
image_provider: Optional[ImageProvider] = None

def get_image_provider() -> ImageProvider:
    """Get or initialize the image provider."""
    global image_provider
    if image_provider is None:
        try:
            image_provider = get_provider_from_env()
            logger.info(f"Initialized {image_provider.get_name()} provider")
            logger.info(f"Supports generation: {image_provider.supports_generation()}")
            logger.info(f"Supports transformation: {image_provider.supports_transformation()}")
        except Exception as e:
            logger.error(f"Failed to initialize image provider: {e}")
            logger.error("Please set IMAGE_PROVIDER environment variable to 'gemini', 'zhipuai', or 'bailian'")
            raise
    return image_provider


# ==================== Utility Functions ====================

async def translate_prompt_for_provider(text: str, provider: ImageProvider) -> str:
    """Translate the user's prompt based on the provider's preferred language.
    
    Args:
        text: The original prompt in any language
        provider: The image provider to use
        
    Returns:
        Translated prompt optimized for the provider
    """
    try:
        # Determine target language based on provider
        target_language = "chinese" if provider.get_name() in ["zhipuai", "bailian"] else "english"
        
        # Skip translation if it's already in the target language
        if target_language == "english" and _is_english(text):
            return text
        elif target_language == "chinese" and _is_chinese(text):
            return text
        
        # Use provider's own translation capability if available
        if provider.get_name() in ["zhipuai", "bailian"] and hasattr(provider, 'translate_text'):
            # Use provider's native translation (GLM-4 for ZhipuAI, Qwen for Bailian)
            translated = await provider.translate_text(text, target_language)
            return translated
        elif provider.get_name() == "gemini":
            # Use Gemini for translation
            from google import genai
            from google.genai import types
            
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                client = genai.Client(api_key=api_key)
                
                # Create translation prompt
                translation_prompt = get_translate_prompt(text, target_language)
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[translation_prompt]
                )
                
                if (response.candidates and response.candidates[0] and 
                    response.candidates[0].content and response.candidates[0].content.parts and
                    response.candidates[0].content.parts[0] and response.candidates[0].content.parts[0].text):
                    translated = response.candidates[0].content.parts[0].text.strip()
                    logger.info(f"Translated prompt from '{text}' to '{translated}'")
                    return translated
        
        # Return original text if translation fails or provider doesn't support it
        logger.info(f"Using original prompt: {text}")
        return text
        
    except Exception as e:
        logger.error(f"Error translating prompt: {str(e)}")
        return text


def _is_english(text: str) -> bool:
    """Simple heuristic to check if text is primarily English."""
    import re
    # Count ASCII letters vs non-ASCII characters
    ascii_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(re.findall(r'\w', text))
    return total_chars == 0 or ascii_chars / total_chars > 0.7


def _is_chinese(text: str) -> bool:
    """Simple heuristic to check if text contains Chinese characters."""
    import re
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(re.findall(r'\w', text))
    return total_chars > 0 and chinese_chars / total_chars > 0.3


async def prepare_prompt_for_provider(user_prompt: str, provider: ImageProvider) -> str:
    """Prepare and optimize the prompt for the specific provider.
    
    Args:
        user_prompt: The original user prompt
        provider: The image provider to use
        
    Returns:
        Optimized prompt for the provider
    """
    # Translate the prompt to the provider's preferred language
    translated_prompt = await translate_prompt_for_provider(user_prompt, provider)
    
    # Apply provider-specific prompt templates
    if provider.get_name() in ["zhipuai", "bailian"]:
        # Use Chinese-optimized prompt for Chinese-focused providers
        return get_chinese_image_generation_prompt(translated_prompt)
    else:
        # Use English prompt for Gemini
        return get_image_generation_prompt(translated_prompt)


async def load_image_from_base64(encoded_image: str) -> Tuple[PIL.Image.Image, str]:
    """Load an image from a base64-encoded string.
    
    Args:
        encoded_image: Base64 encoded image data with header
        
    Returns:
        Tuple containing the PIL Image object and the image format
    """
    if not encoded_image.startswith('data:image/'):
        raise ValueError("Invalid image format. Expected data:image/[format];base64,[data]")
    
    try:
        # Extract the base64 data from the data URL
        image_format, image_data = encoded_image.split(';base64,')
        image_format = image_format.replace('data:', '')  # Get the MIME type e.g., "image/png"
        image_bytes = base64.b64decode(image_data)
        source_image = PIL.Image.open(BytesIO(image_bytes))
        logger.info(f"Successfully loaded image with format: {image_format}")
        return source_image, image_format
    except binascii.Error as e:
        logger.error(f"Error: Invalid base64 encoding: {str(e)}")
        raise ValueError("Invalid base64 encoding. Please provide a valid base64 encoded image.")
    except ValueError as e:
        logger.error(f"Error: Invalid image data format: {str(e)}")
        raise ValueError("Invalid image data format. Image must be in format 'data:image/[format];base64,[data]'")
    except PIL.UnidentifiedImageError:
        logger.error("Error: Could not identify image format")
        raise ValueError("Could not identify image format. Supported formats include PNG, JPEG, GIF, WebP.")
    except Exception as e:
        logger.error(f"Error: Could not load image: {str(e)}")
        raise


# ==================== MCP Tools ====================

@mcp.tool()
async def generate_image_from_text(prompt: str) -> str:
    """Generate an image based on the given text prompt using the configured image provider.

    Args:
        prompt: User's text prompt describing the desired image to generate
        
    Returns:
        Path to the generated image file using the configured provider's image generation capabilities
    """
    try:
        provider = get_image_provider()
        if not provider.supports_generation():
            return f"Error: {provider.get_name()} provider does not support image generation"
        
        logger.info(f"Generating image with {provider.get_name()} provider")
        logger.info(f"User prompt: {prompt}")
        
        # Prepare the optimized prompt for the provider
        optimized_prompt = await prepare_prompt_for_provider(prompt, provider)
        
        # Generate the image using the provider
        _, saved_path, remote_url = await provider.generate_image(optimized_prompt)
        
        logger.info(f"Image generated and saved to: {saved_path}")
        
        # Prepare response with remote URL if available
        response = f"Image saved to: {saved_path}"
        if remote_url:
            response += f"\nRemote URL: {remote_url}"
        
        return response
        
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        logger.error(error_msg)
        return error_msg


# Check if transformation tools should be registered
def _should_register_transformation_tools() -> bool:
    """Check if transformation tools should be registered based on provider capabilities."""
    try:
        provider = get_image_provider()
        return provider.supports_transformation()
    except Exception:
        # If provider can't be initialized, assume no transformation support
        return False

# Only register transformation tools if the provider supports them
if _should_register_transformation_tools():
    
    @mcp.tool()
    async def transform_image_from_encoded(encoded_image: str, prompt: str) -> str:
        """Transform an existing image based on the given text prompt using the configured image provider.

        Args:
            encoded_image: Base64 encoded image data with header. Must be in format:
                        "data:image/[format];base64,[data]"
                        Where [format] can be: png, jpeg, jpg, gif, webp, etc.
            prompt: Text prompt describing the desired transformation or modifications
            
        Returns:
            Path to the transformed image file saved on the server
        """
        try:
            provider = get_image_provider()
            logger.info(f"Processing transform_image_from_encoded request with {provider.get_name()}")
            logger.info(f"Transformation prompt: {prompt}")

            # Load and validate the image
            source_image, _ = await load_image_from_base64(encoded_image)
            
            # Translate the prompt for the provider
            translated_prompt = await translate_prompt_for_provider(prompt, provider)
            
            # Create detailed transformation prompt
            transformation_prompt = get_image_transformation_prompt(translated_prompt)
            
            # Process the transformation using the provider
            _, saved_path, remote_url = await provider.transform_image(source_image, transformation_prompt)
            
            logger.info(f"Image transformed and saved to: {saved_path}")
            
            # Prepare response with remote URL if available
            response = f"Image transformed and saved to: {saved_path}"
            if remote_url:
                response += f"\nRemote URL: {remote_url}"
            
            return response
            
        except Exception as e:
            error_msg = f"Error transforming image: {str(e)}"
            logger.error(error_msg)
            return error_msg


    @mcp.tool()
    async def transform_image_from_url(image_url: str, prompt: str, function: str = "description_edit", mask_image_url: Optional[str] = None) -> str:
        """Transform an existing image from a URL using the configured image provider.

        Args:
            image_url: Public URL of the image to be transformed
            prompt: Text prompt describing the desired transformation or modifications
            function: WanX editing function (default: 'description_edit'). Supported functions:
                     'description_edit', 'description_edit_with_mask', 'stylization_all', 
                     'stylization_local', 'remove_watermark', 'expand', 'super_resolution', 
                     'colorization', 'doodle', 'control_cartoon_feature'
            mask_image_url: URL of mask image (required for 'description_edit_with_mask')
            
        Returns:
            Details about the transformed image including local path and remote URL
        """
        try:
            provider = get_image_provider()
            logger.info(f"Processing transform_image_from_url request with {provider.get_name()}")
            logger.info(f"Image URL: {image_url}")
            logger.info(f"Transformation prompt: {prompt}")
            logger.info(f"Function: {function}")

            # For providers that don't support URL-based transformation, we need to download and convert
            if provider.get_name() == "gemini":
                # Download image and convert to PIL Image for Gemini
                import requests
                response = requests.get(image_url)
                if response.status_code != 200:
                    raise ValueError(f"Failed to download image from URL: {image_url}")
                
                source_image = PIL.Image.open(BytesIO(response.content))
                logger.info(f"Downloaded and loaded image from URL for Gemini")
                
                # Translate the prompt for the provider
                translated_prompt = await translate_prompt_for_provider(prompt, provider)
                
                # Create detailed transformation prompt
                transformation_prompt = get_image_transformation_prompt(translated_prompt)
                
                # Process the transformation using the provider
                _, saved_path, remote_url = await provider.transform_image(source_image, transformation_prompt)
                
            elif provider.get_name() == "bailian":
                # For Bailian, we can use the URL directly
                
                # Translate the prompt for the provider  
                translated_prompt = await translate_prompt_for_provider(prompt, provider)
                
                # Create detailed transformation prompt
                transformation_prompt = get_image_transformation_prompt(translated_prompt)
                
                # Prepare kwargs for Bailian provider
                kwargs = {
                    'function': function,
                    'base_image_url': image_url
                }
                
                # Add mask image URL if provided and function requires it
                if mask_image_url:
                    kwargs['mask_image_url'] = mask_image_url
                elif function == "description_edit_with_mask":
                    raise ValueError("mask_image_url is required for description_edit_with_mask function")
                
                # Use a dummy PIL image since we're passing URL via kwargs
                dummy_image = PIL.Image.new('RGB', (1, 1))
                
                # Process the transformation using the provider
                _, saved_path, remote_url = await provider.transform_image(dummy_image, transformation_prompt, **kwargs)
                
            else:
                # For other providers, download image first
                import requests
                response = requests.get(image_url)
                if response.status_code != 200:
                    raise ValueError(f"Failed to download image from URL: {image_url}")
                
                source_image = PIL.Image.open(BytesIO(response.content))
                logger.info(f"Downloaded and loaded image from URL")
                
                # Translate the prompt for the provider
                translated_prompt = await translate_prompt_for_provider(prompt, provider)
                
                # Create detailed transformation prompt
                transformation_prompt = get_image_transformation_prompt(translated_prompt)
                
                # Process the transformation using the provider
                _, saved_path, remote_url = await provider.transform_image(source_image, transformation_prompt)
            
            logger.info(f"Image transformed and saved to: {saved_path}")
            
            # Prepare response with remote URL if available
            response = f"Image transformed and saved to: {saved_path}"
            if remote_url:
                response += f"\nRemote URL: {remote_url}"
            
            return response
            
        except Exception as e:
            error_msg = f"Error transforming image from URL: {str(e)}"
            logger.error(error_msg)
            return error_msg


    @mcp.tool()
    async def transform_image_from_file(image_file_path: str, prompt: str) -> str:
        """Transform an existing image file based on the given text prompt using the configured image provider.

        Args:
            image_file_path: Path to the image file to be transformed
            prompt: Text prompt describing the desired transformation or modifications
            
        Returns:
            Path to the transformed image file saved on the server
        """
        try:
            provider = get_image_provider()
            logger.info(f"Processing transform_image_from_file request with {provider.get_name()}")
            logger.info(f"Image file path: {image_file_path}")
            logger.info(f"Transformation prompt: {prompt}")

            # Validate file path
            if not os.path.exists(image_file_path):
                raise ValueError(f"Image file not found: {image_file_path}")

            # Load the source image directly using PIL
            try:
                source_image = PIL.Image.open(image_file_path)
                logger.info(f"Successfully loaded image from file: {image_file_path}")
            except PIL.UnidentifiedImageError:
                logger.error("Error: Could not identify image format")
                raise ValueError("Could not identify image format. Supported formats include PNG, JPEG, GIF, WebP.")
            except Exception as e:
                logger.error(f"Error: Could not load image: {str(e)}")
                raise 
            
            # Translate the prompt for the provider
            translated_prompt = await translate_prompt_for_provider(prompt, provider)
            
            # Create detailed transformation prompt
            transformation_prompt = get_image_transformation_prompt(translated_prompt)
            
            # Process the transformation using the provider
            _, saved_path, remote_url = await provider.transform_image(source_image, transformation_prompt)
            
            logger.info(f"Image transformed and saved to: {saved_path}")
            
            # Prepare response with remote URL if available
            response = f"Image transformed and saved to: {saved_path}"
            if remote_url:
                response += f"\nRemote URL: {remote_url}"
            
            return response
            
        except Exception as e:
            error_msg = f"Error transforming image: {str(e)}"
            logger.error(error_msg)
            return error_msg

else:
    try:
        provider = get_image_provider()
        logger.info(f"Transformation tools not registered - {provider.get_name()} provider does not support image transformation")
    except Exception:
        logger.info("Transformation tools not registered - provider not yet configured")


def main():
    try:
        provider = get_image_provider()
        logger.info(f"Starting {provider.get_name()} Image Generator MCP server...")
        logger.info(f"Available capabilities:")
        logger.info(f"  - Image generation: {provider.supports_generation()}")
        logger.info(f"  - Image transformation: {provider.supports_transformation()}")
    except Exception as e:
        logger.error(f"Failed to initialize provider: {e}")
        sys.exit(1)
    
    mcp.run(transport="stdio")
    logger.info("Server stopped")

if __name__ == "__main__":
    main()