# MUDANCAS — Chronic Map (app/ corrigido)

Tudo que foi apontado na revisão foi corrigido. Os 22 testes em `tests/` passam
(`pytest tests/ -v`, usa SQLite e IA simulada, não precisa de MySQL nem de chave do Gemini).

## Como aplicar

1. Substitua a pasta `app/` do projeto pela deste zip e use o `requirements.txt` novo.
2. No `.env` (e no `.env.example`) garanta estas variáveis:

   | Variável | Obrigatória | Observação |
   |---|---|---|
   | `DATABASE_URL` | sim | `mysql+pymysql://usuario:senha@db:3306/NOME?charset=utf8mb4` |
   | `SECRET_KEY` | sim (>= 16 caracteres) | a API **não sobe** sem ela. Gerar: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
   | `GEMINI_API_KEY` | para usar a IA | só no servidor |
   | `GEMINI_MODEL` | não | padrão `gemini-3.8-flash`; troque se o Google renomear modelos |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | não | padrão 60 |
   | `CORS_ORIGINS` | não | padrão `http://localhost:8081` |

3. **Recrie o banco**: a tabela `diagnostico` ganhou a coluna `experiencia_previa` e `area_micro`
   ganhou uma restrição única, e o `create_all` não altera tabelas existentes. Em desenvolvimento:
   `docker-compose down -v && docker-compose up --build`.
   (Para não perder dados no futuro, use o Alembic, que já está no requirements.)
4. `bcrypt` está fixado em `4.0.1` de propósito: o `passlib` 1.7.4 quebra com bcrypt >= 4.1.

## Bloqueadores corrigidos

| Problema | Correção |
|---|---|
| Linha `cat > ... << 'EOF'` colada em `routers/assistente.py` (SyntaxError) | removida |
| `database.py`, `main.py`, `schemas.py`, `ia_service.py` vazios | escritos do zero |
| `assistente_service.py` ausente | criado |
| Faltavam `models/__init__.py` e `routers/__init__.py` | criados (o dos models importa os 7 models) |

## Bugs corrigidos

- **Exercício concluído não persistia** (lista JSON alterada "no lugar"): agora grava uma lista nova. Há teste lendo do banco em sessão separada.
- **Barra final** (`/areas/`, `/diagnostico/` com redirect 307): rotas agora são `/areas` e `/diagnostico`, como no README.
- **Enum no prompt da IA**: usa `.value` (`iniciante`, não `NivelConhecimento.iniciante`).
- **FK inexistente virava erro 500**: agora 404 (subárea) ou 422.
- **Resposta do Gemini sem validação**: validada com Pydantic (`TrilhaIA`, `RespostaAssistenteIA`) antes de salvar, com 1 nova tentativa se vier JSON quebrado. Links que não sejam http(s) são descartados.
- **`datetime.utcnow` deprecado**: trocado por `utcnow()` em `database.py`.
- **Conexão do banco presa durante a chamada à IA**: a transação é encerrada antes de chamar o Gemini.
- **404 em lista vazia de áreas**: agora devolve `[]`.
- **Pergunta 5 do questionário sem campo**: nova coluna `experiencia_previa` (opcional).
- **Horas como texto vs. Integer**: as opções agora trazem `valor` numérico (3, 8, 15, 25) e `campo` indicando qual campo de `DiagnosticoIn` preenchem.
- **`avancar_etapa` aceitava qualquer número**: valida de 0 até o nº de etapas (igual ao nº = concluída).
- **Corrida em cadastro/trilha duplicados**: `IntegrityError` vira 409.

## Segurança (RNF05/RNF06)

- Novo `routers/auth.py`: `POST /auth/cadastro`, `POST /auth/login`, `GET /auth/me` (JWT Bearer, senha em bcrypt, mesma resposta para e-mail inexistente e senha errada).
- Todas as rotas de diagnóstico, trilha, progresso e assistente exigem token e só enxergam dados **do próprio usuário** (dado de outro usuário responde 404; histórico de outro responde 403).
- O `usuario_id` **não vem mais do cliente**: sai do token.
- Erros da IA respondem 502 com mensagem genérica; o detalhe vai só para o log.
- Entrada do usuário vai para o prompt como dado delimitado (mitiga prompt injection).
- CORS restrito às origens do `CORS_ORIGINS`.

## Novos arquivos

`security.py` (bcrypt/JWT), `deps.py` (usuário logado e checagem de dono), `seed.py` (áreas TI, Saúde,
Administração e Engenharia com subáreas, criadas na primeira subida se a tabela estiver vazia),
`services/assistente_service.py`, `tests/test_api.py`, `GET /health`.

## O que muda para o front PHP

| Antes / README | Agora |
|---|---|
| sem autenticação | enviar `Authorization: Bearer <token>` (token vem de `POST /auth/login`) |
| `usuario_id` no corpo | removido (vem do token) |
| `POST /trilha/gerar?diagnostico_id=N` | corpo JSON `{"diagnostico_id": N}` |
| `POST /progresso/{trilha_id}` | **removido**: o progresso (etapa 0) é criado junto com a trilha |
| `PATCH /progresso/{id}/exercicio` com `exercicio_id` | corpo `{"etapa": 0, "indice": 1}`; `exercicios_concluidos` vira lista de `"etapa-indice"` (ex.: `"0-1"`) |
| `POST /assistente/perguntar` | corpo `{"trilha_id": N, "pergunta": "..."}` |
| `GET /diagnostico/perguntas` com `opcoes` em texto | `opcoes` = `[{"valor", "rotulo"}]` e cada pergunta traz `campo`, `numero`, `total` |
| — | novos: `GET /diagnostico` (lista os meus), `GET /diagnostico/{id}`, `DELETE /trilha/{id}`, `GET /assistente/historico/{usuario_id}?trilha_id=&limite=&deslocamento=` |

Lembre de atualizar o README (endpoints novos, `auth.py`, `security.py`, `deps.py`, `seed.py`, coluna
`experiencia_previa` no MER) e de trocar o login/cadastro por `localStorage` do PHP pelas chamadas `/auth/*`.

## Pontos para você decidir

- `DELETE /trilha/{id}` apaga também o progresso e o histórico de dúvidas **daquela trilha** (o diagnóstico fica, e dá para gerar outra trilha dele).
- O pacote `google-generativeai` foi mantido por estar no seu README, mas o Google passou a tratá-lo como legado em favor do SDK `google-genai`. Funciona, só vale planejar a troca (a chamada está isolada em `ia_service._gerar_texto`).
- Os testes não conectam no MySQL real nem no Gemini real: valide o primeiro `docker-compose up` e uma geração de trilha de verdade com a sua chave.
