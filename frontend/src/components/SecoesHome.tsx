import Link from "next/link";
import {
  Accessibility, ArrowRight, ChevronDown, Code2, GraduationCap, Languages, Megaphone, Palette,
  ShieldCheck, Smartphone, Timer, ChartColumn, type LucideIcon,
} from "lucide-react";
import { BlogLista, type PostResumo } from "./BlogLista";

/** Cabecalho padrao das secoes da home. */
function Titulo({ id, titulo, texto }: { id?: string; titulo: string; texto?: string }) {
  return (
    <>
      <h2 id={id} className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">{titulo}</h2>
      {texto && <p className="mt-3 max-w-xl text-muted">{texto}</p>}
    </>
  );
}

/** Secao com um filete no topo: a separacao vem da linha, nao de cartoes. */
const Secao = ({ id, children }: { id?: string; children: React.ReactNode }) => (
  <section id={id} className="mx-auto max-w-6xl scroll-mt-20 border-t border-line px-4 py-20 sm:px-8">
    {children}
  </section>
);

/** Lista em colunas: cada item e um icone + texto, separados por filetes. */
function Itens({ itens, colunas }: { itens: { icon: LucideIcon; titulo: string; texto: string }[]; colunas: string }) {
  return (
    <ul className={`mt-10 grid gap-x-10 ${colunas}`}>
      {itens.map(({ icon: Icon, titulo, texto }) => (
        <li key={titulo} className="flex items-start gap-4 border-t border-line py-6">
          <Icon className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden />
          <div>
            <h3 className="font-display text-lg font-semibold">{titulo}</h3>
            <p className="mt-1 leading-relaxed text-muted">{texto}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}

/* ---------------- Areas ---------------- */
const AREAS: { icon: LucideIcon; titulo: string; texto: string }[] = [
  { icon: Code2, titulo: "Programação", texto: "Web, back-end, banco de dados e lógica." },
  { icon: ChartColumn, titulo: "Dados e IA", texto: "Análise de dados e aprendizado de máquina." },
  { icon: Palette, titulo: "Design", texto: "Interfaces, experiência do usuário e identidade." },
  { icon: Megaphone, titulo: "Marketing e negócios", texto: "Presença digital, vendas e gestão." },
  { icon: Languages, titulo: "Idiomas", texto: "Conversação, escrita e vocabulário." },
  { icon: GraduationCap, titulo: "Carreira e concursos", texto: "Planejamento para provas e transição de área." },
];

export function Areas() {
  return (
    <Secao id="areas">
      <Titulo titulo="Escolha o que você quer aprender" texto="Algumas áreas para começar. No questionário você escolhe a sua e a trilha é montada para ela." />
      <Itens itens={AREAS} colunas="sm:grid-cols-2 lg:grid-cols-3" />
    </Secao>
  );
}

/* ---------------- Para todos ---------------- */
const RECURSOS: { icon: LucideIcon; titulo: string; texto: string }[] = [
  { icon: Accessibility, titulo: "Acessível", texto: "Tema escuro, alto contraste e tamanho de letra ajustável, direto na barra do topo." },
  { icon: Smartphone, titulo: "No celular e no computador", texto: "O mesmo mapa de estudo em qualquer tela, com navegação simples." },
  { icon: Timer, titulo: "No seu ritmo", texto: "Você informa o tempo que tem por semana e a trilha respeita isso." },
  { icon: ShieldCheck, titulo: "Seus dados protegidos", texto: "Pedimos só o necessário e seguimos a LGPD. Você nunca fica sem controle." },
];

export function ParaTodos() {
  return (
    <Secao>
      <Titulo titulo="Feito para todo mundo" texto="Seja qual for sua idade, nível ou tempo livre, o Chronic Map se adapta a você." />
      <Itens itens={RECURSOS} colunas="sm:grid-cols-2" />
    </Secao>
  );
}

/* ---------------- Dicas (blog) ---------------- */
export function Dicas({ posts }: { posts: PostResumo[] }) {
  return (
    <Secao id="dicas">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Titulo titulo="Dicas de estudo" texto="Leituras rápidas para estudar melhor e manter a constância." />
        </div>
        <Link href="/blog" className="inline-flex items-center gap-1.5 font-medium text-primary underline-offset-4 hover:underline">
          Ver todos os artigos <ArrowRight className="size-4" aria-hidden />
        </Link>
      </div>
      <div className="mt-10"><BlogLista posts={posts} /></div>
    </Secao>
  );
}

/* ---------------- FAQ ---------------- */
const PERGUNTAS: { q: string; a: string }[] = [
  { q: "Como a IA monta a minha trilha?", a: "Você responde um questionário com a área, o objetivo, o nível de conhecimento e o tempo semanal. Essas respostas vão para a IA, que divide o estudo em etapas com exercícios e marcos." },
  { q: "O que o tutor faz?", a: "É um chat para tirar dúvidas sobre a sua trilha. Ele explica de outro jeito, sugere materiais e dá exemplos práticos ligados à etapa em que você está." },
  { q: "Posso refazer o questionário?", a: "Sim. Se o plano ficar pesado ou o seu objetivo mudar, responda o questionário de novo e gere uma nova trilha." },
  { q: "Que dados vocês pedem?", a: "Para criar a conta, o servidor recebe apenas nome, e-mail e senha. Os demais campos do cadastro, como CPF e endereço, são conferidos no seu navegador e não são enviados." },
  { q: "Funciona no celular?", a: "Sim. O site foi pensado para funcionar bem tanto no celular quanto no computador." },
];

export function Faq() {
  return (
    <Secao id="perguntas">
      <Titulo titulo="Perguntas frequentes" />
      <div className="mt-8 max-w-3xl divide-y divide-line border-y border-line">
        {PERGUNTAS.map(({ q, a }) => (
          <details key={q} className="group py-4">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium [&::-webkit-details-marker]:hidden">
              {q}
              <ChevronDown className="size-5 shrink-0 text-muted transition-transform group-open:rotate-180" aria-hidden />
            </summary>
            <p className="mt-3 max-w-2xl leading-relaxed text-muted">{a}</p>
          </details>
        ))}
      </div>
    </Secao>
  );
}

/* ---------------- CTA final ---------------- */
export function CtaFinal() {
  return (
    <Secao>
      <div className="flex flex-col gap-8 border-l-4 border-marker bg-surface-2 p-8 sm:flex-row sm:items-center sm:justify-between sm:p-10">
        <div>
          <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">Pronto para começar?</h2>
          <p className="mt-3 max-w-lg text-muted">Crie sua conta, responda o questionário e receba sua primeira trilha em poucos minutos.</p>
        </div>
        <Link href="/cadastro" className="inline-flex shrink-0 items-center justify-center gap-2 rounded-[var(--radius-control)] bg-primary px-6 py-3 font-medium text-primary-fg hover:brightness-110">
          Criar minha conta <ArrowRight className="size-4" aria-hidden />
        </Link>
      </div>
    </Secao>
  );
}
