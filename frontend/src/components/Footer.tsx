"use client";
import Link from "next/link";
import { Logo } from "./Logo";
import { useSession } from "@/lib/auth";

/** Rodape das paginas publicas (home e blog). Sem cartoes: so um filete no topo e outro antes do aviso legal. */
export function Footer() {
  const { user } = useSession(); // logado: troca "Entrar/Criar conta" por atalhos da conta
  const link = "text-muted underline-offset-4 hover:text-fg hover:underline";
  return (
    <footer className="border-t border-line px-4 py-12 sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 sm:flex-row sm:justify-between">
        <div className="max-w-xs">
          <Link href="/" className="flex items-center gap-3">
            <Logo className="h-8" />
            <span className="font-display text-lg font-semibold">Chronic Map</span>
          </Link>
          <p className="mt-3 text-sm text-muted">Trilhas de estudo personalizadas, do seu jeito e no seu ritmo.</p>
        </div>
        <nav aria-label="Rodapé" className="grid grid-cols-2 gap-x-12 gap-y-2.5 text-sm">
          <Link href="/#como-funciona" className={link}>Como funciona</Link>
          <Link href="/blog" className={link}>Blog</Link>
          <Link href="/#perguntas" className={link}>Perguntas frequentes</Link>
          {user ? (
            <>
              <Link href="/trilha" className={link}>Minha trilha</Link>
              <Link href="/perfil" className={link}>Meu perfil</Link>
            </>
          ) : (
            <>
              <Link href="/login" className={link}>Entrar</Link>
              <Link href="/cadastro" className={link}>Criar conta</Link>
            </>
          )}
        </nav>
      </div>
      <p className="mx-auto mt-10 max-w-6xl border-t border-line pt-6 text-xs text-muted">
        Projeto acadêmico UNISUAM. Tratamos seus dados conforme a LGPD (Lei 13.709/2018).
      </p>
    </footer>
  );
}
