import pytest
import pytest_mock
from datetime import datetime, timedelta
from src.handlers import check_str_type, correct_info_in_file, lap_time_for_rider, format_lap_time

LIST_NOT_STR = [451278, None, ['abc', 'def'], {1: 'test'}, 4.5, True, {1, 2}, (1, 2)]


class TestCheckStrType:
    """Tests for check_str_type() function."""

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                check_str_type(not_str_type)


class TestCorrectInfoInFile:
    """Tests for correct_info_in_file() function."""

    def test_correct_info_in_file(self, mocker):
        """Test of opening and reading a mock file and returns it as a list"""
        mock_open = mocker.mock_open(read_data='SVF2018-05-24_12:02:58.917\nRGH2018-05-24_12:05:14.511')
        mocker.patch("builtins.open", mock_open)
        result = correct_info_in_file('test_file.txt')
        assert result == ['SVF2018-05-24_12:02:58.917', 'RGH2018-05-24_12:05:14.511']
        mock_open.assert_called_once_with('test_file.txt', encoding='utf-8')

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                correct_info_in_file(not_str_type)

    def test_file_not_found(self):
        """Should raise FileNotFoundError for incorrect address or missing file."""
        with pytest.raises(FileNotFoundError):
            correct_info_in_file(r' ')


class TestLapTimeForRider:
    """Tests for lap_time_for_rider() function."""

    def test_correct_lap_time(self):
        """Should return correct timedelta for known abbreviation."""
        dict_start = {'SVF': datetime(2018, 5, 24, 12, 2, 58, 917000),
                      'LHM': datetime(2018, 5, 24, 12, 3, 1, 250000)}
        dict_end = {'SVF': datetime(2018, 5, 24, 12, 5, 58, 917000),
                    'LHM': datetime(2018, 5, 24, 12, 4, 1, 250000)}
        result = lap_time_for_rider(dict_start, dict_end)
        assert result == {'SVF': timedelta(seconds=180), 'LHM': timedelta(seconds=60)}

    def test_negative_lap_time(self):
        """Should return negative timedelta if end over start."""
        dict_start = {"SVF": datetime(2018, 5, 24, 12, 2, 58, 917000)}
        dict_end = {"SVF": datetime(2018, 5, 24, 12, 2, 28, 917000)}
        result = lap_time_for_rider(dict_start, dict_end)
        assert result == {"SVF": timedelta(seconds=-30)}

    def test_non_finding_abbreviation(self):
        """Should raise ValueError if end has key not in start."""
        dict_start = {"SVF": datetime(2018, 5, 24, 12, 2, 58, 917000)}
        dict_end = {"SBB": datetime(2018, 5, 24, 12, 2, 28, 917000)}
        with pytest.raises(ValueError):
            lap_time_for_rider(dict_start, dict_end)
