from src.services import AnalyzeService, DataProvider, FileReader, ReportGenerator, ArgsParser


if __name__ == '__main__':
    data_provider = DataProvider()
    file_reader = FileReader()
    report_generator = ReportGenerator()
    args_parser = ArgsParser()

    main_service = AnalyzeService(
        data_provider=data_provider,
        file_reader=file_reader,
        report_generator=report_generator,
        args_parser=args_parser,
    )

    main_service()
