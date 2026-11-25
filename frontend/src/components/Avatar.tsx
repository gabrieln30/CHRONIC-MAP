import { cn } from "@/lib/cn";

/** Iniciais do nome (ate 2 letras), usadas quando o usuario ainda nao tem foto. */
export const iniciais = (nome: string) =>
  nome.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join("");

/** Foto de perfil (data URL vinda do banco) ou, sem foto, as iniciais sobre o azul da marca. */
export function Avatar({ nome, foto, className }: { nome: string; foto?: string | null; className?: string }) {
  const base = "grid shrink-0 place-items-center overflow-hidden rounded-[var(--radius-control)]";
  if (foto) {
    return (
      // eslint-disable-next-line @next/next/no-img-element -- data URL do banco; next/image nao otimiza isso
      <img src={foto} alt="" aria-hidden className={cn(base, "object-cover", className)} />
    );
  }
  return (
    <span aria-hidden className={cn(base, "bg-primary font-display font-semibold text-primary-fg", className)}>
      {iniciais(nome)}
    </span>
  );
}
