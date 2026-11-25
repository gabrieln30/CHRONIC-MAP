/** Fundo decorativo para as telas de acesso. Todo o movimento fica no CSS, sem iframes ou scripts externos. */
export function FluidFieldBackground() {
  return (
    <div className="fluid-field" aria-hidden="true">
      <span className="fluid-field-blob fluid-field-blob-a" />
      <span className="fluid-field-blob fluid-field-blob-b" />
      <span className="fluid-field-blob fluid-field-blob-c" />
      <span className="fluid-field-grid" />
      <span className="fluid-field-noise" />
    </div>
  );
}
