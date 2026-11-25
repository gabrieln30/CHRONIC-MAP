"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, FileDown, Search, ShieldCheck, ShieldOff, Trash2, Users } from "lucide-react";
import { AppPage } from "@/components/AppPage";
import { Button, Field, Modal, Notice, Select, Spinner } from "@/components/ui";
import { useToast } from "@/components/Toast";
import { api, isUnavailable, type UsuarioOut } from "@/lib/api";
import { useSession } from "@/lib/auth";

/**
 * Gestao de usuarios (PDF, so master): busca por nome, ordenacao, paginacao, contador,
 * PDF da lista (Desafio Plus), exclusao de usuarios comuns e promocao/rebaixamento de perfil.
 * Rotas do back: GET /usuarios?q=, PATCH /usuarios/{id}/perfil e DELETE /usuarios/{id}.
 * Se o back responder 404/405, a tela avisa em vez de quebrar.
 */
const POR_PAGINA = 10;

type Ordem = "recentes" | "antigos" | "nome";
type Perfil = "comum" | "master";

const iniciais = (nome: string) =>
  nome.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join("");

const dataCurta = (iso: string) => {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "-" : d.toLocaleDateString("pt-BR");
};

const tempo = (iso: string) => {
  const t = new Date(iso).getTime();
  return Number.isNaN(t) ? 0 : t;
};

export default function UsuariosPage() {
  const toast = useToast();
  const { user: eu } = useSession();
  const [busca, setBusca] = useState("");
  const [ordem, setOrdem] = useState<Ordem>("recentes");
  const [pagina, setPagina] = useState(1);
  const [lista, setLista] = useState<UsuarioOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [indisponivel, setIndisponivel] = useState(false);
  const [alvo, setAlvo] = useState<UsuarioOut | null>(null);
  const [excluindo, setExcluindo] = useState(false);
  const [mudar, setMudar] = useState<{ u: UsuarioOut; perfil: Perfil } | null>(null);
  const [salvando, setSalvando] = useState(false);
  const reqId = useRef(0); // ignora respostas antigas quando a busca muda rapido

  const carregar = useCallback(async (q: string) => {
    const id = ++reqId.current;
    setLoading(true);
    try {
      const r = await api.admin.usuarios(q.trim());
      if (id !== reqId.current) return;
      setLista(r);
      setIndisponivel(false);
    } catch (e) {
      if (id !== reqId.current) return;
      if (isUnavailable(e)) setIndisponivel(true);
      else toast((e as Error).message, "error");
      setLista([]);
    }
    if (id === reqId.current) setLoading(false);
  }, [toast]);

  // Busca com atraso de 300 ms para nao chamar a API a cada tecla.
  useEffect(() => {
    const t = setTimeout(() => carregar(busca), 300);
    return () => clearTimeout(t);
  }, [busca, carregar]);

  // Volta para a primeira pagina quando a busca ou a ordem mudam.
  useEffect(() => { setPagina(1); }, [busca, ordem]);

  const ordenada = useMemo(() => {
    const copia = [...lista];
    if (ordem === "nome") copia.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
    else copia.sort((a, b) => (ordem === "recentes" ? tempo(b.criado_em) - tempo(a.criado_em) : tempo(a.criado_em) - tempo(b.criado_em)));
    return copia;
  }, [lista, ordem]);

  const totalPaginas = Math.max(1, Math.ceil(ordenada.length / POR_PAGINA));
  const paginaAtual = Math.min(pagina, totalPaginas);
  const visiveis = ordenada.slice((paginaAtual - 1) * POR_PAGINA, paginaAtual * POR_PAGINA);

  async function excluir() {
    if (!alvo) return;
    setExcluindo(true);
    try {
      await api.admin.excluir(alvo.id);
      toast("Usuário excluído.", "success");
      setAlvo(null);
      await carregar(busca);
    } catch (e) {
      toast(isUnavailable(e) ? "O servidor ainda não permite excluir usuários." : (e as Error).message, "error");
    }
    setExcluindo(false);
  }

  async function mudarPerfil() {
    if (!mudar) return;
    setSalvando(true);
    try {
      await api.admin.alterarPerfil(mudar.u.id, mudar.perfil);
      toast(mudar.perfil === "master" ? `${mudar.u.nome} agora é administrador.` : `${mudar.u.nome} voltou a ser usuário comum.`, "success");
      setMudar(null);
      await carregar(busca);
    } catch (e) {
      toast(isUnavailable(e) ? "O servidor ainda não permite alterar perfis." : (e as Error).message, "error");
    }
    setSalvando(false);
  }

  async function baixarPdf() {
    const { jsPDF } = await import("jspdf"); // carregado so quando clica (nao pesa na pagina)
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Chronic Map - Usuários", 14, 18);
    doc.setFontSize(9);
    doc.text(`Total: ${ordenada.length}  |  Gerado em ${new Date().toLocaleDateString("pt-BR")}`, 14, 25);
    doc.setFontSize(10);
    let y = 35;
    ordenada.forEach((u, i) => {
      if (y > 280) { doc.addPage(); y = 20; }
      const perfil = u.perfil === "master" ? "  |  Master" : "";
      doc.text(`${i + 1}. ${u.nome}  |  ${u.email}  |  ${dataCurta(u.criado_em)}${perfil}`, 14, y);
      y += 7;
    });
    doc.save("usuarios-chronic-map.pdf");
  }

  const promovendo = mudar?.perfil === "master";

  return (
    <AppPage title="Usuários" subtitle="Consulte os usuários, gerencie o acesso e defina quem é administrador." master wide>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute bottom-3.5 left-4 size-4 text-muted" aria-hidden />
          <Field label="Buscar por nome" value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Digite parte do nome" className="[&_input]:pl-11" />
        </div>
        <Select label="Ordenar por" value={ordem} onChange={(e) => setOrdem(e.target.value as Ordem)} className="sm:w-48">
          <option value="recentes">Mais recentes</option>
          <option value="antigos">Mais antigos</option>
          <option value="nome">Nome (A-Z)</option>
        </Select>
        <Button variant="ghost" onClick={baixarPdf} disabled={!ordenada.length}><FileDown className="size-4" aria-hidden /> Baixar PDF</Button>
      </div>

      <div className="mt-6">
        {indisponivel && (
          <Notice title="Gestão de usuários indisponível no servidor">
            A API ainda não tem a rota de listagem (<code>GET /usuarios</code>). Esta tela já está pronta e passa a funcionar assim que a rota existir.
          </Notice>
        )}

        {loading ? <Spinner /> : !indisponivel && (
          ordenada.length === 0 ? (
            <p className="py-12 text-center text-muted">
              {busca.trim() ? "Nenhum usuário encontrado para essa busca." : "Nenhum usuário cadastrado ainda."}
            </p>
          ) : (
            <>
              <p className="mb-3 flex items-center gap-2 text-sm text-muted" aria-live="polite">
                <Users className="size-4" aria-hidden />
                {ordenada.length} {ordenada.length === 1 ? "usuário" : "usuários"}
                {busca.trim() ? " encontrados" : " cadastrados"}
              </p>

              <ul className="divide-y divide-line overflow-hidden rounded-[var(--radius-card)] border border-line bg-surface">
                {visiveis.map((u) => {
                  const ehMaster = u.perfil === "master";
                  const sou = u.id === eu?.id;
                  return (
                    <li key={u.id} className="flex items-center gap-4 px-5 py-4">
                      <span aria-hidden className="grid size-10 shrink-0 place-items-center rounded-[var(--radius-control)] bg-primary font-display text-sm font-semibold text-primary-fg">
                        {iniciais(u.nome)}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="flex items-center gap-2 font-medium">
                          <span className="truncate">{u.nome}</span>
                          {ehMaster && (
                            <span className="shrink-0 rounded-[4px] bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">Master</span>
                          )}
                          {sou && <span className="shrink-0 text-xs font-normal text-muted">(você)</span>}
                        </p>
                        <p className="truncate text-sm text-muted">{u.email}</p>
                      </div>
                      <p className="hidden shrink-0 text-sm text-muted sm:block">Desde {dataCurta(u.criado_em)}</p>
                      <div className="flex shrink-0 items-center gap-1">
                        {!sou && (
                          <button
                            onClick={() => setMudar({ u, perfil: ehMaster ? "comum" : "master" })}
                            aria-label={ehMaster ? `Remover administrador de ${u.nome}` : `Tornar ${u.nome} administrador`}
                            title={ehMaster ? "Remover administrador" : "Tornar administrador"}
                            className="grid size-10 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg"
                          >
                            {ehMaster ? <ShieldOff className="size-4" aria-hidden /> : <ShieldCheck className="size-4" aria-hidden />}
                          </button>
                        )}
                        {!ehMaster && (
                          <button onClick={() => setAlvo(u)} aria-label={`Excluir ${u.nome}`} title="Excluir usuário" className="grid size-10 place-items-center rounded-lg text-danger hover:bg-danger/10">
                            <Trash2 className="size-4" aria-hidden />
                          </button>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>

              {totalPaginas > 1 && (
                <nav className="mt-4 flex items-center justify-between" aria-label="Paginação">
                  <Button variant="ghost" onClick={() => setPagina(paginaAtual - 1)} disabled={paginaAtual === 1}>
                    <ChevronLeft className="size-4" aria-hidden /> Anterior
                  </Button>
                  <span className="text-sm text-muted">Página {paginaAtual} de {totalPaginas}</span>
                  <Button variant="ghost" onClick={() => setPagina(paginaAtual + 1)} disabled={paginaAtual === totalPaginas}>
                    Próxima <ChevronRight className="size-4" aria-hidden />
                  </Button>
                </nav>
              )}
            </>
          )
        )}
      </div>

      <Modal open={!!mudar} onClose={() => setMudar(null)} title={promovendo ? "Tornar administrador?" : "Remover administrador?"}>
        <p className="text-sm text-muted">
          {promovendo ? (
            <>
              <strong className="text-fg">{mudar?.u.nome}</strong> poderá consultar e excluir usuários, ver os logs de acesso e definir outros administradores.
              Só dê esse acesso a quem você confia.
            </>
          ) : (
            <>
              <strong className="text-fg">{mudar?.u.nome}</strong> deixará de ser administrador e voltará a ser usuário comum.
            </>
          )}
        </p>
        <div className="mt-6 flex gap-3">
          <Button variant="ghost" className="flex-1" onClick={() => setMudar(null)}>Cancelar</Button>
          <Button className="flex-1" loading={salvando} onClick={mudarPerfil}>{promovendo ? "Tornar administrador" : "Remover acesso"}</Button>
        </div>
      </Modal>

      <Modal open={!!alvo} onClose={() => setAlvo(null)} title="Excluir usuário?">
        <p className="text-sm text-muted">
          Você vai excluir <strong className="text-fg">{alvo?.nome}</strong> ({alvo?.email}) e os dados de estudo dele. Esta ação não pode ser desfeita.
        </p>
        <div className="mt-6 flex gap-3">
          <Button variant="ghost" className="flex-1" onClick={() => setAlvo(null)}>Cancelar</Button>
          <Button variant="danger" className="flex-1" loading={excluindo} onClick={excluir}>Excluir</Button>
        </div>
      </Modal>
    </AppPage>
  );
}
