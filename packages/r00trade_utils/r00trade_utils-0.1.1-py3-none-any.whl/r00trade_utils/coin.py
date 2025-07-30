class Coin:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self._moneys = set()

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return f'Coin({self.symbol})'

    @property
    def moneys(self):
        return self._moneys

    def add_money(self, money: str):
        if not money in self._moneys:
            self._moneys.add(money)

