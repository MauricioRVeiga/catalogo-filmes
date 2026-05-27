from pydantic import BaseModel, ConfigDict, Field


class MovieCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100, description="Título do filme")
    genre: str = Field(min_length=1, max_length=60, description="Gênero cinematográfico")
    year: int = Field(ge=1888, le=2100, description="Ano de lançamento")
    rating: float = Field(ge=0, le=10, description="Nota de 0.0 a 10.0")
