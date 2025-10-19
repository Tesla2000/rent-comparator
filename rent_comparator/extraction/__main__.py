from __future__ import annotations

import json
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import Field
from pydantic import PositiveInt
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import CliApp
from pydantic_settings import SettingsConfigDict
from rent_comparator.extraction import OfferExtractor
from tqdm import tqdm


class ExtractionSettings(BaseSettings):
    """Settings for parameter extraction from scraped offers."""

    data_folder: Path = Field(
        default=Path("rent_comparator/data/rent_prices"),
        description="Folder with scraped offers",
    )
    file_extraction_pattern: str = "*.json"
    folder_extraction_pattern: str = "*"
    output_folder: Path = Field(
        default=Path("rent_comparator/data/extracted_parameters"),
        description="Output folder for extracted parameters",
    )
    model: str = Field(default="gpt-5-nano", description="OpenAI model to use")
    openai_api_key: SecretStr
    temperature: float = Field(default=0.0, description="LLM temperature")
    max_workers: PositiveInt = Field(
        default=5, description="Number of parallel extraction workers"
    )
    model_config = SettingsConfigDict(
        cli_parse_args=True,
        env_file=".env",
        extra="ignore",
        cli_kebab_case=True,
        cli_ignore_unknown_args=True,
    )

    @staticmethod
    def _extract_single_offer(
        extractor: OfferExtractor, offer_file: Path, output_file: Path
    ) -> str:
        scraped_data = json.loads(offer_file.read_text(encoding="utf-8"))
        offer_text = scraped_data["text"]

        result = extractor.extract(offer_text)
        output_file.write_text(result.model_dump_json(indent=2))

        return str(output_file)

    def cli_cmd(self) -> None:
        self.output_folder.mkdir(parents=True, exist_ok=True)

        extractor = OfferExtractor(
            model=self.model,
            temperature=self.temperature,
            api_key=self.openai_api_key,
        )

        total_extracted = 0

        for source_folder in self.data_folder.glob(
            self.folder_extraction_pattern
        ):
            if not source_folder.is_dir():
                continue

            source_name = source_folder.name
            print(f"\n=== Extracting from {source_name} ===")

            output_source_folder = self.output_folder / source_name
            output_source_folder.mkdir(parents=True, exist_ok=True)

            offers_to_process = []
            for offer_file in source_folder.glob(self.file_extraction_pattern):
                output_file = output_source_folder / f"{offer_file.stem}.json"
                if output_file.exists():
                    continue
                offers_to_process.append((offer_file, output_file))

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(
                        self._extract_single_offer, extractor, of, out
                    )
                    for of, out in offers_to_process
                ]

                for _ in tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc=f"  {source_name}",
                    unit="offer",
                ):
                    total_extracted += 1

        print("\n=== Extraction Complete ===")
        print(f"Total offers extracted: {total_extracted}")
        print(f"Results saved to: {self.output_folder}")


if __name__ == "__main__":
    CliApp.run(ExtractionSettings)
