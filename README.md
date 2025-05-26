# ComfyUI LM Studio Node

A powerful ComfyUI custom node that seamlessly integrates LM Studio's local language models into your ComfyUI workflows. This node supports both text-only and multimodal (text + image) inputs, making it perfect for complex AI-driven creative workflows.

![ComfyUI LM Studio Example](./example.png)

## Features

- **Unified Interface**: Single node for both text-only and text+image inputs
- **Dual Mode Support**: Works with both LM Studio SDK (recommended) and REST API
- **Vision Model Support**: Process images alongside text prompts with compatible models
- **Real-time Statistics**: Monitor tokens per second, input/output token counts
- **Thinking Tokens**: Optional support for models that use thinking tokens
- **Flexible Configuration**: Adjust temperature, max tokens, and server settings
- **Debug Mode**: Built-in debugging for troubleshooting

## Installation

### Prerequisites

1. **ComfyUI**: Make sure you have ComfyUI installed and running
2. **LM Studio**: Download and install [LM Studio](https://lmstudio.ai/) (free)
3. **Python**: Python 3.8 or higher
4. **Show Text Node**: Install [ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts) for the Show Text node used in the example workflow (any other text display node will also work)

### Installation Steps

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/gabe-init/ComfyUI-LM-Studio
   ```

3. Install the required dependencies:
   ```bash
   cd ComfyUI-LM-Studio
   pip install -r requirements.txt
   ```

4. Restart ComfyUI to load the new node

### LM Studio Setup

1. Open LM Studio and download a model (e.g., Mistral 7B Instruct)
2. Start the local server in LM Studio (default port: 1234)
3. Note the model ID from LM Studio for use in the node

## Usage

### Basic Text Generation

1. Add the "LM Studio Chat Interface" node to your workflow
2. Configure the following inputs:
   - **System Prompt**: Set the assistant's behavior
   - **User Message**: Your input prompt
   - **Model ID**: The exact model ID from LM Studio
   - **Server Address**: Usually `http://127.0.0.1:1234`
   - **Temperature**: Control randomness (0.0-1.0)
   - **Max Tokens**: Maximum response length

### Vision Model Usage

For models that support vision (like LLaVA):

1. Connect an image output to the node's image input
2. The node will automatically process both text and image
3. Make sure you're using the SDK mode for image support

### Configuration Options

- **Use SDK**: Enable for better performance and image support (requires `lmstudio` package)
- **Include Thinking Tokens**: For models that support chain-of-thought reasoning
- **Debug Mode**: Enable to see detailed processing information

## Example Workflow

An example workflow is included in `example_workflow/Example_Workflow.json`. This demonstrates:
- Basic text generation setup
- Parameter configuration
- Integration with other ComfyUI nodes

## Troubleshooting

### Connection Issues
- Ensure LM Studio server is running
- Check the server address matches LM Studio's settings
- Verify firewall isn't blocking local connections

### Performance Tips
- Use SDK mode when possible for better performance
- Adjust max tokens based on your needs
- For vision models, use reasonable image sizes

### Common Errors
- "Model not found": Verify the model ID matches exactly what's shown in LM Studio
- "Connection refused": Make sure LM Studio server is started
- Image processing issues: Install the SDK with `pip install lmstudio`

## Advanced Features

### SDK vs API Mode
- **SDK Mode**: Direct integration, supports images, better performance
- **API Mode**: REST-based fallback, text-only, works without SDK

### Debug Output
Enable debug mode to see:
- Model loading times
- Image processing status
- Token generation statistics
- Detailed error messages

## Requirements

- Python 3.8+
- ComfyUI
- LM Studio (running locally)
- See `requirements.txt` for Python packages

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
