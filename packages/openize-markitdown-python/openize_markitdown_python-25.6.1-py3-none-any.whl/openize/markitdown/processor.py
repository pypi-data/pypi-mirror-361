import logging
from pathlib import Path
from factory import ConverterFactory
from llm_strategy import SaveLocally, LLMFactory


class DocumentProcessor:
    def __init__(self, output_dir=Path("converted_md"), llm_client_name="openai"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.llm_client_name = llm_client_name

    def process_document(self, file_path, insert_into_llm=False):
        file_path = Path(file_path)
        file_extension = file_path.suffix
        converter = ConverterFactory.get_converter(file_extension)

        if not converter:
            logging.warning(f"No converter available for {file_extension}")
            return

        md_file = converter.convert_to_md(file_path, self.output_dir)
        if md_file:
            try:
                strategy = (
                    LLMFactory.get_llm(self.llm_client_name)
                    if insert_into_llm
                    else SaveLocally()
                )
                strategy.process(md_file)
            except ValueError as e:
                logging.error(f"Failed to initialize strategy: {e}")
