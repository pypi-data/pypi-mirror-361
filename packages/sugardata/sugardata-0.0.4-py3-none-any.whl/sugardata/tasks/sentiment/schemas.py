import pandas as pd
from pydantic import BaseModel, Field
from datasets import Dataset
from typing import List, Dict, Union, Optional


class SentimentConfig(BaseModel):
    language: str = Field(description="Language for the sentiment generation, e.g., 'en' for English")
    dimension_prompt: Optional[str] = Field(None, description="Prompt template for generating dimensions related to the concept")
    aspect_prompt: Optional[str] = Field(None, description="Prompt template for generating aspects related to the concept and dimensions")
    sentence_prompt: str = Field(description="Prompt template for generating sentences based on the concept, dimensions, and aspects")
    structure_prompt: Optional[str] = Field(None, description="Prompt template for generating the structure of the sentiment data")
    llm: object = Field(description="LLM object used for generating text, e.g., OpenAI's GPT model")
    n_aspect: Optional[int] = Field(default=1, description="Number of aspects to generate")
    n_sentence: Optional[int] = Field(default=100, description="Number of sentences to generate in total")
    batch_size: int = Field(default=10, description="Number of sentences to generate in each batch")
    label_options: List[str] = Field(default_factory=lambda: ["positive", "negative"], description="List of sentiment labels to choose from")
    export_type: str = Field(default="default", description="Output format of the generated data, e.g., 'dataframe' or 'dataset'")
    aspect_based_generation: bool = Field(default=False, description="Whether to generate data based on aspects. If False, all sentiments for all aspects are same.")
    verbose: bool = Field(default=False, description="Whether to print verbose output during processing")


class DimensionDerivative(BaseModel):
    single_derivative: str = Field(
        title="Single Derivative Dimension",
        description="A single generated dimension related to the concept"
    )


class Dimensions(BaseModel):
    dimensions: List[DimensionDerivative] = Field(
        title="Dimensions",
        description="Multiple dimensions derived from the concept, each containing a single derivative dimension"
    )


class AspectDerivative(BaseModel):
    single_derivative: str = Field(
        title="Single Derivative Aspect",
        description="A single generated aspect related to the concept and dimension"
    )


class Aspects(BaseModel):
    index: int = Field(title="Index", description="Index of the given request")
    aspects: List[AspectDerivative] = Field(
        title="Aspects",
        description="Multiple aspects derived from the concept and dimension, each containing a single derivative aspect"
    )


class Text(BaseModel):
    index: int = Field(title="Index", description="Index of the given request")
    generated_text: str = Field(description="The generated text")


class SentimentResponse(BaseModel):
    concept: str = Field(title="Concept", description="The concept for which the sentiment is generated")
    aspect: str = Field(title="Aspect", description="The aspect related to the concept")
    writing_style: str = Field(
        title="Writing Style",
        description="The writing style used in the generated text, e.g., 'formal', 'informal', 'academic', etc."
    )
    medium: str = Field(
        title="Medium",
        description="The medium for which the text is generated, e.g., 'blog', 'social media', 'email', etc."
    )
    persona: str = Field(
        title="Persona",
        description="The persona of the writer, e.g., 'expert', 'enthusiast', 'casual', etc."
    )
    intention: str = Field(
        title="Intention",
        description="The intention behind the text, e.g., 'inform', 'persuade', 'entertain', etc."
    )
    sentence_length: str = Field(
        title="Sentence Length",
        description="The length of the sentences used in the text, e.g., 'short', 'medium', 'long', etc."
    )
    generated_text: str = Field(
        title="Generated Text",
        description="The actual generated text based on the concept, aspect, and other parameters"
    )
    dimension: str = Field(
        title="Dimension",
        description="The dimension related to the concept, aspect, and generated text"
    )
    sentiment: str = Field(
        title="Sentiment",
        description="The sentiment expressed in the generated text, e.g., 'positive', 'negative', 'neutral', etc."
    )


class SentimentStructure(BaseModel):
    concept: str = Field(title="Concept", description="The concept for which the sentiment is generated")
    aspects: List[str] = Field(
        title="Aspects",
        description="A list of aspects related to the concept, each aspect can have multiple derivatives"
    )
    writing_style: Optional[str] = Field(
        None,
        title="Writing Style",
        description="The writing style used in the generated text, e.g., 'formal', 'informal', 'academic', etc."
    )
    medium: Optional[str] = Field(
        None,
        title="Medium",
        description="The medium for which the text is generated, e.g., 'blog', 'social media', 'email', etc."
    )
    persona: Optional[str] = Field(
        None,
        title="Persona",
        description="The persona of the writer, e.g., 'expert', 'enthusiast', 'casual', etc."
    )
    intention: Optional[str] = Field(
        None,
        title="Intention",
        description="The intention behind the text, e.g., 'inform', 'persuade', 'entertain', etc."
    )
    sentence_length: Optional[str] = Field(
        None,
        title="Sentence Length",
        description="The length of the sentences used in the text, e.g., 'short', 'medium', 'long', etc."
    )
    given_text: str = Field(
        title="Given Text",
        description="The text provided as input for structure extraction"
    )

SentimentOutput = Union[
    List[Dict],
    pd.DataFrame,
    Dataset,
    List[SentimentResponse]
]

