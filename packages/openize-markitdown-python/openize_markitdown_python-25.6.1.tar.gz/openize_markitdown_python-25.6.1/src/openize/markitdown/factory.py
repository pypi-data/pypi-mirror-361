from converters import WordConverter, PDFConverter, ExcelConverter, PowerPointConverter


class ConverterFactory:
    @staticmethod
    def get_converter(file_extension):
        converters = {
            ".docx": WordConverter(),
            ".pdf": PDFConverter(),
            ".xlsx": ExcelConverter(),
            ".pptx": PowerPointConverter(),
        }
        return converters.get(file_extension.lower(), None)