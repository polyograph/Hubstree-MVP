// Cloudflare Worker "hubstree-proxy", na rota hubstree.hubstry.dev/*.
// Repassa as requisições ao serviço do Cloud Run e devolve a resposta sem alterá-la.
// DNS: AAAA hubstree -> 100:: com proxy da Cloudflare ativo (nuvem laranja).
// Dispensa o mapeamento de domínio do Cloud Run e a verificação no Search Console.
const ORIGEM = "https://hubstree-r6yz7ln6bq-uc.a.run.app";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const destino = new URL(url.pathname + url.search, ORIGEM);
    const req = new Request(destino, request);
    req.headers.set("X-Forwarded-Host", url.host);
    return fetch(req, { redirect: "manual" });
  },
};
