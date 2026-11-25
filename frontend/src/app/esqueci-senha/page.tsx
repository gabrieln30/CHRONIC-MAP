"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Eye, EyeOff, KeyRound } from "lucide-react";
import { AuthShell } from "@/components/AuthShell";
import { Button, Field, Notice } from "@/components/ui";
import { useToast } from "@/components/Toast";
import { api, ApiError } from "@/lib/api";

/** 000.000.000-00 enquanto digita. */
const mascaraCpf = (v: string) => {
  const d = v.replace(/\D/g, "").slice(0, 11);
  return d.replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2");
};

type Erros = { email?: string; cpf?: string; nova?: string; confirma?: string };

/**
 * "Esqueci a senha" sem e-mail: quem sabe o e-mail e o CPF da conta define uma nova senha.
 * O back responde sempre a mesma mensagem quando os dados nao conferem (nao revela quais e-mails existem).
 */
export default function EsqueciSenhaPage() {
  const toast = useToast();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [cpf, setCpf] = useState("");
  const [nova, setNova] = useState("");
  const [confirma, setConfirma] = useState("");
  const [ver, setVer] = useState(false);
  const [erros, setErros] = useState<Erros>({});
  const [loading, setLoading] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    const er: Erros = {
      email: email.trim() ? undefined : "Informe o e-mail da conta.",
      cpf: cpf.replace(/\D/g, "").length === 11 ? undefined : "Informe os 11 dígitos do CPF.",
      nova: nova.length >= 8 ? (nova.length <= 72 ? undefined : "Use no máximo 72 caracteres.") : "A nova senha precisa ter pelo menos 8 caracteres.",
      confirma: confirma === nova ? undefined : "As senhas não são iguais.",
    };
    setErros(er);
    if (Object.values(er).some(Boolean)) return toast("Confira os campos destacados.", "warning");

    setLoading(true);
    try {
      await api.auth.esqueciSenha({ email: email.trim(), cpf, nova_senha: nova });
      toast("Senha alterada. Entre com a nova senha.", "success");
      router.push("/login");
    } catch (err) {
      toast(err instanceof ApiError ? err.message : (err as Error).message, "error");
      setLoading(false);
    }
  }

  const toggle = (
    <button type="button" onClick={() => setVer(!ver)} aria-label={ver ? "Ocultar senha" : "Mostrar senha"}
      className="grid size-9 place-items-center rounded-md text-muted hover:text-fg">
      {ver ? <EyeOff className="size-5" aria-hidden /> : <Eye className="size-5" aria-hidden />}
    </button>
  );

  return (
    <AuthShell title="Esqueci a senha" subtitle="Confirme o e-mail e o CPF da sua conta e escolha uma nova senha.">
      <form onSubmit={enviar} noValidate className="space-y-4">
        <Field label="E-mail da conta" type="email" autoComplete="email" value={email} error={erros.email}
          onChange={(e) => setEmail(e.target.value)} placeholder="voce@exemplo.com" />
        <Field label="CPF" inputMode="numeric" autoComplete="off" value={cpf} error={erros.cpf}
          onChange={(e) => setCpf(mascaraCpf(e.target.value))} placeholder="000.000.000-00" />
        <Field label="Nova senha" type={ver ? "text" : "password"} autoComplete="new-password" value={nova} error={erros.nova}
          hint="Mínimo de 8 caracteres." onChange={(e) => setNova(e.target.value)} right={toggle} />
        <Field label="Repita a nova senha" type={ver ? "text" : "password"} autoComplete="new-password" value={confirma} error={erros.confirma}
          onChange={(e) => setConfirma(e.target.value)} />
        <Notice tone="info" title="Contas sem CPF cadastrado e contas de administrador não podem ser recuperadas por aqui." />
        <div className="flex gap-3 pt-2">
          <Button type="submit" loading={loading} className="flex-1"><KeyRound className="size-4" aria-hidden /> Redefinir senha</Button>
          <Link href="/login" className="flex-1"><Button type="button" variant="ghost" className="w-full">Voltar</Button></Link>
        </div>
      </form>
    </AuthShell>
  );
}
