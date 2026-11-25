"use client";
import { createContext, useCallback, useContext, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from "lucide-react";
import { cn } from "@/lib/cn";
import { tFast } from "@/lib/motion";

/** Feedback (PDF: sem alert()). Faixa lateral colorida por tipo; sem sombra. Aparece por resposta a uma acao. */
type Kind = "success" | "error" | "warning" | "info";
type Item = { id: number; kind: Kind; text: string };

const Ctx = createContext<(text: string, kind?: Kind) => void>(() => {});
export const useToast = () => useContext(Ctx);

const ICON = { success: CheckCircle2, error: XCircle, warning: AlertTriangle, info: Info };
const TONE = {
  success: "text-ok",
  error: "text-danger",
  warning: "text-warn",
  info: "text-primary",
};
const FAIXA = {
  success: "border-l-ok",
  error: "border-l-danger",
  warning: "border-l-warn",
  info: "border-l-primary",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<Item[]>([]);
  const n = useRef(0);

  const remove = useCallback((id: number) => setItems((l) => l.filter((i) => i.id !== id)), []);
  const push = useCallback(
    (text: string, kind: Kind = "info") => {
      const id = ++n.current;
      setItems((l) => [...l.slice(-3), { id, kind, text }]);
      setTimeout(() => remove(id), 5000);
    },
    [remove],
  );

  return (
    <Ctx.Provider value={push}>
      {children}
      <div
        className="pointer-events-none fixed inset-x-0 bottom-0 z-50 flex flex-col items-center gap-2 p-4 sm:items-end"
        role="status"
        aria-live="polite"
      >
        <AnimatePresence>
          {items.map((t) => {
            const Icon = ICON[t.kind];
            return (
              <motion.div
                key={t.id}
                layout
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={tFast}
                className={cn(
                  "pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-[var(--radius-control)] border border-l-4 border-line bg-surface p-4",
                  FAIXA[t.kind],
                )}
              >
                <Icon className={cn("mt-0.5 size-5 shrink-0", TONE[t.kind])} aria-hidden />
                <p className="flex-1 text-sm">{t.text}</p>
                <button onClick={() => remove(t.id)} aria-label="Fechar aviso" className="text-muted hover:text-fg">
                  <X className="size-4" aria-hidden />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </Ctx.Provider>
  );
}
