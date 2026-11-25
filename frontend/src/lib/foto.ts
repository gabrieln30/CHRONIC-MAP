/**
 * Prepara a foto de perfil no navegador: recorta em quadrado (centro), reduz para 256x256
 * e converte para JPEG. Assim o que vai para o banco pesa ~20 KB, nao importa o tamanho original.
 */
export const FOTO_LADO = 256;
const TIPOS = ["image/jpeg", "image/png", "image/webp"];
const MAX_ORIGINAL = 10 * 1024 * 1024; // 10 MB: so evita travar o navegador com arquivos enormes

export async function prepararFoto(arquivo: File): Promise<string> {
  if (!TIPOS.includes(arquivo.type)) throw new Error("Use uma imagem JPG, PNG ou WebP.");
  if (arquivo.size > MAX_ORIGINAL) throw new Error("A imagem passa de 10 MB. Escolha uma menor.");

  const url = URL.createObjectURL(arquivo);
  try {
    const img = await new Promise<HTMLImageElement>((ok, erro) => {
      const i = new Image();
      i.onload = () => ok(i);
      i.onerror = () => erro(new Error("Não foi possível ler essa imagem."));
      i.src = url;
    });
    const lado = Math.min(img.naturalWidth, img.naturalHeight);
    if (!lado) throw new Error("Não foi possível ler essa imagem.");
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = FOTO_LADO;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Seu navegador não conseguiu processar a imagem.");
    ctx.fillStyle = "#fff"; // PNG/WebP com fundo transparente viram JPEG: o fundo fica branco
    ctx.fillRect(0, 0, FOTO_LADO, FOTO_LADO);
    ctx.drawImage(img, (img.naturalWidth - lado) / 2, (img.naturalHeight - lado) / 2, lado, lado, 0, 0, FOTO_LADO, FOTO_LADO);
    return canvas.toDataURL("image/jpeg", 0.85);
  } finally {
    URL.revokeObjectURL(url);
  }
}
