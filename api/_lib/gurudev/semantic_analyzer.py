"""GuruDev Semantic Analyzer v1.0.0-alpha - Integracao com Alexandria"""
from typing import Dict, List, Optional, Any
from .ast_nodes import SubescritaLinguagem

try:
    from alexandria import LanguageAnalyzer, TypeMapper, CodeTranslator
    ALEXANDRIA_AVAILABLE = True
except ImportError:
    ALEXANDRIA_AVAILABLE = False


class SemanticAnalysisResult:
    """Resultado da analise semantica de uma subscrita."""

    def __init__(self):
        self.language_comparison = None
        self.type_mappings: Dict[str, str] = {}
        self.warnings: List[str] = []
        self.notes: List[str] = []


class SemanticAnalyzer:
    """Analisador semantico conectado a biblioteca Alexandria."""

    def __init__(self):
        self.available = ALEXANDRIA_AVAILABLE
        self._comparison_cache: Dict[str, Any] = {}
        if self.available:
            self.language_analyzer = LanguageAnalyzer()
            self.type_mapper = TypeMapper()
            self.code_translator = CodeTranslator()

    def _find_lang_name(self, lang: str) -> str:
        """Encontra nome exato da linguagem no banco Alexandria."""
        candidates = [lang, lang.capitalize(), lang.title()]
        for name in candidates:
            try:
                info = self.language_analyzer.get_language_info(name)
                return info.get("nome", name)
            except (ValueError, KeyError):
                pass
        # busca case-insensitive
        for known in self.language_analyzer.list_languages():
            if known.lower() == lang.lower():
                return known
        return lang.capitalize()

    def analyze_subscrita(self, subescrita: SubescritaLinguagem) -> SemanticAnalysisResult:
        """Analisa uma subscrita de linguagem estrangeira usando Alexandria."""
        result = SemanticAnalysisResult()
        if not self.available:
            result.warnings.append("Alexandria nao disponivel")
            return result

        lang = subescrita.linguagem
        result.notes.append(f"Subscrita: {lang}")

        # Language comparison via Alexandria (usa Python como proxy do GuruDev)
        cache_key = f"python_{lang}"
        if cache_key not in self._comparison_cache:
            try:
                match = self._find_lang_name(lang)
                self._comparison_cache[cache_key] = self.language_analyzer.compare(
                    "Python", match
                )
            except (ValueError, KeyError):
                self._comparison_cache[cache_key] = None

        result.language_comparison = self._comparison_cache[cache_key]
        if result.language_comparison is None:
            result.warnings.append(f"Linguagem '{lang}' nao encontrada no banco Alexandria")

        # Type mapping via Alexandria TypeMapper
        lang_lower = lang.lower()
        supported = ["javascript", "rust", "java", "csharp"]
        if lang_lower in supported:
            try:
                mappings = self.type_mapper.map_types("python", lang_lower)
                result.type_mappings = {k: v.target_type for k, v in mappings.items()}
                result.notes.append(f"Mapeamento: {len(result.type_mappings)} tipos")
            except Exception as e:
                result.warnings.append(f"Tipo mapping falhou: {e}")

        return result

    def get_comparison(self, lang_a: str, lang_b: str):
        """Obtem comparacao direta entre duas linguagens via Alexandria."""
        if not self.available:
            return None
        try:
            return self.language_analyzer.compare(lang_a, lang_b)
        except (ValueError, KeyError):
            return None
