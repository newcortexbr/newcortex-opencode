# documentação do projeto

`core/` contém os contratos estáveis da V2. estes arquivos são canônicos e
devem permanecer curtos, rastreáveis e atualizados a cada rodada.

- `core/BACKLOG.md`: o que foi feito, está aberto, bloqueado ou descartado.
- `core/DECISIONS.md`: decisões, contexto, resposta e impacto.
- `core/LOGIC.md`: funcionamento básico e limites dos componentes.
- `core/CONTRACT.md`: contrato mínimo consolidado e provas ainda necessárias.
- `core/VAULT-ARCHITECTURE.md`: desenho do vault e validação do piloto.

`PROMPTS.md` é gerado, não escrito à mão: ele exporta os prompts vigentes a
partir da configuração resolvida pelo launcher. altere `v2/` e rode
`scripts/export-prompts.py`.

contexto de apoio e material temporário pertencem a `additive/`. o mapa completo
dos documentos está em `INDEX.md`.
