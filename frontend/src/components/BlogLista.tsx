import Link from "next/link";
import { ArrowRight, Clock } from "lucide-react";
import type { Post } from "@/lib/blog";

/**
 * Grade de artigos (usada na home e em /blog). Recebe so o necessario do post
 * (sem o texto completo) para nao enviar conteudo desnecessario ao navegador.
 * Cada artigo e um bloco com filete no topo; o titulo sublinha no hover.
 */
export type PostResumo = Pick<Post, "slug" | "titulo" | "resumo" | "categoria" | "minutos">;

export function BlogLista({ posts, colunas = 3 }: { posts: PostResumo[]; colunas?: 2 | 3 }) {
  return (
    <ul className={`grid gap-x-8 sm:grid-cols-2 ${colunas === 3 ? "lg:grid-cols-3" : ""}`}>
      {posts.map((p) => (
        <li key={p.slug} className="flex">
          <Link href={`/blog/${p.slug}`} className="group flex w-full flex-col border-t border-line py-6">
            <div className="flex items-center justify-between text-sm text-muted">
              <span className="font-medium text-primary">{p.categoria}</span>
              <span className="inline-flex items-center gap-1"><Clock className="size-3.5" aria-hidden /> {p.minutos} min</span>
            </div>
            <h3 className="mt-4 font-display text-xl font-semibold leading-snug underline-offset-4 group-hover:underline">{p.titulo}</h3>
            <p className="mt-2 flex-1 leading-relaxed text-muted">{p.resumo}</p>
            <span className="mt-5 inline-flex items-center gap-1 text-sm font-medium text-primary">
              Ler artigo <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" aria-hidden />
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
