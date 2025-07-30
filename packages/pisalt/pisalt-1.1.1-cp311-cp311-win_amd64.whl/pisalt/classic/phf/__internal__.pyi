# IMPORT
from pisalt import __internal__ as _internal # type: ignore
import enum as _enum

# MAIN
class Algorithm:
    class ArgonTwo(_enum.Enum):
        I = "i"
        D = "d"
        ID = "id"

class ArgonTwo:
    def __init__(
            self,
            algorithm: Algorithm.ArgonTwo = Algorithm.ArgonTwo.ID,
            *,
            version: int = 19,
            timecost: int = 3,
            memorycost: int = 65536,
            parallelism: int = 4,
            hashlen: int = 32,
            saltlen: int = 16
        ) -> None:
        ...
    #
    def hash(self, password: bytes) -> bytes:
        ...
    #
    def verify(self, password: bytes, hash: bytes) -> bool:
        ...
    #
    @staticmethod
    def statichash(
        password: bytes,
        *,
        algorithm: Algorithm.ArgonTwo = Algorithm.ArgonTwo.ID,
        version: int = 19,
        timecost: int = 3,
        memorycost: int = 65536,
        parallelism: int = 4,
        hashlen: int = 32,
        saltlen: int = 16
    ) -> bytes:
        ...
    #
    @staticmethod
    def staticverify(password: bytes, hash: bytes) -> bool:
        ...

class Bcrypt:
    def __init__(
            self,
            cost: int = 12
        ) -> None:
        ...
    #
    def hash(self, password: bytes) -> bytes:
        ...
    #
    def verify(self, password: bytes, hash: bytes) -> bool:
        ...
    #
    @staticmethod
    def statichash(
        password: bytes,
        *,
        cost: int = 12
    ) -> bytes:
        ...
    #
    @staticmethod
    def staticverify(password: bytes, hash: bytes) -> bool:
        ...
