import uuid
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import Any, Dict, Optional, List, Literal
from .schemas import Aspect
from .prompts import ASPECT_GENERATION_PROMPT, ABSA_GENERATE_PROMPT
from .service import SentimentGenerator
from ...utility.draw import DrawUtility


class ABSAGenerator(SentimentGenerator):

    def generate(
            self, 
            concept: str,
            n_samples: int = 100, 
            output_format: Literal["pandas", "json", "dictionary", "hg"]="pandas",
            aspects: Optional[List[str]]=None,
            n_generated_aspects: int=5
            ) -> Any:
        
        run_id = str(uuid.uuid4())[-6:]

        concept_en = self._translate_concept(concept)
        
        if not aspects:
            aspects = self._generate_aspects(concept_en, n_generated_aspects)

        batches = self._create_batches(concept_en, aspects, n_samples)

        sentences = self._generate_sentences(batches)
        
        sentences = self._add_additional_info(sentences, batches, run_id)
        
        sentences = self._translate_to_original(sentences)
        
        output = self._create_output(sentences, output_format)
        
        return output

    def _set_prompts(self) -> None:
        self._prompts = {
            "aspect_generation_prompt": ASPECT_GENERATION_PROMPT,
            "generate_prompt": ABSA_GENERATE_PROMPT,
        }
        return

    def _generate_aspects(self, concept: str, n_generated_aspects: int) -> List[str]:
        prompt = PromptTemplate.from_template(self._prompts["aspect_generation_prompt"])
        parser = PydanticOutputParser(pydantic_object=Aspect)
        format_instructions = parser.get_format_instructions()
        chain = prompt | self.llm | parser

        response = chain.invoke({
            "concept":concept,
            "num_aspects":n_generated_aspects,
            "format_instructions":format_instructions
            }
        )

        return response.model_dump()["aspects"]
    
    def _create_batches(self, concept: str, aspects: List[str], n_samples: int) -> List[Dict[str, str]]:
        data = []
        for i in range(n_samples):
            aspect_string, labels = DrawUtility.weighted_random_sample(aspects, self.labels)
            data.append({
                "id": i,
                "concept": concept,
                "aspects": aspect_string,
                "sentiment_label": labels,
                **DrawUtility.draw_style()
            })

        return data
    
    def _add_additional_info(self, data: List[Dict[str, str]], batches: List[Dict[str, str]], run_id) -> List[Dict[str, str]]:
        batch_map = {batch["id"]: batch for batch in batches}
        for item in data:
            batch = batch_map.get(int(item["id"]))
            if batch:
                item["concept"] = batch["concept"]
                item["label"] = batch["sentiment_label"]
                item["aspects"] = batch["aspects"]
                item["writing_style"] = batch["writing_style"]
                item["medium"] = batch["medium"]
                item["persona"] = batch["persona"]
                item["intention"] = batch["intention"]
                item["tone"] = batch["tone"]
                item["audience"] = batch["audience"]
                item["context"] = batch["context"]
                item["language_register"] = batch["language_register"]
                item["run_id"] = run_id

        return data
    