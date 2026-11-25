"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { Camera, KeyRound, LogOut, Trash2, Wand2 } from "lucide-react";
import { AppPage } from "@/components/AppPage";
import { Avatar } from "@/components/Avatar";
import { Button, Field, Spinner } from "@/components/ui";
import { useToast } from "@/components/Toast";
import { api, ApiError, type ProgressoOut, type TrilhaOut } from "@/lib/api";
import { endSession, isMaster, trilhaAtiva, updateUser, useSession } from "@/lib/auth";
import { prepararFoto } from "@/lib/foto";
import { tFast } from "@/lib/motion";

/**
 * Perfil do proprio usuario: dados da conta, edicao de nome e foto, resumo da trilha ativa e atalhos de seguranca.
 * A foto e reduzida no navegador (256x256) e guardada no banco; o e-mail nao pode ser alterado.
 */
const data = (iso: string) => {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "-" : d.toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" });
};

export default function PerfilPage() {
  const { user } = useSession();
  const router = useRouter();
  const toast = useToast();
  const arquivoRef = useRef<HTMLInputElement>(null);
  const [nome, setNome] = useState("");
  const [salvandoNome, setSalvandoNome] = useState(false);
  const [enviandoFoto, setEnviandoFoto] = useState(false);
  const [trilha, setTrilha] = useState<TrilhaOut | null>(null);
  const [prog, setProg] = useState<ProgressoOut | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [temTrilha, setTemTrilha] = useState(false);

  useEffect(() => {
    if (!user) return;
    const id = trilhaAtiva.get(user.id);
    setTemTrilha(!!id);
    if (!id) return void setCarregando(false);
    // Se a API falhar, o perfil continua abrindo (so o resumo da trilha some).
    Promise.all([api.trilha.obter(id), api.progresso.obter(id).catch(() => null)])
      .then(([t, p]) => { setTrilha(t); setProg(p); })
      .catch(() => undefined)
      .finally(() => setCarregando(false));
  }, [user]);

  // Mantem o campo "Nome" em dia com a sessao (inclusive depois de salvar).
  const nomeSessao = user?.nome;
  useEffect(() => { if (nomeSessao !== undefined) setNome(nomeSessao); }, [nomeSessao]);

  if (!user) return <AppPage title="Meu perfil"><Spinner /></AppPage>;

  const total = trilha?.conteudo_json.etapas?.length ?? 0;
  const atual = Math.min(prog?.etapa_atual ?? 0, total);
  const pct = total ? Math.round((atual / total) * 100) : 0;

  const sair = () => { endSession(); router.push("/login"); };

  const nomeLimpo = nome.trim().replace(/\s+/g, " ");
  const nomeMudou = nomeLimpo !== user.nome;
  const msg = (err: unknown) => (err instanceof ApiError || err instanceof Error ? err.message : "Algo deu errado. Tente novamente.");

  async function salvarNome(e: React.FormEvent) {
    e.preventDefault();
    if (nomeLimpo.length < 2) return toast("O nome precisa ter pelo menos 2 caracteres.", "warning");
    setSalvandoNome(true);
    try {
      updateUser(await api.auth.alterarNome(nomeLimpo));
      toast("Nome atualizado.", "success");
    } catch (err) {
      toast(msg(err), "error");
    } finally {
      setSalvandoNome(false);
    }
  }

  async function escolherFoto(e: React.ChangeEvent<HTMLInputElement>) {
    const arquivo = e.target.files?.[0];
    e.target.value = ""; // permite escolher o mesmo arquivo de novo
    if (!arquivo) return;
    setEnviandoFoto(true);
    try {
      updateUser(await api.auth.trocarFoto(await prepararFoto(arquivo)));
      toast("Foto atualizada.", "success");
    } catch (err) {
      toast(msg(err), "error");
    } finally {
      setEnviandoFoto(false);
    }
  }

  async function removerFoto() {
    setEnviandoFoto(true);
    try {
      updateUser(await api.auth.removerFoto());
      toast("Foto removida.", "success");
    } catch (err) {
      toast(msg(err), "error");
    } finally {
      setEnviandoFoto(false);
    }
  }

  return (
    <AppPage title="Meu perfil" subtitle="Seus dados e o andamento dos seus estudos.">
      <div className="divide-y divide-line">
        <section className="flex flex-col gap-6 pb-8 sm:flex-row sm:items-center">
          <Avatar nome={user.nome} foto={user.foto} className="size-20 text-2xl" />
          <div className="min-w-0">
            <h2 className="truncate font-display text-xl font-semibold">{user.nome}</h2>
            <p className="truncate text-muted">{user.email}</p>
            <dl className="mt-3 flex flex-wrap gap-x-8 gap-y-1 text-sm">
              <div><dt className="inline text-muted">Membro desde </dt><dd className="inline font-medium">{data(user.criado_em)}</dd></div>
              <div><dt className="inline text-muted">Conta </dt><dd className="inline font-medium">{isMaster(user) ? "Master" : "Comum"}</dd></div>
            </dl>
          </div>
        </section>

        <section className="py-8">
          <h2 className="font-display text-lg font-semibold">Editar perfil</h2>
          <div className="mt-4 grid gap-8 sm:grid-cols-2">
            <div>
              <p className="mb-1.5 text-sm font-medium">Foto de perfil</p>
              <div className="flex items-center gap-4">
                <Avatar nome={user.nome} foto={user.foto} className="size-16 text-xl" />
                <div className="flex flex-wrap gap-2">
                  <input ref={arquivoRef} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" tabIndex={-1} onChange={escolherFoto} />
                  <Button type="button" variant="ghost" loading={enviandoFoto} onClick={() => arquivoRef.current?.click()}>
                    <Camera className="size-4" aria-hidden /> {user.foto ? "Trocar foto" : "Enviar foto"}
                  </Button>
                  {user.foto && (
                    <Button type="button" variant="ghost" disabled={enviandoFoto} onClick={removerFoto}>
                      <Trash2 className="size-4" aria-hidden /> Remover
                    </Button>
                  )}
                </div>
              </div>
              <p className="mt-2 text-sm text-muted">JPG, PNG ou WebP. A imagem é recortada em quadrado e reduzida antes de ser salva.</p>
            </div>
            <form onSubmit={salvarNome} noValidate className="space-y-3">
              <Field label="Nome" value={nome} maxLength={100} autoComplete="name" onChange={(e) => setNome(e.target.value)}
                hint={`E-mail da conta: ${user.email} (não pode ser alterado).`} />
              <Button type="submit" loading={salvandoNome} disabled={!nomeMudou || nomeLimpo.length < 2}>Salvar nome</Button>
            </form>
          </div>
        </section>

        <section className="py-8">
          <h2 className="font-display text-lg font-semibold">Minha trilha</h2>
          {carregando ? <div className="mt-4"><Spinner /></div> : !temTrilha || !trilha ? (
            <div className="mt-3 flex flex-col items-start gap-3">
              <p className="text-muted">Você ainda não tem uma trilha ativa. Responda o questionário para criar a sua.</p>
              <Link href="/diagnostico"><Button><Wand2 className="size-4" aria-hidden /> Responder questionário</Button></Link>
            </div>
          ) : (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted">Etapa {Math.min(atual + 1, total)} de {total}</span>
                <span className="font-medium">{pct}%</span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-2" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Progresso da trilha">
                <motion.div className="h-full origin-left rounded-full bg-primary" style={{ width: "100%" }} initial={{ scaleX: 0 }} animate={{ scaleX: pct / 100 }} transition={tFast} />
              </div>
              <div className="mt-5 flex flex-wrap gap-3">
                <Link href="/trilha"><Button>Continuar estudando</Button></Link>
                <Link href="/diagnostico"><Button variant="ghost">Refazer questionário</Button></Link>
              </div>
            </div>
          )}
        </section>

        <section className="pt-8">
          <h2 className="font-display text-lg font-semibold">Segurança e privacidade</h2>
          <p className="mt-2 max-w-xl text-muted">
            Sua senha nunca é exibida. Seus dados são tratados conforme a LGPD e usados apenas para o funcionamento da sua conta e da sua trilha.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {!isMaster(user) && <Link href="/senha"><Button variant="ghost"><KeyRound className="size-4" aria-hidden /> Alterar senha</Button></Link>}
            <Button variant="ghost" onClick={sair}><LogOut className="size-4" aria-hidden /> Sair da conta</Button>
          </div>
        </section>
      </div>
    </AppPage>
  );
}
