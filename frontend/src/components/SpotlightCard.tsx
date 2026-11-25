import { cn } from "@/lib/cn";

/**
 * Bloco com filete que realca a borda no hover. Mantido com este nome porque outros componentes
 * o importam; o brilho que seguia o mouse foi removido de proposito.
 */
export function SpotlightCard({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "group relative rounded-[var(--radius-card)] border border-line bg-surface p-6 transition-colors hover:border-primary",
        className,
      )}
    >
      {children}
    </div>
  );
}
