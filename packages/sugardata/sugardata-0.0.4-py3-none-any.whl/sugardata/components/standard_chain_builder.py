from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, RetryCallState
from typing import Dict, Any, Optional, Tuple, List
from .factory import create_llm_object
from ..utility.dynamic import DynamicUtility


def log_before_sleep(retry_state: RetryCallState):
    print(
        f"Retrying {retry_state.fn.__name__} (attempt {retry_state.attempt_number}) "
        f"due to: {retry_state.outcome.exception()!r}"
    )


class CustomChain:

    def __init__(self, chain: object, format_instructions: str):
        self.chain = chain
        self.format_instructions = format_instructions

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), before_sleep=log_before_sleep)
    def invoke(self, inputs: Dict[str, str]) -> object:
        inputs["format_instructions"] = self.format_instructions
        return self.chain.invoke(inputs)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), before_sleep=log_before_sleep)
    async def ainvoke(self, inputs: Dict[str, str]) -> object:
        inputs["format_instructions"] = self.format_instructions
        return await self.chain.ainvoke(inputs)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), before_sleep=log_before_sleep)
    def batch(self, inputs: List[Dict[str, str]]) -> List[object]:
        inputs = [{"format_instructions": self.format_instructions, **input} for input in inputs]
        return self.chain.batch(inputs)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), before_sleep=log_before_sleep)
    async def abatch(self, inputs: List[Dict[str, str]]) -> List[object]:
        inputs = [{"format_instructions": self.format_instructions, **input} for input in inputs]
        return await self.chain.abatch(inputs)


class StandardChainBuilder:

    def __init__(
            self,
            prompt_template: str,
            llm: Optional[object] = None,
            model_vendor: Optional[str] = None,
            model_name: Optional[str] = None,
            model_params: Optional[Dict[str, Any]] = None,
            entity_model: Optional[BaseModel] = None,
            entities: Optional[Dict[str, Any]] = None,
            data_model_name: Optional[str] = "ResultModel",
            **kwargs
        ):
        prompt = ChatPromptTemplate.from_template(prompt_template)
        parser, format_instructions = self._create_output_parser(data_model_name, entity_model, entities)
        if not llm:
            llm = create_llm_object(
                vendor=model_vendor,
                model=model_name,
                **(model_params or {})
            )
        base_chain = prompt | llm | parser
        self.chain = CustomChain(base_chain, format_instructions)

    def build_chain(self) -> CustomChain:
        return self.chain
    
    def _create_output_parser(
            self, 
            title: Optional[str]=None, 
            data_model: Optional[BaseModel]=None, 
            entities: Optional[Dict[str, Any]]=None
        ) -> Tuple[PydanticOutputParser, str]:
        
        if not data_model:
            data_model = DynamicUtility.create_pydantic_base_model(title, entities)

        parser = PydanticOutputParser(pydantic_object=data_model)
        format_instructions = parser.get_format_instructions()
        return parser, format_instructions