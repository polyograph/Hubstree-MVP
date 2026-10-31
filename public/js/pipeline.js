/**
 * pipeline.js — as dez sefirot como operadores determinísticos.
 * Cada etapa recebe o estado acumulado e devolve sua saída.
 * Mapeamento sefirá ↔ categoria de Aristóteles conforme docs/ontology-map.md.
 */
import { RELACOES, analisar, contar, normalizar } from './hexa-engine.js';

export const VERSAO = '2.0.0';
export const LIMITE_CARACTERES = 20000;
export const AMP_HOMOGENEO = 0.15;
export const AMP_DISPERSO = 0.6;
const EPS = 1e-9;

export const SEFIROT = [
  { id: 'keter', nome: 'Keter', categoria: 'Substância', funcao: 'Princípio e identidade da entrada' },
  { id: 'chokhmah', nome: 'Chokhmah', categoria: 'Ação', funcao: 'Termos-chave e combinações recorrentes' },
  { id: 'binah', nome: 'Binah', categoria: 'Qualidade', funcao: 'Decomposição estrutural' },
  { id: 'tiferet', nome: 'Tiferet', categoria: 'Relação', funcao: 'Vetor hexarrelacional π√f(A)' },
  { id: 'gevurah', nome: 'Gevurah', categoria: 'Quantidade', funcao: 'Restrições e limites da leitura' },
  { id: 'chesed', nome: 'Chesed', categoria: 'Paixão / Capacidade', funcao: 'Eixos a explorar' },
  { id: 'netzach', nome: 'Netzach', categoria: 'Lugar', funcao: 'Especificação reprodutível' },
  { id: 'hod', nome: 'Hod', categoria: 'Tempo', funcao: 'Documentação' },
  { id: 'yesod', nome: 'Yesod', categoria: 'Posição relativa', funcao: 'Verificação por política GuruDev' },
  { id: 'malkuth', nome: 'Malkuth', categoria: 'Estado', funcao: 'Entrega final' },
];

const STOPWORDS = new Set(('a o as os um uma uns umas de do da dos das em no na nos nas por pelo pela pelos pelas ' +
  'para pra com sem sob sobre entre ate desde e ou mas que se como quando onde porque pois porem embora enquanto ' +
  'ja nao sim tambem mais menos muito muita muitos muitas pouco cada todo toda todos todas outro outra outros outras ' +
  'este esta estes estas esse essa esses essas isso isto aquilo aquele aquela seu sua seus suas meu minha nosso nossa ' +
  'ele ela eles elas eu tu voce voces nos lhe lhes me te ser estar ter haver foi era sao sera seria tem ha fazer faz ' +
  'pode podem deve devem algo alguem algum alguma nada assim logo entao portanto qual quais cujo cuja ao aos the and of to in is are for').split(' '));

const SENSIBILIDADE = {
  similitude: 'responde ao comprimento (até 60 palavras) e à diversidade lexical',
  homology: 'responde a termos estruturais: algoritmo, matriz, sistema, operador, estrutura, função, relação, rede, processo, regra, modelo',
  equivalence: 'responde a conectores lógicos (portanto, se, então, porque, pois, implica, caso) e à diversidade lexical',
  symmetry: 'responde ao número de sentenças (até 8) e aos conectores lógicos',
  equilibrium: 'responde à proximidade de 0,5 da diversidade lexical e do comprimento relativo',
  compensation: 'responde a termos de contraste (mas, porém, embora, enquanto, complementar) e a termos estruturais',
};

export const OPERACIONALIZACAO = {
  similitude: 'min(1; 0,20 + 0,55·comprimento + 0,25·diversidade). Não compara dois objetos: depende só do comprimento e da diversidade lexical',
  homology: 'min(1; 0,25 + termos estruturais / 8)',
  equivalence: 'min(1; 0,25 + conectores lógicos / 6 + 0,15·diversidade)',
  symmetry: 'min(1; 0,20 + min(sentenças; 8) / 12 + conectores lógicos / 12)',
  equilibrium: 'limitado a [0,1]: 0,85 − 0,7·|0,5 − diversidade| − 0,25·|0,5 − comprimento|',
  compensation: 'min(1; 0,20 + termos de contraste / 5 + termos estruturais / 12)',
};
export const NOTA_OPERACIONAL = 'Os nomes seguem a Álgebra Hexarrelacional. Neste engine, cada componente é operacionalizado por contagens lexicais (comprimento = min(1; palavras/60); diversidade = palavras únicas/palavras). Os valores não medem diretamente as relações semânticas que dão nome aos eixos.';

const pct = (v) => `${(v * 100).toFixed(1).replace('.', ',')}%`;
const num = (v, d = 4) => v.toFixed(d).replace('.', ',');
const rotulo = (r) => `${r.rho} (${r.nome})`;

async function sha256(texto) {
  if (globalThis.crypto?.subtle) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(texto));
    return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
  }
  return null;
}

/* ── Keter · Substância ─────────────────────────────── */
async function keter(entrada) {
  const texto = (entrada ?? '').normalize('NFC');
  const recortado = texto.slice(0, LIMITE_CARACTERES);
  return {
    texto: recortado,
    caracteres: texto.length,
    excedeLimite: texto.length > LIMITE_CARACTERES,
    vazio: !texto.trim(),
    hash: await sha256(recortado),
  };
}

/* ── Chokhmah · Ação ───────────────────────────────── */
function chokhmah(texto) {
  const tokens = normalizar(texto).split(/[^a-z0-9]+/).filter((t) => t.length >= 4 && !STOPWORDS.has(t));
  const freq = new Map();
  tokens.forEach((t) => freq.set(t, (freq.get(t) ?? 0) + 1));
  const termos = [...freq.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 8)
    .map(([termo, n]) => ({ termo, n }));
  const pares = new Map();
  for (let i = 0; i < tokens.length - 1; i += 1) {
    const par = `${tokens[i]} ${tokens[i + 1]}`;
    pares.set(par, (pares.get(par) ?? 0) + 1);
  }
  const combinacoes = [...pares.entries()].filter(([, n]) => n >= 2)
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 5).map(([par, n]) => ({ par, n }));
  return { termos, combinacoes, tokensConteudo: tokens.length };
}

/* ── Binah · Qualidade ─────────────────────────────── */
function binah(texto) {
  const c = contar(texto);
  const diversidade = c.palavras ? c.unicas / c.palavras : 0;
  const sentencas = texto.split(/[.!?]+/).map((s) => s.trim()).filter(Boolean);
  const maiores = sentencas.map((s) => s.split(/\s+/).filter(Boolean).length);
  return {
    ...c,
    diversidade,
    mediaPalavrasPorSentenca: c.sentencas ? c.palavras / c.sentencas : 0,
    maiorSentenca: maiores.length ? Math.max(...maiores) : 0,
  };
}

/* ── Tiferet · Relação ─────────────────────────────── */
function tiferet(texto) {
  const m = analisar(texto);
  const entradas = RELACOES.map((r) => ({ ...r, v: m[r.key] }));
  const valores = entradas.map((e) => e.v);
  const max = Math.max(...valores);
  const min = Math.min(...valores);
  const amp = max - min;
  const saturados = entradas.filter((e) => e.v >= 1 - EPS);
  const topo = entradas.filter((e) => max - e.v <= EPS);
  const base = entradas.filter((e) => e.v - min <= EPS);
  const perfil = amp < AMP_HOMOGENEO ? 'homogêneo' : amp > AMP_DISPERSO ? 'disperso' : 'intermediário';
  const leitura = [
    `Amplitude do vetor: ${(amp * 100).toFixed(1).replace('.', ',')} p.p., perfil ${perfil} pelos limiares declarados (< 15 p.p. homogêneo; > 60 p.p. disperso).`,
    `Maior componente: ${topo.map(rotulo).join(' e ')}. Menor componente: ${base.map(rotulo).join(' e ')}.`,
    saturados.length
      ? `Componentes saturados em 100%: ${saturados.map(rotulo).join(', ')}. Nesses eixos a leitura perde resolução.`
      : 'Nenhum componente saturado.',
  ];
  return {
    metricas: m,
    entradas,
    amplitude: amp,
    perfil,
    saturados: saturados.length,
    leitura,
    operacionalizacao: OPERACIONALIZACAO,
    notaOperacional: NOTA_OPERACIONAL,
    limitacao: 'Esta leitura interpreta o perfil quantitativo produzido pelo engine. Ela não demonstra, por si só, a ocorrência das relações formais no artefato.',
  };
}

/* ── Gevurah · Quantidade ──────────────────────────── */
function gevurah(k, b, t) {
  const limites = [
    { ok: !k.vazio, texto: 'Entrada não vazia' },
    { ok: !k.excedeLimite, texto: `Entrada dentro do limite de ${LIMITE_CARACTERES.toLocaleString('pt-BR')} caracteres` },
    { ok: b.palavras >= 20, texto: `Amostra com pelo menos 20 palavras (atual: ${b.palavras})` },
    { ok: b.sentencas >= 2, texto: `Pelo menos 2 sentenças (atual: ${b.sentencas})` },
    { ok: t.saturados === 0, texto: `Nenhum componente saturado (atual: ${t.saturados})` },
    { ok: b.maiorSentenca <= 40, texto: `Maior sentença com até 40 palavras (atual: ${b.maiorSentenca})` },
  ];
  return { limites, violacoes: limites.filter((l) => !l.ok).length };
}

/* ── Chesed · Paixão / Capacidade ──────────────────── */
function chesed(t) {
  const ordenados = [...t.entradas].sort((a, b) => a.v - b.v || a.key.localeCompare(b.key));
  return {
    eixos: ordenados.slice(0, 2).map((e) => ({
      relacao: rotulo(e),
      valor: e.v,
      sensibilidade: `No engine atual, ${e.rho} ${SENSIBILIDADE[e.key]}.`,
    })),
    nota: 'Indica a que sinais textuais cada eixo é sensível no engine. Não é recomendação de estilo.',
  };
}

/* ── Netzach · Lugar ───────────────────────────────── */
function netzach(k) {
  return {
    especificacao: {
      pipeline: 'hubstree',
      versao: VERSAO,
      engine: 'hexa-engine (porte do HexaSign Lab)',
      politica: 'api/_lib/politica_hubstree.guru',
      limiares: { amplitudeHomogeneo: AMP_HOMOGENEO, amplitudeDisperso: AMP_DISPERSO, palavrasMinimas: 20, sentencasMinimas: 2 },
      entradaSha256: k.hash,
    },
    curl: 'curl -s -X POST https://SEU-DOMINIO/api/verificar -H "Content-Type: application/json" -d \'{"texto":"..."}\'',
  };
}

/* ── Yesod · Posição relativa ──────────────────────── */
async function yesod(texto, metricas, endpoint) {
  const vetor = Object.fromEntries(RELACOES.map((r) => [r.key, metricas[r.key]]));
  try {
    const resp = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto, vetor }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return { ...(await resp.json()), disponivel: true };
  } catch (erro) {
    return {
      veredito: 'BLOQUEADO',
      motivo: `verificação indisponível (${erro.message}); falha fechada`,
      politica_ok: false,
      disponivel: false,
    };
  }
}

/* ── Hod · Tempo ───────────────────────────────────── */
function hod(r, quando) {
  const m = r.tiferet.metricas;
  const linhas = [
    '# Relatório Hubstree',
    '',
    `- Gerado em: ${quando}`,
    `- Pipeline: v${VERSAO}`,
    `- SHA-256 da entrada: ${r.keter.hash ?? 'indisponível neste navegador'}`,
    `- Veredito (Yesod): **${r.yesod.veredito}** — ${r.yesod.motivo}`,
    '',
    '## Estrutura (Binah)',
    `- Palavras: ${r.binah.palavras} · únicas: ${r.binah.unicas} · sentenças: ${r.binah.sentencas}`,
    `- Diversidade lexical: ${pct(r.binah.diversidade)} · média de palavras por sentença: ${num(r.binah.mediaPalavrasPorSentenca, 1)}`,
    '',
    '## Vetor hexarrelacional (Tiferet)',
    '| Relação | Valor | Operacionalização |',
    '|---|---|---|',
    ...RELACOES.map((rel) => `| ${rotulo(rel)} | ${pct(m[rel.key])} | ${OPERACIONALIZACAO[rel.key].replace(/\|/g, '\\|')} |`),
    '',
    `> ${NOTA_OPERACIONAL}`,
    '',
    `- f(A) = ${num(m.goldenNorm)} · Π(A) = ${num(m.piSqrtScore)}`,
    ...r.tiferet.leitura.map((l) => `- ${l}`),
    '',
    `> ${r.tiferet.limitacao}`,
    '',
    '## Termos-chave (Chokhmah)',
    r.chokhmah.termos.length ? r.chokhmah.termos.map((t) => `${t.termo} (${t.n})`).join(', ') : '—',
    '',
    '## Restrições (Gevurah)',
    ...r.gevurah.limites.map((l) => `- [${l.ok ? 'x' : ' '}] ${l.texto}`),
    '',
    '## Eixos a explorar (Chesed)',
    ...r.chesed.eixos.map((e) => `- ${e.relacao}: ${pct(e.valor)}. ${e.sensibilidade}`),
  ];
  return { markdown: linhas.join('\n') };
}

/* ── Malkuth · Estado ──────────────────────────────── */
function malkuth(r) {
  return {
    veredito: r.yesod.veredito,
    resumo: `${r.binah.palavras} palavras · Π(A) = ${num(r.tiferet.metricas.piSqrtScore)} · perfil ${r.tiferet.perfil}`,
    json: {
      versao: VERSAO,
      entrada: { sha256: r.keter.hash, caracteres: r.keter.caracteres },
      estrutura: r.binah,
      termos: r.chokhmah,
      vetor: r.tiferet.metricas,
      perfil: { amplitude: r.tiferet.amplitude, classe: r.tiferet.perfil, leitura: r.tiferet.leitura },
      restricoes: r.gevurah.limites,
      eixos: r.chesed.eixos,
      verificacao: r.yesod,
    },
  };
}

export async function executar(entrada, { endpoint = '/api/verificar', quando = new Date().toISOString(), aoAvancar } = {}) {
  const r = {};
  const passo = async (id, fn) => { aoAvancar?.(id, 'ativo'); r[id] = await fn(); aoAvancar?.(id, 'feito'); };
  await passo('keter', () => keter(entrada));
  const texto = r.keter.texto;
  await passo('chokhmah', () => chokhmah(texto));
  await passo('binah', () => binah(texto));
  await passo('tiferet', () => tiferet(texto));
  await passo('gevurah', () => gevurah(r.keter, r.binah, r.tiferet));
  await passo('chesed', () => chesed(r.tiferet));
  await passo('netzach', () => netzach(r.keter));
  await passo('yesod', () => yesod(entrada ?? '', r.tiferet.metricas, endpoint));
  await passo('hod', () => hod(r, quando));
  await passo('malkuth', () => malkuth(r));
  return r;
}
