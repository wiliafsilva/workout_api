from typing import Optional
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Atleta

router = APIRouter(prefix="/atletas")

@router.get("/")
def listar_atletas(
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Atleta)
    if nome:
        query = query.filter(Atleta.nome.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(Atleta.cpf == cpf)
    return query.all()
