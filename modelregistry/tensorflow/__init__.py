from modelregistry.meta.signature import infer_signature, ModelSignature
from typing import Dict, Any
import os
from modelregistry.utils.config import *
from modelregistry.db.dbstore import DataBase
from modelregistry.meta.signature import infer_signature
from modelregistry.utils.logging import SquirrelLogger
from modelregistry.utils.tmpfiles import *
from modelregistry.utils.s3utils import *
from modelregistry.utils.pip_patch import _CaptureImportedModules
import pickle
import spacy


logger = SquirrelLogger()


def get_signature(input: Any, output=None) -> ModelSignature:
    getSignature = infer_signature(input, output)
    return getSignature


class ModelRegister:
    def __init__(
        self,
        path: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..", "config.yaml")
        ),
    ):
        self.config = load_config(path)
        self.s3client = getClient(self.config["s3"])
        self.db = DataBase(getDbUri(self.config["db"]))

    def saveModel(self, client, data, bucket, model):
        with TempDir() as tmp:
            local_path = tmp.path("tmp")
            os.makedirs(local_path)
            model_path = os.path.join(local_path, "model.spacy")
            data.to_disk(model_path)
            resp = uploadModel(client, bucket, model, model_path, "model.spacy")
            return resp

    def loadModel(self, data):
        with TempDir() as tmp:
            local_path = tmp.path("tmp")
            os.makedirs(local_path)
            model_path = os.path.join(local_path, "model.spacy")
            data.to_disk(model_path)
            return spacy.load(model_path)

    def uploadReqs(self, model, key):
        cap_cm = _CaptureImportedModules()
        with cap_cm:
            self.loadModel(model)
        data = list(cap_cm.imported_modules)
        key = key + "/requirements.txt"
        result = uploadJson(
            self.s3client,
            " ".join((data)),
            str(self.config["bucket"]),
            key,
        )
        return result

    def log_model(
        self, name, model, owner, parameters=None, signature=None, description=None
    ):
        logger.info("Registering the model {0}".format(name))
        try:
            result = self.saveModel(
                self.s3client, model, str(self.config["bucket"]), name
            )
            modelKey = result.get("key")
            version = result.get("version")
            if parameters is not None:
                logger.info("Logging parameters")
                log_parms(
                    self.s3client, parameters, str(self.config["bucket"]), modelKey
                )
            if signature is not None:
                logger.info("Logging Signature")
                data = (
                    signature.to_dict()
                    if isinstance(signature, ModelSignature)
                    else str(signature)
                )
                log_signature(self.s3client, data, self.config["bucket"], modelKey)
            logger.info("Generating requirements.txt")
            self.uploadReqs(model, modelKey)
            logger.info("Updating DB with model")
            self.db.add_model(
                name=name,
                location="s3://{0}/{1}".format(str(self.config["bucket"]), modelKey),
                version=version,
                framework="sklearn",
                owner=owner,
                description=description,
                signature=data,
            )
        except Exception as e:
            raise SquirrelException(e)
