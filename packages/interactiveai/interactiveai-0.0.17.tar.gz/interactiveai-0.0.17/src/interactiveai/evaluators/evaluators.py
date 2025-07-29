from typing import Any, Callable, Dict, Optional, Type
from langchain_core.runnables import Runnable
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel


class Evaluator:
    """
    A generic evaluator class that can be configured for various evaluation tasks.
    """

    def __init__(
        self,
        interactive_client: "Interactive",
        eval_llm: BaseChatModel,
        custom_eval_function: Optional[Callable[[Any, Any, BaseChatModel], Any]] = None,
        placeholders: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        output_schema: Optional[Type[BaseModel]] = None,
    ):
        self.interactive_client = interactive_client
        self.eval_llm = eval_llm
        self.custom_eval_function = custom_eval_function
        self.placeholders = placeholders
        self.prompt = prompt
        self.output_schema = output_schema

    def run(self, input: Any, output: Any, expected_output: Any, **kwargs) -> Any:
        """
        Runs the evaluation.

        If a custom_eval_function is provided, it will be used.
        Otherwise, it will perform a default evaluation using a language model.
        """
        if self.custom_eval_function:
            return self.custom_eval_function(input, output, expected_output, self.eval_llm, **kwargs)

        if not self.prompt or not self.output_schema or not self.placeholders:
            raise ValueError(
                "For default evaluation, 'prompt', 'output_schema', and 'placeholders' must be provided."
            )
        
        prompt_template = self.interactive_client.get_prompt(self.prompt)

        if self.output_schema:
            assert hasattr(self.eval_llm, "with_structured_output"), "eval_llm must have a with_structured_output method"
            chain: Runnable = prompt_template | self.eval_llm.with_structured_output(self.output_schema)
        else:
            chain: Runnable = prompt_template | self.eval_llm
        
        return chain.invoke(self.placeholders)