from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Depends
from pydantic import UUID4
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from fastapi_pagination import Page, paginate

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter(prefix="/atletas")

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn = Body(...)
):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'A categoria {categoria_nome} não foi encontrada.')
    
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado.')
    
    atleta_model = AtletaModel(
        nome=atleta_in.nome,
        cpf=atleta_in.cpf,
        idade=atleta_in.idade,
        peso=atleta_in.peso,
        altura=atleta_in.altura,
        sexo=atleta_in.sexo,
        created_at=datetime.utcnow(),
        categoria_id=categoria.pk_id,
        centro_treinamento_id=centro_treinamento.pk_id
    )
    try:
        db_session.add(atleta_model)
        await db_session.commit()
        await db_session.refresh(atleta_model)
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}'
        )
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro ao inserir os dados no banco'
        )
    
    return AtletaOut.from_orm(atleta_model)

@router.get(
    '/', 
    summary='Consultar todos os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaOut],
)
async def query(
    db_session: DatabaseDependency, 
    nome: Optional[str] = None,
    cpf: Optional[str] = None
) -> Page[AtletaOut]:
    query_statement = select(AtletaModel)
    if nome:
        query_statement = query_statement.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    if cpf:
        query_statement = query_statement.filter(AtletaModel.cpf == cpf)

    result = await db_session.execute(query_statement)
    atletas = result.scalars().all()

    return paginate(atletas)

@router.get(
    '/{id}', 
    summary='Consulta um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(pk_id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado no id: {id}')
    
    return AtletaOut.from_orm(atleta)

@router.patch(
    '/{id}', 
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(pk_id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado no id: {id}')
    
    update_data = atleta_up.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return AtletaOut.from_orm(atleta)

@router.delete(
    '/{id}', 
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(pk_id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado no id: {id}')
    
    await db_session.delete(atleta)
    await db_session.commit()
