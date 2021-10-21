"""from squirrel.utils import signature
import boto3
import json
import tempfile
import shutil
import os
from typing import Dict, Any
import pickle
from squirrel.utils.tmpfiles import *
from squirrel.meta.signature import *
from squirrel.utils.pip_patch import *
from squirrel.utils.pip_patch import _CaptureImportedModules
import importlib

s3_parms = {
    "endpoint_url": "http://localhost:4566",
    "aws_access_key_id": "dev",
    "aws_secret_access_key": "dev",
}

bucket = "models"




def getClient(parms: Dict):
    return boto3.client("s3", **parms)


def getVersion(client, bucket, model) -> int:
    existingkeys = []
    theobjects = client.list_objects_v2(
        Bucket=bucket, Prefix=model, StartAfter=model + "/"
    )
    try:
        for object in theobjects["Contents"]:
            existingkeys.append(object["Key"])
    except KeyError as e:
        print("New Model")
        return 1
    return (
        max(list(map(lambda x: int(x.split("/")[-2].split("=")[-1]), existingkeys))) + 1
    )


def uploadModel(client, bucket: str, model: str, path: str) -> Dict:
    version = getVersion(client, bucket, model)
    key = "{0}/version={1}".format(model, version)
    try:
        with open(path, "rb") as data:
            client.upload_fileobj(data, bucket, "{0}/model.pkl".format(key))
    except Exception as e:
        print(e)
    return {"key": key, "version": version}


def uploadJson(client, data, bucket: str, key: str) -> Dict:
    try:
        client.put_object(Body=json.dumps(data), Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
    return {"Status": "Success"}


def saveModel(client, data, bucket, model):
    with TempDir() as tmp:
        local_path = tmp.path("tmp")
        os.makedirs(local_path)
        model_path = os.path.join(local_path, "model.pkl")
        pickle.dump(data, open(model_path, "wb+"))
        resp = uploadModel(client, bucket, model, model_path)
        return resp


def log_model(model_name: str, model_binary):
    client = getClient(s3_parms)
    result = saveModel(client, model_binary, bucket, model_name)
    return result


def log_parms(parms: Dict, key: str):
    client = getClient(s3_parms)
    key = key + "/config.json"
    result = uploadJson(client, parms, bucket, key)
    return result


def get_signature(input: Any, output=None) -> str:
    getSignature = infer_signature(input, output)
    return getSignature


def log_signature(data: str, key: str):
    client = getClient(s3_parms)
    key = key + "/signature.json"
    result = uploadJson(client, str(data), bucket, key)
    return result


def loadModel(data):
    with TempDir() as tmp:
        local_path = tmp.path("tmp")
        os.makedirs(local_path)
        model_path = os.path.join(local_path, "model.pkl")
        pickle.dump(data, open(model_path, "wb+"))
        return pickle.load(open(model_path, "rb+"))


def uploadReqs(model, key):
    cap_cm = _CaptureImportedModules()
    with cap_cm:
        loadModel(model)
    data = list(cap_cm.imported_modules)
    client = getClient(s3_parms)
    key = key + "/requirements.txt"
    result = uploadJson(client, data, bucket, key)
    return result


def ModelRegister(model_name, model, parms, signature):
    print("Registering the Model")
    try:
        result = log_model(model_name, model)
        key = result.get("key")
        log_parms(parms, key)
        log_signature(signature, key)
        uploadReqs(model, key)
    except Exception as e:
        print(e)
"""
