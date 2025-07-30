from typing import Dict, Any, List, Optional, Literal, Any
from .tasks.sentiment.service import SentimentGenerator
from .tasks.sentiment.service_absa import ABSAGenerator


def generate_sentiments(
        concept: str,
        n_samples: int=100,
        model_provider: str="openai",
        model_name: str="gpt-4o-mini",
        model_kwargs: Optional[Dict[str, Any]]=None,
        batch_size: int=16,
        language: str="en",
        n_labels: int=2,
        output_format: Literal["pandas", "json", "dictionary", "hg"]="pandas"
        ) -> Any:
        """
        Generate sentiments for a given concept using the SentimentGenerator class.
        This function serves as a wrapper around the SentimentGenerator class to provide a simplified interface for generating sentiments.
        It allows users to specify the concept, number of samples, model provider, model name, model kwargs, batch size, language, and number of labels.
        The function creates an instance of the SentimentGenerator class and calls its generate method to generate sentiments.
        The generated sentiments are returned as a list of dictionaries, where each dictionary contains the generated sentiment and its corresponding label.
        The function also provides default values for the parameters, making it easy to use without specifying all arguments.
        The function is designed to be flexible and extensible, allowing users to customize the sentiment generation process according to their needs.

        Example:

        >>> import sugardata as su

        >>> # Generate sentiments for the concept "Nike"
        >>> sentiments = su.generate_sentiments(
        >>>     concept="Nike",
        >>>     n_samples=10,
        >>>     model_provider="openai",
        >>>     model_name="gpt-4o-mini",
        >>>     model_kwargs=None,
        >>>     batch_size=16,
        >>>     language="en",
        >>>     n_labels=2
        >>> )

        Args:
        concept (str): The concept for which to generate sentiments. For example, "Nike".

        n_samples (int, optional): The number of samples to generate. Defaults to 100.
        model_provider (str, optional): The model provider to use for sentiment generation. Defaults to "openai". Options are "openai", "google", "together", "groq", "ollama". The model provider determines the underlying model used for sentiment generation.
        
        model_name (str, optional): The name of the model to use for sentiment generation. Defaults to "gpt-4o-mini". The model name specifies the specific model variant to be used.
        
        model_kwargs (Optional[Dict[str, Any]], optional): Additional keyword arguments to pass to the model. Defaults to None. This allows users to customize the behavior of the model by providing additional parameters.
        For example, you can specify the temperature, max tokens, etc.
        
        batch_size (int, optional): The batch size for generating sentiments. Defaults to 16. The batch size determines how many samples are processed at once, which can affect performance and memory usage.

        language (str, optional): The language in which to generate sentiments. Defaults to "en". The language parameter specifies the language for sentiment generation, allowing for multilingual support.

        n_labels (int, optional): The number of sentiment labels to generate. Defaults to 2. The n_labels parameter determines how many different sentiment labels will be generated for the given concept.
        2: ["positive", "negative"],
        3: ["positive", "neutral", "negative"],
        5: ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]

        output_format (Literal["pandas", "json", "dictionary", "hg"], optional): The format of the output. Defaults to "pandas". The output format determines how the generated sentiments are returned. Options are:
        - "pandas": Returns a pandas DataFrame containing the generated sentiments.
        - "json": Returns a JSON object containing the generated sentiments.
        - "dictionary": Returns a list of dictionaries, where each dictionary contains the generated sentiment and its corresponding label.
        - "hg": Returns a Hugging Face dataset containing the generated sentiments.
        The output format can be specified to suit the user's needs and preferences.

        Returns:
                Any: The generated sentiments in the specified output format based on the output_format parameter.
        """
        if not isinstance(concept, str):
            raise ValueError("Concept must be a string.")
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("Number of samples must be a positive integer.")
        if not isinstance(model_provider, str):
            raise ValueError("Model provider must be a string.")
        if not isinstance(model_name, str):
            raise ValueError("Model name must be a string.")
        if model_kwargs is not None and not isinstance(model_kwargs, dict):
            raise ValueError("Model kwargs must be a dictionary.")
        if not isinstance(batch_size, int) or batch_size <= 0:  
            raise ValueError("Batch size must be a positive integer.")
        if not isinstance(language, str):
            raise ValueError("Language must be a string.")
        if not isinstance(n_labels, int) or n_labels <= 0:
            raise ValueError("Number of labels must be a positive integer.")
        if not isinstance(output_format, str):
            raise ValueError("Output format must be a string.")
        if output_format not in ["pandas", "json", "dictionary", "hg"]:
            raise ValueError("Output format must be one of ['pandas', 'json', 'dictionary', 'hg'].")

        service = SentimentGenerator(
                        model_provider=model_provider, 
                        model_name=model_name, 
                        model_kwargs=model_kwargs, 
                        batch_size=batch_size, 
                        language=language, 
                        n_labels=n_labels
                        )
    
        return service.generate(concept=concept, n_samples=n_samples, output_format=output_format)


def generate_aspect_sentiments(
        concept: str,
        n_samples: int=100,
        model_provider: str="openai",
        model_name: str="gpt-4o-mini",
        model_kwargs: Optional[Dict[str, Any]]=None,
        batch_size: int=16,
        language: str="en",
        n_labels: int=2,
        output_format: Literal["pandas", "json", "dictionary", "hg"]="pandas",
        aspects: Optional[List[str]]=None,
        n_generated_aspects: int=5,
        ) -> Any:
        """
        Generate aspect sentiments for a given concept using the ABSAGenerator class.
        This function serves as a wrapper around the ABSAGenerator class to provide a simplified interface for generating aspect sentiments.
        It allows users to specify the concept, number of samples, model provider, model name, model kwargs, batch size, language, number of labels, output format, aspects, and number of generated aspects.
        The function creates an instance of the ABSAGenerator class and calls its generate method to generate aspect sentiments.
        The generated aspect sentiments are returned as a list of dictionaries, where each dictionary contains the generated aspect sentiment and its corresponding label.
        The function also provides default values for the parameters, making it easy to use without specifying all arguments.
        The function is designed to be flexible and extensible, allowing users to customize the aspect sentiment generation process according to their needs.
        
        Example:
        >>> import sugardata as su
        >>> # Generate aspect sentiments for the concept "Nike"
        >>> aspect_sentiments = su.generate_aspect_sentiments(
        >>>     concept="Nike",
        >>>     n_samples=10,
        >>>     model_provider="openai",
        >>>     model_name="gpt-4o-mini",
        >>>     model_kwargs=None,
        >>>     batch_size=16,
        >>>     language="en",
        >>>     n_labels=2,
        >>>     output_format="pandas",
        >>>     aspects=["quality", "price", "design"],
        >>> )

        Args:
        concept (str): The concept for which to generate sentiments. For example, "Nike".

        n_samples (int, optional): The number of samples to generate. Defaults to 100.
        model_provider (str, optional): The model provider to use for sentiment generation. Defaults to "openai". Options are "openai", "google", "together", "groq", "ollama". The model provider determines the underlying model used for sentiment generation.
        
        model_name (str, optional): The name of the model to use for sentiment generation. Defaults to "gpt-4o-mini". The model name specifies the specific model variant to be used.
        
        model_kwargs (Optional[Dict[str, Any]], optional): Additional keyword arguments to pass to the model. Defaults to None. This allows users to customize the behavior of the model by providing additional parameters.
        For example, you can specify the temperature, max tokens, etc.
        
        batch_size (int, optional): The batch size for generating sentiments. Defaults to 16. The batch size determines how many samples are processed at once, which can affect performance and memory usage.

        language (str, optional): The language in which to generate sentiments. Defaults to "en". The language parameter specifies the language for sentiment generation, allowing for multilingual support.

        n_labels (int, optional): The number of sentiment labels to generate. Defaults to 2. The n_labels parameter determines how many different sentiment labels will be generated for the given concept.
        2: ["positive", "negative"],
        3: ["positive", "neutral", "negative"],
        5: ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]

        output_format (Literal["pandas", "json", "dictionary", "hg"], optional): The format of the output. Defaults to "pandas". The output format determines how the generated sentiments are returned. Options are:
        - "pandas": Returns a pandas DataFrame containing the generated sentiments.
        - "json": Returns a JSON object containing the generated sentiments.
        - "dictionary": Returns a list of dictionaries, where each dictionary contains the generated sentiment and its corresponding label.
        - "hg": Returns a Hugging Face dataset containing the generated sentiments.
        The output format can be specified to suit the user's needs and preferences.
        
        aspects (Optional[List[str]], optional): The aspects to consider for sentiment generation. Defaults to None. If not provided, the function will generate aspects based on the concept.
        
        n_generated_aspects (int, optional): The number of aspects to generate. Defaults to 5. This parameter determines how many different aspects will be generated for the given concept.

        Returns:
                Any: The generated aspect sentiments in the specified output format based on the output_format parameter.
        """
        if not isinstance(concept, str):
            raise ValueError("Concept must be a string.")
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise ValueError("Number of samples must be a positive integer.")
        if not isinstance(model_provider, str):
            raise ValueError("Model provider must be a string.")
        if not isinstance(model_name, str):
            raise ValueError("Model name must be a string.")
        if model_kwargs is not None and not isinstance(model_kwargs, dict):
            raise ValueError("Model kwargs must be a dictionary.")
        if not isinstance(batch_size, int) or batch_size <= 0:  
            raise ValueError("Batch size must be a positive integer.")
        if not isinstance(language, str):
            raise ValueError("Language must be a string.")
        if not isinstance(n_labels, int) or n_labels <= 0:
            raise ValueError("Number of labels must be a positive integer.")
        if not isinstance(output_format, str):
            raise ValueError("Output format must be a string.")
        if output_format not in ["pandas", "json", "dictionary", "hg"]:
            raise ValueError("Output format must be one of ['pandas', 'json', 'dictionary', 'hg'].")
        if aspects is not None and not isinstance(aspects, list):
            raise ValueError("Aspects must be a list.")
        if aspects:
            print("Warning! 'n_generated_aspects' will be ignored if 'aspects' is provided.")


        service = ABSAGenerator(
                        model_provider=model_provider, 
                        model_name=model_name, 
                        model_kwargs=model_kwargs, 
                        batch_size=batch_size, 
                        language=language, 
                        n_labels=n_labels
                        )
        
        return service.generate(concept=concept, aspects=aspects, n_samples=n_samples, 
                                n_generated_aspects=n_generated_aspects, output_format=output_format)



