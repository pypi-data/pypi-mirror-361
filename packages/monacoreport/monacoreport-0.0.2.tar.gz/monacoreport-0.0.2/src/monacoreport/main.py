from src.monacoreport.report_builder import build_report, print_report

if __name__ == '__main__':
    valid_result, invalid_result = build_report('data')
    print_report(valid_result, invalid_result)
