import random
from typing import Dict, Any, List, Optional
from .schemas import Dimensions, Aspects, Text, SentimentResponse, SentimentConfig, SentimentOutput
from ..base import NlpTask
from ...components.standard_chain_builder import StandardChainBuilder
from ...utility.draw import DrawUtility


class SentimentGenerator(NlpTask):

    def __init__(self, config: SentimentConfig):
        self.config = config

    def generate(
            self, 
            concept: str, 
            dimensions: Optional[List[str]]=None,
            aspects: Optional[List[str]]=None
    ) -> SentimentOutput:
        dimensions = dimensions or self._generate_dimensions(concept)
        aspect_map = self._resolve_aspects(concept, dimensions, aspects)
        batch_defs = self._compose_batches(concept, dimensions, aspect_map)
        sentence_objs = self._generate_sentences(batch_defs)
        parsed_rows = self._merge_and_parse_batches(batch_defs, sentence_objs)
        return self._convert_to_output(parsed_rows, SentimentResponse)

    def _generate_dimensions(self, concept: str) -> List[str]:
        chain = StandardChainBuilder(
            prompt_template=self.config.dimension_prompt,
            llm=self.config.llm,
            entity_model=Dimensions
        ).build_chain()

        try:
            response = chain.invoke({"concept":concept})
        except Exception as e:
            raise ValueError(f"Failed to generate dimensions for concept '{concept}': {e}")
        
        response_dict = response.model_dump()
        return [
            x["single_derivative"]
            for x in response_dict.get("dimensions", [])
            if isinstance(x, dict) and "single_derivative" in x
        ]
    
    def _resolve_aspects(self, concept: str, dimensions: List[str], aspects: Optional[List[str]]) -> Dict[str, List[str]]:
        if aspects is not None:
            return {dim: aspects for dim in dimensions}
        return self._generate_aspects(concept, dimensions)
    
    def _generate_aspects(self, concept: str, dimensions: List[str]) -> Dict[str, List[str]]:
        chain = StandardChainBuilder(
            prompt_template=self.config.aspect_prompt,
            llm=self.config.llm,
            entity_model=Aspects
        ).build_chain()

        batch_inputs = [
            {"concept": concept, "dimension": dim, "index": idx}
            for idx, dim in enumerate(dimensions)
        ]

        responses = []
        for i in range(0, len(batch_inputs), self.config.batch_size):
            batch = batch_inputs[i:i + self.config.batch_size]
            try:
                batch_responses = chain.batch(batch)
            except Exception as e:
                if self.config.verbose:
                    print(f"Warning: Failed to process batch {i} - {i + self.config.batch_size}: {e}. Continuing with next batch.")
                continue
            responses.extend(batch_responses)
        response_dicts = [resp.model_dump() for resp in responses]

        aspects_by_dim = {}
        for batch in batch_inputs:
            idx = batch["index"]
            dim = batch["dimension"]
            resp = next((rd for rd in response_dicts if rd.get("index") == idx), None)
            aspects_by_dim[dim] = [
                x["single_derivative"] for x in resp.get("aspects", []) if isinstance(x, dict)
            ] if resp else []
        return aspects_by_dim
    
    def _compose_batches(self, concept: str, dimensions: List[str], aspects: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        batches = []
        for i in range(self.config.n_sentence):
            if self.config.n_aspect == 1:
                dim = random.choice(dimensions)
                asp = random.choice(aspects[dim])
                label = random.choice(self.config.label_options)
                aspect_string = f"Dimension: {dim} -> Aspect: {asp} -> Sentiment: {label} |"
                batch = {
                    "index": i,
                    "concept": concept,
                    "aspect": aspect_string,
                    **DrawUtility.draw_style()
                }
                batches.append(batch)
            else:
                dims, asps, labels = [], [], []
                for _ in range(self.config.n_aspect):
                    dim = random.choice(dimensions)
                    candidate_asp = None
                    tries = 0
                    while True:
                        asp = random.choice(aspects[dim])
                        if asp not in asps:
                            candidate_asp = asp
                            break
                        tries += 1
                        if tries > 10: 
                            break
                    dims.append(dim)
                    asps.append(candidate_asp or asp)
                    labels.append(random.choice(self.config.label_options))
                aspect_string = " | ".join(
                    f"Dimension: {dim} -> Aspect: {asp} -> Sentiment: {lbl}"
                    for dim, asp, lbl in zip(dims, asps, labels)
                )
                batch = {
                    "index": i,
                    "concept": concept,
                    "aspect": aspect_string,
                    **DrawUtility.draw_style()
                }
                batches.append(batch)
        return batches
    
    def _generate_sentences(self, batches: List[Dict[str, Any]]) -> List[Text]:
        chain = StandardChainBuilder(
            prompt_template=self.config.sentence_prompt,
            llm=self.config.llm,
            entity_model=Text
        ).build_chain()

        results = []
        for i in range(0, len(batches), self.config.batch_size):
            batch = batches[i:i + self.config.batch_size]
            try:
                responses = chain.batch(batch)
                if self.config.verbose and i % (self.config.batch_size * 100) == 0:
                    print(f"Processing batch {i // self.config.batch_size + 1}/{len(batches) // self.config.batch_size + 1}")
            except Exception as e:
                if self.config.verbose:
                    print(f"Warning: Error processing batch {i//self.config.batch_size}: {e}. Continuing with next batch.")
                continue
            results.extend(responses)

        return results
    
    def _merge_and_parse_batches(self, batches: List[Dict[str, Any]], sentences: List[Text]) -> List[Dict[str, Any]]:
        for sentence in sentences:
            sentence_dict = sentence.model_dump()
            index = sentence_dict.get("index")
            batch = batches[index]
            batch["generated_text"] = sentence_dict.get("generated_text", "")
        
        rows = []
        for batch in batches:
            for aspect_fragment in self._split_aspect_string(batch.get("aspect", "")):
                row = dict(batch) 
                row.update(self.parse_line(aspect_fragment))
                rows.append(row)
        return rows
    
    @staticmethod
    def _split_aspect_string(aspect_str: str) -> List[str]:
        return [frag.strip() for frag in aspect_str.split('|') if frag.strip()]
        
    @staticmethod
    def parse_line(line: str) -> Dict:
        parts = [p.strip() for p in line.split("->")]

        result = {}
        for part in parts:
            key, value = part.split(":", 1)
            result[key.strip()] = value.strip()
        
        return {
            "dimension":    result.get("Dimension"),
            "aspect":       result.get("Aspect"),
            "sentiment":    result.get("Sentiment"),
        }