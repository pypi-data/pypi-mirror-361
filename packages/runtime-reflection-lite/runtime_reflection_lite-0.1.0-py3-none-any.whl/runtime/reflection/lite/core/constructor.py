from typing import Any

from runtime.reflection.lite.core.signature import Signature
from runtime.reflection.lite.core.method import Method
from runtime.reflection.lite.core.function_kind import FunctionKind
from runtime.reflection.lite.core.undefined import Undefined
from runtime.reflection.lite.core.member_type import MemberType
from runtime.reflection.lite.core.types import FUNCTION_AND_METHOD_TYPES

class Constructor(Method):
    __slots__ = [ ]

    def __init__(
        self,
        bound_cls: type[Any],
        signature: Signature,
        reflected: FUNCTION_AND_METHOD_TYPES
    ):
        super().__init__(MemberType.METHOD, FunctionKind.CONSTRUCTOR, bound_cls, signature, False, reflected)

    @property
    def return_type(self) -> type[Any]:
        return Undefined