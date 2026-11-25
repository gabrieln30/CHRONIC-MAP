"""Schemas Pydantic (v2): validam o que entra e sai da API."""
from datetime import date, datetime
import re
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.diagnostico import EstiloAprendizado, ExperienciaPrevia, NivelConhecimento

_EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ───────────────────────── Autenticação / Usuário ─────────────────────────
class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=150, pattern=_EMAIL_RE)
    # bcrypt só considera os primeiros 72 bytes; limitamos para não truncar em silêncio.
    senha: str = Field(min_length=8, max_length=72)
    nascimento: Optional[date] = None
    sexo: Optional[Literal["F", "M", "O"]] = None
    nome_mae: Optional[str] = Field(default=None, min_length=2, max_length=100)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=14)
    celular: Optional[str] = Field(default=None, max_length=20)
    telefone_fixo: Optional[str] = Field(default=None, max_length=20)
    cep: Optional[str] = Field(default=None, min_length=8, max_length=9)
    logradouro: Optional[str] = Field(default=None, max_length=150)
    numero: Optional[str] = Field(default=None, max_length=20)
    bairro: Optional[str] = Field(default=None, max_length=100)
    cidade: Optional[str] = Field(default=None, max_length=100)
    uf: Optional[str] = Field(default=None, min_length=2, max_length=2)

    @field_validator("email")
    @classmethod
    def _email_minusculo(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("nome")
    @classmethod
    def _nome_limpo(cls, v: str) -> str:
        return v.strip()

    @field_validator("cpf")
    @classmethod
    def _cpf_limpo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        digitos = re.sub(r"\D", "", v)
        if len(digitos) != 11:
            raise ValueError("CPF inválido")
        return digitos

    @field_validator("cep")
    @classmethod
    def _cep_limpo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        digitos = re.sub(r"\D", "", v)
        if len(digitos) != 8:
            raise ValueError("CEP inválido")
        return f"{digitos[:5]}-{digitos[5:]}"

    @field_validator("nome_mae", "celular", "telefone_fixo", "logradouro", "numero", "bairro", "cidade", "uf")
    @classmethod
    def _texto_limpo(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else None

    @field_validator("uf")
    @classmethod
    def _uf_maiuscula(cls, v: Optional[str]) -> Optional[str]:
        return v.upper() if v else None


class LoginIn(BaseModel):
    email: str = Field(max_length=150)
    senha: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def _email_minusculo(cls, v: str) -> str:
        return v.strip().lower()


class UsuarioOut(_Out):
    id: int
    nome: str
    email: str
    criado_em: datetime
    perfil: str = "comum"
    foto: Optional[str] = None


class UsuarioListaOut(_Out):
    """Item da lista do admin: só dados básicos, sem nenhum dado sensível."""
    id: int
    nome: str
    email: str
    criado_em: datetime
    perfil: str


class PerfilUpdate(BaseModel):
    perfil: Literal["comum", "master"]


class NomeUpdate(BaseModel):
    """Troca do próprio nome (o e-mail não muda)."""
    nome: str = Field(min_length=2, max_length=100)

    @field_validator("nome")
    @classmethod
    def _nome_limpo(cls, v: str) -> str:
        v = " ".join(v.split())
        if len(v) < 2:
            raise ValueError("Informe um nome com pelo menos 2 caracteres.")
        return v


class FotoUpdate(BaseModel):
    """Foto como data URL. O formato e o tamanho são conferidos na rota, com mensagem em português."""
    foto: str


class SenhaEsquecidaIn(BaseModel):
    """Recuperação sem e-mail: quem sabe o e-mail E o CPF da conta define uma nova senha."""
    email: str = Field(max_length=150)
    cpf: str = Field(min_length=11, max_length=14)
    nova_senha: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def _email_minusculo(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("cpf")
    @classmethod
    def _cpf_limpo(cls, v: str) -> str:
        digitos = re.sub(r"\D", "", v)
        if len(digitos) != 11:
            raise ValueError("CPF inválido")
        return digitos


class LogOut(_Out):
    id: int
    criado_em: datetime
    nome: str
    segundo_fator: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ───────────────────────────── Áreas ─────────────────────────────
class AreaMicroOut(_Out):
    id: int
    nome: str
    area_macro_id: int


class AreaMacroOut(_Out):
    id: int
    nome: str


# ───────────────────────────── Diagnóstico ─────────────────────────────
class OpcaoOut(BaseModel):
    valor: Union[int, str]
    rotulo: str


class PerguntaOut(BaseModel):
    id: int
    numero: int          # "pergunta 2 de 5" (RF06)
    total: int
    campo: str           # campo de DiagnosticoIn que esta pergunta preenche
    pergunta: str
    tipo: str            # multipla_escolha | texto_livre
    opcoes: list[OpcaoOut]


class DiagnosticoIn(BaseModel):
    area_micro_id: int = Field(gt=0)
    nivel_conhecimento: NivelConhecimento
    tempo_semanal_horas: int = Field(ge=1, le=80)
    objetivo: str = Field(min_length=3, max_length=1000)
    estilo_aprendizado: EstiloAprendizado
    experiencia_previa: Optional[ExperienciaPrevia] = None

    @field_validator("objetivo")
    @classmethod
    def _objetivo_limpo(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("objetivo muito curto")
        return v


class DiagnosticoOut(_Out):
    id: int
    usuario_id: int
    area_micro_id: int
    nivel_conhecimento: NivelConhecimento
    tempo_semanal_horas: int
    objetivo: str
    estilo_aprendizado: EstiloAprendizado
    experiencia_previa: Optional[ExperienciaPrevia] = None
    criado_em: datetime


# ───────────────────────────── Trilha ─────────────────────────────
class EtapaIA(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str = Field(min_length=1)
    exercicios: list[str] = Field(default_factory=list)
    marco: str = Field(min_length=1)


class TrilhaIA(BaseModel):
    """Formato que o Gemini PRECISA devolver (validado antes de salvar)."""
    etapas: list[EtapaIA] = Field(min_length=1, max_length=30)


class TrilhaGerarIn(BaseModel):
    diagnostico_id: int = Field(gt=0)


class TrilhaOut(_Out):
    id: int
    diagnostico_id: int
    conteudo_json: dict[str, Any]
    criado_em: datetime


# ───────────────────────────── Progresso ─────────────────────────────
class ProgressoOut(_Out):
    id: int
    trilha_id: int
    usuario_id: int
    etapa_atual: int
    exercicios_concluidos: list[str]
    atualizado_em: datetime


class EtapaUpdate(BaseModel):
    # 0..len(etapas); igual a len(etapas) significa trilha concluída.
    etapa_atual: int = Field(ge=0)


class ExercicioUpdate(BaseModel):
    etapa: int = Field(ge=0)
    indice: int = Field(ge=0)


# ───────────────────────────── Assistente / Dúvidas ─────────────────────────────
class DuvidaIn(BaseModel):
    trilha_id: int = Field(gt=0)
    pergunta: str = Field(min_length=3, max_length=2000)

    @field_validator("pergunta")
    @classmethod
    def _pergunta_limpa(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("pergunta muito curta")
        return v


class MaterialIA(BaseModel):
    tipo: str = "curso"
    plataforma: str = ""
    titulo: str
    url: Optional[str] = None

    @field_validator("url")
    @classmethod
    def _so_http(cls, v: Optional[str]) -> Optional[str]:
        # A IA pode inventar links; só aceitamos http(s) e descartamos o resto.
        if v and v.strip().lower().startswith(("http://", "https://")):
            return v.strip()
        return None


class RespostaAssistenteIA(BaseModel):
    """Formato que o Gemini PRECISA devolver no assistente de dúvidas."""
    diagnostico: str
    plano_de_melhoria: list[str] = Field(default_factory=list)
    materiais: list[MaterialIA] = Field(default_factory=list)
    exemplo_pratico: str = ""


class DuvidaOut(_Out):
    id: int
    usuario_id: int
    trilha_id: int
    etapa_referencia: Optional[int] = None
    pergunta: str
    resposta_json: dict[str, Any]
    criado_em: datetime
