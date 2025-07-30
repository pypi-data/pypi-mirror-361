from datafinder.typed_attributes import *
from datafinder import QueryRunnerBase, DataFrame
from account_finder import AccountRelatedFinder


class TradeFinder:
    __table = 'trade'

    __symbol = StringAttribute('sym', 'VARCHAR', 'trade')
    __price = FloatAttribute('price', 'DOUBLE', 'trade')
    __account = AccountRelatedFinder(Attribute('account_id', 'INT', 'trade'),Attribute('id', 'INT', 'account'))

    @staticmethod
    def symbol() -> StringAttribute:
        return TradeFinder.__symbol

    @staticmethod
    def price() -> FloatAttribute:
        return TradeFinder.__price

    @staticmethod
    def account() -> AccountRelatedFinder:
        return TradeFinder.__account

    @staticmethod
    def find_all(date_from: datetime.date, date_to: datetime.date, as_of: str,
                 display_columns: list[Attribute],
                 filter_op: Operation = NoOperation()) -> DataFrame:
        return QueryRunnerBase.get_runner().select(display_columns, TradeFinder.__table, filter_op)


class TradeRelatedFinder:
    def __init__(self, source: Attribute, target: Attribute):
        join = JoinOperation(source,target)
        self.__symbol = StringAttribute('sym', 'VARCHAR', 'trade', join)
        self.__price = FloatAttribute('price', 'DOUBLE', 'trade', join)
        self.__account = AccountRelatedFinder(Attribute('account_id', 'INT', 'trade'),Attribute('id', 'INT', 'account'))

    def symbol(self) -> StringAttribute:
        return self.__symbol

    def price(self) -> FloatAttribute:
        return self.__price

    def account(self) -> AccountRelatedFinder:
        return self.__account

