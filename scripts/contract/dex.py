class DEX:
    def __init__(self, address: str, name: str, estim: str=None, avail: str=None):
        self.__address = address
        self.__name = name
        self.__estim = estim if estim else address
        self.__avail = avail if avail else address

    def get_address(self) -> str:
        return self.__address
    
    def get_estim(self) -> str:
        return self.__estim
    
    def get_avail(self) -> str:
        return self.__avail
    
    def __str__(self) -> str:
        return self.__name