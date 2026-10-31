import { RELACOES } from './hexa-engine.js';
import { SEFIROT, executar } from './pipeline.js';

const EXEMPLO = 'A linguagem organiza a experiência em camadas de sentido. Cada palavra carrega uma história, e o mesmo termo muda de valor conforme a tradição que o recebe. '
  + 'Quando comparamos textos de épocas distintas, a analogia revela continuidades inesperadas. Porém, toda tradução também perde algo do original. '
  + 'O trabalho do hub é tornar visíveis essas passagens entre línguas, disciplinas e formas de pensar.';

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = (v) => `${(v * 100).toFixed(1).replace('.', ',')}%`;
const num = (v, d = 4) => Number(v).toFixed(d).replace('.', ',');

let ultimo = null;

function desenharArvore() {
  $('arvore').innerHTML = SEFIROT.map((s, i) =>
    `<li id="no-${s.id}"><b>${i + 1}. ${esc(s.nome)}</b><small>${esc(s.categoria)} · ${esc(s.funcao)}</small></li>`).join('');
}

function marcar(id, estado) {
  const no = $(`no-${id}`);
  if (no) { no.classList.remove('ativo', 'feito'); no.classList.add(estado); }
}

function radar(m) {
  const c = 150; const r = 110;
  const ponto = (i, v) => {
    const a = -Math.PI / 2 + (i * Math.PI) / 3;
    return [c + Math.cos(a) * r * v, c + Math.sin(a) * r * v];
  };
  const anel = (v) => RELACOES.map((_, i) => ponto(i, v).map((x) => x.toFixed(1)).join(',')).join(' ');
  const forma = RELACOES.map((rel, i) => ponto(i, m[rel.key]).map((x) => x.toFixed(1)).join(',')).join(' ');
  const rotulos = RELACOES.map((rel, i) => {
    const [x, y] = ponto(i, 1.22);
    return `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-size="12" fill="#44516B">${rel.rho} ${rel.nome}</text>`;
  }).join('');
  return `<svg viewBox="-45 0 390 300" role="img" aria-label="Radar do vetor hexarrelacional: ${RELACOES.map((rel) => `${rel.nome} ${pct(m[rel.key])}`).join(', ')}">
    ${[0.25, 0.5, 0.75, 1].map((v) => `<polygon points="${anel(v)}" fill="none" stroke="#D5DEEC" stroke-width="1"/>`).join('')}
    <polygon points="${forma}" fill="rgba(0,112,140,0.18)" stroke="#00708C" stroke-width="2"/>
    ${rotulos}</svg>`;
}

function cartao(s, corpo) {
  return `<article class="etapa" id="etapa-${s.id}"><header><h3>${esc(s.nome)}</h3><span class="cat">${esc(s.categoria)}</span><span class="fn">${esc(s.funcao)}</span></header>${corpo}</article>`;
}

function renderizar(r) {
  const y = r.yesod;
  const v = $('veredito');
  v.className = `veredito ${esc(y.veredito)}`;
  v.innerHTML = `<span class="kicker">Veredito · Yesod (política GuruDev)</span><br><b>${esc(y.veredito)}</b><p>${esc(y.motivo)}</p>`;
  const m = r.tiferet.metricas;
  $('radar').innerHTML = radar(m);
  $('formula').textContent = `f(A) = ${num(m.goldenNorm)} · Π(A) = ${num(m.piSqrtScore)}`;

  const corpos = {
    keter: `<p>${r.keter.caracteres.toLocaleString('pt-BR')} caracteres${r.keter.excedeLimite ? ' (acima do limite; recortado)' : ''}.</p><p class="nota">SHA-256: <code>${esc(r.keter.hash ?? 'indisponível neste navegador')}</code></p>`,
    chokhmah: `${r.chokhmah.termos.length ? `<ul class="chips">${r.chokhmah.termos.map((t) => `<li>${esc(t.termo)} · ${t.n}</li>`).join('')}</ul>` : '<p>Nenhum termo de conteúdo encontrado.</p>'}
      ${r.chokhmah.combinacoes.length ? `<p class="nota">Combinações recorrentes: ${r.chokhmah.combinacoes.map((c) => `${esc(c.par)} (${c.n})`).join(', ')}</p>` : ''}`,
    binah: `<table><tbody>
      <tr><td>Palavras</td><td class="n">${r.binah.palavras}</td></tr>
      <tr><td>Palavras únicas</td><td class="n">${r.binah.unicas}</td></tr>
      <tr><td>Sentenças</td><td class="n">${r.binah.sentencas}</td></tr>
      <tr><td>Diversidade lexical</td><td class="n">${pct(r.binah.diversidade)}</td></tr>
      <tr><td>Média de palavras por sentença</td><td class="n">${num(r.binah.mediaPalavrasPorSentenca, 1)}</td></tr>
      <tr><td>Conectores lógicos · termos estruturais · contraste</td><td class="n">${r.binah.conectores} · ${r.binah.estruturais} · ${r.binah.contraste}</td></tr>
      </tbody></table>`,
    tiferet: `<table><tbody>${RELACOES.map((rel) => `<tr><td>${rel.rho} ${esc(rel.nome)}</td><td class="n">${pct(m[rel.key])}</td></tr>`).join('')}</tbody></table>
      <ul>${r.tiferet.leitura.map((l) => `<li>${esc(l)}</li>`).join('')}</ul><p class="nota">${esc(r.tiferet.limitacao)}</p>`,
    gevurah: `<ul>${r.gevurah.limites.map((l) => `<li class="${l.ok ? 'ok' : 'no'}">${l.ok ? '✓' : '✗'} <span style="color:var(--ink)">${esc(l.texto)}</span></li>`).join('')}</ul>`,
    chesed: `<ul>${r.chesed.eixos.map((e) => `<li><b>${esc(e.relacao)}</b> · ${pct(e.valor)}. ${esc(e.sensibilidade)}</li>`).join('')}</ul><p class="nota">${esc(r.chesed.nota)}</p>`,
    netzach: `<pre>${esc(JSON.stringify(r.netzach.especificacao, null, 2))}</pre><pre>${esc(r.netzach.curl)}</pre>`,
    hod: `<p>Relatório em Markdown pronto para download.</p><pre>${esc(r.hod.markdown.split('\n').slice(0, 8).join('\n'))}\n…</pre>`,
    yesod: `<p><b>${esc(y.veredito)}</b> — ${esc(y.motivo)}</p>
      ${y.indicadores ? `<pre>${esc(JSON.stringify(y.indicadores, null, 2))}</pre>` : ''}
      <p class="nota">${y.disponivel ? `Indicadores recalculados no servidor e decididos por <code>${esc(y.politica)}</code> no interpretador GuruDev. Falha fechada.` : 'Sem verificação, o pipeline não confirma o resultado (falha fechada).'}</p>`,
    malkuth: `<p>${esc(r.malkuth.resumo)}</p><p class="nota">Use os botões abaixo para baixar o JSON completo ou o relatório.</p>`,
  };
  $('etapas').innerHTML = SEFIROT.map((s) => cartao(s, corpos[s.id])).join('');
  $('resultado').hidden = false;
}

function baixar(nome, conteudo, tipo) {
  const url = URL.createObjectURL(new Blob([conteudo], { type: tipo }));
  const a = Object.assign(document.createElement('a'), { href: url, download: nome });
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function carimbo() {
  return new Date().toISOString().replace(/[-:]/g, '').replace(/\..+/, '').replace('T', '-');
}

desenharArvore();
const texto = $('texto');
const atualizarContador = () => { $('contador').textContent = `${texto.value.length.toLocaleString('pt-BR')} caracteres`; };
texto.addEventListener('input', atualizarContador);
$('exemplo').addEventListener('click', () => { texto.value = EXEMPLO; atualizarContador(); texto.focus(); });
$('processar').addEventListener('click', async () => {
  const botao = $('processar');
  botao.disabled = true; botao.textContent = 'Processando…';
  desenharArvore();
  try {
    ultimo = await executar(texto.value, { aoAvancar: marcar });
    renderizar(ultimo);
    $('veredito').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } finally {
    botao.disabled = false; botao.textContent = 'Processar';
  }
});
$('baixar-json').addEventListener('click', () => ultimo && baixar(`hubstree-${carimbo()}.json`, JSON.stringify(ultimo.malkuth.json, null, 2), 'application/json'));
$('baixar-md').addEventListener('click', () => ultimo && baixar(`hubstree-relatorio-${carimbo()}.md`, ultimo.hod.markdown, 'text/markdown'));
