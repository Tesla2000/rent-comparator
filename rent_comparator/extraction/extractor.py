from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from .models import OfferParameters


class OfferExtractor:
    """Extracts structured parameters from rental offer text using LLM."""

    def __init__(
        self,
        api_key: SecretStr,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
    ):
        self.llm = ChatOpenAI(
            model=model, api_key=api_key, temperature=temperature
        ).with_structured_output(OfferParameters)

    def extract(self, offer_text: str) -> OfferParameters:
        """Extract parameters from offer text."""
        messages = [
            SystemMessage(
                content=(
                    "You are an expert at extracting structured information from rental property listings. "
                    "Extract all relevant parameters from the offer text. "
                    "If a parameter is not mentioned or unclear, set it to null. "
                    "For prices, extract only numeric values without currency symbols. "
                    "For boolean fields, determine based on context. "
                    "For address, extract the full street address if available. "
                    "For location, extract the neighborhood, district, or general area. "
                    "For minimal_rent_duration_months, extract the minimum rental period in months."
                )
            ),
            HumanMessage(
                content=f"Extract rental parameters from this offer:\n\n{offer_text}"
            ),
        ]

        return self.llm.invoke(messages)
