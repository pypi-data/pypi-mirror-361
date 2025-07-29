# Universal Image Generator MCP Server

Multi-provider AI image generation server for MCP clients. Generate high-quality images using Google Gemini, ZHIPU AI CogView-4, or Alibaba Bailian through any MCP-compatible application.

## Features

- **Multi-Provider Support**: Choose between Gemini, ZhipuAI, or Bailian
- **Image Generation**: Text-to-image for all providers  
- **Image Transformation**: Edit existing images (Gemini & Bailian only)
- **Smart Language Optimization**: Automatic prompt translation and optimization
- **Local Storage**: Save generated images to your specified directory

## Quick Setup

### 1. Install via uvx

No manual installation required! The server will be automatically downloaded and run.

### 2. Get API Keys

Choose one provider and get an API key:

- **Gemini**: [Google AI Studio](https://aistudio.google.com/apikey)
- **ZhipuAI**: [ZHIPU AI Platform](https://bigmodel.cn/dev/api) 
- **Bailian**: [Alibaba DashScope](https://dashscope.aliyun.com)

### 3. Configure MCP Client

Add to your MCP client configuration (e.g., `claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "universal-image-generator": {
            "command": "uvx",
            "args": [
                "universal-image-generator-mcp"
            ],
            "env": {
                "IMAGE_PROVIDER": "zhipuai",
                "ZHIPU_API_KEY": "your-api-key-here",
                "GEMINI_API_KEY": "your-api-key-here",
                "DASHSCOPE_API_KEY": "your-api-key-here",
                "OUTPUT_IMAGE_PATH": "/path/to/save/images"
            }
        }
    }
}
```

**Environment Variables:**
- `IMAGE_PROVIDER`: `"gemini"`, `"zhipuai"`, or `"bailian"`
- Set the corresponding API key for your chosen provider
- `OUTPUT_IMAGE_PATH`: Directory to save generated images (optional)

## Available Tools

### `generate_image_from_text`
Create images from text descriptions.
```
generate_image_from_text(prompt: str) -> str
```

### `transform_image_from_encoded` *(Gemini & Bailian only)*
Transform images using base64-encoded image data.
```
transform_image_from_encoded(encoded_image: str, prompt: str) -> str
```

### `transform_image_from_file` *(Gemini & Bailian only)*
Transform existing image files.
```
transform_image_from_file(image_file_path: str, prompt: str) -> str
```

## Usage Examples

Once configured, ask your AI assistant:

- "Generate an image of a sunset over mountains"
- "Create a 3D rendered flying pig in a sci-fi city"
- "Transform this image by adding snow to the scene"

Generated images are saved to your configured output directory.

## Example Output

**Prompt:** "Create a 3D rendered image of a pig with wings and a top hat flying over a futuristic sci-fi city with lots of greenery"

![Flying pig over sci-fi city](examples/flying_pig_scifi_city.png)

**Transform:** "Add a cute baby whale flying alongside the pig"

![Flying pig with baby whale](examples/pig_cute_baby_whale.png)

## Provider Capabilities

| Provider | Generation | Transformation | Language Optimization |
|----------|------------|----------------|----------------------|
| Gemini   | ✅         | ✅             | English prompts       |
| ZhipuAI  | ✅         | ❌             | Chinese prompts       |
| Bailian  | ✅         | ✅             | Chinese prompts       |

## Development

Test the server locally:
```bash
git clone https://github.com/ECNU3D/universal-image-generator-mcp.git
cd universal-image-generator-mcp
fastmcp dev src/universal_image_generator_mcp/server.py
```

Visit http://localhost:5173/ to use the MCP Inspector for testing.

## License

MIT License
