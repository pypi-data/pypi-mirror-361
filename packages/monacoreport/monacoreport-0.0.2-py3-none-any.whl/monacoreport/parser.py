from datetime import datetime
from src.monacoreport.handlers import correct_info_in_file


def parse_time_start_or_end(filepath: str) -> dict:
    """Reads a text file and returns dictionary with abbreviations and correct time format.

    Args:
        filepath (str): Path to the file.

    Returns:
        dict: Dictionary mapping abbreviation to correct time format (datetime).

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If any other error except FileNotFoundError.
    """
    result = {}
    file_lines = correct_info_in_file(filepath)
    for line in file_lines:
        abbreviations = line[:3]
        time_start_or_end = line[3:].replace('_', " ").strip()
        time_start_or_end += '000'
        correct_date_time = datetime.strptime(time_start_or_end, "%Y-%m-%d %H:%M:%S.%f")
        result[abbreviations] = correct_date_time
    return result


def parse_name_racer_and_brand(filepath: str) -> tuple[dict, dict]:
    """Parses racer abbreviation file and returns two dictionaries:
        - Abbreviation to full racer name
        - Abbreviation to car brand

    Args:
        filepath (str): Path to the file.

    Returns:
        tuple[dict, dict]:
        - Dictionary mapping abbreviation to full racer name.
        - Dictionary mapping abbreviation to car brand.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If any other error except FileNotFoundError.
    """
    abbreviation_name_racer = {}
    abbreviation_car_brand = {}
    file_lines = correct_info_in_file(filepath)
    for line in file_lines:
        list_info = line.replace('_', " ").split(' ')
        abbreviation = list_info[0]
        first_and_last_name = f'{list_info[1]} {list_info[2]}'
        car_brand = ' '.join(list_info[3:])
        abbreviation_name_racer[abbreviation] = first_and_last_name
        abbreviation_car_brand[abbreviation] = car_brand
    return abbreviation_name_racer, abbreviation_car_brand
