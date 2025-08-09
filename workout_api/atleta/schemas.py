from typing import Annotated, Optional
from pydantic import BaseModel, Field, PositiveFloat
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.centro_treinamento.schemas import CentroTreinamentoAtleta, CentroTreinamentoOut
from workout_api.contrib.schemas import BaseSchema, OutMixin

class AtletaBase(BaseSchema):
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao', max_length=50)]
    cpf: Annotated[str, Field(description='CPF do atleta', example='12345678900', max_length=11)]
    idade: Annotated[int, Field(description='Idade do atleta', example=25)]
    peso: Annotated[PositiveFloat, Field(description='Peso do atleta', example=75.5)]
    altura: Annotated[PositiveFloat, Field(description='Altura do atleta', example=1.70)]
    sexo: Annotated[str, Field(description='Sexo do atleta', example='M', max_length=1)]

class AtletaIn(AtletaBase):
    categoria: CategoriaIn
    centro_treinamento: CentroTreinamentoAtleta

class AtletaOut(AtletaBase, OutMixin):
    categoria: CategoriaOut
    centro_treinamento: CentroTreinamentoOut

class AtletaUpdate(BaseSchema):
    nome: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=11)
    idade: Optional[int] = None
    peso: Optional[PositiveFloat] = None
    altura: Optional[PositiveFloat] = None
    sexo: Optional[str] = Field(None, max_length=1)
