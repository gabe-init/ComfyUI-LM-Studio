import requests
import json
import re
import os
import tempfile
import time
import numpy as np
from PIL import Image
from typing import Optional, Dict, Tuple, Any

# Try to import LM Studio SDK
try:
    import lmstudio as lms
    HAS_SDK = True
    print("LM Studio SDK found and loaded")
except ImportError:
    lms = None
    HAS_SDK = False
    print("LM Studio SDK not found. Using API fallback. Install SDK with: pip install lmstudio")


class LMStudioNode:
    """
    Unified LM Studio Chat Interface with Vision Support
    Supports both text-only and text+image inputs
    """

    def __init__(self):
        self.default_stats = "Tokens per Second: 0.00\nInput Tokens: 0\nOutput Tokens: 0"

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "You are a helpful assistant."
                }),
                "user_message": ("STRING", {
                    "multiline": True,
                    "default": "Explain quantum computing in simple terms"
                }),
                "model_id": ("STRING", {
                    "multiline": False,
                    "default": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
                }),
                "server_address": ("STRING", {
                    "multiline": False,
                    "default": "http://127.0.0.1:1234"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "max_tokens": ("INT", {
                    "default": 1000,
                    "min": 1,
                    "max": 4096,
                    "step": 1
                }),
                "thinking_tokens": ("BOOLEAN", {
                    "default": True,
                    "label": "Include thinking tokens"
                }),
                "use_sdk": ("BOOLEAN", {
                    "default": True,
                    "label": "Use SDK (if available)"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
                "debug": ("BOOLEAN", {
                    "default": False
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "stats")
    FUNCTION = "get_response"
    CATEGORY = "LM Studio"

    def _clean_thinking_tokens(self, text: str) -> str:
        """Remove thinking tokens from text if needed"""
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    def _prepare_image(self, image: np.ndarray, debug: bool = False) -> Optional[str]:
        """Convert numpy array to temporary file and return path"""
        try:
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(np.uint8(image[0] * 255))
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
                pil_image.save(temp_path, format="JPEG")
            
            if debug:
                print(f"Debug: Saved image to temporary file: {temp_path}")
            
            return temp_path
        except Exception as e:
            if debug:
                print(f"Debug: Error preparing image: {str(e)}")
            return None

    def _format_stats(self, tokens_per_sec: float, input_tokens: int, output_tokens: int) -> str:
        """Format statistics output"""
        return (
            f"Tokens per Second: {tokens_per_sec:.2f}\n"
            f"Input Tokens: {input_tokens}\n"
            f"Output Tokens: {output_tokens}"
        )

    def get_response(self, system_prompt: str, user_message: str, model_id: str, 
                    server_address: str, temperature: float, max_tokens: int,
                    thinking_tokens: bool, use_sdk: bool = True, 
                    image: Optional[np.ndarray] = None, debug: bool = False) -> Tuple[str, str]:
        """Main entry point for getting LM Studio response"""
        
        # Clean message content if thinking tokens disabled
        if not thinking_tokens:
            user_message = self._clean_thinking_tokens(user_message)

        # Debug information
        if debug:
            print(f"Debug: Starting get_response method")
            print(f"Debug: Model: {model_id}")
            print(f"Debug: Use SDK: {use_sdk}")
            print(f"Debug: Has image: {image is not None}")
            if image is not None:
                print(f"Debug: Image shape: {image.shape}")

        # Route to appropriate method
        if HAS_SDK and use_sdk:
            return self._get_response_sdk(
                system_prompt, user_message, model_id, temperature, 
                max_tokens, thinking_tokens, image, debug
            )
        else:
            if image is not None and debug:
                print("Warning: Image input is not supported with API mode. Install LM Studio SDK for image support.")
            return self._get_response_api(
                system_prompt, user_message, model_id, server_address, 
                temperature, thinking_tokens, debug
            )

    def _get_response_sdk(self, system_prompt: str, user_message: str, model_id: str,
                         temperature: float, max_tokens: int, thinking_tokens: bool,
                         image: Optional[np.ndarray] = None, debug: bool = False) -> Tuple[str, str]:
        """Use the LM Studio SDK to get a response"""
        temp_path = None
        
        try:
            # Load the model
            start_time = time.time() if debug else 0
            model = lms.llm(model_id)
            
            if debug:
                print(f"Debug: Model loaded in {time.time() - start_time:.2f}s")
            
            # Create a new chat
            chat = lms.Chat(system_prompt)
            
            # Handle image if provided
            if image is not None:
                temp_path = self._prepare_image(image, debug)
                if temp_path:
                    image_handle = lms.prepare_image(temp_path)
                    chat.add_user_message(user_message, images=[image_handle])
                    if debug:
                        print(f"Debug: Added image to chat message")
                else:
                    # Fallback to text-only if image preparation failed
                    chat.add_user_message(user_message)
            else:
                chat.add_user_message(user_message)
            
            # Configure generation parameters
            config = {
                "temperature": temperature,
                "maxTokens": max_tokens,
            }
            
            if debug:
                print(f"Debug: Sending request with config: {config}")
            
            # Generate response
            result = model.respond(chat, config=config)
            
            if debug:
                print(f"Debug: Response received: {result.content[:100]}...")
                print(f"Debug: Generation time: {result.stats.generation_time_sec}s")
            
            # Extract statistics
            tokens_per_sec = getattr(result.stats, 'tokens_per_second', 0.0)
            input_tokens = getattr(result.stats, 'prompt_tokens_count', 0)
            output_tokens = getattr(result.stats, 'predicted_tokens_count', 0)
            
            # Format output
            output = result.content
            if not thinking_tokens:
                output = self._clean_thinking_tokens(output)
            
            stats_str = self._format_stats(tokens_per_sec, input_tokens, output_tokens)
            
            return (output, stats_str)
            
        except Exception as e:
            error_message = f"Error processing with LM Studio SDK: {str(e)}"
            print(error_message)
            return (error_message, self.default_stats)
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                if debug:
                    print(f"Debug: Removed temporary file: {temp_path}")

    def _get_response_api(self, system_prompt: str, user_message: str, model_id: str,
                         server_address: str, temperature: float, thinking_tokens: bool,
                         debug: bool = False) -> Tuple[str, str]:
        """Use the LM Studio API to get a response (text-only)"""
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "stream": False
        }

        try:
            response = requests.post(
                f"{server_address}/api/v0/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=120
            )
            response.raise_for_status()

            result = response.json()

            # Extract main response
            output = result['choices'][0]['message']['content']
            if not thinking_tokens:
                output = self._clean_thinking_tokens(output)

            # Extract statistics
            usage = result.get('usage', {})
            stats = result.get('stats', {})
            
            tokens_per_sec = stats.get("tokens_per_second", 0.0)
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            stats_str = self._format_stats(tokens_per_sec, input_tokens, output_tokens)

            return (output, stats_str)

        except requests.ConnectionError:
            return (f"Connection error - is LM Studio running at {server_address}?", self.default_stats)
        except requests.Timeout:
            return ("Request timed out - try increasing timeout duration", self.default_stats)
        except Exception as e:
            return (f"Error: {str(e)}", self.default_stats)


# Node registration
NODE_CLASS_MAPPINGS = {
    "LMStudioNode": LMStudioNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LMStudioNode": "LM Studio Chat Interface"
}