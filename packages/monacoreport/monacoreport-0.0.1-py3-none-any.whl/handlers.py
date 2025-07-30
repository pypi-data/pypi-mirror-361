from datetime import timedelta


def check_str_type(text: str):
    """
    Checks if parameter is of type str.

    Args:
        text (any): The parameter to check.

    Raises:
        TypeError: If the parameter is not a str.
    """
    if not isinstance(text, str):
        raise TypeError(f'The value {text} must be a string')


def correct_info_in_file(filepath: str) -> list:
    """Reads a text file and returns it as a formatted list.

    Args:
        filepath (str): Path to the file.

    Returns:
        list: Formatted text from file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If any other error except FileNotFoundError.
    """
    check_str_type(filepath)
    try:
        with open(filepath, encoding="utf-8") as file:
            file_lines = file.read().strip().split('\n')
        return file_lines
    except FileNotFoundError:
        raise FileNotFoundError(f'File at {filepath} not found')
    except Exception as e:
        raise Exception(f'Error: {e}')


def lap_time_for_rider(correct_dict_start: dict, correct_dict_end: dict) -> dict:
    """Calculates the race time from the end time and the start time of the race.

    The function processes 2 dictionaries (start/end) and
    returns a dictionary of abbreviations and the
    best time for the racer to complete a lap.

    Args:
        correct_dict_start (dict): Dictionary of racing abbreviations and race start times.
        correct_dict_end (dict): Dictionary of racing abbreviations and race end times.

    Returns:
        dict: Dictionary mapping abbreviation to best race times (timedelta).

    Raises:
        ValueError: If racer abbreviation from end log is not found in start log.
    """
    result = {}
    for abbreviation, correct_date_time in correct_dict_end.items():
        if abbreviation in correct_dict_start:
            best_time_for_rider = correct_date_time - correct_dict_start[abbreviation]
            result[abbreviation] = best_time_for_rider
        else:
            raise ValueError(f'Start time not found for abbreviation {abbreviation}.')
    return result


def format_lap_time(delta: timedelta) -> str:
    """Edits the timedelta time format to a string of the format 'm:ss.SSS'.

    Args:
        delta (timedelta): Time format timedelta.

    Returns:
        str: Formatted string from timedelta.

    Raises:
        TypeError: If not timedelta format.
    """
    if not isinstance(delta, timedelta):
        raise TypeError(f'The time format must be timedelta')
    total_mseconds = int(delta.total_seconds() * 1000)
    minutes = total_mseconds // 60000
    seconds = (total_mseconds % 60000) // 1000
    milliseconds = total_mseconds % 1000
    return f"{minutes}:{seconds:02}.{milliseconds:03}"
