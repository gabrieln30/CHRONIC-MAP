import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.log_acesso import LogAcesso
from app.models.usuario import Usuario
from app.schemas import LoginIn, TokenOut, UsuarioCreate, UsuarioOut
from app.security import criar_token, hash_senha, verificar_senha

logger = logging.getLogger("chronic_map")

router = APIRouter(prefix="/auth", tags=["Autenticação"])


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
