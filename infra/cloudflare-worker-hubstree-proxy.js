// Worker "hubstree-proxy": rota hubstree.hubstry.dev/* (zona hubstry.dev).
// Origem primária: Cloud Run (us-central1). Origem de redundância: Render (free).
// Failover: se a primária falhar na rede, estourar o tempo limite ou responder 5xx,
// a mesma requisição é repetida na redundância. O cabeçalho X-Hubstree-Origem
// informa qual origem atendeu, para conferência e monitoramento.
const ORIGENS = [
  { nome: "cloud-run", url: "https://hubstree-r6yz7ln6bq-uc.a.run.app", limiteMs: 10000 },
  { nome: "render", url: "https://hubstree-mvp.onrender.com", limiteMs: 70000 }, // free acorda em ~1 min
];

export default {
  async fetch(request) {
    const url = new URL(request.url);
    // O corpo só pode ser lido uma vez; guardado em memória para permitir a repetição.
    const corpo = ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer();
    let ultimaFalha = "sem origem";

    for (const origem of ORIGENS) {
      const destino = new URL(url.pathname + url.search, origem.url);
      const cabecalhos = new Headers(request.headers);
      cabecalhos.set("X-Forwarded-Host", url.host);
      try {
        const resp = await fetch(destino, {
          method: request.method,
          headers: cabecalhos,
          body: corpo,
          redirect: "manual",
          signal: AbortSignal.timeout(origem.limiteMs),
        });
        if (resp.status >= 500) { ultimaFalha = `${origem.nome} ${resp.status}`; continue; }
        const saida = new Response(resp.body, resp);
        saida.headers.set("X-Hubstree-Origem", origem.nome);
        return saida;
      } catch (erro) {
        ultimaFalha = `${origem.nome} ${erro.name}`;
      }
    }
    return new Response(JSON.stringify({ status: "indisponivel", detalhe: ultimaFalha }), {
      status: 503,
      headers: { "Content-Type": "application/json; charset=utf-8", "Retry-After": "30" },
    });
  },
};
