import pytest
from src.schemas import ReportConfig, GDPRecord, CountryAverage


class TestReportConfig:
    def test_create_report_config(self):
        config = ReportConfig(
            input_files=["file1.csv", "file2.csv"],
            report_type="average-gdp"
        )
        assert config.input_files == ["file1.csv", "file2.csv"]
        assert config.report_type == "average-gdp"

    def test_report_config_default_report_type(self):
        config = ReportConfig(input_files=["file.csv"])
        assert config.report_type == "average-gdp"

    def test_report_config_validation(self):
        with pytest.raises(Exception):
            ReportConfig(input_files="not_a_list")


class TestGDPRecord:
    def test_create_gdp_record(self):
        record = GDPRecord(country="USA", year=2020, gdp=21427.7)
        assert record.country == "USA"
        assert record.year == 2020
        assert record.gdp == 21427.7

    def test_gdp_record_validation_empty_country(self):
        with pytest.raises(ValueError, match='Country name cannot be empty'):
            GDPRecord(country="", year=2020, gdp=100.0)

    def test_gdp_record_validation_whitespace_country(self):
        with pytest.raises(ValueError, match='Country name cannot be empty'):
            GDPRecord(country="   ", year=2020, gdp=100.0)

    def test_gdp_record_validation_negative_gdp(self):
        with pytest.raises(ValueError, match='GDP cannot be negative'):
            GDPRecord(country="USA", year=2020, gdp=-100.0)

    def test_gdp_record_optional_year(self):
        record = GDPRecord(country="USA", gdp=21427.7)
        assert record.year is None

    def test_gdp_record_country_stripped(self):
        record = GDPRecord(country="  USA  ", year=2020, gdp=21427.7)
        assert record.country == "USA"


class TestCountryAverage:
    def test_create_country_average(self):
        avg = CountryAverage(country="USA", average_gdp=20000.5)
        assert avg.country == "USA"
        assert avg.average_gdp == 20000.5

    def test_country_average_rounding(self):
        avg = CountryAverage(country="USA", average_gdp=20000.555)
        assert avg.average_gdp == 20000.555
