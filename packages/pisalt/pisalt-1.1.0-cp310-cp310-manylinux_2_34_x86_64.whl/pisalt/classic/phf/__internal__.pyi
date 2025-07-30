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
    def hash(self, password: str) -> str:
        ...
    #
    def verify(self, password: str, hash: str) -> bool:
        ...
    #
    @staticmethod
    def statichash(
        password: str,
        *,
        algorithm: Algorithm.ArgonTwo | str = Algorithm.ArgonTwo.ID,
        version: int = 19,
        timecost: int = 3,
        memorycost: int = 65536,
        parallelism: int = 4,
        hashlen: int = 32,
        saltlen: int = 16
    ) -> str:
        ...
    #
    @staticmethod
    def staticverify(password: str, hash: str) -> bool:
        ...

class Bcrypt:
    def __init__(
            self,
            *,
            cost: int = 12
        ) -> None:
        ...
    #
    def hash(self, password: str) -> str:
        ...
    #
    def verify(self, password: str, hash: str) -> bool:
        ...
    #
    @staticmethod
    def statichash(
        password: str,
        *,
        cost: int = 12
    ) -> str:
        ...
    #
    @staticmethod
    def staticverify(password: str, hash: str) -> bool:
        ...
