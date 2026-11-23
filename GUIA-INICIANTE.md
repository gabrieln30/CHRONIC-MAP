# Como rodar o Chronic Map (guia para iniciantes)

Este guia explica como abrir o projeto no seu computador Windows. Você não precisa saber programar para seguir os passos: copie os comandos exatamente como aparecem.

## O que você vai precisar

Antes de começar, instale estes dois programas:

1. **Python 3.12 ou mais recente**: https://www.python.org/downloads/
   - Durante a instalação, marque a opção **Add Python to PATH**.
2. **Node.js LTS**: https://nodejs.org/
   - Escolha a versão **LTS**, não a versão "Current".

Depois de instalar, feche e abra o PowerShell novamente.

## 1. Baixar ou abrir o projeto

Se o projeto já está na Área de Trabalho, abra a pasta:

`CHRONIC-MAP-main`

Se precisar baixar do GitHub:

1. Abra https://github.com/gabrieln30/CHRONIC-MAP.
2. Clique em **Code** e depois em **Download ZIP**.
3. Extraia o ZIP na Área de Trabalho.
4. Abra a pasta extraída chamada `CHRONIC-MAP-main`.

> Atenção: use a pasta que contém as pastas `app`, `frontend`, `php` e `scripts`.

## 2. Abrir o PowerShell na pasta do projeto

1. Abra a pasta do projeto no Explorador de Arquivos.
2. Clique na barra de endereço no topo da janela.
3. Digite `powershell` e pressione **Enter**.

Uma janela azul ou preta será aberta já apontando para a pasta correta.

## 3. Criar e configurar o arquivo `.env`

O arquivo `.env` guarda configurações privadas e não é enviado ao GitHub.

No PowerShell, execute:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Se o arquivo `.env` já existir, esse comando o preserva.

O Bloco de Notas abrirá. Preencha estas informações:

```env
DATABASE_URL=cole_aqui_a_url_do_banco_Supabase
GEMINI_API_KEY=cole_aqui_sua_chave_do_Gemini
GEMINI_MODEL=gemini-3.8-flash
SECRET_KEY=cole_uma_chave_longa_e_aleatoria_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000
```

Onde conseguir cada valor:

- `DATABASE_URL`: peça à pessoa/equipe responsável pelo banco Supabase do projeto. Sem ela, cadastro e login não funcionam.
- `GEMINI_API_KEY`: crie uma chave no Google AI Studio ou peça a chave de desenvolvimento da equipe. Sem ela, o site abre, mas não consegue gerar trilhas com IA.
- `SECRET_KEY`: no PowerShell, execute o comando abaixo, copie o resultado e cole depois de `SECRET_KEY=`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Salve o arquivo no Bloco de Notas com `Ctrl + S` e feche-o.

> Nunca envie o arquivo `.env`, a chave Gemini ou a senha do banco para o GitHub, WhatsApp ou e-mail.

## 4. Iniciar o projeto

No mesmo PowerShell, execute este único comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-project.ps1
```

Na primeira vez, ele pode demorar alguns minutos porque instala as bibliotecas necessárias. O script abre uma segunda janela para o back-end e mantém esta janela para o front-end. Não feche as duas enquanto estiver usando o projeto.

Quando aparecer que o servidor está pronto, abra no navegador:

http://localhost:3000

## 5. Confirmar que funcionou

No navegador:

1. Abra `http://localhost:3000`.
2. Faça um cadastro ou login.
3. Responda ao questionário e tente gerar uma trilha.

Para conferir apenas a API, abra:

http://localhost:8000/docs

Se essa página abrir, o back-end está funcionando.

## Como parar o projeto

Em cada janela do PowerShell que está rodando o projeto, pressione:

```text
Ctrl + C
```

Depois confirme com `S`, caso o PowerShell pergunte se deseja encerrar.

## Problemas comuns

### "python não é reconhecido"

O Python não foi instalado ou não foi adicionado ao PATH. Reinstale o Python e marque **Add Python to PATH**. Depois abra outro PowerShell.

### "npm não é reconhecido"

Instale o Node.js na versão LTS e abra outro PowerShell.

### A página abre, mas cadastro/login falha

Confira se o valor de `DATABASE_URL` no `.env` foi preenchido corretamente e se o banco Supabase está acessível.

### A trilha mostra erro de alta demanda

É uma indisponibilidade temporária do Gemini. Espere alguns minutos e clique em **Tentar de novo**. O sistema já tenta novamente automaticamente antes de mostrar o erro.

### Aparece "401 Unauthorized"

Saia da conta, feche a aba, abra o site novamente e faça login. O token de acesso expira após 30 minutos.

### A porta 3000 ou 8000 já está em uso

Feche outras janelas do projeto que possam estar abertas. Se não resolver, reinicie o computador e inicie o projeto outra vez.

## Nas próximas vezes

Depois que tudo estiver instalado e o `.env` configurado, basta abrir o PowerShell na pasta do projeto e executar novamente:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-project.ps1
```
