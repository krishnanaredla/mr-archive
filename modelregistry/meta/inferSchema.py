from modelregistry.meta.schema import *
from modelregistry.utils.exception import *
import numpy as np


class TensorsNotSupportedException(SquirrelException):
    def __init__(self, msg):
        super().__init__(
            "Multidimensional arrays (aka tensors) are not supported. " "{}".format(msg)
        )


def _get_tensor_shape(data: np.ndarray, variable_dimension: Optional[int] = 0) -> tuple:

    if not isinstance(data, np.ndarray):
        raise TypeError("Expected numpy.ndarray, got '{}'.".format(type(data)))
    variable_input_data_shape = data.shape
    if variable_dimension is not None:
        try:
            variable_input_data_shape = list(variable_input_data_shape)
            variable_input_data_shape[variable_dimension] = -1
        except IndexError:
            raise SquirrelException(
                "The specified variable_dimension {0} is out of bounds with"
                "respect to the number of dimensions {1} in the input dataset".format(
                    variable_dimension, data.ndim
                )
            )
    return tuple(variable_input_data_shape)


def clean_tensor_type(dtype: np.dtype):
    if not isinstance(dtype, np.dtype):
        raise TypeError(
            "Expected `type` to be instance of `{0}`, received `{1}`".format(
                np.dtype, dtype.__class__
            )
        )

    # Special casing for np.str_ and np.bytes_
    if dtype.char == "U":
        return np.dtype("str")
    elif dtype.char == "S":
        return np.dtype("bytes")
    return dtype


def _infer_numpy_dtype(dtype) -> DataType:
    supported_types = np.dtype

    # noinspection PyBroadException
    try:
        from pandas.core.dtypes.base import ExtensionDtype

        supported_types = (np.dtype, ExtensionDtype)
    except ImportError:
        # This version of pandas does not support extension types
        pass
    if not isinstance(dtype, supported_types):
        raise TypeError(
            "Expected numpy.dtype or pandas.ExtensionDtype, got '{}'.".format(
                type(dtype)
            )
        )

    if dtype.kind == "b":
        return DataType.boolean
    elif dtype.kind == "i" or dtype.kind == "u":
        if dtype.itemsize < 4 or (dtype.kind == "i" and dtype.itemsize == 4):
            return DataType.integer
        elif dtype.itemsize < 8 or (dtype.kind == "i" and dtype.itemsize == 8):
            return DataType.long
    elif dtype.kind == "f":
        if dtype.itemsize <= 4:
            return DataType.float
        elif dtype.itemsize <= 8:
            return DataType.double

    elif dtype.kind == "U":
        return DataType.string
    elif dtype.kind == "S":
        return DataType.binary
    elif dtype.kind == "O":
        raise Exception(
            "Can not infer np.object without looking at the values, call "
            "_map_numpy_array instead."
        )
    elif dtype.kind == "M":
        return DataType.datetime
    raise SquirrelException(
        "Unsupported numpy data type '{0}', kind '{1}'".format(dtype, dtype.kind)
    )


def _infer_pandas_column(col: pd.Series) -> DataType:
    if not isinstance(col, pd.Series):
        raise TypeError("Expected pandas.Series, got '{}'.".format(type(col)))
    if len(col.values.shape) > 1:
        raise SquirrelException(
            "Expected 1d array, got array with shape {}".format(col.shape)
        )

    class IsInstanceOrNone(object):
        def __init__(self, *args):
            self.classes = args
            self.seen_instances = 0

        def __call__(self, x):
            if x is None:
                return True
            elif any(map(lambda c: isinstance(x, c), self.classes)):
                self.seen_instances += 1
                return True
            else:
                return False

    if col.dtype.kind == "O":
        col = col.infer_objects()
    if col.dtype.kind == "O":
        is_binary_test = IsInstanceOrNone(bytes, bytearray)
        if all(map(is_binary_test, col)) and is_binary_test.seen_instances > 0:
            return DataType.binary
        elif pd.api.types.is_string_dtype(col):
            return DataType.string
        else:
            raise SquirrelException(
                "Unable to map 'np.object' type to MLflow DataType. np.object can"
                "be mapped iff all values have identical data type which is one "
                "of (string, (bytes or byterray),  int, float)."
            )
    else:

        return _infer_numpy_dtype(col.dtype)


def _infer_schema(input):
    if isinstance(input, pd.DataFrame):
        schema = Schema(
            [
                ColSpec(type=_infer_pandas_column(input[col]), name=col)
                for col in input.columns
            ]
        )
        return schema
    elif isinstance(input, np.ndarray):
        schema = Schema(
            [
                TensorSpec(
                    type=clean_tensor_type(input.dtype), shape=_get_tensor_shape(input)
                )
            ]
        )
        return schema
    else:
        SquirrelException("Invalid Data type")
