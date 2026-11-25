import base64
import binascii
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.database import utcnow
from app.deps import eh_master, get_current_user
from app.models.log_acesso import LogAcesso
from app.models.recuperacao import TentativaRecuperacao
from app.models.usuario import Usuario
from app.schemas import (
    FotoUpdate,
    LoginIn,
    NomeUpdate,
    SenhaEsquecidaIn,
    TokenOut,
    UsuarioCreate,
    UsuarioOut,
)
from app.security import criar_token, hash_senha, verificar_senha

logger = logging.getLogger("chronic_map")

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# "Esqueci a senha": 5 erros por e-mail travam a recuperação desse e-mail por 15 minutos.
_MAX_FALHAS_RECUPERACAO = 5
_JANELA_RECUPERACAO = timedelta(minutes=15)

# Foto de perfil: o front já entrega 256x256 em JPEG (~20 KB); isto só protege o banco.
_FOTO_MAX_BYTES = 150_000
_FOTO_FORMATOS = {  # prefixo do data URL -> confere os primeiros bytes do arquivo
    "data:image/jpeg;base64,": lambda b: b.startswith(b"\xff\xd8\xff"),
    "data:image/png;base64,": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
    "data:image/webp;base64,": lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP",
}


@router.post("/cadastro", response_model=UsuarioOut, status_code=201)
def cadastrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria um usuário e persiste os dados do formulário de cadastro."""
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    perfil = dados.model_dump(exclude={"senha", "cpf", "nome_mae"})
    usuario = Usuario(
        **perfil,
        senha_hash=hash_senha(dados.senha),
        # Dados usados para identificação/2FA ficam protegidos por hash.
        cpf_hash=hash_senha(dados.cpf) if dados.cpf else None,
        nome_mae_hash=hash_senha(dados.nome_mae.lower()) if dados.nome_mae else None,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:  # dois cadastros simultâneos com o mesmo e-mail
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    """Valida e-mail e senha e devolve um token JWT (Bearer)."""
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not verificar_senha(dados.senha, usuario.senha_hash if usuario else None):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    # Registra o acesso para a tela de logs do admin. Se falhar, o login continua funcionando.
    try:
        db.add(LogAcesso(usuario_id=usuario.id, nome=usuario.nome))
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        logger.exception("Falha ao registrar log de acesso")

    return TokenOut(access_token=criar_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    """Dados do usuário logado."""
    return usuario


@router.patch("/perfil", response_model=UsuarioOut)
def alterar_nome(dados: NomeUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """O usuário troca o PRÓPRIO nome. E-mail e perfil (comum/master) não mudam por aqui."""
    usuario.nome = dados.nome
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/foto", response_model=UsuarioOut)
def trocar_foto(dados: FotoUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Guarda a foto do próprio usuário no banco (coluna usuario.foto)."""
    foto = dados.foto.strip()
    prefixo = next((p for p in _FOTO_FORMATOS if foto.startswith(p)), None)
    if prefixo is None:
        raise HTTPException(status_code=400, detail="Formato de imagem não aceito. Use JPG, PNG ou WebP.")
    if len(foto) > _FOTO_MAX_BYTES * 4 // 3 + 200:
        raise HTTPException(status_code=413, detail="Imagem grande demais. Escolha outra foto.")
    try:
        bruto = base64.b64decode(foto[len(prefixo):], validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Imagem inválida.")
    if len(bruto) > _FOTO_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Imagem grande demais. Escolha outra foto.")
    if not _FOTO_FORMATOS[prefixo](bruto):  # o conteúdo precisa ser mesmo uma imagem do tipo declarado
        raise HTTPException(status_code=400, detail="Imagem inválida.")
    usuario.foto = foto
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/foto", response_model=UsuarioOut)
def remover_foto(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    usuario.foto = None
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/esqueci-senha", status_code=204)
def esqueci_senha(dados: SenhaEsquecidaIn, db: Session = Depends(get_db)):
    """Redefine a senha de quem informa e-mail + CPF da conta (sem envio de e-mail).

    - A resposta de erro é sempre a mesma, exista o e-mail ou não, para não revelar cadastros.
    - Contas sem CPF cadastrado e contas master não podem ser recuperadas por aqui.
    - 5 falhas por e-mail travam por 15 minutos (tabela tentativa_recuperacao).
    """
    agora = utcnow()
    db.query(TentativaRecuperacao).filter(TentativaRecuperacao.criado_em < agora - timedelta(days=1)).delete()

    falhas = (
        db.query(TentativaRecuperacao)
        .filter(TentativaRecuperacao.email == dados.email, TentativaRecuperacao.criado_em >= agora - _JANELA_RECUPERACAO)
        .count()
    )
    if falhas >= _MAX_FALHAS_RECUPERACAO:
        db.commit()
        raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente em 15 minutos.")

    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    # verificar_senha gasta o mesmo tempo mesmo sem usuário/CPF cadastrado (evita medir o tempo).
    cpf_confere = verificar_senha(dados.cpf, usuario.cpf_hash if usuario else None)
    if usuario is None or not cpf_confere or eh_master(usuario):
        db.add(TentativaRecuperacao(email=dados.email))
        db.commit()
        raise HTTPException(status_code=400, detail="Não foi possível redefinir a senha com os dados informados.")

    usuario.senha_hash = hash_senha(dados.nova_senha)
    db.query(TentativaRecuperacao).filter(TentativaRecuperacao.email == dados.email).delete()
    db.commit()
