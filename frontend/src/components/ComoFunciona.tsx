import { Bot, ClipboardList, Map as MapIcon, type LucideIcon } from "lucide-react";

/**
 * Tela principal: como o Chronic Map funciona. Deixa clara a ordem do fluxo e onde entram
 * as DUAS IAs: a construtora de trilhas (passo 2) e o tutor em chat (passo 3).
 * Os passos sao uma sequencia real, por isso ficam numerados e ligados por uma linha.
 */
const PASSOS: { icon: LucideIcon; titulo: string; texto: string }[] = [
  {
    icon: ClipboardList,
    titulo: "Faça o diagnóstico",
    texto: "Escolha a área e responda poucas perguntas sobre seu nível, tempo semanal e objetivo.",
  },
  {
    icon: MapIcon,
    titulo: "Receba sua trilha",
    texto: "A IA construtora monta um plano em etapas, com exercícios e marcos para você acompanhar.",
  },
  {
    icon: Bot,
    titulo: "Estude com um tutor",
    texto: "Travou em algo? O tutor responde no chat, sugere materiais e exemplos ligados à sua etapa.",
  },
];

export function ComoFunciona() {
  return (
    <section id="como-funciona" className="mx-auto max-w-6xl scroll-mt-20 border-t border-line px-4 py-24 sm:px-8">
      <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">Como funciona</h2>
      <p className="mt-3 max-w-xl text-muted">
        Do diagnóstico ao objetivo, em três passos e com duas inteligências artificiais ajudando você.
      </p>

      <ol className="relative mt-14 grid gap-10 md:grid-cols-3 md:gap-8">
        <span aria-hidden className="absolute left-[17px] top-4 hidden h-0.5 w-[calc(100%-2rem)] bg-line md:block" />
        {PASSOS.map(({ icon: Icon, titulo, texto }, i) => (
          <li key={titulo} className="relative pl-14 md:pl-0 md:pt-14">
            <span
              aria-hidden
              className="absolute left-0 top-0 z-10 grid size-9 place-items-center rounded-full border-2 border-primary bg-bg text-sm font-semibold text-primary md:top-0"
            >
              {i + 1}
            </span>
            <h3 className="flex items-center gap-2 font-display text-lg font-semibold">
              <Icon className="size-5 shrink-0 text-primary" aria-hidden /> {titulo}
            </h3>
            <p className="mt-2 max-w-sm leading-relaxed text-muted">{texto}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
