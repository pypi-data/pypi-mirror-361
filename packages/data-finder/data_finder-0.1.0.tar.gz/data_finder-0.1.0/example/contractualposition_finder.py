from datafinder.typed_attributes import *
from datafinder import QueryRunnerBase, DataFrame
from instrument_finder import InstrumentRelatedFinder


class ContractualPositionFinder:
    __table = 'contractualposition'

    __quantity = FloatAttribute('QUANTITY', 'DOUBLE', 'contractualposition')
    __counterparty = IntegerAttribute('CPTY_ID', 'INT', 'contractualposition')
    __npv = FloatAttribute('NPV', 'DOUBLE', 'contractualposition')
    __instrument = InstrumentRelatedFinder(Attribute('INSTRUMENT', 'VARCHAR', 'contractualposition'),Attribute('SYM', 'VARCHAR', 'price'))

    @staticmethod
    def quantity() -> FloatAttribute:
        return ContractualPositionFinder.__quantity

    @staticmethod
    def counterparty() -> IntegerAttribute:
        return ContractualPositionFinder.__counterparty

    @staticmethod
    def instrument() -> InstrumentRelatedFinder:
        return ContractualPositionFinder.__instrument

    @staticmethod
    def npv() -> FloatAttribute:
        return ContractualPositionFinder.__npv

    @staticmethod
    def find_all(date_from: datetime.date, date_to: datetime.date, as_of: str,
                 display_columns: list[Attribute],
                 filter_op: Operation = NoOperation()) -> DataFrame:
        return QueryRunnerBase.get_runner().select(display_columns, ContractualPositionFinder.__table, filter_op)


class ContractualPositionRelatedFinder:
    def __init__(self, source: Attribute, target: Attribute):
        join = JoinOperation(source,target)
        self.__quantity = FloatAttribute('QUANTITY', 'DOUBLE', 'contractualposition', join)
        self.__counterparty = IntegerAttribute('CPTY_ID', 'INT', 'contractualposition', join)
        self.__npv = FloatAttribute('NPV', 'DOUBLE', 'contractualposition', join)
        self.__instrument = InstrumentRelatedFinder(Attribute('INSTRUMENT', 'VARCHAR', 'contractualposition'),Attribute('SYM', 'VARCHAR', 'price'))

    def quantity(self) -> FloatAttribute:
        return self.__quantity

    def counterparty(self) -> IntegerAttribute:
        return self.__counterparty

    def instrument(self) -> InstrumentRelatedFinder:
        return self.__instrument

    def npv(self) -> FloatAttribute:
        return self.__npv

