import argparse
from src.monacoreport.report_builder import build_report, print_report, rider_report


def race_report_cli(argv=None):
    parser = argparse.ArgumentParser(description="Prints a formatted report of race results")
    parser.add_argument("--files", type=str, required=True, help='Path to the folder with log files')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--asc', action='store_true', help='Sorting from fast to slow racer')
    group.add_argument('--desc', action='store_true', help='Sorting from slow to fast racer')

    parser.add_argument("--driver", type=str, help='Displays the rider\'s statistics')

    args = parser.parse_args(argv)
    folder_path = args.files
    valid_result, invalid_result = build_report(folder_path)

    if args.driver:
        name_racer = args.driver
        rider_report(valid_result, invalid_result, name_racer)
    elif args.files:
        result_sort = not args.desc
        print_report(valid_result, invalid_result, sort=result_sort)
    else:
        parser.error("Use --files <folder_path> and --asc | --desc for sorting"
                     "or --files <folder_path> and --driver <name> for statistics on the racer")


if __name__ == '__main__':
    race_report_cli()
