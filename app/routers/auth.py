from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas import LoginIn, TokenOut, UsuarioCreate, UsuarioOut
from app.security import criar_token, hash_senha, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/cadastro", response_model=UsuarioOut, status_code=201)
def cadastrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário (senha guardada só como hash bcrypt)."""
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    usuario = Usuario(nome=dados.nome, email=dados.email, senha_hash=hash_senha(dados.senha))
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
    return TokenOut(access_token=criar_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    """Dados do usuário logado."""
    return usuario
