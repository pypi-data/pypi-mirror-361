import os
from processor import DocumentProcessor
from llm_strategy import LLMFactory, SaveLocally
import logging

class MarkItDown:
    def __init__(self, output_dir, llm_client_name=None):
        self.output_dir = output_dir
        self.llm_client_name = llm_client_name
        self.llm_client = None

        if llm_client_name:
            try:
                self.llm_client = LLMFactory.get_llm(llm_client_name)
            except ValueError as e:
                logging.error(f"LLM client error: {e}")
                self.llm_client = SaveLocally()
        else:
            self.llm_client = SaveLocally()

    def convert_document(self, input_file):
        """Run the document conversion process."""
        processor = DocumentProcessor(self.output_dir)
        md_file = processor.process_document(input_file)

        if md_file and self.llm_client:
            self.llm_client.process(md_file)

    def convert_directory(self, input_dir: str):
        supported_exts = [".docx", ".pdf", ".xlsx", ".pptx"]
        for filename in os.listdir(input_dir):
            filepath = os.path.join(input_dir, filename)
            if os.path.isfile(filepath) and os.path.splitext(filename)[1].lower() in supported_exts:
                self.convert_document(filepath)
