# Hubstree · Pipeline Ontológico Cognitivo

Hubstree é um pipeline determinístico em dez etapas. Cada etapa corresponde a uma sefirá da Árvore da Vida, cruzada com uma das dez categorias de Aristóteles (mapa em [`docs/ontology-map.md`](docs/ontology-map.md)). Projeto da Hubstry Deep Tech, publicado pela Polyograph.

A versão 2 substitui as respostas simuladas da v1 por operadores reais, unindo dois projetos do ecossistema:

- **HexaSign Lab** — o engine da Álgebra Hexarrelacional de Significância π√f(A) alimenta as etapas analíticas. Ele calcula seis componentes em [0,1] (similitude, homologia, equivalência, simetria, equilíbrio e compensação), a norma ponderada pela razão áurea f(A) e o operador Π(A) = f(A)^(1/π).
- **GuruDev** — a etapa Yesod executa uma política escrita em GuruDev, no interpretador real da linguagem. O desenho vem do Evidence Gate da GuruDev: indicadores tipados, política estática, falha fechada.

Nenhum modelo de linguagem participa do pipeline.

## As dez etapas

| # | Sefirá | Categoria | O que faz |
|---|---|---|---|
| 1 | Keter | Substância | Normaliza a entrada (Unicode NFC), aplica o limite de 20.000 caracteres e calcula o SHA-256 |
| 2 | Chokhmah | Ação | Termos-chave por frequência e combinações recorrentes |
| 3 | Binah | Qualidade | Palavras, sentenças, diversidade lexical, conectores, termos estruturais e de contraste |
| 4 | Tiferet | Relação | Vetor hexarrelacional, f(A), Π(A) e leitura do perfil com limiares declarados |
| 5 | Gevurah | Quantidade | Restrições que limitam a leitura (amostra curta, saturação, sentenças longas) |
| 6 | Chesed | Paixão / Capacidade | Os dois eixos mais baixos e a que sinais o engine é sensível neles |
| 7 | Netzach | Lugar | Especificação reprodutível (versão, limiares, hash) e chamada à API |
| 8 | Hod | Tempo | Relatório em Markdown |
| 9 | Yesod | Posição relativa | Recalcula o vetor no servidor, compara com o do navegador e aplica a política GuruDev |
| 10 | Malkuth | Estado | Entrega final em JSON |

### Vereditos da política (`api/_lib/politica_hubstree.guru`)

| Veredito | Quando |
|---|---|
| `BLOQUEADO` | entrada vazia ou acima do limite, vetor fora de [0,1], vetor enviado fora do contrato (seis números finitos em [0,1], sem texto nem booleano), divergência entre navegador e servidor, verificação indisponível ou qualquer erro da política |
| `AMOSTRA_INSUFICIENTE` | menos de 20 palavras |
| `LEITURA_LIMITADA` | algum componente saturado em 1, ou uma única sentença |
| `PROCESSADO` | nenhuma das condições acima |

Os limiares moram na política GuruDev, não no Python. O texto do usuário nunca é executado: só o arquivo `.guru` passa pelo parser.

O endpoint aceita só `{"texto": string, "vetor"?: objeto}`. Recusa com HTTP 400 chaves extras ou duplicadas, `NaN`/`Infinity`, JSON malformado e aninhamento excessivo. Qualquer exceção interna vira `BLOQUEADO`, nunca um erro 500 sem veredito.

## Limite do método

As heurísticas do engine são determinísticas e experimentais. Os resultados são saídas analíticas, não medições científicas validadas. A leitura do perfil evita afirmações de magnitude absoluta e de qualidade do texto, seguindo a especificação MS-01 do HexaSign Lab.

Os nomes dos seis componentes seguem a Álgebra Hexarrelacional, mas neste engine cada um é operacionalizado por contagens lexicais. A similitude, por exemplo, não compara dois objetos: é função do comprimento e da diversidade lexical. A interface e o relatório mostram a fórmula de cada componente ao lado do valor.

| Componente | Operacionalização |
|---|---|
| ρ₁ Similitude | min(1; 0,20 + 0,55·comprimento + 0,25·diversidade) |
| ρ₂ Homologia | min(1; 0,25 + termos estruturais / 8) |
| ρ₃ Equivalência | min(1; 0,25 + conectores lógicos / 6 + 0,15·diversidade) |
| ρ₄ Simetria | min(1; 0,20 + min(sentenças; 8) / 12 + conectores lógicos / 12) |
| ρ₅ Equilíbrio | limitado a [0,1]: 0,85 − 0,7·\|0,5 − diversidade\| − 0,25·\|0,5 − comprimento\| |
| ρ₆ Compensação | min(1; 0,20 + termos de contraste / 5 + termos estruturais / 12) |

Onde comprimento = min(1; palavras/60) e diversidade = palavras únicas / palavras.

## Contrato de normalização

São duas normalizações diferentes, com papéis diferentes:

1. **Keter (entrada):** Unicode NFC (forma de composição canônica), aplicada no navegador e repetida no servidor, que não confia na normalização do cliente. O limite de 20.000 caracteres é medido em pontos de código Unicode do texto NFC (`Array.from()` no JavaScript, `len()` no Python), não em unidades UTF-16. Texto com surrogate isolado ou com caractere de controle C0 (exceto tabulação, LF e CR) é recusado nos dois lados, com os códigos `TEXTO_UNICODE_INVALIDO` e `TEXTO_CONTROLE_INVALIDO`.
2. **Engine (análise):** NFD (forma de decomposição canônica), remoção apenas do bloco U+0300–U+036F e conversão para minúsculas. Marcas combinantes fora desse bloco permanecem. É o mesmo recorte do `hexa-engine.ts` original.

Espaço em branco, para dividir palavras e aparar sentenças, é exatamente o conjunto do `\s` do ECMAScript, escrito por extenso nos dois engines. Os limites de palavra das expressões regulares são ASCII nos dois lados.

### Contrato de `POST /api/verificar`

Corpo: `{"texto", "vetor"?, "input_sha256"?}`. O navegador envia o texto NFC integral, o vetor das seis relações e o SHA-256 desse texto. A resposta mantém as chaves anteriores e acrescenta `codigo` (identificador estável do motivo), `origem_resultado`, `politica_avaliada` e `proveniencia`:

| Campo | Conteúdo |
|---|---|
| `proveniencia.input_sha256` | SHA-256 dos bytes UTF-8 do texto NFC integral, calculado no servidor |
| `proveniencia.analise_sha256` | SHA-256 do trecho analisado (até 20.000 pontos de código) |
| `proveniencia.hash_status` | `verificado`, `ausente_legado` (cliente sem hash) ou `divergente`, que bloqueia pela política |

O hash detecta inconsistência entre o texto enviado e o recebido; não autentica o cliente. Erros de contrato devolvem HTTP 400 ou 413 com `codigo` (`HASH_MALFORMADO`, `CHAVE_NAO_PERMITIDA`, `CORPO_REQUISICAO_ACIMA_LIMITE` e outros). No navegador, 413, 400 e falhas de rede viram `BLOQUEADO` com `origem_resultado: "cliente"` e `politica_avaliada: false`: a política não chegou a avaliar a entrada.

A paridade JS↔Python é testada em 446 amostras determinísticas (`tests/unicode_amostras.json`). Elas cobrem marcas combinantes dentro e fora do bloco removido, hangul, vietnamita, hebraico, árabe, devanágari, CJK, emoji com ZWJ, sigma final, I turco e espaços Unicode. A paridade é exigida para caracteres atribuídos nas duas bases Unicode. Caracteres muito recentes, que um dos ambientes ainda não conhece, podem ter ordem NFD diferente. Nesse caso o Yesod detecta a divergência e devolve `BLOQUEADO`, e há teste para isso.

## Estrutura

```
public/               frontend estático (HTML, CSS e módulos ES, sem build)
  js/hexa-engine.js   porte fiel do hexa-engine.ts do HexaSign Lab
  js/pipeline.js      as dez etapas
  js/app.js           interface
api/verificar.py      função serverless da Vercel (POST /api/verificar)
api/_lib/
  hexa_engine.py      o mesmo engine em Python, para o recálculo independente
  yesod.py            indicadores, validação e execução da política
  politica_hubstree.guru
  gurudev/            interpretador GuruDev vendorizado (ver VENDOR.md)
tests/                paridade JS↔Python, vereditos e falha fechada
servidor.py           servidor único (estático + API) para Cloud Run e uso local
Dockerfile            imagem do serviço
scripts/dev.py        servidor local de desenvolvimento
```

## Rodar localmente

```bash
pip install -r requirements.txt pytest
python3 scripts/dev.py          # http://127.0.0.1:8000
npm test                        # testes JS (node --test) e Python (pytest)
```

## Deploy

### Cloud Run (recomendado)

O plano Hobby da Vercel é só para uso pessoal e não comercial. Como o Hubstree é apresentado como produto da Hubstry, o destino recomendado é o Cloud Run, do Google Cloud, que aceita uso comercial.

Um único serviço atende tudo: `servidor.py` serve o frontend de `public/` e o `POST /api/verificar`, com a mesma função da Vercel. A imagem (`Dockerfile`) usa Python 3.12, roda como usuário sem privilégios e já traz as tabelas do parser da GuruDev geradas. Com tráfego de demonstração e mínimo de zero instâncias, o custo tende a zero.

No Cloud Shell:

```bash
gcloud config get-value project   # confira o projeto ativo
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
git clone https://github.com/polyograph/Hubstree-MVP.git && cd Hubstree-MVP
gcloud run deploy hubstree --source . --region us-central1 --allow-unauthenticated \
  --memory 256Mi --cpu 1 --min-instances 0 --max-instances 2 --concurrency 20 --timeout 30
```

O último comando imprime a URL do serviço. Rotas úteis: `/` (interface), `/api/verificar` (Yesod) e `/saude` (verificação de funcionamento).

Para rodar o mesmo servidor localmente: `python3 servidor.py` (http://127.0.0.1:8000).

### Domínio: hubstree.hubstry.dev

O endereço público é https://hubstree.hubstry.dev. O DNS do hubstry.dev fica na Cloudflare. Um Worker da Cloudflare (`infra/cloudflare-worker-hubstree-proxy.js`) recebe as requisições e as repassa ao serviço do Cloud Run. O registro DNS é `AAAA hubstree → 100::`, com o proxy da Cloudflare ativo. Esse arranjo dispensa o mapeamento de domínio do Cloud Run e mantém o HTTPS e a proteção da Cloudflare. Se a URL de alguma origem mudar, atualize a lista `ORIGENS` no Worker.

### Redundância multicloud: Render

O mesmo `servidor.py` roda também no Render (plano free), em https://hubstree-mvp.onrender.com, como origem de redundância. O Worker tenta primeiro o Cloud Run, com limite de 10 segundos; se houver falha de rede, estouro do tempo ou resposta 5xx (erro do servidor), repete a mesma requisição, com o mesmo corpo, no Render. O cabeçalho de resposta `X-Hubstree-Origem` informa qual origem atendeu (`cloud-run` ou `render`). Se as duas falharem, o Worker devolve 503 com `Retry-After`.

Configuração do serviço no Render (runtime nativo, sem Docker):

- Build Command: `python3 -m pip install --target .pydeps -r requirements.txt`
- Start Command: `PYTHONPATH=.pydeps HOST=0.0.0.0 python3 servidor.py`
- Health Check Path: `/saude`

O plano free do Render desliga a instância após 15 minutos sem tráfego e leva cerca de um minuto para religá-la. Por isso o Worker espera até 70 segundos pelo Render. Os termos do Render não vedam uso comercial no plano free, mas o classificam como inadequado para produção; aqui ele é só contingência, não a origem principal.

### Vercel (legado)

`vercel.json` continua no repositório como referência: `public/` como estático e `api/verificar.py` como função Python. O projeto na Vercel está pausado, porque o plano Hobby não admite uso comercial.

## Licenças

O código do Hubstree segue a licença Apache 2.0 (`LICENSE`). O interpretador GuruDev em `api/_lib/gurudev/` segue a Business Source License 1.1 do seu autor (`api/_lib/gurudev/LICENSE`).

A BSL 1.1 da GuruDev libera uso acadêmico, educacional, pessoal e de avaliação não comercial. O uso comercial do Hubstree com a GuruDev depende de autorização expressa do licenciante, registrada por escrito.

Generated by Claude
