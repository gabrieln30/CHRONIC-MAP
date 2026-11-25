"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, BookOpen, Bot, Map as MapIcon, Wand2, type LucideIcon } from "lucide-react";
import { AppPage } from "@/components/AppPage";
import { Button } from "@/components/ui";
import { trilhaAtiva, useSession } from "@/lib/auth";

/** Painel do usuario: uma chamada principal (onde continuar) e a lista dos demais caminhos. */
const ATALHOS: { href: string; icon: LucideIcon; titulo: string; texto: string }[] = [
  { href: "/diagnostico", icon: Wand2, titulo: "Nova trilha", texto: "Responda o questionário e deixe a IA montar seu plano de estudo." },
  { href: "/trilha", icon: MapIcon, titulo: "Minha trilha", texto: "Veja o mapa das etapas, marque exercícios e acompanhe sua evolução." },
  { href: "/tutor", icon: Bot, titulo: "Tutor", texto: "Tire dúvidas sobre a etapa em que você está, direto no chat." },
  { href: "/blog", icon: BookOpen, titulo: "Dicas de estudo", texto: "Artigos curtos para estudar melhor e manter a constância." },
];

export default function DashboardPage() {
  const { user } = useSession();
  // undefined = ainda checando (evita piscar o aviso); null = sem trilha ativa
  const [trilha, setTrilha] = useState<number | null | undefined>(undefined);
  useEffect(() => { if (user) setTrilha(trilhaAtiva.get(user.id)); }, [user]);

  const semTrilha = trilha === null;

  return (
    <AppPage title={`Olá, ${user?.nome.split(" ")[0] ?? ""}`} subtitle="O que você quer fazer agora?" wide titleClassName="font-sans tracking-normal">
      {trilha !== undefined && (
        <section className="mb-12 flex flex-col gap-5 border-l-4 border-marker bg-surface-2 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-sans text-xl font-semibold tracking-tight">
              {semTrilha ? "Comece pelo questionário" : "Continue de onde parou"}
            </h2>
            <p className="mt-1 max-w-xl text-muted">
              {semTrilha
                ? "Conte qual área quer estudar, seu objetivo, seu nível e o tempo que tem. Com isso a IA monta a sua primeira trilha."
                : "Abra a sua trilha para ver a etapa atual, marcar exercícios e acompanhar o progresso."}
            </p>
          </div>
          <Link href={semTrilha ? "/diagnostico" : "/trilha"} className="shrink-0">
            <Button>
              {semTrilha
                ? <><Wand2 className="size-4" aria-hidden /> Responder agora</>
                : <>Abrir minha trilha <ArrowRight className="size-4" aria-hidden /></>}
            </Button>
          </Link>
        </section>
      )}

      <ul className="divide-y divide-line border-y border-line">
        {ATALHOS.map(({ href, icon: Icon, titulo, texto }) => (
          <li key={href}>
            <Link href={href} className="group flex items-center gap-5 px-1 py-5 transition-colors hover:bg-surface-2 sm:px-3">
              <Icon className="size-5 shrink-0 text-primary" aria-hidden />
              <span className="min-w-0 flex-1">
                <span className="block font-sans text-lg font-semibold tracking-tight">{titulo}</span>
                <span className="block text-muted">{texto}</span>
              </span>
              <ArrowRight className="size-5 shrink-0 text-muted transition-transform group-hover:translate-x-1" aria-hidden />
            </Link>
          </li>
        ))}
      </ul>
    </AppPage>
  );
}
