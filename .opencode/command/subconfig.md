---
description: configura o modelo e o effort de um subagente ou recarrega o catálogo
---

use exclusivamente a ferramenta `subconfig`.

se a ferramenta não estiver disponível, informe que este comando requer o
launcher V2 (`opencode-isolated`) e pare; não tente simular nem editar arquivos.

se o primeiro argumento for `reload`, chame a ferramenta com `agent: "reload"`.
caso contrário, chame-a com:

- `agent`: `$1`
- `model`: `$2`
- `effort`: `$3`

não use bash, read, edit ou outra ferramenta. mostre a resposta da ferramenta
sem alterar o pedido. a alteração só entra depois que o usuário reiniciar
o OpenCode.
