from typing import Protocol, List, Dict, Any
from src.schemas import GDPRecord, CountryAverage, ReportConfig


class IArgsParser(Protocol):
    # args: List[Argument]

    def parse(self) -> ReportConfig:
        """Получает аргументы при запуске кода"""
        ...

    # def add_arg(self, arg: Argument):
    #     """Добавляет аргумент"""
    #     ...


class IFileReader(Protocol):
    def read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Читает CSV файл и возвращает список словарей"""
        ...

    def write_csv(self, file_path: str, data: List[List[Any]], headers: List[str]) -> None:
        """Записывает данные в CSV файл"""
        ...


class IDataProvider(Protocol):
    def get_gdp_records(self, file_paths: List[str]) -> List[GDPRecord]:
        """Извлекает записи ВВП из файлов"""
        ...


class IReportGenerator(Protocol):
    def generate(self, records: List[GDPRecord]) -> List[CountryAverage]:
        """Генерирует отчет на основе записей"""
        ...

    def export(self, report_data: List[CountryAverage], output_path: str) -> None:
        """Экспортирует отчет в файл"""
        ...
