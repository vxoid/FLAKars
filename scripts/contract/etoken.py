class Token:
    def __init__(self, address: str, symbol: str):
        self.__address = address
        self.__symbol = symbol

    def get_address(self) -> str:
        return self.__address
    
    def __str__(self) -> str:
        return self.__symbol