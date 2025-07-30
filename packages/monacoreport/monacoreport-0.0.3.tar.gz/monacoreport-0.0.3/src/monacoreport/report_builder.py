import os
from monacoreport.parser import parse_time_start_or_end, parse_name_racer_and_brand
from monacoreport.handlers import lap_time_for_rider, format_lap_time


def get_file_paths_from_folder(folder: str) -> tuple[str, str, str]:
    """Returns full paths to the three log files given a folder path.

    Args:
        folder (str): Path to the folder with files.

    Returns:
        tuple:
            - str: Full path to file start.log.
            - str: Full path to file end.log.
            - str: Full path to file abbreviations.txt.

    Raises:
        FileNotFoundError: If the directory is not found.
    """
    base_dir = os.path.dirname(__file__)
    try:
        data_dir = os.path.join(base_dir, '..', folder)
    except FileNotFoundError:
        raise FileNotFoundError(f'Directory \'{folder}\' not found')
    start_path = os.path.join(data_dir, 'start.log')
    end_path = os.path.join(data_dir, 'end.log')
    abbreviations_path = os.path.join(data_dir, 'abbreviations.txt')
    return start_path, end_path, abbreviations_path


def build_report(folder: str) -> tuple[list, list]:
    """
    Builds a result of lap times for each racer based on parsed log files.

    Reads start and end times from log files, parses racer names and car brands,
    calculates lap times, separates valid and invalid results.

    Args:
        folder (str): Path to the folder with files.

    Returns:
        tuple:
            - list: Valid results containing racer name, car brand and lap time.
            - list: Invalid results containing racer name, car brand, and error message.

    Raises:
        FileNotFoundError: If any of the required files are missing.
        ValueError: If racer abbreviation from end log is not found in start log.
    """
    start_path, end_path, abbreviations_path = get_file_paths_from_folder(folder)
    try:
        time_start = parse_time_start_or_end(start_path)
    except FileNotFoundError:
        raise FileNotFoundError('File with race start time not found')
    try:
        time_end = parse_time_start_or_end(end_path)
    except FileNotFoundError:
        raise FileNotFoundError('File with race end time not found')
    try:
        name_racer, car_brand = parse_name_racer_and_brand(abbreviations_path)
    except FileNotFoundError:
        raise FileNotFoundError('Racing abbreviations file not found')
    lap_time = lap_time_for_rider(time_start, time_end)

    valid_result = []
    invalid_result = []
    for key, value in sorted(lap_time.items(), key=lambda item: item[1]):
        if value.days < 0:
            invalid_result.append((name_racer[key], car_brand[key], 'Race time cannot be negative'))
        else:
            valid_result.append((name_racer[key], car_brand[key], value))
    return valid_result, invalid_result


def rider_report(valid_result: list, invalid_result: list, name: str) -> None:
    """Displays the rider's statistics

    Args:
        valid_result (list): In list - each tuple contains racer name, car brand, and lap time (datetime).
        invalid_result (list): In list - each tuple contains racer name, car brand, and error message.
        name (str): Racer's name and surname

    Raises:
        ValueError: If the rider's name is not in the list of riders.
    """
    result = ''
    for i, idx in enumerate(valid_result, start=1):
        if name in ' '.join(idx[0:1]):
            result = name
            print(f'Racer in {i}st position of leadership, {idx[0]} | {idx[1]} | {format_lap_time(idx[2])}')

    for idx in invalid_result:
        if name in idx[0]:
            result = name
            print(f'{idx[0]} has invalid race data | {idx[1]}')
    if result == '':
        raise ValueError(f'{name} not found in rider list')


def print_report(valid_result: list, invalid_result: list, sort=True) -> None:
    """
    Prints a formatted report of race results.

    Displays the top 15 racers with formatted lap times
    and the rest after underline,
    followed by racers with invalid or erroneous data.

    Args:
        valid_result (list): In list - each tuple contains racer name, car brand, and lap time (datetime).
        invalid_result (list): In list - each tuple contains racer name, car brand, and error message.
        sort (bool): Sort by racer - time, False - from high to low
    """
    valid_result = valid_result if sort else valid_result[::-1]
    total_valid_racer = len(valid_result)
    for i, idx in enumerate(valid_result, start=1):
        num = i if sort else total_valid_racer - i + 1
        print(f'{num}. {idx[0]} | {idx[1]} | {format_lap_time(idx[2])}')
        if i == 15:
            print('-' * 70)

    for idx in invalid_result:
        print(f'{idx[0]} | {idx[1]} | {idx[2]}')
