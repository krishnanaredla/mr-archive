from typing import Dict
import json
from modelregistry.utils.exception import SquirrelException


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


def uploadModel(client, bucket: str, model: str, path: str, binary_name: str) -> Dict:
    version = getVersion(client, bucket, model)
    key = "{0}/version={1}".format(model, version)
    try:
        with open(path, "rb") as data:
            client.upload_fileobj(data, bucket, "{0}/{1}".format(key, binary_name))
    except Exception as e:
        raise SquirrelException(e)
    return {"key": key, "version": version}


def uploadFile(client, path: str, bucket: str, key: str) -> Dict:
    try:
        with open(path, "rb") as data:
            client.upload_fileobj(data, Bucket=bucket, Key=key)
    except Exception as e:
        raise SquirrelException(e)
    return {"Status": "Success"}


def uploadJson(client, data, bucket: str, key: str) -> Dict:
    try:
        client.put_object(Body=json.dumps(data), Bucket=bucket, Key=key)
    except Exception as e:
        raise SquirrelException(e)
    return {"Status": "Success"}


def log_parms(client, parms: Dict, bucket: str, key: str):
    key = key + "/config.json"
    result = uploadJson(client, parms, bucket, key)
    return result


def log_signature(client, data: Dict, bucket: str, key: str):
    key = key + "/signature.json"
    result = uploadJson(client, data, bucket, key)
    return result
