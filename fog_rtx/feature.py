from typing import Any, List, Optional, Tuple
from sqlalchemy import Integer, String, LargeBinary, Float
from fog_rtx.database.utils import type_py2sql, type_np2sql
import numpy as np 


SUPPORTED_DTYPES = [
    "null",
    "bool",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float16",
    "float32",
    "float64",
    "timestamp(s)",
    "timestamp(ms)",
    "timestamp(us)",
    "timestamp(ns)",
    "timestamp(s, tz)",
    "timestamp(ms, tz)",
    "timestamp(us, tz)",
    "timestamp(ns, tz)",
    "binary",
    "large_binary",
    "string",
    "large_string",
]


class FeatureType:
    """
    class for feature definition and conversions
    """

    def __init__(
        self,
        dtype: Optional[str] = None,
        shape: Any = None,
        tf_feature_spec = None,
        data = None, 
    ) -> None:
        # scalar: (), vector: (n,), matrix: (n,m)

        # if self.dtype == "double":  # fix inferred type
        #     self.dtype = "float64"
        # if self.dtype == "float":  # fix inferred type
        #     self.dtype = "float32"
        if data is not None:
            self.from_data(data)
        elif tf_feature_spec is not None:
            self.from_tf_feature_type(tf_feature_spec)
        elif dtype is not None:
            self._set(dtype, shape)
        else:
            raise ValueError("Either dtype or data must be provided")

    def __str__(self):
        return f"dtype={self.dtype}, shape={self.shape})"

    def __repr__(self):
        return self.__str__()

    def _set(self, dtype: str, shape: Any):
        if dtype not in SUPPORTED_DTYPES:
            raise ValueError(f"Unsupported dtype: {dtype}")
        if shape is not None and not isinstance(shape, tuple):
            raise ValueError(f"Shape must be a tuple: {shape}")
        self.dtype = dtype
        self.shape = shape


    def from_tf_feature_type(self, tf_feature_spec):
        """
        Convert from tf feature
        """
        shape = tf_feature_spec.shape
        np_dtype = tf_feature_spec.np_dtype
        self._set(str(np_dtype), shape)
        # self.dtype = str(self.np_dtype)
        # self.is_np = True
        return self
    
    def from_data(self, data: Any):
        """
        Infer feature type from the provided data.
        """
        if isinstance(data, np.ndarray):
            self._set(data.dtype.name, data.shape)
        elif isinstance(data, list):
            dtype = type(data[0]).__name__
            shape = (len(data),)
            self._set(dtype.name, shape)
        else:
            dtype = type(data).__name__
            shape = ()
            self._set(dtype.name, shape)
        return self

    def to_tf_feature_type(self): 
        """
        Convert to tf feature
        """
        from tensorflow_datasets.core.features import Tensor, Image, FeaturesDict, Scalar, Text
        if len(self.shape) == 0:
            if self.dtype == "string":
                return Text()
            else:
                return Scalar(dtype=self.dtype)
        elif len(self.shape) >= 1:
            return Tensor(shape=self.shape, dtype=self.dtype)
        else:
            raise ValueError(f"Unsupported conversion to tf feature: {self}")

    def to_sql_type(self):
        """
        Convert to sql type
        """
        if self.is_np:
            return LargeBinary
        else:
            try:
                return type_np2sql(self.dtype)
            except:
                return LargeBinary
    
    def to_pld_storage_type(self):
        if len(self.shape) == 0:
            if self.dtype == "string":
                return "string"
            else:
                return self.dtype
        else:
            return "object"