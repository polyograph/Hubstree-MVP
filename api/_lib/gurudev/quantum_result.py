"""
QuantumResult — Resultado Probabilistico de Delegacao Quantica

Implementa o resultado probabilistico de operacoes quanticas delegadas
pelo protocolo GuruDev. O resultado NAO e um valor colapsado — e uma
distribuicao de probabilidades (counts) que preserva a natureza quantica.

GuruDev e o protocolo semantico da interface classico-quantica (como TCP/IP
para redes). Nao executa computacao quantica real — simula o comportamento
probabilistico esperado pela classificacao de delegacao.

Autor: Guilherme Goncalves Machado (Hubstry-DeepTech)
Versao: 0.3.0 | Licenca: MIT
Referencia: Machado (2026b). pi*sqrt(f(A)) e Computacao Quantica.
    DOI: 10.5281/zenodo.18776462
"""

import math
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class QuantumResult:
    """
    Resultado probabilistico de delegacao quantica.

    Em vez de retornar um valor colapsado (como uma linguagem quantica faria),
    GuruDev retorna a distribuicao completa — preservando a informacao
    probabilistica e permitindo que o consumidor decida como colapsar.

    Attributes:
        counts: Dicionario de resultado -> frequencia absoluta (int)
        shots: Numero total de execucoes/medicoes simuladas
        delegacao_tipo: Tipo de delegacao usada (emergencia/anomalia/etc)
        operacao: Nome da operacao quântica delegada
        perfil_rho: Perfil hexarrelacional usado na classificacao [rho1..rho6]
        colapsado: Se o resultado foi colapsado para um valor unico
        valor_colapsado: Valor apos colapso (se colapsado=True)
        metadata: Metadados adicionais da delegacao
        erro: Mensagem de erro (se contencao falhou)
    """

    counts: Dict[str, int]
    shots: int
    delegacao_tipo: str = ""
    operacao: str = ""
    perfil_rho: List[float] = field(default_factory=list)
    colapsado: bool = False
    valor_colapsado: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    erro: Optional[str] = None

    # ── Propriedades derivadas ──────────────────────────────

    @property
    def distribution(self) -> Dict[str, float]:
        """Distribuicao de probabilidades normalizada."""
        if self.shots == 0:
            return {}
        return {k: v / self.shots for k, v in self.counts.items()}

    @property
    def outcomes(self) -> List[str]:
        """Lista de resultados possiveis (keys de counts)."""
        return list(self.counts.keys())

    @property
    def entropy(self) -> float:
        """Entropia de Shannon da distribuicao (em bits)."""
        probs = self.distribution.values()
        if not probs:
            return 0.0
        return -sum(p * math.log2(p) for p in probs if p > 0)

    @property
    def is_error(self) -> bool:
        """Se o resultado e um erro de contencao."""
        return self.erro is not None

    # ── Metodos ────────────────────────────────────────────

    def most_likely(self) -> Optional[str]:
        """Retorna o resultado mais provavel (maior frequencia)."""
        if not self.counts:
            return None
        return max(self.counts, key=self.counts.get)

    def probability(self, outcome: str) -> float:
        """Probabilidade de um resultado especifico."""
        return self.distribution.get(outcome, 0.0)

    def collapse(self, seed: Optional[int] = None) -> str:
        """
        Colapsa a distribuicao para um unico resultado (amostragem).

        Apos o colapso, o resultado fica armazenado em valor_colapsado.
        GuruDev permite colapso explicito — a decisao e do consumidor,
        nao do protocolo.

        Args:
            seed: Semente para reprodutibilidade (opcional)

        Returns:
            Resultado amostrado
        """
        if self.is_error:
            raise RuntimeError(f"Nao e possivel colapsar resultado com erro: {self.erro}")

        if not self.counts:
            raise RuntimeError("Nenhum resultado para colapsar — counts vazio")

        rng = random.Random(seed)
        outcomes = list(self.counts.keys())
        weights = list(self.counts.values())
        resultado = rng.choices(outcomes, weights=weights, k=1)[0]

        self.colapsado = True
        self.valor_colapsado = resultado
        return resultado

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o resultado para dicionario."""
        d = {
            "counts": self.counts,
            "shots": self.shots,
            "distribution": self.distribution,
            "delegacao_tipo": self.delegacao_tipo,
            "operacao": self.operacao,
            "perfil_rho": self.perfil_rho,
            "entropy": round(self.entropy, 6),
            "most_likely": self.most_likely(),
            "outcomes": self.outcomes,
            "colapsado": self.colapsado,
            "valor_colapsado": self.valor_colapsado,
        }
        if self.erro:
            d["erro"] = self.erro
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    # ── Factory methods ────────────────────────────────────

    @classmethod
    def from_counts(
        cls,
        counts: Dict[str, int],
        delegacao_tipo: str = "",
        operacao: str = "",
        perfil_rho: Optional[List[float]] = None,
    ) -> "QuantumResult":
        """
        Cria QuantumResult a partir de counts absolutos.

        Args:
            counts: Dicionario resultado -> frequencia
            delegacao_tipo: Tipo de delegacao
            operacao: Nome da operacao
            perfil_rho: Perfil hexarrelacional usado

        Returns:
            QuantumResult com distribuicao calculada
        """
        shots = sum(counts.values())
        return cls(
            counts=counts,
            shots=shots,
            delegacao_tipo=delegacao_tipo,
            operacao=operacao,
            perfil_rho=perfil_rho or [],
        )

    @classmethod
    def simulate(
        cls,
        n_qubits: int,
        delegacao_tipo: str = "",
        operacao: str = "",
        perfil_rho: Optional[List[float]] = None,
        shots: int = 1024,
        seed: Optional[int] = None,
    ) -> "QuantumResult":
        """
        Simula resultado de medicao de n qubits.

        Gera uma distribuicao probabilistica simulada para n qubits.
        O perfil rho influencia a distribuicao: rho6 alto gera distribuicao
        mais uniforme (emergencia), rho3 alto gera resultado mais concentrado.

        Args:
            n_qubits: Numero de qubits medidos
            delegacao_tipo: Tipo de delegacao
            operacao: Nome da operacao
            perfil_rho: Perfil hexarrelacional [rho1..rho6]
            shots: Numero de medicoes simuladas
            seed: Semente para reprodutibilidade

        Returns:
            QuantumResult simulado
        """
        rng = random.Random(seed)
        n_outcomes = 2 ** n_qubits

        # Perfil influencia a concentracao da distribuicao
        if perfil_rho and len(perfil_rho) >= 6:
            rho6 = perfil_rho[5]  # compensacao
            rho3 = perfil_rho[2]  # equivalencia
            # rho3 alto → concentracao (resultado mais provavel dominante)
            # rho6 alto → dispersao (distribuicao mais uniforme)
            concentracao = rho3 - rho6 * 0.5  # [-0.5, 1.0]
            concentracao = max(-1.0, min(1.0, concentracao))
        else:
            concentracao = 0.0

        # Gerar pesos
        weights = []
        base_weight = 1.0 / n_outcomes
        for i in range(n_outcomes):
            if concentracao > 0:
                # Concentrado: resultado 0 dominante
                w = base_weight * (1.0 + concentracao * (n_outcomes - 1)) if i == 0 else base_weight * (1.0 - concentracao)
            elif concentracao < 0:
                # Disperso: distribuicao mais uniforme
                w = base_weight * (1.0 + concentracao * 0.5)
            else:
                w = base_weight
            weights.append(max(0.001, w))

        # Normalizar
        total = sum(weights)
        weights = [w / total for w in weights]

        # Amostrar
        labels = [format(i, f"0{n_qubits}b") for i in range(n_outcomes)]
        samples = rng.choices(labels, weights=weights, k=shots)

        counts = {}
        for s in samples:
            counts[s] = counts.get(s, 0) + 1

        return cls(
            counts=counts,
            shots=shots,
            delegacao_tipo=delegacao_tipo,
            operacao=operacao,
            perfil_rho=perfil_rho or [],
            metadata={"n_qubits": n_qubits, "seed": seed},
        )

    @classmethod
    def error(cls, mensagem: str, operacao: str = "") -> "QuantumResult":
        """
        Cria resultado de erro (operacao nao contida no protocolo).

        Args:
            mensagem: Mensagem de erro
            operacao: Nome da operacao tentada

        Returns:
            QuantumResult com erro
        """
        return cls(
            counts={},
            shots=0,
            operacao=operacao,
            erro=mensagem,
        )
