# README — Como o Sistema Funciona (Arquivo por Arquivo)


6. Como o grupo roda depois

powershell
git clone -b Chronic-Map-FULL-Front https://github.com/gabrieln30/CHRONIC-MAP.git
cd CHRONIC-MAP
Copy-Item .env.example .env

Depois preenchem a GEMINI_API_KEY e a SECRET_KEY no .env e rodam docker compose up --build.

Se aparecer qualquer erro em algum passo, cole a mensagem aqui.


Este documento explica o papel de cada arquivo e pasta do projeto **Chronic Map**, como eles se comunicam entre si e qual membro da equipe é responsável por cada parte.

---

## Visão Geral do Fluxo

```
Usuário
  │
  ▼
php/ (site PHP — porta 8081)
  │  consome via HTTP
  ▼
app/ (API FastAPI — porta 8000)
  │  lê e escreve
  ▼
MySQL (banco de dados — porta 3306)
  │
  ▼
phpMyAdmin (administração — porta 8080)

app/ também chama:
  ├──▶ Gemini API (geração da trilha personalizada)
  └──▶ Gemini API (assistente de dúvidas com contexto do usuário)
```

---

## Estrutura Completa de Arquivos

```
chronic_map/
├── app/                              # API principal (FastAPI)
│   ├── __init__.py
│   ├── main.py                       # Ponto de entrada da API
│   ├── database.py                   # Conexão com MySQL
│   ├── schemas.py                    # Schemas Pydantic (validação de dados)
│   ├── models/                       # Tabelas do banco (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── area_macro.py
│   │   ├── area_micro.py
│   │   ├── diagnostico.py
│   │   ├── trilha.py
│   │   ├── progresso.py
│   │   └── duvida.py
│   ├── routers/                      # Rotas da API (endpoints)
│   │   ├── __init__.py
│   │   ├── areas.py
│   │   ├── diagnostico.py
│   │   ├── trilha.py
│   │   ├── progresso.py
│   │   └── assistente.py
│   └── services/                     # Lógica de negócio / integrações externas
│       ├── __init__.py
│       ├── ia_service.py
│       └── assistente_service.py
├── php/                              # Front-end (PHP)
│   ├── index.php                     # Página inicial / landing
│   ├── login.php                     # Tela de login com validação e toast
│   ├── cadastro.php                  # Cadastro de novo usuário
│   ├── 2fa.php                       # Verificação em duas etapas (segurança)
│   ├── dashboard.php                 # Painel principal com os produtos de IA
│   ├── chat.php                      # Assistente de dúvidas com IA (Tutor IA)
│   ├── mapas.php                     # Mapas mentais do plano de aprendizado
│   ├── progresso.php                 # Acompanhamento de evolução e trilha
│   ├── api_trilhas.php               # API PHP interna (listagem e simulação de trilhas)
│   ├── menu.php                      # Navbar reutilizável (incluída em todas as páginas)
│   ├── style.css                     # Estilo global do Chronic Map
│   └── acessibilidade.js             # Tema escuro, tamanho de fonte, perfil, logout
├── Dockerfile                        # Imagem Docker da API FastAPI
├── docker-compose.yml                # Orquestração de todos os serviços
├── requirements.txt                  # Dependências Python
├── .env                              # Variáveis de ambiente (não versionar)
├── .env.example                      # Modelo de variáveis (versionar)
└── .gitignore                        # Arquivos ignorados pelo Git
```

---

## Arquivo por Arquivo

---

### `docker-compose.yml`
**Responsável:** Jota e Nunes

Orquestra os 4 serviços do projeto em containers Docker:

| Serviço | Imagem | Porta | Função |
|---|---|---|---|
| `db` | mysql:8.0 | 3306 | Banco de dados MySQL |
| `phpmyadmin` | phpmyadmin:latest | 8080 | Interface visual do banco |
| `api` | (Dockerfile local) | 8000 | API FastAPI |
| `php` | php:8.2-apache | 8081 | Front-end PHP |

Todos os serviços compartilham a mesma rede interna (`trilha_net`), permitindo que se comuniquem pelo nome do container (ex.: a API acessa o banco pelo host `db`, não por `localhost`).

---

### `Dockerfile`
**Responsável:** Jota e Nunes

Define como a imagem da API FastAPI é construída:
1. Parte de uma imagem Python 3.11
2. Instala as dependências do `requirements.txt`
3. Copia a pasta `app/` para dentro do container
4. Sobe o servidor com `uvicorn` na porta 8000

---

### `.env` e `.env.example`
**Responsável:** Jota e Nunes (criam e documentam); toda a equipe (preenche localmente)

Guardam as variáveis de ambiente sensíveis:
- Credenciais do MySQL (`MYSQL_USER`, `MYSQL_PASSWORD`, etc.)
- URL de conexão do banco (`DATABASE_URL`) usada pelo SQLAlchemy
- Chave da Gemini API (`GEMINI_API_KEY`) usada pelo `ia_service.py` e pelo `assistente_service.py`
- Chave JWT (`SECRET_KEY`) para autenticação

O `.env` **nunca vai pro Git** (está no `.gitignore`). O `.env.example` é o modelo que cada membro copia e preenche localmente.

---

### `requirements.txt`
**Responsável:** Jota e Nunes

Lista todas as bibliotecas Python do projeto:

| Biblioteca | Para quê serve |
|---|---|
| `fastapi` | Framework da API |
| `uvicorn` | Servidor ASGI que roda o FastAPI |
| `sqlalchemy` | ORM — mapeia classes Python para tabelas MySQL |
| `pymysql` | Driver de conexão Python → MySQL |
| `alembic` | Gerencia migrations do banco |
| `pydantic` | Validação de dados (vem integrado ao FastAPI) |
| `pydantic-settings` | Leitura de variáveis do `.env` |
| `python-dotenv` | Carrega o `.env` no ambiente |
| `google-generativeai` | SDK oficial da Gemini API |
| `python-jose` | Geração e validação de tokens JWT |
| `passlib[bcrypt]` | Hash seguro de senhas |

---

### `app/main.py`
**Responsável:** Jota e Nunes

Ponto de entrada da API. É o arquivo que o `uvicorn` executa. Faz três coisas:
1. Cria a instância do FastAPI
2. Registra todos os routers (areas, diagnostico, trilha, progresso, assistente)
3. Cria as tabelas no banco na inicialização (via SQLAlchemy)

---

### `app/database.py`
**Responsável:** Jota e Nunes

Configura a conexão com o MySQL usando SQLAlchemy:
- Lê a `DATABASE_URL` do `.env`
- Cria o `engine` (motor de conexão)
- Cria o `SessionLocal` (sessão usada em cada requisição)
- Expõe o `Base` que todos os models herdam

---

### `app/schemas.py`
**Responsável:** cada dupla/pessoa adiciona os seus schemas

Define os schemas Pydantic — estruturas que validam os dados que entram e saem da API:

| Schema | Responsável |
|---|---|
| `AreaMacroOut` | Jota e Nunes |
| `DiagnosticoIn` | JV e Kauã |
| `TrilhaOut` | Dozza |
| `DuvidaIn` / `DuvidaOut` | Dozza |

---

### `app/models/`
**Responsável:** Jota e Nunes (estrutura base); demais ajustam conforme necessidade

| Arquivo | Tabela | Responsável |
|---|---|---|
| `usuario.py` | `usuario` | Jota e Nunes |
| `area_macro.py` | `area_macro` | Jota e Nunes |
| `area_micro.py` | `area_micro` | Jota e Nunes |
| `diagnostico.py` | `diagnostico` | JV e Kauã |
| `trilha.py` | `trilha` | Dozza |
| `progresso.py` | `progresso` | JV e Kauã |
| `duvida.py` | `duvida` | Dozza |

---

### `app/routers/`

#### `areas.py` — Jota e Nunes
- `GET /areas` — retorna todas as áreas macro
- `GET /areas/{id}/subareas` — retorna as subáreas de uma área macro

#### `diagnostico.py` — JV e Kauã
- `GET /diagnostico/perguntas` — retorna as perguntas do questionário
- `POST /diagnostico` — recebe e salva as respostas do usuário

#### `trilha.py` — Dozza
- `POST /trilha/gerar` — recebe o ID do diagnóstico, chama a IA e salva a trilha
- `GET /trilha/{id}` — retorna uma trilha salva

#### `progresso.py` — JV e Kauã
- `GET /progresso/{trilha_id}` — retorna o progresso atual do usuário
- `PATCH /progresso/{trilha_id}/etapa` — marca uma etapa como concluída
- `PATCH /progresso/{trilha_id}/exercicio` — marca um exercício como feito

#### `assistente.py` — Dozza
- `POST /assistente/perguntar` — recebe a dúvida, consulta contexto e retorna resposta da IA com materiais sugeridos
- `GET /assistente/historico/{usuario_id}` — retorna o histórico de perguntas e respostas

---

### `app/services/ia_service.py`
**Responsável:** Dozza

Integração com Gemini API para geração da trilha. Monta o prompt com base no diagnóstico, envia ao Gemini Pro e faz o parsing do JSON retornado.

Formato esperado da trilha (JSON):
```json
{
  "etapas": [
    {
      "titulo": "Nome da etapa",
      "descricao": "O que o usuário vai aprender",
      "exercicios": ["exercício 1", "exercício 2"],
      "marco": "O que indica que essa etapa foi concluída"
    }
  ]
}
```

---

### `app/services/assistente_service.py`
**Responsável:** Dozza

Lógica do assistente de dúvidas. Recebe a pergunta com o contexto completo do usuário (área, nível, etapa atual), monta prompt contextualizado, chama o Gemini Pro e salva a resposta no banco.

Formato esperado da resposta (JSON):
```json
{
  "diagnostico": "Explicação do que está causando a dificuldade",
  "plano_de_melhoria": ["passo 1", "passo 2", "passo 3"],
  "materiais": [
    {
      "tipo": "curso",
      "plataforma": "Udemy / Coursera / DIO / Alura / YouTube",
      "titulo": "Nome do curso ou vídeo sugerido",
      "url": "link se disponível"
    }
  ],
  "exemplo_pratico": "Exemplo direto relacionado à dificuldade relatada"
}
```

---

## Front-end PHP (Arquivo por Arquivo)

**Responsável geral:** JV e Kauã

---

### `menu.php`
Navbar reutilizável incluída em todas as páginas via `<?php include 'menu.php'; ?>`. Contém:
- Logo e links de navegação (Início, Tutor IA, Mapas, Progresso)
- Dropdown de acessibilidade (tema escuro, tamanho de fonte)
- Dropdown de perfil do usuário (dados, trilha ativa, segurança, logout)
- Modal de perfil completo com 3 abas: Dados Cadastrais, Trilha Ativa e Segurança & 2FA

---

### `style.css`
Arquivo de estilos global do Chronic Map. Define:
- Paleta de cores e tipografia do projeto
- Estilos do navbar, dropdowns e cards
- Suporte ao tema escuro (classe `.tema-escuro` aplicada no `<html>`)
- Layout responsivo para mobile e desktop

---

### `acessibilidade.js`
Script carregado em todas as páginas. Centraliza toda a interatividade do front-end:
- Alternância de tema claro/escuro (salvo no `localStorage`)
- Controle de tamanho de fonte (A+ / A-)
- Dropdown de acessibilidade e de perfil (abrir/fechar com teclado e clique fora)
- Preenchimento dinâmico dos dados do usuário no menu (nome, email, CEP, data de nascimento)
- Função de logout (limpa `sessionStorage` e `localStorage`)
- Animação de scroll reveal nos elementos com classe `.reveal-on-scroll`

---

### `index.php`
Página inicial / landing page do Chronic Map. Apresenta o sistema ao visitante e direciona para login ou cadastro.

---

### `login.php`
Tela de login do usuário. Funcionalidades:
- Formulário com e-mail e senha
- Botão de mostrar/ocultar senha
- Validação no front-end com toast de feedback (Bootstrap Toast)
- Após login bem-sucedido, redireciona para `2fa.php` (verificação em duas etapas)
- Dados comparados com o `localStorage` (temporário até integração com a API)

---

### `cadastro.php`
Tela de cadastro de novo usuário. Coleta nome, e-mail, senha e dados para o 2FA (nome materno, data de nascimento, CEP). Salva temporariamente no `localStorage` até integração com o banco via API.

---

### `2fa.php`
Verificação em duas etapas após o login. Funcionalidades:
- Sorteia aleatoriamente uma das 3 perguntas de segurança (nome da mãe, data de nascimento, CEP)
- Compara a resposta com os dados salvos no `sessionStorage`
- Limita a 3 tentativas — após isso, redireciona para `login.php`
- Após verificação bem-sucedida, redireciona para `dashboard.php`

---

### `dashboard.php`
Painel principal do usuário após o login. Exibe os 3 produtos principais do Chronic Map em cards:
- **Tutor IA** → `chat.php`
- **Mapas Mentais** → `mapas.php`
- **Atividades e Progresso** → `progresso.php`

---

### `chat.php`
Tela do Assistente de Dúvidas (Tutor IA). Funcionalidades:
- Interface de chat com bolhas de mensagem (usuário e IA)
- Histórico de conversa salvo no `localStorage`
- Carrega o histórico automaticamente ao abrir a página
- Resposta da IA atualmente mockada — será substituída pela chamada ao endpoint `POST /assistente/perguntar` da API FastAPI quando o back-end estiver pronto

---

### `mapas.php`
Tela de Mapas Mentais do plano de aprendizado. Funcionalidades:
- Exibe cards com os mapas mentais do usuário
- Botão "Novo Mapa" cria um card dinamicamente via `prompt()` (temporário)
- Será integrado com a trilha gerada pela IA (etapas viram nós do mapa)

---

### `progresso.php`
Tela de acompanhamento de evolução. Exibe:
- Total de mensagens trocadas com a IA (lido do `localStorage`)
- Módulos concluídos (fixo por enquanto — será integrado com `GET /progresso/{trilha_id}`)
- Nível atual e barra de progresso da trilha

---

### `api_trilhas.php`
API PHP interna do Chronic Map. Retorna dados de trilhas em JSON. Suporta dois modos via `?acao=`:
- `listar` — lista as trilhas disponíveis com filtro por área e busca por texto
- `simular` — calcula o tempo estimado para concluir uma trilha com base nas horas semanais e nível do usuário

Contém 8 trilhas pré-cadastradas nas áreas: TI, Saúde, Administração e Engenharia.

> **Nota:** este arquivo é uma API auxiliar do front-end PHP, separada da API principal FastAPI. Será substituído gradualmente pelos endpoints do back-end Python conforme a integração avança.

---

## Como os Serviços se Comunicam

```
php/login.php + cadastro.php + 2fa.php  [JV e Kauã]
  └──▶ Autenticação via localStorage/sessionStorage (temporário)
         └──▶ Futuramente: POST /auth/login e POST /auth/cadastro (API FastAPI)

php/dashboard.php  [JV e Kauã]
  └──▶ Exibe os produtos — sem chamada de API por enquanto

php/chat.php  [JV e Kauã — front | Dozza — back]
  └──▶ POST http://api:8000/assistente/perguntar
         └──▶ app/routers/assistente.py
                └──▶ app/services/assistente_service.py
                       └──▶ Gemini API
                └──▶ app/models/duvida.py (salva no MySQL)

php/progresso.php  [JV e Kauã]
  └──▶ GET http://api:8000/progresso/{trilha_id}
         └──▶ app/routers/progresso.py
                └──▶ app/models/progresso.py (lê do MySQL)

php/mapas.php  [JV e Kauã]
  └──▶ GET http://api:8000/trilha/{id}
         └──▶ app/routers/trilha.py  [Dozza]
                └──▶ app/models/trilha.py (lê do MySQL)

php/api_trilhas.php  [JV e Kauã]
  └──▶ API PHP auxiliar (dados pré-cadastrados em array PHP)
         └──▶ Será substituída pelos endpoints FastAPI conforme integração avança
```

---

## Como Rodar o Projeto

1. Clone o repositório
2. Copie o `.env.example` para `.env` e preencha as variáveis
3. Execute:
   ```bash
   docker-compose up --build
   ```
4. Acesse:
   - Site PHP (Chronic Map): http://localhost:8081
   - API FastAPI: http://localhost:8000
   - Documentação automática da API: http://localhost:8000/docs
   - phpMyAdmin: http://localhost:8080

---

## Resumo de Responsabilidades

| Membro | Arquivos principais |
|---|---|
| Jota e Nunes | `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `.env.example`, `app/main.py`, `app/database.py`, `app/models/usuario.py`, `app/models/area_macro.py`, `app/models/area_micro.py`, `app/routers/areas.py` |
| JV e Kauã | `app/routers/diagnostico.py`, `app/routers/progresso.py`, `app/models/diagnostico.py`, `app/models/progresso.py`, todos os arquivos da pasta `php/` |
| Dozza | `app/routers/trilha.py`, `app/routers/assistente.py`, `app/services/ia_service.py`, `app/services/assistente_service.py`, `app/models/trilha.py`, `app/models/duvida.py` |

---

## MER — Modelo Entidade-Relacionamento

### Entidades e Atributos

**Usuario**
- id (PK)
- nome
- email
- senha_hash
- criado_em

**AreaMacro**
- id (PK)
- nome

**AreaMicro**
- id (PK)
- nome
- area_macro_id (FK → AreaMacro)

**Diagnostico**
- id (PK)
- usuario_id (FK → Usuario)
- area_micro_id (FK → AreaMicro)
- nivel_conhecimento
- tempo_semanal_horas
- objetivo
- estilo_aprendizado
- criado_em

**Trilha**
- id (PK)
- diagnostico_id (FK → Diagnostico)
- conteudo_json
- criado_em

**Progresso**
- id (PK)
- trilha_id (FK → Trilha)
- usuario_id (FK → Usuario)
- etapa_atual
- exercicios_concluidos (JSON)
- atualizado_em

**Duvida**
- id (PK)
- usuario_id (FK → Usuario)
- trilha_id (FK → Trilha)
- etapa_referencia
- pergunta
- resposta_json
- criado_em

### Relacionamentos

- Um **Usuario** pode ter vários **Diagnosticos**
- Uma **AreaMacro** possui várias **AreasMicro**
- Uma **AreaMicro** pertence a uma **AreaMacro**
- Um **Diagnostico** pertence a um **Usuario** e a uma **AreaMicro**
- Um **Diagnostico** gera uma **Trilha**
- Uma **Trilha** possui um **Progresso** por **Usuario**
- Um **Usuario** pode ter várias **Duvidas**, cada uma vinculada a uma **Trilha** e etapa

---

## DER — Diagrama Entidade-Relacionamento

```
+----------------+          +----------------+
|    Usuario     |          |   AreaMacro    |
+----------------+          +----------------+
| PK id          |          | PK id          |
|    nome        |          |    nome        |
|    email       |          +-------+--------+
|    senha_hash  |                  | 1
|    criado_em   |                  |
+---+--------+---+                  | N
    |        |            +---------+--------+
    | 1      | 1          |    AreaMicro     |
    |        |            +------------------+
    | N      | N          | PK id            |
    |        |            |    nome          |
+---+------+ +-----+      | FK area_macro_id |
|Diagnostico| |Duvida|    +--------+---------+
+-----------+ +------+             | 1
| PK id     | | PK id|             |
| FK usuario| | FK   |             | N
| FK area   | | usuario            |
| nivel     | | FK   |    +--------+---------+
| tempo     | | trilha|   |   Diagnostico    |
| objetivo  | | etapa |   +------------------+
| estilo    | | pergunta  | PK id            |
| criado_em | | resposta  | FK usuario_id    |
+-----------+ | criado_em || FK area_micro_id |
    | 1       +------+---+ |    nivel         |
    |                |     |    tempo         |
    | 1              |     |    objetivo      |
    |                |     |    estilo        |
+---+--------+       |     |    criado_em     |
|   Trilha   |       |     +--------+---------+
+------------+       |              | 1
| PK id      +-------+              |
| FK diagn.  |    N                 | 1
| conteudo   |              +-------+------+
| criado_em  |              |    Trilha    |
+-----+------+              +--------------+
      | 1                   | PK id        |
      |                     | FK diagn_id  |
      | 1                   | conteudo_json|
      |                     | criado_em    |
+-----+---------+           +--------------+
|   Progresso   |
+---------------+
| PK id         |
| FK trilha_id  |
| FK usuario_id |
| etapa_atual   |
| exercicios    |
| atualizado_em |
+---------------+
```

### Cardinalidades

| Entidade A | Relacionamento | Entidade B |
|---|---|---|
| AreaMacro | 1:N | AreaMicro |
| Usuario | 1:N | Diagnostico |
| AreaMicro | 1:N | Diagnostico |
| Diagnostico | 1:1 | Trilha |
| Trilha | 1:1 | Progresso |
| Usuario | 1:N | Duvida |
| Trilha | 1:N | Duvida |

---

## Requisitos Funcionais

| # | Requisito |
|---|---|
| RF01 | O usuário pode escolher uma área geral (ex.: TI, Saúde, Administração, Engenharia). |
| RF02 | O sistema mostra os subsetores dessa área para o usuário escolher. |
| RF03 | O usuário pode voltar e mudar a área ou o subsetor escolhido. |
| RF04 | O sistema faz perguntas para entender o nível de conhecimento, o tempo disponível por semana, o objetivo e o estilo de aprendizado do usuário. |
| RF05 | O sistema muda as próximas perguntas dependendo das respostas anteriores. |
| RF06 | O sistema mostra em que pergunta o usuário está (ex.: "pergunta 2 de 5"). |
| RF07 | O sistema gera, com IA, uma trilha de estudo personalizada em passos. |
| RF08 | O sistema gera exercícios práticos com nível de dificuldade. |
| RF09 | O sistema gera um plano para o usuário acompanhar sua evolução. |
| RF10 | O sistema mostra um resumo da trilha gerada. |
| RF11 | O usuário pode refazer o diagnóstico e gerar uma nova trilha. |

---

## Requisitos Não Funcionais

| # | Requisito |
|---|---|
| RNF01 | A trilha deve ser gerada rapidamente, com uma indicação visual de carregamento. |
| RNF02 | A interface deve ser responsiva. |
| RNF03 | Deve ficar claro em qual etapa o usuário está, com opção de voltar. |
| RNF04 | Se a IA falhar ou ficar indisponível, o sistema não deve quebrar — deve permitir tentar de novo. |
| RNF05 | Os dados pessoais e respostas do diagnóstico devem ser guardados com segurança. |
| RNF06 | As chaves de acesso à IA não podem ficar visíveis no código do lado do usuário. |
| RNF07 | O sistema deve seguir a LGPD na coleta e uso de dados pessoais. |
| RNF08 | O sistema deve ser organizado em partes separadas (diagnóstico, geração da trilha, tela), facilitando manutenção. |
| RNF09 | O sistema deve funcionar nos principais navegadores (Chrome, Firefox, Edge, Safari). |

---

## Status atual

🚧 Em desenvolvimento ativo — Front-end PHP concluído, back-end FastAPI e integração com IA em andamento.
