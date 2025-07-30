from langchain_openai import ChatOpenAI


def create_llm_object(vendor: str, model: str, **kwargs) -> object:
    """
    Supported vendors:
    - openai
    - ollama [manual installation required]
    - gemini [manual installation required]
    - groq [manual installation required]
    - together [manual installation required]
    """
    if vendor is None:
        raise ValueError("Vendor must be specified. Supported vendors are: openai, ollama, gemini, groq.")
    if model is None:
        raise ValueError("Model must be specified.")
    
    if vendor == "openai":
        return ChatOpenAI(model=model, **kwargs)
    elif vendor == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("Please install `langchain-ollama` package to use this feature.")
        return ChatOllama(model=model, **kwargs)
    elif vendor == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError("Please install `langchain-google-genai` package to use this feature.")
        return ChatGoogleGenerativeAI(model=model, **kwargs)
    elif vendor == "groq":
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise ImportError("Please install `langchain-groq` package to use this feature.")
        return ChatGroq(model=model, **kwargs)
    elif vendor == "together":
        try:
            from langchain_together import ChatTogether
        except ImportError:
            raise ImportError("Please install `langchain-together` package to use this feature.")
        return ChatTogether(model=model, **kwargs)
    else:
        raise ValueError(f"Unsupported vendor: {vendor}. Supported vendors are: openai, ollama, gemini, groq.")
