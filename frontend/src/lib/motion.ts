/**
 * Presets de animacao (biblioteca: Motion, pacote "motion/react").
 * Regras: so animar `transform` e `opacity` (GPU, sem travar). Movimento so onde responde a uma
 * acao da pessoa (abrir, confirmar, avancar progresso); nada de entradas em cascata ao carregar.
 * `prefers-reduced-motion` e tratado por <MotionConfig reducedMotion="user"> no layout.
 */
import type { Transition, Variants } from "motion/react";

export const EASE = [0.16, 1, 0.3, 1] as const; // ease-out-expo

export const tFast: Transition = { duration: 0.18, ease: EASE };
export const tBase: Transition = { duration: 0.25, ease: EASE };
export const spring: Transition = { type: "spring", stiffness: 260, damping: 28 };

/**
 * Aparece com um fade curto, sem deslocamento. O nome `fadeUp` foi mantido porque outros
 * componentes importam esse preset; o efeito de "subir" foi removido de proposito.
 */
export const fadeUp: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: tBase },
};

/** Container dos filhos com `fadeUp`: escalonamento minimo (30ms). */
export const stagger: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.03 } },
};

export const viewportOnce = { once: true, margin: "-40px" } as const;
