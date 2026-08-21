from app.database import Base, engine
from app.models import task, lead, platform_result, cost_log


def init_db():
    Base.metadata.create_all(bind=engine)
