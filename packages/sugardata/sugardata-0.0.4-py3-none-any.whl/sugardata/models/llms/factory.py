from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_together import ChatTogether
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from typing import Literal, Any


def create_langchain_llm(
        provider: Literal["openai", "google", "together", "groq", "ollama"],
        model: str, 
        temperature: float=0.95, 
        **kwargs
        ) -> Any:
    """
    Creates a Langchain LLM instance based on the provider.

    Args:
        provider (str): The provider of the LLM model. Options: 'openai', 'google', 'together', 'groq', 'ollama'.
        model (str): The model name. For example: gpt-4o-mini.
        temperature (float, optional): The temperature of the model. Defaults to 0.95.
        **kwargs: Additional parameters for the LLM model.
    Raises:
        ValueError: If the provider is not valid.
        e: If the LLM model cannot be created.

    Returns:
        Any: The Langchain LLM instance.
    """
    try:
        if provider == "openai":
            return ChatOpenAI(model=model, temperature=temperature, **kwargs)
        elif provider == "google":
            return ChatGoogleGenerativeAI(model=model, temperature=temperature, **kwargs)
        elif provider == "together":
            return ChatTogether(model=model, temperature=temperature, **kwargs)
        elif provider == "groq":
            return ChatGroq(model=model, temperature=temperature, **kwargs)
        elif provider == "ollama":
            return ChatOllama(model=model, temperature=temperature, **kwargs)
        else:
            raise ValueError(f"Invalid provider: {provider}. Available providers: 'openai', 'google', 'together', 'groq', 'ollama'.")
    except Exception as e:
        print("I could not create the LLM model. Please check the provider and model parameters.")
        raise e