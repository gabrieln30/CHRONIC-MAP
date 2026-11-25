"use client";
import Link from "next/link";
import { HeroCanvas } from "./HeroCanvas";
import { Logo } from "./Logo";
import { cn } from "@/lib/cn";

const PASSOS = [
  { titulo: "Responda o questionário", texto: "Área, objetivo, nível e tempo disponível por semana." },
  { titulo: "Receba sua trilha", texto: "Etapas com exercícios e marcos, montadas pela IA para o seu caso." },
  { titulo: "Tire dúvidas com o tutor", texto: "Pergunte sobre a etapa em que você está." },
];

/**
 * Moldura das telas de acesso (login, 2FA, cadastro). Nas telas curtas, mostra ao lado o caminho
 * do produto em 3 passos (uma sequencia real, por isso numerada); no cadastro, so o formulario.
 */
export function AuthShell({
  title, subtitle, children, footer, wide,
}: { title: string; subtitle?: string; children: React.ReactNode; footer?: React.ReactNode; wide?: boolean }) {
  return (
    <div className="auth-scene isolate min-h-[100svh] overflow-hidden">
      <div className="auth-orbit" aria-hidden>
        <HeroCanvas className="h-full w-full" />
      </div>
      <div className="relative z-10 mx-auto max-w-5xl px-4 pb-16 pt-28 sm:px-8">
        <div className={wide ? "mx-auto max-w-3xl" : "grid items-start gap-16 lg:grid-cols-[1fr_26rem]"}>
          <div className="auth-panel rounded-[var(--radius-card)] border border-line bg-surface p-6 sm:p-8 lg:col-start-2 lg:row-start-1">
            <div className="flex items-center gap-3">
              <Logo className="h-9" />
              <div>
                <span className="font-display text-lg font-semibold">Chronic Map</span>
                <span className="auth-eyebrow">aprendizado conectado</span>
              </div>
            </div>
            <h1 className="mt-6 font-display text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h1>
            {subtitle && <p className="mt-2 text-muted">{subtitle}</p>}
            <div className="mt-6">{children}</div>
            {footer && <div className="mt-6 text-center text-sm text-muted">{footer}</div>}
          </div>

          {!wide && (
            <aside className="auth-story hidden lg:col-start-1 lg:row-start-1 lg:block lg:pt-4" aria-label="Como funciona">
              <p className="auth-eyebrow">uma rota por vez</p>
              <p className="mt-3 max-w-md font-display text-4xl font-semibold leading-tight tracking-tight">
                Seu plano de estudo, etapa por etapa.
              </p>
              <ol className="relative mt-12 max-w-md space-y-9 pl-12">
                <span aria-hidden className="absolute bottom-4 left-[15px] top-4 w-px bg-line" />
                {PASSOS.map((p, i) => (
                  <li key={p.titulo} className="relative">
                    <span
                      aria-hidden
                      className={cn(
                        "absolute -left-12 top-0 grid size-8 place-items-center rounded-full border-2 text-sm font-semibold",
                        i === 0 ? "border-marker bg-marker text-ink-950" : "border-line bg-bg text-muted",
                      )}
                    >
                      {i + 1}
                    </span>
                    <p className="font-display text-lg font-semibold">{p.titulo}</p>
                    <p className="mt-0.5 text-muted">{p.texto}</p>
                  </li>
                ))}
              </ol>
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}

export const AuthLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <Link href={href} className="font-medium text-primary underline-offset-4 hover:underline">
    {children}
  </Link>
);
