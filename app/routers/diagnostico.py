from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.area_micro import AreaMicro
from app.models.diagnostico import Diagnostico
from app.models.usuario import Usuario
from app.schemas import DiagnosticoIn, DiagnosticoOut, PerguntaOut

router = APIRouter(prefix="/diagnostico", tags=["Diagnóstico"])

# Cada pergunta indica o `campo` de DiagnosticoIn que ela preenche, e as opções
# já trazem o `valor` no tipo certo (ex.: horas como número, não como texto).
# Questionário fixo; a versão adaptativa (RF05) pode ser feita depois.
PERGUNTAS = [
    {"id": 1, "campo": "nivel_conhecimento",
     "pergunta": "Qual é o seu nível atual de conhecimento na área escolhida?",
     "tipo": "multipla_escolha",
     "opcoes": [{"valor": "iniciante", "rotulo": "Iniciante"},
                {"valor": "intermediario", "rotulo": "Intermediário"},
                {"valor": "avancado", "rotulo": "Avançado"}]},
    {"id": 2, "campo": "tempo_semanal_horas",
     "pergunta": "Quantas horas por semana você tem disponível para estudar?",
     "tipo": "multipla_escolha",
     "opcoes": [{"valor": 3, "rotulo": "1 a 5 horas"},
                {"valor": 8, "rotulo": "6 a 10 horas"},
                {"valor": 15, "rotulo": "11 a 20 horas"},
                {"valor": 25, "rotulo": "Mais de 20 horas"}]},
    {"id": 3, "campo": "objetivo",
     "pergunta": "Qual é o seu principal objetivo com essa trilha de aprendizado?",
     "tipo": "texto_livre",
     "opcoes": []},
    {"id": 4, "campo": "estilo_aprendizado",
     "pergunta": "Como você aprende melhor?",
     "tipo": "multipla_escolha",
     "opcoes": [{"valor": "visual", "rotulo": "Visual (diagramas e mapas)"},
                {"valor": "pratico", "rotulo": "Prático (mão na massa)"},
                {"valor": "leitura", "rotulo": "Leitura"},
                {"valor": "video", "rotulo": "Vídeo-aulas"}]},
    {"id": 5, "campo": "experiencia_previa",
     "pergunta": "Você tem alguma experiência prática anterior na área?",
     "tipo": "multipla_escolha",
     "opcoes": [{"valor": "nenhuma", "rotulo": "Nenhuma"},
                {"valor": "projetos_pessoais", "rotulo": "Projetos pessoais"},
                {"valor": "profissional", "rotulo": "Experiência profissional"}]},
]


# IMPORTANTE: rotas fixas (/perguntas) ficam ANTES de /{diagnostico_id}.
@router.get("/perguntas", response_model=list[PerguntaOut])
def listar_perguntas():
    """Retorna as perguntas do questionário (com 'numero' e 'total' para o RF06)."""
    total = len(PERGUNTAS)
    return [{**p, "numero": i + 1, "total": total} for i, p in enumerate(PERGUNTAS)]


@router.post("", response_model=DiagnosticoOut, status_code=201)
def criar_diagnostico(
    dados: DiagnosticoIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Salva as respostas do diagnóstico do usuário logado."""
    if not db.get(AreaMicro, dados.area_micro_id):
        raise HTTPException(status_code=404, detail="Subárea não encontrada.")

    novo = Diagnostico(
        usuario_id=usuario.id,
        area_micro_id=dados.area_micro_id,
        nivel_conhecimento=dados.nivel_conhecimento,
        tempo_semanal_horas=dados.tempo_semanal_horas,
        objetivo=dados.objetivo,
        estilo_aprendizado=dados.estilo_aprendizado,
        experiencia_previa=dados.experiencia_previa,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("", response_model=list[DiagnosticoOut])
def listar_meus_diagnosticos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista os diagnósticos do usuário logado (útil para refazer, RF11)."""
    return (
        db.query(Diagnostico)
        .filter(Diagnostico.usuario_id == usuario.id)
        .order_by(Diagnostico.criado_em.desc(), Diagnostico.id.desc())
        .all()
    )


@router.get("/{diagnostico_id}", response_model=DiagnosticoOut)
def buscar_diagnostico(
    diagnostico_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna um diagnóstico do usuário logado."""
    diag = (
        db.query(Diagnostico)
        .filter(Diagnostico.id == diagnostico_id, Diagnostico.usuario_id == usuario.id)
        .first()
    )
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnóstico não encontrado.")
    return diag
