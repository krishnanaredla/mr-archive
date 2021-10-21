import boto3
import yaml
import os
from typing import Dict
from modelregistry.utils.exception import SquirrelException


def load_config(path: str = None) -> Dict:
    if not path:
        path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        )
    with open(path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise FileNotFoundError(exc)
    return config


def getClient(parms: Dict):
    return boto3.client("s3", **parms)


def getDbUri(parms: Dict):
    try:
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**parms)
    except Exception as e:
        raise SquirrelException(
            "Failed while creating DB uri with reason {0}".format(e)
        )
