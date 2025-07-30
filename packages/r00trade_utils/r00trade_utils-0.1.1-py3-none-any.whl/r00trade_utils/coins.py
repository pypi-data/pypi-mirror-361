from typing import Dict, Optional, List, Iterator

from .coin import Coin


class Coins:
    def __init__(self):
        # Используем Dict для type hinting внутренней структуры
        self._coins: Dict[str, Coin] = {}

    def append(self, symbol: str, money: Optional[str] = None):
        """Добавляет монету или обновляет ее список связанных валют."""
        symbol = symbol.upper()
        if symbol not in self._coins:
            self._coins[symbol] = Coin(symbol)

        if money:
            money_upper = money.upper()
            if money_upper:
                 self._coins[symbol].add_money(money_upper)

    def sorted(self) -> 'Coins':
        """
        Возвращает новый объект Coins, содержащий те же монеты,
        отсортированные по символу (алфавитному порядку).
        """
        new_sorted_coins = Coins()
        sorted_keys = sorted(self._coins.keys())
        # Заполняем новый объект Coins в отсортированном порядке
        for key in sorted_keys:
            new_sorted_coins._coins[key] = self._coins[key]
        return new_sorted_coins


    def __getitem__(self, symbol: str) -> Coin:
        """Позволяет получить объект Coin по символу."""
        symbol = symbol.upper()
        if symbol in self._coins:
            return self._coins[symbol]
        else:
            raise KeyError(f"Coin '{symbol}' not found.")

    def __contains__(self, symbol: str) -> bool:
        """Проверяет наличие монеты по символу."""
        return symbol.upper() in self._coins

    def __iter__(self) -> Iterator[Coin]:
        """
        Возвращает итератор для перебора объектов Coin, хранящихся в коллекции.
        Порядок итерации соответствует порядку добавления в современных версиях Python (3.7+).
        Если нужен гарантированно отсортированный порядок, используйте:
        for symbol in coins_obj.get_sorted_symbols(): coin = coins_obj[symbol] ...
        """
        return iter(self.sorted()._coins.values())

    def __len__(self) -> int:
        """Возвращает количество монет в коллекции."""
        return len(self._coins)

    def __str__(self) -> str:
        """Возвращает строковое представление коллекции (символы через запятую)."""
        # Итерируем по значениям (объектам Coin)
        return ', '.join(str(coin) for coin in self._coins.values())

    def __repr__(self) -> str:
        """Возвращает строковое представление для разработчика."""
        # Показываем список ключей (символов)
        return f'Coins({list(self._coins.keys())})'