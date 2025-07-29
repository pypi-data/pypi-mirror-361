import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
from claude_code_sdk import ClaudeCodeOptions, Message, query
from dotenv import load_dotenv
from google import genai
from litellm import completion, speech
from loguru import logger
from swarms.utils.formatter import formatter
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
)


# Initialize the client
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")


load_dotenv()


class BrowserAgent:
    """
    A high-level browser automation agent that executes web-based tasks using natural language instructions.

    The BrowserAgent class provides a user-friendly interface for performing browser automation tasks
    by interpreting natural language commands and executing them through a browser automation system.
    It supports both synchronous and asynchronous execution modes, making it flexible for various
    use cases.

    Key Features:
        - Natural language task interpretation
        - Asynchronous and synchronous execution modes
        - Browser automation with state management
        - Structured JSON output for task results
        - Error handling and recovery

    Attributes:
        agent_name (str): Name identifier for the agent instance
        model_name (str): The language model to use for task interpretation

    Example:
        >>> agent = BrowserAgent(agent_name="MyBrowserBot")
        >>> result = agent.run("Go to example.com and get the page title")
        >>> print(result)  # JSON-formatted result with actions and outputs

    Notes:
        - The agent uses a language model to interpret natural language commands
        - All browser interactions are automated and headless by default
        - Results are returned in a structured JSON format for easy parsing
        - The agent maintains session state across multiple commands
        - Error handling is built in for common browser automation issues
    """

    def __init__(
        self,
        agent_name: str = "BrowserAgent",
        model_name: str = "claude-3-5-sonnet-20240620",
    ):
        """
        Initialize a new BrowserAgent instance.

        Args:
            agent_name (str, optional): Name identifier for this agent instance.
                Defaults to "BrowserAgent".
            model_name (str, optional): The language model to use for task interpretation.
                Defaults to "claude-3-5-sonnet-20240620".
        """
        self.agent_name = agent_name

    async def call_browser_agent(self, task: str):
        """
        Asynchronously executes a browser automation agent to perform a specified task.

        This method creates an instance of the BrowserAgentBase, which is configured to use
        a language model (currently hardcoded to OpenAI's GPT-4o) to interpret and execute
        the provided task in a browser environment. The agent is run asynchronously, and upon
        completion, the result is serialized to a JSON-formatted string with indentation for readability.

        Args:
            task (str): A natural language description of the task to be performed by the browser agent.
                This could be anything from "search for the latest news on AI" to "fill out a web form".

        Returns:
            str: A JSON-formatted string representing the result of the browser agent's execution.
                The structure of the JSON includes details about the actions taken, the final state,
                and any outputs or errors encountered during execution.

        Example:
            >>> agent = BrowserAgent()
            >>> asyncio.run(agent.call_browser_agent("Search for weather in New York"))
            '{\n    "model_output": {...},\n    "result": [...],\n    "state": {...}\n}'
        """
        from browser_use import Agent as BrowserAgentBase
        from langchain_openai import ChatOpenAI

        agent = BrowserAgentBase(
            task=task,
            llm=ChatOpenAI(model="gpt-4o"),
        )
        result = await agent.run()
        return result.model_dump_json(indent=4)

    def run(self, task: str):
        """
        Synchronously runs the browser agent for a given task.

        This method wraps the asynchronous `call_browser_agent` method, allowing users to
        invoke the browser agent in a blocking (synchronous) manner. It is suitable for
        scripts or environments where asynchronous execution is not desired or supported.

        Args:
            task (str): The task description for the browser agent to perform. This should be
                a clear, natural language instruction describing what the agent should do in the browser.

        Returns:
            str: The JSON-formatted result of the browser agent's execution, as returned by
                `call_browser_agent`. This includes the full trace of actions, results, and state.

        Example:
            >>> result = BrowserAgent().run("Find the top 3 trending GitHub repositories")
            >>> print(result)
            {
                "model_output": {...},
                "result": [...],
                "state": {...}
            }
        """
        return asyncio.run(self.call_browser_agent(task))


class HuggingFaceAPI:
    """
    A comprehensive wrapper for interacting with Hugging Face models and pipelines.

    This class provides a unified interface for working with various Hugging Face models,
    supporting multiple tasks such as text generation, question answering, and more.
    It handles model loading, device management, and provides robust error handling.

    Key Features:
        - Automatic device selection (GPU/CPU)
        - Pipeline-based and manual model loading
        - Support for model quantization
        - Flexible text generation options
        - Robust error handling and fallback mechanisms

    Attributes:
        model_id (str): The identifier of the Hugging Face model
        task_type (str): The type of task the model should perform
        device (str): The device to run the model on ("cuda" or "cpu")
        max_length (int): Maximum length for generated text
        quantize (bool): Whether to use model quantization
        quantization_config (dict): Configuration for model quantization
        pipeline: The Hugging Face pipeline instance
        model: The raw model instance (if pipeline initialization fails)
        tokenizer: The model's tokenizer (if pipeline initialization fails)

    Example:
        >>> # Initialize for text generation
        >>> api = HuggingFaceAPI(
        ...     model_id="gpt2",
        ...     task_type="text-generation",
        ...     max_length=100
        ... )
        >>> # Generate text
        >>> result = api.generate("Once upon a time")
        >>> print(result)

    Notes:
        - The class automatically handles GPU/CPU device selection
        - Pipeline initialization failures trigger fallback to manual model loading
        - Error handling is built in for all operations
        - Supports both pipeline-based and raw model interactions
        - Memory management is handled automatically
    """

    def __init__(
        self,
        model_id: str,
        task_type: str = "text-generation",
        device: Optional[str] = None,
        max_length: int = 100,
        quantize: bool = False,
        quantization_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize the HuggingFace API wrapper.

        Args:
            model_id (str): The model ID from Hugging Face Hub
            task_type (str): Type of task ("text-generation", "question-answering", etc.)
            device (str, optional): Device to run the model on ("cuda", "cpu")
            max_length (int): Maximum length for generated text
            quantize (bool): Whether to use quantization
            quantization_config (dict, optional): Configuration for quantization
            **kwargs: Additional arguments for model initialization
        """
        self.model_id = model_id
        self.task_type = task_type
        self.device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.max_length = max_length
        self.quantize = quantize
        self.quantization_config = quantization_config or {}

        # Initialize the pipeline based on task type
        try:
            self.pipeline = pipeline(
                task=task_type,
                model=model_id,
                device=self.device,
                **kwargs,
            )
        except Exception as e:
            print(f"Error initializing pipeline: {e}")
            # Fallback to manual model loading
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=self.device,
                torch_dtype=(
                    torch.float16
                    if self.device == "cuda"
                    else torch.float32
                ),
                **kwargs,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.pipeline = None

    def generate(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        num_return_sequences: int = 1,
        **kwargs,
    ) -> Union[str, List[str]]:
        """
        Generate text using the model.

        Args:
            prompt (str): Input text prompt
            max_length (int, optional): Override default max_length
            num_return_sequences (int): Number of sequences to generate
            **kwargs: Additional generation parameters

        Returns:
            Union[str, List[str]]: Generated text or list of generated texts
        """
        try:
            if self.pipeline:
                outputs = self.pipeline(
                    prompt,
                    max_length=max_length or self.max_length,
                    num_return_sequences=num_return_sequences,
                    **kwargs,
                )

                if isinstance(outputs, list):
                    if self.task_type == "text-generation":
                        return [
                            out["generated_text"] for out in outputs
                        ]
                    return outputs
                return (
                    outputs["generated_text"]
                    if "generated_text" in outputs
                    else outputs
                )

            # Manual generation if pipeline is not available
            inputs = self.tokenizer(prompt, return_tensors="pt").to(
                self.device
            )
            outputs = self.model.generate(
                **inputs,
                max_length=max_length or self.max_length,
                num_return_sequences=num_return_sequences,
                **kwargs,
            )
            return self.tokenizer.batch_decode(
                outputs, skip_special_tokens=True
            )

        except Exception as e:
            print(f"Error in generation: {e}")
            return f"Error generating text: {str(e)}"

    def run(self, task: str, **kwargs) -> str:
        """
        Run the model on a given task.

        Args:
            task (str): The task/prompt to process
            **kwargs: Additional parameters for generation

        Returns:
            str: Generated output
        """
        result = self.generate(task, **kwargs)
        if isinstance(result, list):
            return result[0]
        return result


def call_huggingface_model(
    task: str,
    model_id: str,
    max_length: int = 100,
) -> str:
    """
    Call a Hugging Face model to perform a text generation task.

    This function provides a simplified interface to interact with Hugging Face models.
    It creates a new instance of HuggingFaceAPI for each call, which ensures clean
    state management but may impact performance for repeated calls to the same model.

    Args:
        task (str): The text prompt or task description to be processed by the model.
            This could be a question, a text completion prompt, or any other text input
            that the model should process.

        model_id (str): The identifier of the Hugging Face model to use.
            Examples:
            - "gpt2" for OpenAI's GPT-2 model
            - "facebook/opt-350m" for Meta's OPT model
            - "bigscience/bloom" for the BLOOM model
            For a complete list, visit: https://huggingface.co/models

        max_length (int, optional): The maximum length of the generated text in tokens.
            Defaults to 100. This parameter helps control the length of the model's
            output and manage computational resources.

    Returns:
        str: The generated text output from the model. The exact format depends on
            the model being used, but typically includes:
            - For text generation: The completed text based on the input prompt
            - For question answering: The answer to the provided question
            - For other tasks: Task-specific output in text format

    Examples:
        >>> # Generate text with GPT-2
        >>> result = call_huggingface_model(
        ...     task="Once upon a time",
        ...     model_id="gpt2",
        ...     max_length=50
        ... )
        >>> print(result)

        >>> # Use a larger model for more complex tasks
        >>> answer = call_huggingface_model(
        ...     task="What is quantum computing?",
        ...     model_id="facebook/opt-1.3b",
        ...     max_length=200
        ... )
        >>> print(answer)

    Notes:
        - The function creates a new model instance for each call, which may be
          inefficient for repeated calls to the same model.
        - The model is automatically placed on GPU if available, falling back to CPU.
        - Error handling is managed by the underlying HuggingFaceAPI class.
        - The actual output length may be shorter than max_length depending on the
          model's generation parameters and stopping criteria.

    Raises:
        Exception: Any exceptions from model loading or generation are caught by
            HuggingFaceAPI and returned as error messages in the output string.
    """
    model = HuggingFaceAPI(
        model_id=model_id,
        task_type="text-generation",
        max_length=max_length,
    )
    return model.run(task)


async def call_terminal_developer_agent_async(
    task: str,
    max_turns: int = 3,
    system_prompt: str = "You are a helpful assistant",
    cwd: str = None,
    allowed_tools: list = None,
    permission_mode: str = "acceptEdits",
):
    """
    Call the Claude Code terminal developer agent with the specified parameters.

    Args:
        task (str): The prompt or task to send to the agent.
        max_turns (int): Maximum number of conversational turns. Default is 3.
        system_prompt (str): System prompt for the agent. Default is a helpful assistant.
        cwd (str, optional): Working directory for the agent. Default is None.
        allowed_tools (list, optional): List of allowed tools. Default is ["Read", "Write", "Bash"].
        permission_mode (str): Permission mode for the agent. Default is "acceptEdits".

    Returns:
        list: List of serialized Message objects returned by the agent.
    """

    # if allowed_tools is None:
    allowed_tools = ["Read", "Write", "Bash"]

    async def main():
        messages: list[Message] = []
        options = ClaudeCodeOptions(
            max_turns=max_turns,
            system_prompt=system_prompt,
            cwd=Path(cwd) if cwd else None,
            allowed_tools=allowed_tools,
            permission_mode=permission_mode,
        )
        async for message in query(prompt=task, options=options):
            messages.append(message)
            logger.info(
                f"Claude Code Terminal Developer Agent Message: {message}"
            )

        # Convert messages to serializable format
        serialized_messages = []
        for msg in messages:
            try:
                # Try to get message attributes
                msg_dict = {
                    "type": (
                        msg.type if hasattr(msg, "type") else None
                    ),
                    "content": (
                        msg.content
                        if hasattr(msg, "content")
                        else None
                    ),
                    "role": (
                        msg.role if hasattr(msg, "role") else None
                    ),
                    "metadata": (
                        msg.metadata
                        if hasattr(msg, "metadata")
                        else None
                    ),
                }
                # Remove None values
                msg_dict = {
                    k: v for k, v in msg_dict.items() if v is not None
                }
                serialized_messages.append(msg_dict)
            except Exception as e:
                logger.error(f"Error serializing message: {e}")
                # Include basic string representation if serialization fails
                serialized_messages.append({"content": str(msg)})

        return json.dumps(serialized_messages, indent=2)

    return await main()


def call_terminal_developer_agent(
    task: str,
    max_turns: int = 3,
    system_prompt: str = "You are a helpful assistant",
    cwd: str = None,
    allowed_tools: list = None,
    permission_mode: str = "acceptEdits",
) -> str:
    """
    Call the Claude Code terminal developer agent with the specified parameters. This Terminal developer agent
    can transform feature descriptions into code, build entire applications, and much much more.

    Args:
        task (str): The prompt or task to send to the agent. This should be a clear instruction
            or question that the agent can act upon.
        max_turns (int, optional): Maximum number of conversational turns the agent can take.
            Defaults to 3. Higher values allow for more complex multi-step interactions.
        system_prompt (str, optional): System-level prompt that defines the agent's behavior and role.
            Defaults to "You are a helpful assistant".
        cwd (str, optional): Working directory for the agent to operate in. If None, uses the
            current working directory. Defaults to None.
        allowed_tools (list, optional): List of tools the agent is allowed to use.
            Defaults to ["Read", "Write", "Bash"] if None is provided.
        permission_mode (str, optional): Controls how the agent handles permissions for actions.
            Defaults to "acceptEdits". Other options may be available based on the agent's configuration.

    Returns:
        str: A JSON string containing the list of serialized Message objects with the agent's responses and actions.
            Each Message object contains the details of the agent's interactions and outputs.

    Example:
        >>> messages = call_terminal_developer_agent(
        ...     task="Create a new Python file that prints 'Hello World'",
        ...     max_turns=2,
        ...     cwd="/path/to/project"
        ... )
        >>> print(messages)  # Returns JSON string of messages

    Notes:
        - This function uses asyncio.run() internally to run the async version
        - The function blocks until the agent completes its task or reaches max_turns
        - All exceptions from the async version are propagated to the caller
        - The returned messages can be used to track the agent's actions and reasoning
    """
    import json

    logger.info(f"Calling terminal developer agent with task: {task}")
    output = asyncio.run(
        call_terminal_developer_agent_async(
            task=task,
            max_turns=max_turns,
            system_prompt=system_prompt,
            cwd=cwd,
            allowed_tools=allowed_tools,
            permission_mode=permission_mode,
        )
    )
    return json.dumps(output, indent=2)


def list_models_on_litellm():
    """
    List all models supported by the litellm library.

    This function retrieves a comprehensive list of all language models available through
    the litellm library. The list includes models from various providers such as OpenAI,
    Anthropic, and others that are supported by litellm's unified interface.

    Returns:
        List[str]: A list of model identifiers that can be used with litellm.
            Each identifier is a string that can be passed to call_models_on_litellm().

    Example:
        >>> models = list_models_on_litellm()
        >>> print("Available models:")
        >>> for model in models:
        ...     print(f"- {model}")

    Notes:
        - The list of available models may change based on your litellm version
        - Some models may require specific API keys or authentication
        - Models may have different capabilities and token limits
        - Check litellm's documentation for the most up-to-date model list
    """
    from litellm import model_list

    return model_list


def generate_speech(
    text: str,
    voice: Optional[str] = "alloy",
    model: Optional[str] = "openai/tts-1",
    file_path: Optional[str] = "speech.mp3",
):
    """
    Generate speech audio from text using a specified voice and model.

    This function converts the provided text into speech using the OpenAI TTS API (or any compatible model via LiteLLM).
    It saves the generated audio to the specified file path.

    Example usage:
        >>> audio_path = generate_speech(
        ...     text="Hello, world!",
        ...     voice="alloy",
        ...     model="openai/tts-1",
        ...     file_path="hello.mp3"
        ... )
        >>> print(f"Audio saved at: {audio_path}")

    Args:
        text (str): The text to be converted into speech.
        voice (str, optional): The voice to use for speech synthesis. Defaults to "alloy".
        model (str, optional): The speech synthesis model to use. Defaults to "openai/tts-1".
        file_path (str, optional): The path where the generated audio file will be saved. Defaults to "speech.mp3".

    Returns:
        Path: The path to the generated speech audio file.

    Notes for the model:
        - You can use this function to generate speech from any text output.
        - If a user requests audio output, call this function with the desired text.
        - The function supports different voices and models if available.
        - The resulting audio file can be played back or sent to the user.

    """

    speech_file_path = Path(__file__).parent / file_path
    response = speech(
        model=model,
        voice=voice,
        input=text,
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path


def call_models_on_litellm(
    model_name: str,
    task: str,
    temperature: float = 0.5,
):
    """
    Call various LLM models through litellm's unified interface with automatic token management.

    This function provides a standardized way to interact with multiple LLM providers and models
    through litellm's abstraction layer. It automatically handles token limits and provides a
    consistent interface across different model providers.

    Available Models:

    Anthropic Claude Models:
        - 'claude-opus-4-20250514': Latest Claude Opus model (most capable)
        - 'claude-sonnet-4-20250514': Latest Claude Sonnet model (balanced)
        - 'claude-3-7-sonnet-20250219': Claude 3.7 Sonnet
        - 'claude-3-5-sonnet-20240620': Claude 3.5 Sonnet
        - 'claude-3-haiku-20240307': Claude 3 Haiku (fastest)
        - 'claude-3-opus-20240229': Claude 3 Opus
        - 'claude-3-sonnet-20240229': Claude 3 Sonnet
        - 'claude-2.1': Legacy Claude 2.1
        - 'claude-2': Legacy Claude 2
        - 'claude-instant-1.2': Legacy Claude Instant 1.2
        - 'claude-instant-1': Legacy Claude Instant 1

    OpenAI GPT Models:

    Other Models:
        - 'gpt-4o-mini': GPT-4 Optimized Mini variant
        - 'gpt-4o': GPT-4 Optimized
        - 'gpt-4.1': GPT-4.1 (latest)

    Args:
        model_name (str): The identifier for the model to use. Must be one of the supported
            model names listed above.
        task (str): The task or prompt to send to the model.
        temperature (float, optional): Controls randomness in the model's output.
            Ranges from 0.0 (deterministic) to 1.0 (creative). Defaults to 0.5.
        system_prompt (str, optional): A system-level prompt to guide the model's behavior.
            If None, no system prompt is used.

    Returns:
        str: The model's response text.

    Examples:
        >>> # Using Claude 3 Opus for complex reasoning
        >>> response = call_models_on_litellm(
        ...     model_name="claude-3-opus-20240229",
        ...     task="Explain quantum computing to a high school student",
        ...     temperature=0.7,
        ...     system_prompt="You are a helpful physics teacher"
        ... )
        >>> print(response)

        >>> # Using GPT-4 for code generation
        >>> code = call_models_on_litellm(
        ...     model_name="gpt-4",
        ...     task="Write a Python function to calculate Fibonacci numbers",
        ...     temperature=0.2
        ... )
        >>> print(code)

    Notes:
        - Token limits are automatically handled by litellm based on the model's capabilities
        - The function uses litellm's completion endpoint which provides a unified interface
        - System prompts can help guide the model's behavior and role
        - Temperature values closer to 0 are better for tasks requiring accuracy
        - Temperature values closer to 1 are better for creative tasks
    """
    from litellm.utils import get_max_tokens

    max_llm_tokens = get_max_tokens(model_name)

    response = completion(
        model=model_name,
        messages=[
            # {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ],
        temperature=temperature,
        max_tokens=max_llm_tokens,
        top_p=1,
    )

    return response.choices[0].message.content


def safe_calculator(expression: str) -> str:
    """
    Safely evaluate mathematical expressions and perform calculations.

    This function provides a secure way to evaluate mathematical expressions by:
    1. Only allowing basic mathematical operations and numbers
    2. Sanitizing input to prevent code injection
    3. Handling division by zero and other mathematical errors

    Args:
        expression (str): A mathematical expression as a string.
            Examples:
            - "2 + 2"
            - "10 * 5"
            - "(3 + 4) * 2"
            - "10 / 2"
            - "2 ** 3"  # Exponentiation
            - "9 % 4"   # Modulo

    Returns:
        str: The result of the calculation as a string, or an error message if:
            - The expression is invalid
            - Division by zero is attempted
            - The expression contains unauthorized operations
            - Any other mathematical error occurs

    Examples:
        >>> safe_calculator("2 + 2")
        '4'
        >>> safe_calculator("(3 + 4) * 2")
        '14'
        >>> safe_calculator("10 / 0")
        'Error: Division by zero'
        >>> safe_calculator("import os")
        'Error: Invalid expression'
    """
    # List of allowed characters
    allowed_chars = set("0123456789.+-*/(). %")
    # Remove all whitespace
    expression = "".join(expression.split())

    # Check if expression only contains allowed characters
    if not all(c in allowed_chars for c in expression):
        return "Error: Invalid expression - only basic mathematical operations are allowed"

    try:
        # Additional security check for potentially dangerous expressions
        if any(
            keyword in expression.lower()
            for keyword in ["eval", "exec", "import", "__"]
        ):
            return "Error: Invalid expression"

        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})

        # Format the result
        if isinstance(result, (int, float)):
            # Handle very large or very small numbers
            if abs(result) > 1e15 or (
                abs(result) < 1e-15 and result != 0
            ):
                return f"{result:.2e}"
            # For regular floats, limit decimal places
            elif isinstance(result, float):
                return f"{result:.6f}".rstrip("0").rstrip(".")
            return str(result)
        return "Error: Invalid result type"

    except ZeroDivisionError:
        return "Error: Division by zero"
    except (SyntaxError, NameError, TypeError):
        return "Error: Invalid expression"
    except Exception as e:
        return f"Error: {str(e)}"


def process_video_with_gemini(
    video_path: str = None,
    task: str = "Create a detailed and comprehensive summary of the video",
    model_name: str = "gemini-2.0-flash",
):
    """
    Process a video file using Google's Gemini model for analysis and understanding.

    This function uploads a video file to Google's Gemini model and processes it according
    to the specified task. It can perform various video analysis tasks such as:
    - Summarization
    - Object detection
    - Action recognition
    - Scene understanding
    - Content analysis

    Args:
        video_path (str, optional): Path to the video file to be processed.
            If None, the function will raise an error. Defaults to None.
        task (str, optional): The specific task or instruction for video analysis.
            Defaults to "Create a detailed and comprehensive summary of the video".
        model_name (str, optional): The specific Gemini model version to use.
            Defaults to "gemini-2.0-flash".

    Returns:
        None: The function prints the model's response directly to stdout.
            Future versions may return the response instead of printing.

    Example:
        >>> process_video_with_gemini(
        ...     video_path="path/to/video.mp4",
        ...     task="Identify all people and their actions in the video",
        ...     model_name="gemini-2.0-flash"
        ... )

    Notes:
        - Requires the 'google.generativeai' package to be installed
        - Needs proper authentication set up for Google's API
        - Video file size and format limitations apply based on Gemini's constraints
        - Processing time depends on video length and complexity
        - The model's response is printed to stdout (may be changed in future versions)
    """
    from google import genai

    client = genai.Client()

    myfile = client.files.upload(file=video_path)

    response = client.models.generate_content(
        model=model_name, contents=[myfile, task]
    )

    print(response.text)


def run_browser_agent(task: str) -> str:
    """
    Run the browser agent on a given task and return the result as a JSON-formatted string.

    This is a convenience function that instantiates a `BrowserAgent` and executes the specified
    task using the agent. It abstracts away the details of agent instantiation and execution,
    providing a simple interface for running browser automation tasks.

    Args:
        task (str): The task description for the browser agent to perform. This should be a
            natural language instruction, such as "navigate to example.com and extract the headline".

    Returns:
        str: The JSON-formatted result of the browser agent's execution. The output includes
            detailed information about the actions performed, the resulting browser state,
            and any outputs or errors encountered.

    Example:
        >>> output = run_browser_agent("Go to Wikipedia and summarize the main page")
        >>> print(output)
        {
            "model_output": {...},
            "result": [...],
            "state": {...}
        }

    Notes:
        - The agent uses a language model (currently GPT-4o) to interpret and execute the task.
        - The returned JSON can be parsed for further programmatic analysis or logging.
        - This function is blocking and should be called from synchronous code.
    """
    model: BrowserAgent = BrowserAgent()
    return model.run(task)


def respond_to_user(response: str):
    """
    Respond to the user and don't use any tools.

    This tool should be used when the agent's response does not require invoking any external tools,
    plugins, or APIs, and the answer can be provided directly as a text response to the user.

    Use this function when:
      - The user's request can be answered directly from the agent's own knowledge or reasoning.
      - No file processing, web browsing, code execution, or external data retrieval is needed.
      - The agent should simply return a message, summary, or explanation in natural language.

    Do NOT use this function if:
      - The response requires searching documents, browsing the web, or running code.
      - Any tool or plugin must be invoked to fulfill the user's request.
    """
    formatter.print_panel(
        content=response,
        title="AgentOS Response",
    )

    return response


def generate_video_single_clip(
    prompt: str,
    number_of_videos: int = 2,
    video_path: str = "output.mp4",
):
    """
    Generate a video using Google's Veo 3.0 video generation model via the GenAI SDK.

    This function takes a natural language prompt and generates a video (or multiple videos)
    according to the specified parameters. It uses the "veo-3.0-generate-preview" model
    hosted on Vertex AI, and supports options such as video duration, number of videos,
    aspect ratio, and whether to enhance the prompt and generate audio.

    Args:
        prompt (str):
            A detailed natural language description of the video you want to generate.
            The prompt should clearly specify the scene, actions, style, and any other
            relevant details to guide the model in producing the desired video.
            Example: "A futuristic cityscape at night with flying cars and neon lights."
        number_of_videos (int, optional):
            The number of video variations to generate for the given prompt. Default is 2.
            Each video will be a unique interpretation of the prompt.
        video_path (str, optional):
            The file path where the first generated video will be saved. Default is "output.mp4".

    Returns:
        str: The file path where the generated video has been saved.

    Notes:
        - The function currently saves only the first generated video, even if multiple are requested.
        - The model supports additional configuration options such as aspect ratio, prompt enhancement, and audio generation.
        - Ensure that your Google Cloud project has access to the Veo 3.0 model and that you have the necessary permissions.
        - Video generation may take several minutes depending on the prompt and duration.
        - For best results, use clear and descriptive prompts.

    Example:
        >>> generate_video(
        ...     prompt="A cat surfing on a wave at sunset, cinematic style",
        ...     video_duration=10,
        ...     number_of_videos=1,
        ...     video_path="cat_surfing.mp4"
        ... )
        Video saved as cat_surfing.mp4

    """
    client = genai.Client(
        vertexai=True, project=PROJECT_ID, location=LOCATION
    )

    # Submit the video generation request to the Veo 3.0 model
    operation = client.models.generate_videos(
        model="veo-3.0-generate-preview",
        prompt=prompt,
        config=genai.types.GenerateVideosConfig(
            aspect_ratio="16:9",
            number_of_videos=number_of_videos,
            duration_seconds=8,
            enhance_prompt=True,
            generate_audio=True,
        ),
    )

    # Poll the operation status until the video is ready
    while not operation.done:
        time.sleep(15)
        operation = client.operations.get(operation)
        print("Operation status:", operation)

    # Save the first generated video to the specified file path
    if operation.response:
        video_bytes = operation.result.generated_videos[
            0
        ].video.video_bytes
        with open(video_path, "wb") as out_file:
            out_file.write(video_bytes)
        print(f"Video saved as {video_path}")

    return video_path
