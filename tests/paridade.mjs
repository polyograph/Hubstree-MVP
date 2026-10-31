// Imprime as métricas do engine JS para cada texto de tests/textos.json.
import { readFileSync } from 'node:fs';
import { analisar } from '../public/js/hexa-engine.js';

const textos = JSON.parse(readFileSync(new URL('./textos.json', import.meta.url), 'utf8'));
process.stdout.write(JSON.stringify(textos.map((t) => analisar(t))));
