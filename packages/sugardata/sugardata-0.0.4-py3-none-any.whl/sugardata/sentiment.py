import json
import uuid
import random
import pandas as pd
from itertools import product
from langchain.prompts import PromptTemplate
from langchain import FewShotPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from datasets import Dataset
from deep_translator import GoogleTranslator
from typing import Any, Dict, List, Literal, Optional
from .models.llms.factory import create_langchain_llm
from .tasks.sentiment.schemas import (
    OntologyConcepts, WritingStyles, GeneratedText
)
from .tasks.sentiment.prompts import (
    CONCEPT_EXAMPLES, CONCEPT_EXAMPLE_TEMPLATE, CONCEPT_PREFIX, CONCEPT_SUFFIX, STYLE_EXAMPLES, 
    STYLE_PREFIX, STYLE_SUFFIX, STYLE_EXAMPLE_TEMPLATE, GENERATE_PROMPT
)


class SentimentGenerator:
    """
    Generates synthetic sentiment analysis data based on the input concept and the number of samples.
    """

    _SENTENCE_LENGTH_OPTIONS = ["1 short sentence", "1 sentence", "2 sentences", "Short Paragraph", "Long Paragraph"]
    _SENTENCE_LENGTH_WEIGHTS = [0.45, 0.25, 0.15, 0.1, 0.05]
    
    def __init__(
            self,
            provider: str,
            model: str,
            temperature: float=0.9,
            model_params: Optional[Dict[str, Any]]=None,
            batch_size: int=16,
            language: str="en",
            n_label: int= 2,
            output_type: Literal["pandas", "json", "dictionary", "hg"] = "pandas"
        ):
        """

        Args:
            provider (str): The llm provider to use. Options: 'openai', 'google', 'together', 'groq', 'ollama'.
            model (str): The model name to use.
            temperature (float, optional): The temperature of the model. Defaults to 0.9.
            model_params (Dict[str, Any], optional): Additional parameters for the LLM model. Defaults to None.
            batch_size (int, optional): The batch size for generating the data. Defaults to 16.
            language (str, optional): The language to use. Defaults to "en".
            n_label (int, optional): The number of labels to use. Defaults to 2. Options: 2, 3, 5.
            output_type (str, optional): The output type. Defaults to "pandas". Options: 'pandas', 'json', 'dictionary', 'hg'.
        """
        
        if not isinstance(n_label, int):
            raise ValueError("Number of labels must be an integer")
        
        if not isinstance(batch_size, int):
            raise ValueError("Batch size must be an integer")
        
        if not isinstance(temperature, float):
            raise ValueError("Temperature must be a float")

        self._llm = create_langchain_llm(provider=provider, model=model, temperature=temperature, **(model_params or {}))
        self._labels = self._set_labels(n_label)
        self._language = language
        self._batch_size = batch_size
        self._output_type = output_type
        self.outputs = {}

        self._set_prompts()

    def generate(self, concept: str, n: int) -> Any:
        """
        Generates synthetic sentiment analysis data based on the input concept and the number of samples.

        Args:
            concept (str): The concept to use for generating the data.
            n (int): The number of samples to generate.

        Returns:
            Any: The generated data based on the input concept and the number of samples and the output type.
        """
        if not isinstance(n, int) or n < 1:
            raise ValueError("Number of samples must be an integer greater than 0")
        
        if not isinstance(concept, str):
            raise ValueError("Concept must be a string")
        
        run_id = str(uuid.uuid4())
        
        concept_translated = self._translate_concept(concept)

        sub_concepts = self._extend_concept(concept_translated)
        styles = self._find_styles(concept_translated)
        variations = [{**d1, **d2} for d1, d2 in product(sub_concepts, styles)]

        batches = self._create_batches(concept_translated, variations, n)

        data = self._generate_sentences(batches)

        data = self._add_additional_info(data, batches)
        data = self._translate_data(data)
        self.outputs[run_id] = data
        result = self._convert_output()
        return result
    
    def _set_labels(self, n_label: int) -> List[str]:
        """
        Sets the labels based on the number of labels.
        """
        label_map = {
            2: ["positive", "negative"],
            3: ["positive", "neutral", "negative"],
            5: ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
        }
        if n_label not in label_map:
            raise ValueError("Invalid number of labels. Please choose between 2, 3, or 5 labels")
        return label_map[n_label]

    def _set_prompts(self) -> None:
        ## NOTE TO SELF: For the other languages than English, we can translate the prompts here, 
        ## if it is understood that the default behavior doesn't work and prompts in 
        ## original language performs better. In that case, this function will handle the
        ## translation of the prompts.
        self._prompts = {
            "concept_examples": CONCEPT_EXAMPLES,
            "concept_example_template": CONCEPT_EXAMPLE_TEMPLATE,
            "concept_prefix": CONCEPT_PREFIX,
            "concept_suffix": CONCEPT_SUFFIX,
            "style_examples": STYLE_EXAMPLES,
            "style_prefix": STYLE_PREFIX,
            "style_suffix": STYLE_SUFFIX,
            "style_example_template": STYLE_EXAMPLE_TEMPLATE,
            "generate_prompt": GENERATE_PROMPT,
        }
        return
    
    def _translate_concept(self, concept: str) -> str:
        """
        Translates the concept to English if the language is not English.
        """
        if self._language == "en":
            return concept
        try:
            return GoogleTranslator(source=self._language, target="en").translate(concept)
        except Exception as e:
            print("Error in translating concept: ", e)
            raise e
    
    def _extend_concept(self, concept: str) -> List[Dict[str, str]]:
        """
        Extends the concept by finding sub or related concepts.
        """
        try:
            prompt = FewShotPromptTemplate(
                examples=self._prompts["concept_examples"],
                example_prompt=PromptTemplate(
                    input_variables=["concept", "generated_concept", "explanation"], 
                    template=self._prompts["concept_example_template"]
                ),
                prefix=self._prompts["concept_prefix"],
                suffix=self._prompts["concept_suffix"],
                input_variables=["concept"],
                example_separator="\n\n"
            )

            parser = PydanticOutputParser(pydantic_object=OntologyConcepts)
            format_instructions = parser.get_format_instructions()
            chain = prompt | self._llm | parser

            response = chain.invoke({
                "concept":concept,
                "format_instructions": format_instructions
                }
            )

            return [concept.model_dump() for concept in response.concepts]
        except Exception as e:
            print("Error in extending concept: ", e)
            raise e
    
    def _find_styles(self, concept: str) -> List[Dict[str, str]]:
        """
        Finds the writing styles based on the concept.
        """
        try:
            prompt = FewShotPromptTemplate(
                examples=self._prompts["style_examples"],
                example_prompt=PromptTemplate(
                    input_variables=["concept", "medium", "persona", "writing_style"],
                    template=self._prompts["style_example_template"],
                ),
                prefix=self._prompts["style_prefix"],
                suffix=self._prompts["style_suffix"],
                input_variables=["concept"],
                example_separator="\n\n"
            )
            
            parser = PydanticOutputParser(pydantic_object=WritingStyles)
            format_instructions = parser.get_format_instructions()
            chain = prompt | self._llm | parser

            response = chain.invoke({
                "concept":concept,
                "format_instructions": format_instructions
                }
            )

            return [style.model_dump() for style in response.styles]
        except Exception as e:
            print("Error in finding styles: ", e)
            raise e
        
    def _create_batches(self, concept: str, variations: List[Dict[str, str]], n: int) -> List[Dict[str, str]]:
        """
        Creates batches based on the concept and the variations.
        """
        return [
            {
                **random.choice(variations),
                "concept": concept,
                "id": i,
                "sentiment_label": random.choice(self._labels),
                "sentence_length": random.choices(self._SENTENCE_LENGTH_OPTIONS, weights=self._SENTENCE_LENGTH_WEIGHTS, k=1)[0],
            }
            for i in range(min(n, len(variations)))
        ]
    
    def _generate_sentences(self, batches: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Generates sentences based on the batches.
        """
        data = []

        prompt = PromptTemplate(
            input_variables=[
                "concept", "generated_concept", "explanation", "medium", "persona", 
                "writing_style", "sentiment_label", "sentence_length", "id", "format_instructions"
            ],
            template=self._prompts["generate_prompt"]
        )

        parser = PydanticOutputParser(pydantic_object=GeneratedText)
        format_instructions = parser.get_format_instructions()

        chain = prompt | self._llm | parser
        for i in range(0, len(batches), self._batch_size):
            batch = batches[i:i+self._batch_size]
            for item in batch:
                item["format_instructions"] = format_instructions
            response = chain.batch(batch)
            response = [resp.model_dump() for resp in response]

            for resp in response:
                resp["concept"] = batch[0]["concept"]

            data.extend(response)
        return data

    def _add_additional_info(self, data: List[Dict[str, str]], batches: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Adds additional information to the data based on the batches.
        """
        batch_map = {batch["id"]: batch for batch in batches}
        for item in data:
            batch = batch_map.get(int(item["id"]))
            if batch:
                item["concept"] = batch["concept"]
                item["label"] = batch["sentiment_label"]
        return data

    def _translate_data(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        If the language is not English, translates the data to the target language.
        """
        if self._language == "en":
            return data
        
        try:
            translated_data = []
            for item in data:
                translated_item = {k: GoogleTranslator(source="en", target=self._language).translate(v) for k, v in item.items()}
                translated_data.append(translated_item)
            return translated_data
        except Exception as e:
            print("Error in translating data: ", e)
            raise e

    def _convert_output(self) -> Any:
        """
        Prepares the output based on the output type.
        """
        if not self.outputs:
            return pd.DataFrame() if self._output_type == "pandas" else {}

        if self._output_type == "pandas":
            return pd.concat([pd.DataFrame(data).assign(run_id=run_id) for run_id, data in self.outputs.items()], ignore_index=True)
        if self._output_type == "json":
            return json.dumps(self.outputs, indent=4)
        if self._output_type == "dictionary":
            return self.outputs
        if self._output_type == "hg":
            return Dataset.from_pandas(pd.concat([pd.DataFrame(data).assign(run_id=run_id) for run_id, data in self.outputs.items()], ignore_index=True))
        raise ValueError("Invalid output type. Please choose between 'pandas', 'json', 'dictionary', or 'hg'")
            
    def get_raw_outputs(self) -> List[Dict[str, str]]:
        """
        Getter for the raw outputs.
        """
        return self.output