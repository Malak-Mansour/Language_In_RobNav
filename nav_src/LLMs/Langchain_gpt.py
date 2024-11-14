from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
import time

class Custom_GPT(LLM):
    model: Any  #: :meta private:

    """Key word arguments passed to the model."""
    temperature: float = 0.6
    top_p: float = 0.9
    max_seq_len: int = 128
    max_gen_len: int = 64
    max_batch_size: int = 4

    @property
    def _llm_type(self) -> str:
        return "custom_GPT"

    @classmethod
    def from_model_id(
        cls,
        BASE_URL: str,
        API_KEY: str,
        DEPLOYMENT_NAME: str,
        API_VERSION: str,
        temperature: float = 0.6,
        top_p: float = 0.9,
        max_seq_len: int = 128,
        max_gen_len: int = 64,
        max_batch_size: int = 4,
        **kwargs: Any,
    ) -> LLM:
        """Construct the pipeline object from model_id and task."""

        model = AzureChatOpenAI(
            openai_api_base=BASE_URL,
            openai_api_version=API_VERSION,
            deployment_name=DEPLOYMENT_NAME,
            openai_api_key=API_KEY,
            openai_api_type="azure",
            temperature=0,
            # max_tokens=16384,
            # max_retries=10,
        )

        return cls(
            model = model,
            # set as default
            temperature = temperature,
            top_p = top_p,
            max_seq_len = max_seq_len,
            max_gen_len = max_gen_len,
            max_batch_size = max_batch_size,
            **kwargs,
        )

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        # if stop is not None:
        #     raise ValueError("stop kwargs are not permitted.")
        return self.model.invoke(prompt).content