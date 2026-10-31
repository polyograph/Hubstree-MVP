import { test } from 'node:test';
import assert from 'node:assert/strict';
import { executar, SEFIROT } from '../public/js/pipeline.js';
import { analisar, goldenNorm, piSqrt, PHI } from '../public/js/hexa-engine.js';

const EXEMPLO = 'A linguagem organiza a experiência em camadas de sentido. Cada palavra carrega uma história, e o mesmo termo muda de valor conforme a tradição que o recebe. Quando comparamos textos de épocas distintas, a analogia revela continuidades inesperadas. Porém, toda tradução também perde algo do original. O trabalho do hub é tornar visíveis essas passagens entre línguas, disciplinas e formas de pensar.';

test('norma áurea e Π seguem a definição do manuscrito', () => {
  assert.equal(goldenNorm([1, 0, 0, 0, 0, 0]), 1);
  assert.ok(Math.abs(goldenNorm([0, 1, 0, 0, 0, 0]) - Math.sqrt(PHI)) < 1e-12);
  assert.ok(Math.abs(piSqrt(2) - 2 ** (1 / Math.PI)) < 1e-12);
  assert.equal(piSqrt(0), 0);
});

test('vetor fica em [0,1] e entrada vazia zera tudo', () => {
  const m = analisar(EXEMPLO);
  for (const k of ['similitude', 'homology', 'equivalence', 'symmetry', 'equilibrium', 'compensation']) {
    assert.ok(m[k] >= 0 && m[k] <= 1, k);
  }
  assert.equal(analisar('   ').goldenNorm, 0);
});

test('pipeline percorre as dez sefirot e falha fechado sem servidor', async () => {
  const vistos = [];
  const r = await executar(EXEMPLO, { endpoint: 'http://127.0.0.1:9/indisponivel', aoAvancar: (id, e) => e === 'feito' && vistos.push(id) });
  assert.deepEqual([...vistos].sort(), SEFIROT.map((s) => s.id).sort());
  assert.equal(r.yesod.veredito, 'BLOQUEADO');
  assert.equal(r.yesod.disponivel, false);
  assert.match(r.hod.markdown, /# Relatório Hubstree/);
  assert.equal(r.keter.hash.length, 64);
  assert.equal(r.gevurah.violacoes, 0);
  assert.equal(r.chesed.eixos.length, 2);
});
