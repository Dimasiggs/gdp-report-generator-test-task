import argparse
from collections import defaultdict
from typing import Any, List, Dict, Optional
import csv
import os

from tabulate import tabulate

from src.interfaces import IDataProvider, IFileReader, IReportGenerator, IArgsParser
from src.schemas import ReportConfig, GDPRecord, CountryAverage


class AnalyzeService:
    def __init__(
            self,
            data_provider: IDataProvider,
            file_reader: IFileReader,
            report_generator: IReportGenerator,
            args_parser: IArgsParser
    ) -> None:
        self.data_provider = data_provider
        self.file_reader = file_reader
        self.report_generator = report_generator
        self.args_parser = args_parser

    def __call__(self) -> None:
        """Полный процесс генерации отчета"""
        # Парсинг аргументов
        config = self.args_parser.parse()

        # Получение данных через DataProvider
        records = self.data_provider.get_gdp_records(config.input_files)

        if not records:
            print("No valid records found to process.")
            return

        # Генерация отчета
        report_data = self.report_generator.generate(records)

        # Экспорт в файл (Если надо будет реализовать)
        # self.report_generator.export(report_data, output_path)
        # print(f"Report exported to: {output_path}")

        # Вывод отчета в консоль
        table_data = [(i + 1, report_data[i].country, report_data[i].average_gdp) for i in range(len(report_data))]

        print("\nGenerated Report:")
        print(tabulate(table_data, headers=['№', 'country', 'gdp'], tablefmt='grid'))


class ArgsParser(IArgsParser):
    def parse(self) -> ReportConfig:
        parser = argparse.ArgumentParser()
        parser.add_argument('--files', nargs='+', required=True)
        parser.add_argument('--report', required=True)

        args = parser.parse_args()

        result = ReportConfig(
            input_files=args.files,
            report_type=args.report,
        )

        return result


class FileReader(IFileReader):
    def read_csv(self, file_path: str) -> List[Dict]:
        """Чтение CSV файла в список словарей"""

        with open(file_path, "r", newline="") as file:
            reader = csv.DictReader(file)
            return list(reader)

    def write_csv(self, file_path: str, data: List[List[Any]], headers: List[str]) -> None:
        """Запись данных в CSV файл"""
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)


class ReportGenerator(IReportGenerator):
    def generate(self, records: List[GDPRecord]) -> List[CountryAverage]:
        """Генерирует отчет на основе записей"""
        countries_gdp: dict[str, List[float]] = defaultdict(list)

        # Агрегация данных по странам
        for record in records:
            countries_gdp[record.country].append(record.gdp)

        result: List[CountryAverage] = []

        # Расчет среднего значения
        for country, gdp_list in countries_gdp.items():
            if not gdp_list:
                continue
            avg_val = sum(gdp_list) / len(gdp_list)
            result.append(CountryAverage(
                country=country,
                average_gdp=round(avg_val, 2)
            ))

        # Сортировка по убыванию среднего ВВП
        result.sort(key=lambda x: x.average_gdp, reverse=True)

        return result

    def export(self, report_data: List[CountryAverage], output_path: str) -> None:
        """
        Экспортирует отчет в файл (CSV).
        """
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["country", "average_gdp"])
            writer.writeheader()
            for row in report_data:
                writer.writerow(row.model_dump())


class DataProvider(IDataProvider):
    def get_gdp_records(self, file_paths: List[str]) -> List[GDPRecord]:
        """Извлекает записи ВВП из CSV файлов."""
        records: List[GDPRecord] = []

        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            try:
                with open(file_path, "r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file)

                    for row_num, row in enumerate(reader, start=2):
                        try:
                            record = self._parse_row(row, file_path, row_num)
                            if record:
                                records.append(record)
                        except (KeyError, ValueError) as e:
                            print(f"Error parsing row {row_num} in {file_path}: {e}")
                            continue

            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue

        return records

    def _parse_row(self, row: dict, file_path: str, row_num: int) -> Optional[GDPRecord]:
        """Парсит одну строку CSV в объект GDPRecord."""
        if "country" not in row or "gdp" not in row:
            raise KeyError("Missing required columns: 'country' or 'gdp'")

        # Очистка и валидация данных
        country = row["country"].strip()
        if not country:
            raise ValueError("Empty country name")

        gdp_str = row["gdp"]
        gdp = float(gdp_str)

        # Год - опциональное поле
        year = None
        if "year" in row and row["year"]:
            try:
                year = int(row["year"])
            except ValueError:
                print(f"Warning: Invalid year '{row['year']}' at row {row_num} in {file_path}")

        return GDPRecord(
            country=country,
            year=year,
            gdp=gdp
        )
