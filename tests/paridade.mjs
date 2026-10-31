// Imprime métricas e contagens do engine JS para um arquivo de textos (padrão: textos.json).
import { readFileSync } from 'node:fs';
import { analisar, contar, normalizar } from '../public/js/hexa-engine.js';

const arquivo = process.argv[2] ?? 'textos.json';
const textos = JSON.parse(readFileSync(new URL(`./${arquivo}`, import.meta.url), 'utf8'));
process.stdout.write(JSON.stringify(textos.map((t) => ({ m: analisar(t), c: contar(t), n: normalizar(t) }))));
