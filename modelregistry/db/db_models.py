from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class ModelRegistry(Base):
    __tablename__ = "modelregistry"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    version = Column(String)
    framework = Column(String)
    owner = Column(String)
    description = Column(String)
    signature = Column(JSON)
    creation_time = Column(TIMESTAMP)

    def __repr__(self):
        return """<ModelRegistry(name='{}', location='{}', version={}, framework={}, owner={}, description={}, signature={}, creation_time={})>""".format(
            self.name,
            self.location,
            self.version,
            self.framework,
            self.owner,
            self.description,
            self.signature,
            self.creation_time,
        )
