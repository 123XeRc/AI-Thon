from config.config import AzureOpenAIConfig
from openai import  AsyncAzureOpenAI
from typing import AsyncGenerator, List
from typing import Optional
import time
import random
import asyncio
from pydantic import BaseModel, Field,RootModel
from typing import Dict, Any,List,Optional,Union

from pydantic import BaseModel


class DecodeJsonResult(BaseModel):
    data: Any = None
    error: Union[str, None] = None    
    

class AzureResponseModel(BaseModel):
    content: str
    input_tokens: int
    output_tokens: int
    latency_seconds: Optional[float] = None    
    
    

class EmbeddingResponseModel(BaseModel):
    embedding: List[float]
    model: str
    latency_seconds: float
class StreamingResponseChunk(BaseModel):
    content: str


class AsyncAzureOpenAIHelper:
    def __init__(self):

        self.azure_endpoint = AzureOpenAIConfig.AZURE_ENDPOINT
        self.api_key = AzureOpenAIConfig.AZURE_API_KEY
        self.api_version = AzureOpenAIConfig.API_VERSION
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    async def get_response(
        self,
        system_prompt: str,
        user_prompt: str = "",
        json_mode: bool = False,
        model: str = AzureOpenAIConfig.LLM_DEPLOYMENT,
        retries: int = 3,
        image_b64: Optional[str] = None,
    ) -> AzureResponseModel:
        """
        Sends a chat completion request to Azure OpenAI asynchronously and returns the response.
        """

        input_tokens, output_tokens = 0, 0

        # Build messages depending on text vs multimodal
        if image_b64:
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                        },
                    ],
                },
            ]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

        for attempt in range(1, retries + 1):
            try:
                start = time.time()

                # Base kwargs
                request_kwargs = {
                    "model": model,
                    "messages": messages,
                    
                }

                # Default JSON mode (applied to both reasoning + generation)
                if json_mode:
                    request_kwargs["response_format"] = {"type": "json_object"}

                if model == "gpt-5-mini":
                    # Reasoning API (no temperature/seed)
                    request_kwargs["reasoning_effort"] = "minimal"
                else:
                    # Standard completion API
                    request_kwargs["temperature"] = 0
                    request_kwargs["seed"] = 123

                response = await self.client.chat.completions.create(**request_kwargs)

                end = time.time()
                latency = end - start
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens


                return AzureResponseModel(
                    content=response.choices[0].message.content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_seconds=latency,
                )

            except Exception as ex:
                backoff = (2**attempt) + random.random()
                await asyncio.sleep(backoff)

        raise RuntimeError("Azure OpenAI not responding after all retries")
    
    async def stream_chat_response(

            self,
            system_prompt,
            user_prompt,

            model: str = AzureOpenAIConfig.LLM_DEPLOYMENT,

        ) -> AsyncGenerator[StreamingResponseChunk, None]:

            """

            Streams chat responses asynchronously from Azure OpenAI.
    
            Args:

                prompt (List[dict]): A list of message dictionaries for the chat completion.

                model (str): The Azure OpenAI model to use for generation. Defaults to GPT_GENERATION_4O_MODEL.
    
            Yields:

                AsyncGenerator[StreamingResponseChunk, None]: Yields individual chunks of streamed content wrapped in a Pydantic model.

            """

            try:
                messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
                response = await self.client.chat.completions.create(

                    model=model,

                    temperature=0,

                    messages=messages,

                    stream=True

                )
    
                async for chunk in response:

                    # Only yield chunks with actual content

                    if chunk.choices and chunk.choices[0].delta.content:

                        yield StreamingResponseChunk(content=chunk.choices[0].delta.content)
    
            except Exception as e:


                # Optionally, you can raise or stop iteration

                raise RuntimeError(f"Streaming chat failed: {e}")
    

    async def generate_embeddings(self, text, model=AzureOpenAIConfig.EMBEDDING_DEPLOYMENT):
        """
        Generates embeddings for a given text using the specified model from Azure OpenAI.

        Args:
            text (str): The input text for which embeddings need to be generated.
            model (str): The model used for generating embeddings. Default is configured in the settings.

        Returns:
            list: The generated embeddings.
        """
        
        for delay_secs in (2**x for x in range(0, 2)):
            try:
                
                # Capture start time
                start = time.time()

                # Generate embeddings
                response = await self.client.embeddings.create(input=[text], model=model)
                embedding = response.data[0].embedding

                # Capture end time
                end = time.time()

                # Log the time taken for embedding generation
                return embedding
            except Exception as ex:
                random_value = random.randint(0, 1000) / 1000.0
                sleep_dur = delay_secs + random_value
                time.sleep(sleep_dur)
                continue
    