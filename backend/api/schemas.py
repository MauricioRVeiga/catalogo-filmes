from pydantic import BaseModel, Field, ValidationError

class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    genre: str = Field(min_length=1, max_length=60)
    year: int = Field(ge=1888, le=2100)
    rating: float = Field(ge=0, le=10)