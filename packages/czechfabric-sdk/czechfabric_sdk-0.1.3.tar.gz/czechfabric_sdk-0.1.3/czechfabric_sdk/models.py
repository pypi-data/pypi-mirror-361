from pydantic import BaseModel


class TripRequest(BaseModel):
    from_place: str
    to_place: str


class DeparturesRequest(BaseModel):
    stop_name: str


class GeocodeRequest(BaseModel):
    name: str
