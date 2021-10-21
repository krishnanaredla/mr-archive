from datetime import datetime

from sqlalchemy.sql.expression import desc
from modelregistry.db.db_models import ModelRegistry, Base
from modelregistry.db.dbutils import *
import sqlalchemy
import datetime
from typing import Dict


class DataBase:
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.engine = create_sqlalchemy_engine(db_uri)
        Base.metadata.create_all(self.engine, checkfirst=True)
        verify_table_exists(self.engine)
        Base.metadata.bind = self.engine
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.ManagedSessionMaker = get_managed_session_maker(self.Session)

    def _save_to_db(self, session, objs):
        if type(objs) is list:
            session.add_all(objs)
        else:
            session.add(objs)

    def add_model(
        self,
        name: str,
        location: str,
        version: str,
        framework: str,
        owner: str,
        description: str,
        signature: Dict,
    ):
        validate_model_name(name)
        with self.ManagedSessionMaker() as session:
            try:
                new_model = ModelRegistry(
                    name=name,
                    location=location,
                    version=version,
                    framework=framework,
                    owner=owner,
                    description=description,
                    signature=signature,
                    creation_time=datetime.datetime.now(),
                )
                self._save_to_db(session, new_model)
                session.commit()
                session.flush()
            except Exception as e:
                raise SquirrelException(
                    "Error While Inserting new model into DB.Failed with error {0}".format(
                        e
                    )
                )
