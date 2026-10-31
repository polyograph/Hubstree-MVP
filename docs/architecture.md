# Arquitetura do Hubstree v2

## Fluxo

```
Navegador                                         Vercel (Python)
─────────                                         ───────────────
Keter → Chokhmah → Binah → Tiferet ──┐
                                     │  POST /api/verificar {texto, vetor}
Gevurah → Chesed → Netzach ──────────┼──────────────▶ hexa_engine.analisar(texto)
                                     │                 indicadores tipados (bool/int)
                                     │                 política GuruDev (.guru)
Yesod ◀──────────────────────────────┘◀────────────── {veredito, motivo, indicadores}
Hod → Malkuth (relatório e JSON)
```

## Decisões

1. **Dois engines idênticos, de propósito.** O vetor é calculado no navegador (JS) e de novo no servidor (Python). O Yesod compara os dois com tolerância de 1e-9. Divergência bloqueia. Os testes garantem a paridade, inclusive com acentos, cedilha, grego e ideogramas.
2. **Regras na linguagem, não no código.** Os limiares (20 palavras, 2 sentenças, saturação) ficam na política GuruDev. Mudar uma regra é editar um arquivo `.guru` versionado.
3. **Falha fechada.** Indicador ausente, extra ou de tipo errado, erro do interpretador, veredito desconhecido ou servidor indisponível resultam em `BLOQUEADO`.
4. **Sem execução de entrada.** O texto do usuário só é lido como dado. O parser da GuruDev processa apenas a política do repositório.
5. **Sem build.** O frontend usa módulos ES nativos. Isso reduz a superfície de dependências no plano Hobby da Vercel.

## Origem dos componentes

| Componente | Origem |
|---|---|
| `public/js/hexa-engine.js`, `api/_lib/hexa_engine.py` | `guilherme-machado-ceo/hubstry-hexasign-lab`, `src/lib/hexa-engine.ts` |
| Leitura do perfil (Tiferet) | Princípios de `src/lib/profile-reading.ts` (MS-01): só comparações intra-vetor e limiares declarados |
| `api/_lib/gurudev/` | `Hubstry-DeepTech/gurudev-core`, `src/` (commit fixado em `api/_lib/gurudev/VENDOR.md`) |
| Desenho do Yesod | `gurudev-core/evidence_gate` (`politica.py`, `politica.guru`) |
