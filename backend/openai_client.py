from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """
    Return one shared OpenAI client for the backend process.
    """

    return OpenAI()
