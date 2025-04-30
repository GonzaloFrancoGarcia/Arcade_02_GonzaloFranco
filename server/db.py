from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Crea (o abre) resultados.db en el directorio actual
engine = create_engine('sqlite:///resultados.db', echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Crea las tablas definidas en models.py si no existen.
    Llamar al arrancar el servidor para inicializar la BD.
    """
    Base.metadata.create_all(bind=engine)

