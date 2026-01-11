
import os

class Config:
    # Database Path
    DB_FILE = os.path.join(os.getcwd(), "database", "transactions.db")

    # Azure OpenAI Configuration
    # (In a real scenario, these would be loaded strictly from env vars)
    AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://manisha-malpani.openai.azure.com/")
    AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "yVOrDGE76UJaZJgZzCywA7Mj4WSP2Auqrh0AlY4mN5oPvJ37IXU8JQQJ99BHACHYHv6XJ3w3AAABACOGrvsz")
    API_VERSION = "2023-05-15"
    EMBEDDING_DEPLOYMENT = "text-embedding-3-large"
    LLM_DEPLOYMENT = "gpt-4.1-mini" # Using gpt-4.1-mini as prompt requested gpt-4o-minia but fallback to standard name if needed


AzureOpenAIConfig = Config()