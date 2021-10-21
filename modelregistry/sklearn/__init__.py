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
            model_path = os.path.join(local_path, "model.pkl")
            pickle.dump(data, open(model_path, "wb+"))
            resp = uploadModel(client, bucket, model, model_path, "model.pkl")
            return resp

    def loadModel(self, data):
        with TempDir() as tmp:
            local_path = tmp.path("tmp")
            os.makedirs(local_path)
            model_path = os.path.join(local_path, "model.pkl")
            pickle.dump(data, open(model_path, "wb+"))
            return pickle.load(open(model_path, "rb+"))

    def uploadReqs(self, pyreqs, key):
        # cap_cm = _CaptureImportedModules()
        # with cap_cm:
        #    self.loadModel(model)
        # data = list(cap_cm.imported_modules)
        if isinstance(pyreqs, dict):
            data = pyreqs
        elif isinstance(pyreqs, list):
            data = {_: "" for _ in pyreqs}
        else:
            raise SquirrelException("Unsupported format for python reqs")
        with TempDir() as tmp:
            local_path = tmp.path("tmp")
            os.makedirs(local_path)
            req_path = os.path.join(local_path, "requirements.txt")
            req_file = open(req_path, "w")
            for i in data:
                req_file.write("{0}={1}".format(i, data[i]))
                req_file.write("\n")
            req_file.close()
            key = key + "/requirements.txt"
            result = uploadFile(self.s3client, req_path, str(self.config["bucket"]), key)
        # result = uploadJson(
        #    self.s3client,
        #    " ".join((data)),
        #    str(self.config["bucket"]),
        #    key,
        # )
        return result

    def saved_model(
        self,
        name,
        modelpath,
        owner,
        parameters=None,
        signature=None,
        pyrequirements=None,
        description=None,
    ):
        logger.info("Registering the model {0}".format(name))
        try:
            resp = uploadModel(
                self.s3client, str(self.config["bucket"]), name, modelpath, "model.pkl"
            )
            modelKey = resp.get("key")
            version = resp.get("version")
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
            self.uploadReqs(pyrequirements, modelKey)
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

    def log_model(
        self,
        name,
        model,
        owner,
        parameters=None,
        signature=None,
        pyrequirements=None,
        description=None,
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
            self.uploadReqs(pyrequirements, modelKey)
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
