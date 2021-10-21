from typing import Dict, Any, Union, TYPE_CHECKING
from modelregistry.meta.schema import *
from modelregistry.meta.inferSchema import _infer_schema
from modelregistry.utils.exception import *
import ast


class ModelSignature(object):
    def __init__(self, inputs: Schema, outputs: Schema = None):
        if not isinstance(inputs, Schema):
            raise TypeError("inputs must Schema, got '{}'".format(type(inputs)))
        if outputs is not None and not isinstance(outputs, Schema):
            raise TypeError(
                "outputs must be either None or mlflow.models.signature.Schema, "
                "got '{}'".format(type(inputs))
            )
        self.inputs = inputs
        self.outputs = outputs

    def to_dict(self) -> Dict[str, Any]:

        return {
            "inputs": self.inputs.to_json(),
            "outputs": self.outputs.to_json() if self.outputs is not None else None,
        }

    @classmethod
    def from_dict(cls, signature_dict: Dict[str, Any]):

        inputs = Schema.from_json(signature_dict["inputs"])
        if "outputs" in signature_dict and signature_dict["outputs"] is not None:
            outputs = Schema.from_json(signature_dict["outputs"])
            return cls(inputs, outputs)
        else:
            return cls(inputs)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ModelSignature)
            and self.inputs == other.inputs
            and self.outputs == other.outputs
        )

    def __repr__(self) -> str:
        return (
            "inputs: \n"
            "  {}\n"
            "outputs: \n"
            "  {}\n".format(repr(self.inputs), repr(self.outputs))
        )


def infer_signature(model_input: Any, model_output=None) -> ModelSignature:

    inputs = _infer_schema(model_input)
    outputs = _infer_schema(model_output) if model_output is not None else None
    return ModelSignature(inputs, outputs)
