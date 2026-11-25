"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { Eraser, Send } from "lucide-react";
import { AuthShell } from "@/components/AuthShell";
import { Button, Field, Select } from "@/components/ui";
import { useToast } from "@/components/Toast";
import { api } from "@/lib/api";
import { saveTwoFA } from "@/lib/twofa";
import * as v from "@/lib/validators";

/**
 * Cadastro (PDF secao 5). Regras: todos os campos obrigatorios, nome 15-80 letras, CPF com digito,
 * CEP via API (ViaCEP) com preenchimento manual se falhar, telefones (+55)XX-XXXXXXXX,
 * senha com confirmacao igual. O acesso e feito com o E-MAIL (nao ha campo de login separado).
 *
 * Os dados validados são enviados por HTTPS à API e persistidos no Supabase. Senha, CPF e
 * resposta de 2FA são guardados apenas como hashes no servidor.
 *
 * Layout: campos agrupados em secoes com titulo e filete, na ordem em que sao preenchidos.
 */
const VAZIO = {
  nome: "", nascimento: "", sexo: "", mae: "", cpf: "", email: "", celular: "", fixo: "",
  cep: "", logradouro: "", numero: "", bairro: "", cidade: "", uf: "", senha: "", confirma: "",
};
type Form = typeof VAZIO;
type Erros = Partial<Record<keyof Form, string>>;

function validar(f: Form): Erros {
  const e: Erros = {};
  const obrig = (k: keyof Form, msg = "Campo obrigatório.") => { if (!f[k].trim()) e[k] = msg; };
  (Object.keys(VAZIO) as (keyof Form)[]).forEach((k) => obrig(k));
  if (!e.nome && !v.nomeValido(f.nome)) e.nome = "Use de 15 a 80 letras (sem números ou símbolos).";
  if (!e.nascimento && !v.dataNascimentoValida(f.nascimento)) e.nascimento = "Data inválida.";
  if (!e.cpf && !v.cpfValido(f.cpf)) e.cpf = "CPF inválido.";
  if (!e.email && !v.emailValido(f.email)) e.email = "E-mail inválido.";
  if (!e.celular && !v.telefoneValido(f.celular)) e.celular = "Use o formato (+55)XX-XXXXXXXX.";
  if (!e.fixo && !v.telefoneValido(f.fixo)) e.fixo = "Use o formato (+55)XX-XXXXXXXX.";
  if (!e.cep && !v.cepValido(f.cep)) e.cep = "CEP inválido.";
  if (!e.senha && f.senha.length < 8) e.senha = "Mínimo de 8 caracteres.";
  if (!e.senha && f.senha.length > 72) e.senha = "Máximo de 72 caracteres.";
  if (!e.confirma && f.confirma !== f.senha) e.confirma = "As senhas não coincidem.";
  return e;
}

/** Grupo de campos do cadastro, com ritmo visual sem alterar a ordem de preenchimento. */
function Secao({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div role="group" aria-label={titulo} className="cadastro-section grid gap-x-4 gap-y-4 sm:grid-cols-2">
      <h2 className="cadastro-section-title sm:col-span-2">{titulo}</h2>
      {children}
    </div>
  );
}

export default function CadastroPage() {
  const toast = useToast();
  const router = useRouter();
  const [f, setF] = useState<Form>(VAZIO);
  const [erros, setErros] = useState<Erros>({});
  const [loading, setLoading] = useState(false);
  const [cepBusy, setCepBusy] = useState(false);
  const numeroRef = useRef<HTMLInputElement>(null);

  const set = (k: keyof Form, mask?: (s: string) => string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setF((p) => ({ ...p, [k]: mask ? mask(e.target.value) : e.target.value }));

  /** Preenche o endereco pelo CEP assim que ele chega a 8 digitos. Se falhar, o usuario digita (regra 4 do PDF). */
  const ultimoCep = useRef("");
  async function buscaCep(cep: string) {
    const d = v.soDigitos(cep);
    if (d.length !== 8 || d === ultimoCep.current) return;
    ultimoCep.current = d; // evita buscar duas vezes o mesmo CEP (digitar + sair do campo)
    setCepBusy(true);
    try {
      const r = await fetch(`https://viacep.com.br/ws/${d}/json/`);
      if (!r.ok) throw new Error("falha na consulta");
      const dados = await r.json();
      if (dados.erro) {
        toast("CEP não encontrado. Confira o número ou preencha o endereço manualmente.", "warning");
        return;
      }
      // So preenche se o CEP continua o mesmo (o usuario pode ter corrigido enquanto buscava).
      setF((p) => v.soDigitos(p.cep) !== d ? p : ({
        ...p, logradouro: dados.logradouro ?? "", bairro: dados.bairro ?? "", cidade: dados.localidade ?? "", uf: dados.uf ?? "",
      }));
      numeroRef.current?.focus();
    } catch {
      ultimoCep.current = ""; // permite tentar de novo
      toast("Não foi possível buscar o CEP. Preencha o endereço manualmente.", "warning");
    } finally {
      setCepBusy(false);
    }
  }

  const aoDigitarCep = (e: React.ChangeEvent<HTMLInputElement>) => {
    const valor = v.maskCep(e.target.value);
    setF((p) => ({ ...p, cep: valor }));
    if (v.soDigitos(valor).length < 8) ultimoCep.current = ""; // CEP apagado/alterado: libera nova busca
    void buscaCep(valor);
  };

  async function enviar(ev: React.FormEvent) {
    ev.preventDefault();
    const e = validar(f);
    setErros(e);
    if (Object.keys(e).length) return toast("Corrija os campos destacados.", "error");

    setLoading(true);
    try {
      await api.auth.cadastro({
        nome: f.nome.trim(), email: f.email.trim(), senha: f.senha, nascimento: f.nascimento,
        sexo: f.sexo as "F" | "M" | "O", nome_mae: f.mae.trim(), cpf: f.cpf,
        celular: f.celular, telefone_fixo: f.fixo, cep: f.cep, logradouro: f.logradouro.trim(),
        numero: f.numero.trim(), bairro: f.bairro.trim(), cidade: f.cidade.trim(), uf: f.uf.trim(),
      });
      await saveTwoFA(f.email, { mae: f.mae, nascimento: f.nascimento, cep: f.cep });
      toast("Cadastro realizado! Faça login para continuar.", "success");
      setTimeout(() => router.push("/login"), 1200);
    } catch (err) {
      toast((err as Error).message, "error");
      setLoading(false);
    }
  }

  const E = (k: keyof Form) => erros[k];
  return (
    <AuthShell title="Criar conta" subtitle="Preencha seus dados para começar." wide>
      <form onSubmit={enviar} noValidate className="space-y-10">
        <Secao titulo="Dados pessoais">
          <Field className="sm:col-span-2" label="Nome completo" value={f.nome} onChange={set("nome")} error={E("nome")} autoComplete="name" />
          <Field label="Data de nascimento" type="date" value={f.nascimento} onChange={set("nascimento")} error={E("nascimento")} autoComplete="bday" />
          <Select label="Sexo" value={f.sexo} onChange={set("sexo")} error={E("sexo")}>
            <option value="">Selecione</option>
            <option value="F">Feminino</option>
            <option value="M">Masculino</option>
            <option value="O">Outro</option>
          </Select>
          <Field label="Nome materno" value={f.mae} onChange={set("mae")} error={E("mae")} />
          <Field label="CPF" inputMode="numeric" value={f.cpf} onChange={set("cpf", v.maskCpf)} error={E("cpf")} placeholder="000.000.000-00" />
        </Secao>

        <Secao titulo="Contato">
          <Field className="sm:col-span-2" label="E-mail (será o seu login)" type="email" value={f.email} onChange={set("email")} error={E("email")} autoComplete="email" />
          <Field label="Telefone celular" type="tel" inputMode="tel" autoComplete="tel" maxLength={18} value={f.celular} onChange={set("celular", v.maskTelefone)} error={E("celular")} placeholder="(+55)21-999999999" />
          <Field label="Telefone fixo" type="tel" inputMode="tel" autoComplete="tel-national" maxLength={18} value={f.fixo} onChange={set("fixo", v.maskTelefone)} error={E("fixo")} placeholder="(+55)21-22223333" />
        </Secao>

        <Secao titulo="Endereço">
          <Field label="CEP" inputMode="numeric" value={f.cep} onChange={aoDigitarCep} onBlur={() => buscaCep(f.cep)} error={E("cep")}
            hint={cepBusy ? "Buscando endereço..." : undefined} placeholder="00000-000" />
          <Field label="Logradouro" value={f.logradouro} onChange={set("logradouro")} error={E("logradouro")} />
          <Field ref={numeroRef} label="Número" value={f.numero} onChange={set("numero")} error={E("numero")} />
          <Field label="Bairro" value={f.bairro} onChange={set("bairro")} error={E("bairro")} />
          <Field label="Cidade" value={f.cidade} onChange={set("cidade")} error={E("cidade")} />
          <Field label="UF" maxLength={2} value={f.uf} onChange={set("uf", (s) => s.toUpperCase())} error={E("uf")} />
        </Secao>

        <Secao titulo="Senha">
          <Field label="Senha" type="password" value={f.senha} onChange={set("senha")} error={E("senha")} autoComplete="new-password" hint="Mínimo de 8 caracteres." />
          <Field label="Confirmar senha" type="password" value={f.confirma} onChange={set("confirma")} error={E("confirma")} autoComplete="new-password" />
          <div className="flex gap-3 pt-2 sm:col-span-2">
            <Button type="submit" loading={loading} className="flex-1"><Send className="size-4" aria-hidden /> Enviar</Button>
            <Button type="button" variant="ghost" className="flex-1" onClick={() => { setF(VAZIO); setErros({}); }}>
              <Eraser className="size-4" aria-hidden /> Limpar
            </Button>
          </div>
        </Secao>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        Já tem conta? <Link href="/login" className="font-medium text-primary hover:underline">Entrar</Link>
      </p>
    </AuthShell>
  );
}
