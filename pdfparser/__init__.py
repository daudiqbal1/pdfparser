from .parser import PDFParser


def parse_pdf(path: str):
    parser = PDFParser()
    return parser.parse(path)
