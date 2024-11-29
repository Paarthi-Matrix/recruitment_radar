from db import Base, engine
from models import models
from models import company
from models import factor
from models import user
from models import summary
from models import candidate

# Create tables
Base.metadata.create_all(bind=engine)

