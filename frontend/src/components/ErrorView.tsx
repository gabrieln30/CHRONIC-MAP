"use client";
import Link from "next/link";
import { AuthShell } from "./AuthShell";

/** Tela de erro (PDF): algo inesperado, como falha de autenticacao ou acesso negado. */
export function ErrorView({ titulo, texto, onRetry }: { titulo: string; texto: string; onRetry?: () => void }) {
  return (
    <AuthShell title={titulo} subtitle={texto}>
      <div className="flex flex-col gap-3 border-l-4 border-danger pl-4">
        {onRetry && (
          <button onClick={onRetry} className="rounded-[var(--radius-control)] bg-primary px-5 py-2.5 font-medium text-primary-fg hover:brightness-110">Tentar novamente</button>
        )}
        <Link href="/login" className="rounded-[var(--radius-control)] border border-line px-5 py-2.5 text-center font-medium hover:border-muted hover:bg-surface-2">Ir para o login</Link>
        <Link href="/" className="text-sm text-muted underline-offset-4 hover:text-fg hover:underline">Voltar ao início</Link>
      </div>
    </AuthShell>
  );
}
