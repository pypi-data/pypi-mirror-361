from datafinder.typed_attributes import *
from datafinder import QueryRunnerBase, DataFrame


class InstrumentFinder:
    __table = 'price'

    __symbol = StringAttribute('SYM', 'VARCHAR', 'price')
    __price = FloatAttribute('PRICE', 'DOUBLE', 'price')

    @staticmethod
    def symbol() -> StringAttribute:
        return InstrumentFinder.__symbol

    @staticmethod
    def price() -> FloatAttribute:
        return InstrumentFinder.__price

    @staticmethod
    def find_all(date_from: datetime.date, date_to: datetime.date, as_of: str,
                 display_columns: list[Attribute],
                 filter_op: Operation = NoOperation()) -> DataFrame:
        return QueryRunnerBase.get_runner().select(display_columns, InstrumentFinder.__table, filter_op)


class InstrumentRelatedFinder:
    def __init__(self, source: Attribute, target: Attribute):
        join = JoinOperation(source,target)
        self.__symbol = StringAttribute('SYM', 'VARCHAR', 'price', join)
        self.__price = FloatAttribute('PRICE', 'DOUBLE', 'price', join)

    def symbol(self) -> StringAttribute:
        return self.__symbol

    def price(self) -> FloatAttribute:
        return self.__price

