# Rodar sem Docker

O banco agora é o PostgreSQL do Supabase; não há MySQL local, phpMyAdmin nem containers para iniciar.

## Preparação

1. Instale Python 3.12+ e Node.js LTS (o Node inclui `npm`).
2. Confirme que o arquivo `.env` existe na raiz e contém `DATABASE_URL`, `GEMINI_API_KEY` e uma `SECRET_KEY` longa. Use `.env.example` somente como modelo.
3. Em dois terminais PowerShell, na raiz do projeto, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-backend.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\start-frontend.ps1
```

4. Abra http://localhost:3000. A documentação da API fica em http://localhost:8000/docs.

O Next.js encaminha chamadas de `/api/*` para o FastAPI local, portanto o navegador não precisa conhecer credenciais do Supabase ou do Gemini.
