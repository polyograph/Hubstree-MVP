// Fase 0 no navegador: fronteira de entrada canônica e resultados locais.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { executar, codigoTextoInvalido, LIMITE_CARACTERES } from '../public/js/pipeline.js';

const TEXTO = 'A linguagem organiza a experiência em camadas de sentido. Cada palavra carrega uma história, e o mesmo termo muda de valor conforme a tradição que o recebe. Quando comparamos textos de épocas distintas, a analogia revela continuidades inesperadas.';

// Substitui fetch por um servidor de mentira e devolve as chamadas recebidas.
function stub(resposta) {
  const chamadas = [];
  globalThis.fetch = async (url, init) => {
    chamadas.push(JSON.parse(init.body));
    if (resposta instanceof Error) throw resposta;
    return resposta;
  };
  return chamadas;
}
const json = (status, corpo) => new Response(JSON.stringify(corpo), { status, headers: { 'Content-Type': 'application/json' } });

test('surrogate isolado e controle C0 bloqueiam no navegador sem chamar o servidor', async () => {
  assert.equal(codigoTextoInvalido('a\uD800b'), 'TEXTO_UNICODE_INVALIDO');
  assert.equal(codigoTextoInvalido('a\u0000b'), 'TEXTO_CONTROLE_INVALIDO');
  assert.equal(codigoTextoInvalido('a\tb\nc\r\nd'), null);
  assert.equal(codigoTextoInvalido('emoji 😀 e DEL \u007F e C1 \u0085'), null);
  for (const [texto, codigo] of [[`${TEXTO}\uDC00`, 'TEXTO_UNICODE_INVALIDO'], [`${TEXTO}\u0007`, 'TEXTO_CONTROLE_INVALIDO']]) {
    const chamadas = stub(json(200, {}));
    const r = await executar(texto);
    assert.equal(chamadas.length, 0);
    assert.equal(r.yesod.veredito, 'BLOQUEADO');
    assert.equal(r.yesod.codigo, codigo);
    assert.equal(r.yesod.origem_resultado, 'cliente');
    assert.equal(r.yesod.politica_avaliada, false);
  }
});

test('envia o texto NFC integral e o hash da entrada canônica', async () => {
  const chamadas = stub(json(200, { veredito: 'PROCESSADO', origem_resultado: 'servidor', politica_avaliada: true }));
  const r = await executar(TEXTO.normalize('NFD'));
  assert.equal(chamadas.length, 1);
  assert.equal(chamadas[0].texto, TEXTO.normalize('NFC'));
  assert.equal(chamadas[0].input_sha256, r.keter.inputSha256);
  assert.match(chamadas[0].input_sha256, /^[0-9a-f]{64}$/);
  assert.equal(Object.keys(chamadas[0].vetor).length, 6);
  assert.equal(r.yesod.veredito, 'PROCESSADO');
});

test('limite em pontos de código: 1.000 emojis contam 1.000, não 2.000', async () => {
  stub(json(200, {}));
  const texto = 'a'.repeat(19000) + '😀'.repeat(1000); // 20.000 pontos de código, 21.000 unidades UTF-16
  const r = await executar(texto);
  assert.equal(r.keter.caracteres, LIMITE_CARACTERES);
  assert.equal(r.keter.excedeLimite, false);
  assert.equal(r.keter.texto, texto);
});

test('HTTP 413, 400 e falha de rede viram resultados locais distintos', async () => {
  const casos = [
    [new Response('{}', { status: 413 }), 'CORPO_REQUISICAO_ACIMA_LIMITE'],
    [json(400, { erro: 'x', codigo: 'HASH_MALFORMADO' }), 'REQUISICAO_INVALIDA'],
    [new Response('falha', { status: 502 }), 'VERIFICACAO_INDISPONIVEL'],
    [new TypeError('fetch failed'), 'VERIFICACAO_INDISPONIVEL'],
  ];
  for (const [resposta, codigo] of casos) {
    stub(resposta);
    const r = await executar(TEXTO);
    assert.equal(r.yesod.veredito, 'BLOQUEADO');
    assert.equal(r.yesod.codigo, codigo);
    assert.equal(r.yesod.origem_resultado, 'cliente');
    assert.equal(r.yesod.politica_avaliada, false);
    if (codigo === 'REQUISICAO_INVALIDA') assert.equal(r.yesod.codigo_servidor, 'HASH_MALFORMADO');
  }
});
