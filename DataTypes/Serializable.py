import abc



class Serializable():


    @abc.abstractmethod
    def pack(self) -> bytes:
        raise NotImplementedError

    def __new__(cls, x):
        return super().__new__(cls, x)