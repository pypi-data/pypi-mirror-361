import asyncio
import pandas as pd
from datasets import Dataset
from typing import Optional, Dict, List, Union
from .schemas import SentimentConfig, SentimentOutput
from .generate_sync import SentimentGenerator
from .generate_async import SentimentGeneratorAsync
from .augment_sync import SentimentAugmenter
from .augment_async import SentimentAugmenterAsync
from .prompts import get_dimension_prompt, get_aspect_prompt, get_sentence_prompt, get_structure_prompt, get_augment_sentence_prompt
from ...components.factory import create_llm_object
from ...utility.translate import TranslationUtility
from ...utility.config import DEFAULT_VENDORS


def augment_sentiment_data(
        examples: List[str],
        language: Optional[str]=None,
        vendor: str="openai",
        model: str="gpt-4o-mini",
        model_params: Optional[Dict]=None,
        batch_size: int=10,
        label_options: Optional[List]=["positive", "negative"],
        export_type: str="default",
        aspect_based_generation: bool=False,
        verbose: bool=False,
        **kwargs
) -> SentimentOutput:
    
    if not language:
        language = TranslationUtility.detect_language(examples[0])

    if not model_params:
        model_params = {"temperature": 0.95}
    if "temperature" not in model_params:
        model_params["temperature"] = 0.95
    
    llm = create_llm_object(vendor=vendor, model=model, **model_params)

    config = SentimentConfig(
        language=language,
        sentence_prompt=get_augment_sentence_prompt(language=language),
        structure_prompt=get_structure_prompt(language=language),
        llm=llm,
        batch_size=batch_size,
        label_options=label_options,
        export_type=export_type,
        aspect_based_generation=aspect_based_generation,
        verbose=verbose
    )
    
    return SentimentAugmenter(config=config).generate(examples=examples)


async def augment_sentiment_data_async(
        examples: List[str],
        language: Optional[str]=None,
        vendor: str="openai",
        model: str="gpt-4o-mini",
        model_params: Optional[Dict]=None,
        batch_size: int=10,
        label_options: Optional[List]=["positive", "negative"],
        export_type: str="default",
        aspect_based_generation: bool=False,
        verbose: bool=False,
        **kwargs
) -> SentimentOutput:
    
    if not language:
        language = await TranslationUtility.detect_language_async(examples[0])

    if not model_params:
        model_params = {"temperature": 0.95}
    if "temperature" not in model_params:
        model_params["temperature"] = 0.95

    llm = create_llm_object(vendor=vendor, model=model, **model_params)

    config = SentimentConfig(
        language=language,
        sentence_prompt=get_augment_sentence_prompt(language=language),
        structure_prompt=get_structure_prompt(language=language),
        llm=llm,
        batch_size=batch_size,
        label_options=label_options,
        export_type=export_type,
        aspect_based_generation=aspect_based_generation,
        verbose=verbose
    )

    return await SentimentAugmenterAsync(config=config).generate(examples=examples)
    

async def augment_sentiment_multi_vendor_async(
        examples: List[str],
        language: Optional[str]=None,
        vendors: Optional[Dict[str, str]]=None,
        batch_size: int=10,
        label_options: Optional[List]=["positive", "negative"],
        export_type: str="default",
        aspect_based_generation: bool=False,
        verbose: bool=False,
        **kwargs
) -> SentimentOutput:
        if not vendors:
            vendors = DEFAULT_VENDORS
        
        tasks = [
            asyncio.create_task(
                augment_sentiment_data_async(
                    examples=examples,
                    language=language,
                    vendor=vendor,
                    model=model,
                    batch_size=batch_size,
                    label_options=label_options,
                    export_type=export_type,
                    aspect_based_generation=aspect_based_generation,
                    verbose=verbose,
                    **kwargs
                )
            )
            for vendor, model in vendors.items()
        ]

        results_list = await asyncio.gather(*tasks)

        return dict(zip(vendors.keys(), results_list))


def generate_sentiment_data(
        concept: str=None,
        language: Optional[str]=None,
        vendor: str="openai",
        model: str="gpt-4o-mini",
        model_params: Optional[Dict]=None,
        n_aspect: int=1,
        n_sentence: int=100,
        batch_size: int=10,
        label_options: Optional[List]=["positive", "negative"],
        export_type: str="default",
        dimensions: Optional[List[str]]=None,
        aspects: Optional[List[str]]=None,
        verbose: bool=False,
        **kwargs
    ) -> SentimentOutput:

    if not language:
        language = TranslationUtility.detect_language(concept)

    if not model_params:
        model_params = {"temperature": 0.95}
    if "temperature" not in model_params:
        model_params["temperature"] = 0.95
    
    llm = create_llm_object(vendor=vendor, model=model, **model_params)

    config = SentimentConfig(
        language=language,
        dimension_prompt=get_dimension_prompt(language=language),
        aspect_prompt=get_aspect_prompt(language=language),
        sentence_prompt=get_sentence_prompt(language=language),
        llm=llm,
        n_aspect=n_aspect,
        n_sentence=n_sentence,
        batch_size=batch_size,
        label_options=label_options,
        export_type=export_type,
        verbose=verbose
    )

    return SentimentGenerator(config=config).generate(concept=concept, dimensions=dimensions, aspects=aspects)


async def generate_sentiment_data_async(
        concept: str=None,
        language: Optional[str]=None,
        vendor: str="openai",
        model: str="gpt-4o-mini",
        model_params: Optional[Dict]=None,
        n_aspect: int=1,
        n_sentence: int=100,
        batch_size: int=10,
        label_options: Optional[List]=["positive", "negative"],
        export_type: str="default",
        dimensions: Optional[List[str]]=None,
        aspects: Optional[List[str]]=None,
        verbose: bool=False,
        **kwargs
) -> SentimentOutput:

    if not language:
        language = TranslationUtility.detect_language(concept)

    if not model_params:
        model_params = {"temperature": 0.95}
    if "temperature" not in model_params:
        model_params["temperature"] = 0.95

    llm = create_llm_object(vendor=vendor, model=model, **model_params)

    config = SentimentConfig(
        language=language,
        dimension_prompt=get_dimension_prompt(language=language),
        aspect_prompt=get_aspect_prompt(language=language),
        sentence_prompt=get_sentence_prompt(language=language),
        llm=llm,
        n_aspect=n_aspect,
        n_sentence=n_sentence,
        batch_size=batch_size,
        label_options=label_options,
        export_type=export_type,
        verbose=verbose
    )

    return await SentimentGeneratorAsync(config=config).generate(concept=concept, dimensions=dimensions, aspects=aspects)

async def generate_sentiment_multi_vendor_async(
        concept: str=None,
        language: Optional[str]=None,
        vendors: Dict[str, str]=None,
        model_params: Optional[Dict]=None,
        n_aspect: int=1,
        n_sentence: int=100,
        batch_size: int=10,
        label_options: Optional[List]=["positive", "negative"],
        export_type: str="default",
        dimensions: Optional[List[str]]=None,
        aspects: Optional[List[str]]=None,
        verbose: bool=False,
        **kwargs
) -> Dict[str, SentimentOutput]:

    if not vendors:
        vendors = DEFAULT_VENDORS

    tasks = [
        asyncio.create_task(
            generate_sentiment_data_async(
                concept=concept,
                language=language,
                vendor=vendor,
                model=model,
                model_params=model_params,
                n_aspect=n_aspect,
                n_sentence=n_sentence,
                batch_size=batch_size,
                label_options=label_options,
                export_type=export_type,
                dimensions=dimensions,
                aspects=aspects,
                verbose=verbose,
                **kwargs
            )
        )
        for vendor, model in vendors.items()
    ]

    results_list = await asyncio.gather(*tasks)

    return dict(zip(vendors.keys(), results_list))

