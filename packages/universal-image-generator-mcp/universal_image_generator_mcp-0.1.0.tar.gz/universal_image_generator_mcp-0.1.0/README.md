# Multi-Provider Image Generator MCP Server

Generate high-quality images from text prompts using Google's Gemini model or ZHIPU AI's CogView-4 through the MCP protocol.

## Overview

This MCP server allows any AI assistant to generate images using either Google's Gemini AI model or ZHIPU AI's CogView-4 model. The server features a scalable provider architecture, automatic language optimization, intelligent prompt engineering, and local image storage, making it easy to create and manage AI-generated images through any MCP client.

## Supported Providers

### Google Gemini (gemini)
- **Models**: Gemini 2.0 Flash
- **Capabilities**: Text-to-image generation, image transformation
- **Language**: Optimized for English prompts
- **API Key Required**: `GEMINI_API_KEY`

### ZHIPU AI (zhipuai)
- **Models**: CogView-4-250304, CogView-4, CogView-3-Flash (image generation), GLM-4 (translation)
- **Capabilities**: Text-to-image generation only (no transformation), built-in translation via GLM-4
- **Language**: Optimized for Chinese prompts with native GLM-4 translation
- **API Key Required**: `ZHIPU_API_KEY`

### Alibaba Cloud Bailian (bailian)
- **Models**: WanX-2.1 (image generation/editing), Qwen-Plus (translation)
- **Capabilities**: Text-to-image generation and image transformation, built-in translation via Qwen
- **Language**: Optimized for Chinese prompts with native Qwen translation
- **API Key Required**: `DASHSCOPE_API_KEY`

## Features

- **Multi-Provider Support**: Choose between Gemini 2.0 Flash and CogView-4 via environment configuration
- **Scalable Architecture**: Easy to add new image generation providers in the future
- **Language Optimization**: Automatic translation and prompt optimization for each provider
  - English-optimized prompts for Gemini (using Gemini's translation)
  - Chinese-optimized prompts for ZhipuAI (using native GLM-4 translation)
  - Chinese-optimized prompts for Bailian (using native Qwen translation)
- **Capability-Based Tools**: Tools are dynamically registered based on provider capabilities
  - Image generation: Available for all providers
  - Image transformation: Available for Gemini and Bailian (ZhipuAI doesn't support it)
- **Smart Prompt Engineering**: Provider-specific prompt templates for optimal results
- **Multiple Input Formats**: Support for text prompts, file-based images, and base64-encoded images
- **Automatic Filename Generation**: Intelligent filename creation based on prompts
- **Local Image Storage**: Configurable output path for generated images
- **High-Quality Output**: Optimized settings for each provider
- **Strict Text Exclusion**: No text rendered in generated images regardless of prompts

## Available MCP Tools

The server provides the following MCP tools for AI assistants:

### 1. `generate_image_from_text`

Creates a new image from a text prompt description using the configured provider.

```
generate_image_from_text(prompt: str) -> str
```

**Parameters:**
- `prompt`: Text description of the image you want to generate (in any language)

**Returns:**
- Path to the saved image file

**Language Handling:**
- **Gemini**: Prompts are translated to English using Gemini's translation and use English-optimized templates
- **ZhipuAI**: Prompts are translated to Chinese using native GLM-4 and use Chinese-optimized templates
- **Bailian**: Prompts are translated to Chinese using native Qwen and use Chinese-optimized templates

**Examples:**
- "Generate an image of a sunset over mountains"
- "Create a photorealistic flying pig in a sci-fi city"
- "生成一只可爱的小猫咪的图片" (Chinese input works with any provider)

#### Example Output

This image was generated using the prompt:

```
"Hi, can you create a 3d rendered image of a pig with wings and a top hat flying over a happy futuristic scifi city with lots of greenery?"
```

![Flying pig over sci-fi city](examples/flying_pig_scifi_city.png)

*A 3D rendered pig with wings and a top hat flying over a futuristic sci-fi city filled with greenery*

### Known Issues

When using this MCP server with Claude Desktop Host:

1. **Performance Issues**: Using `transform_image_from_encoded` may take significantly longer to process compared to other methods. This is due to the overhead of transferring large base64-encoded image data through the MCP protocol.

2. **Path Resolution Problems**: There may be issues with correctly resolving image paths when using Claude Desktop Host. The host application might not properly interpret the returned file paths, making it difficult to access the generated images.

For the best experience, consider using alternative MCP clients or the `transform_image_from_file` method when possible. 

### 2. `transform_image_from_encoded` *(Gemini & Bailian)*

Transforms an existing image based on a text prompt using base64-encoded image data.

> **Note**: This tool is only available when using the Gemini or Bailian providers. ZhipuAI does not support image transformation.

```
transform_image_from_encoded(encoded_image: str, prompt: str) -> str
```

**Parameters:**
- `encoded_image`: Base64 encoded image data with format header (must be in format: "data:image/[format];base64,[data]")
- `prompt`: Text description of how you want to transform the image

**Returns:**
- Path to the saved transformed image file

**Example:**
- "Add snow to this landscape"
- "Change the background to a beach"

### 3. `transform_image_from_file` *(Gemini & Bailian)*

Transforms an existing image file based on a text prompt.

> **Note**: This tool is only available when using the Gemini or Bailian providers. ZhipuAI does not support image transformation.

```
transform_image_from_file(image_file_path: str, prompt: str) -> str
```

**Parameters:**
- `image_file_path`: Path to the image file to be transformed
- `prompt`: Text description of how you want to transform the image

**Returns:**
- Path to the saved transformed image file

**Examples:**
- "Add a llama next to the person in this image"
- "Make this daytime scene look like night time"

#### Example Transformation

Using the flying pig image created above, we applied a transformation with the following prompt:

```
"Add a cute baby whale flying alongside the pig"
```

**Before:**
![Flying pig over sci-fi city](examples/flying_pig_scifi_city.png)

**After:**
![Flying pig with baby whale](examples/pig_cute_baby_whale.png)

*The original flying pig image with a cute baby whale added flying alongside it*

## Setup

### Prerequisites

- Python 3.11+
- API key for your chosen provider:
  - **Gemini**: Google AI API key 
  - **ZhipuAI**: ZHIPU AI API key
  - **Bailian**: Alibaba Cloud DashScope API key
- MCP host application (Claude Desktop App, Cursor, or other MCP-compatible clients)

### Getting API Keys

#### For Gemini Provider
1. Visit [Google AI Studio API Keys page](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your new API key for use in the configuration
5. Note: The API key provides a certain quota of free usage per month. You can check your usage in the Google AI Studio

#### For ZhipuAI Provider
1. Visit [ZHIPU AI Open Platform](https://bigmodel.cn/dev/api)
2. Register and log in to your account
3. Navigate to API Keys section in your user center
4. Create a new API key
5. Copy your API key for use in the configuration
6. Note: CogView-4 pricing is ¥0.06 per generation, GLM-4 pricing varies. Check [pricing details](https://www.bigmodel.cn/pricing)

#### For Bailian Provider
1. Visit [Alibaba Cloud DashScope](https://dashscope.aliyun.com)
2. Register and log in to your Alibaba Cloud account
3. Navigate to API Keys section in the console
4. Create a new API key
5. Copy your API key for use in the configuration
6. Note: WanX pricing is ¥0.14-¥0.20 per generation, Qwen pricing varies. Check [pricing details](https://www.aliyun.com/product/dashscope)

### Installation

### Installing via PyPi

To be updated


### Manual Installation
1. Clone the repository:
```
git clone https://github.com/ECNU3D/universal-image-generator-mcp.git
cd universal-image-generator-mcp
```

2. Create a virtual environment and install dependencies:
```
# Using regular venv
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Or using uv
uv venv
source .venv/bin/activate
uv pip install -e .
```

3. Copy the example environment file and add your API key:
```
cp .env.example .env
```

4. Edit the `.env` file to configure your chosen provider:

**For Gemini Provider:**
```bash
IMAGE_PROVIDER=gemini
GEMINI_API_KEY="your-gemini-api-key-here"
OUTPUT_IMAGE_PATH="/path/to/save/images"
```

**For ZhipuAI Provider:**
```bash
IMAGE_PROVIDER=zhipuai
ZHIPU_API_KEY="your-zhipu-api-key-here"
OUTPUT_IMAGE_PATH="/path/to/save/images"
```

**For Bailian Provider:**
```bash
IMAGE_PROVIDER=bailian
DASHSCOPE_API_KEY="your-dashscope-api-key-here"
OUTPUT_IMAGE_PATH="/path/to/save/images"
```

### Configure Claude Desktop

Add the following to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**For Gemini Provider:**
```json
{
    "mcpServers": {
        "image-generator": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/universal-image-generator-mcp",
                "run",
                "python",
                "-m",
                "src.mcp_server_gemini_image_generator.server"
            ],
            "env": {
                "IMAGE_PROVIDER": "gemini",
                "GEMINI_API_KEY": "your-gemini-api-key-here",
                "OUTPUT_IMAGE_PATH": "/path/to/save/images"
            }
        }
    }
}
```

**For ZhipuAI Provider:**
```json
{
    "mcpServers": {
        "image-generator": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/universal-image-generator-mcp",
                "run",
                "python",
                "-m",
                "src.mcp_server_gemini_image_generator.server"
            ],
            "env": {
                "IMAGE_PROVIDER": "zhipuai",
                "ZHIPU_API_KEY": "your-zhipu-api-key-here",
                "OUTPUT_IMAGE_PATH": "/path/to/save/images"
            }
        }
    }
}
```

**For Bailian Provider:**
```json
{
    "mcpServers": {
        "image-generator": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/universal-image-generator-mcp",
                "run",
                "python",
                "-m",
                "src.mcp_server_gemini_image_generator.server"
            ],
            "env": {
                "IMAGE_PROVIDER": "bailian",
                "DASHSCOPE_API_KEY": "your-dashscope-api-key-here",
                "OUTPUT_IMAGE_PATH": "/path/to/save/images"
            }
        }
    }
}
```

## Usage

Once installed and configured, you can ask Claude to generate or transform images using prompts like:

### Generating New Images
- "Generate an image of a sunset over mountains"
- "Create an illustration of a futuristic cityscape"
- "Make a picture of a cat wearing sunglasses"

### Transforming Existing Images
- "Transform this image by adding snow to the scene"
- "Edit this photo to make it look like it was taken at night"
- "Add a dragon flying in the background of this picture"

The generated/transformed images will be saved to your configured output path and displayed in Claude. With the updated return types, AI assistants can also work directly with the image data without needing to access the saved files.

## Testing

You can test the application by running the FastMCP development server:

```
fastmcp dev server.py
```

This command starts a local development server and makes the MCP Inspector available at http://localhost:5173/. 
The MCP Inspector provides a convenient web interface where you can directly test the image generation tool without needing to use Claude or another MCP client. 
You can enter text prompts, execute the tool, and see the results immediately, which is helpful for development and debugging.

## License

MIT License
