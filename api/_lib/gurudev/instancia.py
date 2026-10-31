"""
GuruDev — instancia de classe em tempo de execucao.

A identidade da instancia (a classe a que pertence) e uma propriedade
explicita do objeto, e nao uma convencao sobre dicionarios. E sobre
essa identidade que a camada semantica (entidade = classe + semantica)
devera se apoiar.
"""


class Instancia:
    """Objeto criado a partir de uma classe GuruDev."""

    def __init__(self, classe, definicao, atributos=None):
        self.classe = classe  # nome da classe, ex.: "Empresa"
        self.definicao = definicao  # namespace da classe (metodos, atributos)
        self.atributos = dict(atributos or {})

    def metodo(self, nome):
        """Retorna a DefinicaoFuncao do metodo, ou None."""
        return self.definicao.get("__metodos__", {}).get(nome)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.atributos.items())
        return f"<{self.classe} {{{attrs}}}>"
