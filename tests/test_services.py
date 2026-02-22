import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services import (
    ArgsParser, FileReader, ReportGenerator,
    DataProvider, AnalyzeService
)
from src.schemas import ReportConfig, GDPRecord, CountryAverage


class TestArgsParser:
    @patch('src.services.argparse.ArgumentParser')
    def test_parse_arguments(self, mock_parser_class):
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = MagicMock(
            files=["file1.csv", "file2.csv"],
            report="average-gdp"
        )
        mock_parser_class.return_value = mock_parser

        parser = ArgsParser()
        config = parser.parse()

        assert isinstance(config, ReportConfig)
        assert config.input_files == ["file1.csv", "file2.csv"]
        assert config.report_type == "average-gdp"


class TestFileReader:
    def test_read_csv_success(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("country,year,gdp\nUSA,2020,21427.7\nUK,2020,2827.1")

        reader = FileReader()
        data = reader.read_csv(str(csv_file))

        assert len(data) == 2
        assert data[0]["country"] == "USA"
        assert data[0]["gdp"] == "21427.7"

    def test_read_csv_empty_file(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("country,year,gdp\n")

        reader = FileReader()
        data = reader.read_csv(str(csv_file))

        assert len(data) == 0

    def test_read_csv_file_not_found(self):
        reader = FileReader()
        with pytest.raises(FileNotFoundError):
            reader.read_csv("nonexistent.csv")

    def test_write_csv(self, tmp_path):
        csv_file = tmp_path / "output.csv"
        data = [["USA", 2020, 21427.7], ["UK", 2020, 2827.1]]
        headers = ["country", "year", "gdp"]

        reader = FileReader()
        reader.write_csv(str(csv_file), data, headers)

        assert csv_file.exists()
        content = csv_file.read_text()
        assert "country" in content
        assert "USA" in content


class TestReportGenerator:
    def test_generate_report(self):
        records = [
            GDPRecord(country="USA", year=2020, gdp=21427.7),
            GDPRecord(country="USA", year=2021, gdp=23319.0),
            GDPRecord(country="UK", year=2020, gdp=2827.1),
        ]

        generator = ReportGenerator()
        result = generator.generate(records)

        assert len(result) == 2
        assert result[0].country == "USA"
        assert result[0].average_gdp == round((21427.7 + 23319.0) / 2, 2)
        assert result[1].country == "UK"

    def test_generate_report_empty_records(self):
        generator = ReportGenerator()
        result = generator.generate([])

        assert len(result) == 0

    def test_generate_report_sorting(self):
        records = [
            GDPRecord(country="A", year=2020, gdp=100.0),
            GDPRecord(country="B", year=2020, gdp=300.0),
            GDPRecord(country="C", year=2020, gdp=200.0),
        ]

        generator = ReportGenerator()
        result = generator.generate(records)

        assert result[0].country == "B"
        assert result[1].country == "C"
        assert result[2].country == "A"

    def test_export_report(self, tmp_path):
        output_file = tmp_path / "report.csv"
        report_data = [
            CountryAverage(country="USA", average_gdp=22000.0),
            CountryAverage(country="UK", average_gdp=2800.0),
        ]

        generator = ReportGenerator()
        generator.export(report_data, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "country" in content
        assert "average_gdp" in content
        assert "USA" in content


class TestDataProvider:
    def test_get_gdp_records(self, tmp_path):
        csv_file = tmp_path / "gdp.csv"
        csv_file.write_text("country,year,gdp\nUSA,2020,21427.7\nUK,2020,2827.1")

        provider = DataProvider()
        records = provider.get_gdp_records([str(csv_file)])

        assert len(records) == 2
        assert records[0].country == "USA"
        assert records[0].gdp == 21427.7

    def test_get_gdp_records_file_not_found(self, capsys):
        provider = DataProvider()
        records = provider.get_gdp_records(["nonexistent.csv"])

        assert len(records) == 0
        captured = capsys.readouterr()
        assert "Warning: File not found" in captured.out

    def test_get_gdp_records_invalid_row(self, tmp_path, capsys):
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("country,year,gdp\nUSA,2020,invalid_gdp")

        provider = DataProvider()
        records = provider.get_gdp_records([str(csv_file)])

        assert len(records) == 0
        captured = capsys.readouterr()
        assert "Error parsing row" in captured.out

    def test_get_gdp_records_missing_columns(self, tmp_path, capsys):
        csv_file = tmp_path / "missing.csv"
        csv_file.write_text("name,year,value\nUSA,2020,100")

        provider = DataProvider()
        records = provider.get_gdp_records([str(csv_file)])

        assert len(records) == 0
        captured = capsys.readouterr()
        assert "Missing required columns" in captured.out

    def test_get_gdp_records_optional_year(self, tmp_path):
        csv_file = tmp_path / "no_year.csv"
        csv_file.write_text("country,gdp\nUSA,21427.7")

        provider = DataProvider()
        records = provider.get_gdp_records([str(csv_file)])

        assert len(records) == 1
        assert records[0].year is None

    def test_get_gdp_records_multiple_files(self, tmp_path):
        file1 = tmp_path / "file1.csv"
        file1.write_text("country,year,gdp\nUSA,2020,21427.7")

        file2 = tmp_path / "file2.csv"
        file2.write_text("country,year,gdp\nUK,2020,2827.1")

        provider = DataProvider()
        records = provider.get_gdp_records([str(file1), str(file2)])

        assert len(records) == 2


class TestAnalyzeService:
    def test_analyze_service_initialization(self):
        data_provider = Mock()
        file_reader = Mock()
        report_generator = Mock()
        args_parser = Mock()

        service = AnalyzeService(
            data_provider=data_provider,
            file_reader=file_reader,
            report_generator=report_generator,
            args_parser=args_parser
        )

        assert service.data_provider == data_provider
        assert service.file_reader == file_reader
        assert service.report_generator == report_generator
        assert service.args_parser == args_parser

    def test_analyze_service_call(self, capsys):
        config = ReportConfig(input_files=["file.csv"], report_type="average-gdp")
        records = [GDPRecord(country="USA", year=2020, gdp=21427.7)]
        report_data = [CountryAverage(country="USA", average_gdp=21427.7)]

        args_parser = Mock()
        args_parser.parse.return_value = config

        data_provider = Mock()
        data_provider.get_gdp_records.return_value = records

        report_generator = Mock()
        report_generator.generate.return_value = report_data

        service = AnalyzeService(
            data_provider=data_provider,
            file_reader=Mock(),
            report_generator=report_generator,
            args_parser=args_parser
        )

        service()

        args_parser.parse.assert_called_once()
        data_provider.get_gdp_records.assert_called_once_with(["file.csv"])
        report_generator.generate.assert_called_once_with(records)
        captured = capsys.readouterr()
        assert "Generated Report" in captured.out

    def test_analyze_service_no_records(self, capsys):
        config = ReportConfig(input_files=["file.csv"], report_type="average-gdp")

        args_parser = Mock()
        args_parser.parse.return_value = config

        data_provider = Mock()
        data_provider.get_gdp_records.return_value = []

        service = AnalyzeService(
            data_provider=data_provider,
            file_reader=Mock(),
            report_generator=Mock(),
            args_parser=args_parser
        )

        service()

        captured = capsys.readouterr()
        assert "No valid records found" in captured.out
