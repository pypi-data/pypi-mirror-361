import os
import logging
import time
import asyncio
import base64
import sys
from typing import Optional, Tuple
from io import BytesIO
import PIL.Image
import requests

from .base_provider import ImageProvider
from .utils import save_image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class BailianProvider(ImageProvider):
    """Alibaba Cloud Bailian provider supporting WanX (image generation/editing) and Qwen (translation)."""
    
    def __init__(self):
        self.api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable not set")
        self.base_url = "https://dashscope.aliyuncs.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_name(self) -> str:
        return "bailian"
    
    def supports_generation(self) -> bool:
        return True
    
    def supports_transformation(self) -> bool:
        return True
    
    async def _create_async_task(self, endpoint: str, data: dict) -> str:
        """Create an async task and return task_id."""
        headers = self.headers.copy()
        headers["X-DashScope-Async"] = "enable"
        
        response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to create task: {response.status_code} {response.text}")
        
        result = response.json()
        task_id = result.get("output", {}).get("task_id")
        if not task_id:
            raise ValueError(f"No task_id in response: {result}")
        
        logger.info(f"Created async task: {task_id}")
        return task_id
    
    async def _poll_task_result(self, task_id: str, timeout: int = 300) -> dict:
        """Poll task status until completion or timeout."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to query task: {response.status_code} {response.text}")
            
            result = response.json()
            task_status = result.get("output", {}).get("task_status")
            
            logger.info(f"Task {task_id} status: {task_status}")
            
            if task_status == "SUCCEEDED":
                return result
            elif task_status == "FAILED":
                raise ValueError(f"Task failed: {result}")
            elif task_status in ["PENDING", "RUNNING"]:
                # Wait before polling again
                await asyncio.sleep(3)
                continue
            else:
                raise ValueError(f"Unknown task status: {task_status}")
        
        raise ValueError(f"Task {task_id} timeout after {timeout} seconds")
    
    async def _download_image_from_url(self, image_url: str) -> bytes:
        """Download image from URL and return bytes."""
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download image: {response.status_code}")
        return response.content
    
    async def generate_image(self, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Generate image using WanX text-to-image model."""
        model = kwargs.get('model', 'wanx2.1-t2i-turbo')
        size = kwargs.get('size', '1024*1024')
        n = kwargs.get('n', 1)
        
        data = {
            "model": model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": size,
                "n": n
            }
        }
        logger.info(f"Generating image with WanX: {data}")
        try:
            # Create async task
            task_id = await self._create_async_task("/api/v1/services/aigc/text2image/image-synthesis", data)
            
            # Poll for results
            result = await self._poll_task_result(task_id)
            
            # Extract image URL
            results = result.get("output", {}).get("results", [])
            if not results or not results[0].get("url"):
                raise ValueError(f"No image URL in result: {result}")
            
            image_url = results[0]["url"]
            logger.info(f"Generated image URL: {image_url}")
            
            # Download image
            image_bytes = await self._download_image_from_url(image_url)
            
            # Generate filename and save image
            filename = await self.convert_prompt_to_filename(prompt)
            saved_path = await save_image(image_bytes, filename)
            
            return image_bytes, saved_path, image_url
            
        except Exception as e:
            logger.error(f"Error generating image with WanX: {str(e)}")
            raise
    
    async def transform_image(self, image: PIL.Image.Image, prompt: str, **kwargs) -> Tuple[bytes, str, Optional[str]]:
        """Transform image using WanX image editing model.
        
        Args:
            image: Source image to transform (PIL Image object)
            prompt: Text description for transformation
            **kwargs: Additional parameters including:
                - function: Editing function (default: 'description_edit')
                - base_image_url: URL of the source image (if provided, overrides image parameter)
                - mask_image_url: URL of mask image (for description_edit_with_mask function)
                - n: Number of images to generate (default: 1)
        
        Returns:
            Tuple of (image_bytes, saved_image_path, remote_image_url)
        """
        function = kwargs.get('function', 'description_edit')  # Default to instruction editing
        n = kwargs.get('n', 1)
        
        # Check if base_image_url is provided directly
        base_image_url = kwargs.get('base_image_url')
        
        if not base_image_url:
            # Convert PIL image to bytes for potential future upload implementation
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
            
            # For now, we still need a public URL. In production, you would:
            # 1. Upload the image to OSS/cloud storage
            # 2. Get the public URL
            # 3. Use that URL as base_image_url
            raise NotImplementedError(
                "Image transformation requires a public URL for the source image. "
                "Please provide 'base_image_url' in kwargs with a publicly accessible image URL, "
                "or implement image upload to cloud storage (e.g., OSS) to get a public URL."
            )
        
        # Prepare request data based on function type
        data = {
            "model": "wanx2.1-imageedit",
            "input": {
                "function": function,
                "prompt": prompt,
                "base_image_url": base_image_url
            },
            "parameters": {
                "n": n
            }
        }
        
        # Add mask image URL if required for description_edit_with_mask
        if function == "description_edit_with_mask":
            mask_image_url = kwargs.get('mask_image_url')
            if not mask_image_url:
                raise ValueError("mask_image_url is required for description_edit_with_mask function")
            data["input"]["mask_image_url"] = mask_image_url
        
        logger.info(f"Transforming image with WanX: {data}")
        
        try:
            # Create async task for image editing
            task_id = await self._create_async_task("/api/v1/services/aigc/image2image/image-synthesis", data)
            
            # Poll for results
            result = await self._poll_task_result(task_id)
            
            # Extract image URL from results
            results = result.get("output", {}).get("results", [])
            if not results or not results[0].get("url"):
                raise ValueError(f"No image URL in result: {result}")
            
            image_url = results[0]["url"]
            logger.info(f"Transformed image URL: {image_url}")
            
            # Download the transformed image
            image_bytes = await self._download_image_from_url(image_url)
            
            # Generate filename and save image
            filename = await self.convert_prompt_to_filename(f"transform_{prompt}")
            saved_path = await save_image(image_bytes, filename)
            
            return image_bytes, saved_path, image_url
            
        except Exception as e:
            logger.error(f"Error transforming image with WanX: {str(e)}")
            raise
    
    async def translate_text(self, text: str, target_language: str = "chinese") -> str:
        """Translate text using Qwen model."""
        try:
            if target_language.lower() == "chinese":
                system_prompt = "你是一个专业的翻译助手。请将用户输入的文本准确翻译成中文，保持原意不变。只返回翻译结果，不要添加任何解释。"
                user_prompt = f"请将以下文本翻译成中文：{text}"
            else:
                system_prompt = "You are a professional translation assistant. Please accurately translate the user's input text into English while preserving the original meaning. Return only the translation result without any explanations."
                user_prompt = f"Please translate the following text into English: {text}"
            
            data = {
                "model": "qwen-plus",
                "input": {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                },
                "parameters": {
                    "temperature": 0.1,
                    "max_tokens": 1000,
                    "result_format": "message"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/services/aigc/text-generation/generation",
                headers=self.headers,
                json=data
            )
            
            if response.status_code != 200:
                logger.error(f"Qwen API error: {response.status_code} {response.text}")
                return text
            
            result = response.json()
            
            # Extract translated text from response
            choices = result.get("output", {}).get("choices", [])
            if choices and choices[0].get("message", {}).get("content"):
                translated_text = choices[0]["message"]["content"].strip()
                logger.info(f"Qwen translation: '{text}' -> '{translated_text}'")
                return translated_text
            
            logger.warning("No translation result from Qwen, returning original text")
            return text
                
        except Exception as e:
            logger.error(f"Error translating with Qwen: {str(e)}")
            return text
    
    async def convert_prompt_to_filename(self, prompt: str) -> str:
        """Generate simple filename for Bailian images."""
        import uuid
        import re
        
        # Clean prompt for filename
        clean_prompt = re.sub(r'[^\w\s-]', '', prompt)
        clean_prompt = re.sub(r'[\s-]+', '_', clean_prompt)
        truncated = clean_prompt[:20]
        
        return f"bailian_{truncated}_{str(uuid.uuid4())[:8]}" 