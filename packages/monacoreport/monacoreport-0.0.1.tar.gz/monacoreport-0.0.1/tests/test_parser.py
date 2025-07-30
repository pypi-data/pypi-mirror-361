import pytest
import pytest_mock
from datetime import datetime
from src.parser import parse_time_start_or_end, parse_name_racer_and_brand

LIST_NOT_STR = [451278, None, ['abc', 'def'], {1: 'test'}, 4.5, True, {1, 2}, (1, 2)]


class TestParseTimeStartOrEnd:
    """Tests for parse_time_start_or_end() function."""

    def test_parse_time_start_or_end(self, mocker):
        """Test of opening and reading a mock file and return dict
        with parsed start/end time"""
        mock_open = mocker.mock_open(read_data='SVF2018-05-24_12:02:58.917\nLHM2018-05-24_12:03:01.250')
        mocker.patch("builtins.open", mock_open)
        result = parse_time_start_or_end('test_file.txt')
        assert result == {'SVF': datetime(2018, 5, 24, 12, 2, 58, 917000),
                          'LHM': datetime(2018, 5, 24, 12, 3, 1, 250000)}
        mock_open.assert_called_once_with('test_file.txt', encoding='utf-8')

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                parse_time_start_or_end(not_str_type)

    def test_file_not_found(self):
        """Should raise FileNotFoundError for incorrect address or missing file."""
        with pytest.raises(FileNotFoundError):
            parse_time_start_or_end(r' ')


class TestParseNameBrand:
    """Tests for parse_name_racer_and_brand() function."""

    def test_parse_name_racer_and_brand(self, mocker):
        """Test of opening and reading a mock file and returns it as a tuple[dict, dict]"""
        mock_open = mocker.mock_open(read_data='LHM_Lewis Hamilton_MERCEDES')
        mocker.patch("builtins.open", mock_open)
        result = parse_name_racer_and_brand('test_file.txt')
        assert result == ({'LHM': 'Lewis Hamilton'}, {'LHM': 'MERCEDES'})
        mock_open.assert_called_once_with('test_file.txt', encoding='utf-8')

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                parse_name_racer_and_brand(not_str_type)

    def test_file_not_found(self):
        """Should raise FileNotFoundError for incorrect address or missing file."""
        with pytest.raises(FileNotFoundError):
            parse_name_racer_and_brand(r' ')
