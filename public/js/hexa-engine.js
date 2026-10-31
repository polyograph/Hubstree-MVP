/**
 * hexa-engine.js
 * Álgebra Hexarrelacional de Significância π√f(A), porte fiel do
 * hexa-engine.ts do HexaSign Lab (guilherme-machado-ceo/hubstry-hexasign-lab).
 * Mesmas heurísticas e coeficientes. O servidor (api/_lib/hexa_engine.py)
 * recalcula o mesmo vetor e a etapa Yesod compara os dois.
 *
 * Limite: heurísticas determinísticas e experimentais; não são instrumento
 * de medição científica validado.
 */

export const PHI = (1 + Math.sqrt(5)) / 2;

export const RELACOES = [
  { key: 'similitude', rho: 'ρ₁', nome: 'Similitude' },
  { key: 'homology', rho: 'ρ₂', nome: 'Homologia' },
  { key: 'equivalence', rho: 'ρ₃', nome: 'Equivalência' },
  { key: 'symmetry', rho: 'ρ₄', nome: 'Simetria' },
  { key: 'equilibrium', rho: 'ρ₅', nome: 'Equilíbrio' },
  { key: 'compensation', rho: 'ρ₆', nome: 'Compensação' },
];

const CONECTORES = /\b(portanto|logo|assim|se|entao|quando|porque|pois|implica|caso)\b/g;
const ESTRUTURAIS = /\b(algoritmo|matriz|sistema|operador|estrutura|funcao|relacao|rede|processo|regra|modelo)\b/g;
const CONTRASTE = /\b(mas|porem|porém|embora|enquanto|complementar|compensacao|emergencia|emergente)\b/g;

// Espaço em branco: o conjunto do \s / trim() do ECMAScript, escrito por extenso
// para que o contrato com o Python (api/_lib/hexa_engine.py) fique explícito.
export const ESPACO = /[\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]+/;

export const normalizar = (texto) =>
  texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

export const goldenNorm = (vetor) =>
  Math.sqrt(vetor.reduce((acc, v, i) => acc + Math.pow(PHI, i) * v * v, 0));

export const piSqrt = (norma) => (norma <= 0 ? 0 : Math.pow(norma, 1 / Math.PI));

export const contar = (texto) => {
  const n = normalizar(texto);
  const palavras = n.split(ESPACO).filter(Boolean);
  return {
    palavras: palavras.length,
    unicas: new Set(palavras).size,
    sentencas: n.split(/[.!?]+/).map((s) => s.trim()).filter(Boolean).length,
    conectores: (n.match(CONECTORES) ?? []).length,
    estruturais: (n.match(ESTRUTURAIS) ?? []).length,
    contraste: (n.match(CONTRASTE) ?? []).length,
  };
};

export const analisar = (texto) => {
  if (!texto?.trim()) {
    return { similitude: 0, homology: 0, equivalence: 0, symmetry: 0, equilibrium: 0, compensation: 0, goldenNorm: 0, piSqrtScore: 0 };
  }
  const c = contar(texto);
  const diversidade = c.palavras ? c.unicas / c.palavras : 0;
  const comprimento = Math.min(1, c.palavras / 60);
  const v = {
    similitude: Math.min(1, 0.20 + comprimento * 0.55 + diversidade * 0.25),
    homology: Math.min(1, 0.25 + c.estruturais / 8),
    equivalence: Math.min(1, 0.25 + c.conectores / 6 + diversidade * 0.15),
    symmetry: Math.min(1, 0.20 + Math.min(c.sentencas, 8) / 12 + c.conectores / 12),
    equilibrium: Math.max(0, Math.min(1, 0.85 - Math.abs(0.5 - diversidade) * 0.7 - Math.abs(0.5 - comprimento) * 0.25)),
    compensation: Math.min(1, 0.20 + c.contraste / 5 + c.estruturais / 12),
  };
  const norma = goldenNorm(RELACOES.map((r) => v[r.key]));
  return { ...v, goldenNorm: norma, piSqrtScore: piSqrt(norma) };
};
