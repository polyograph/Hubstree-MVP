"""GuruDev Core v1.2.0-alpha"""
from .parser import parse
from .interpreter import Interpreter, GuruDevError
from .semantic_analyzer import SemanticAnalyzer, SemanticAnalysisResult


def interpretar(codigo, debug=False):
    """Parseia e interpreta codigo GuruDev."""
    ast = parse(codigo, debug=debug)
    return Interpreter().interpretar(ast)
