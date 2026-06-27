"""Tests for grid.data.csv_parser"""
import pytest
from unittest.mock import patch, MagicMock
from grid.data.exceptions import DataException
from grid.data.csv_parser import parse


REQUIRED = ['A', 'B']
IGNORED = ['C', 'D']


def _mock_response(text: str, status: int = 200):
    mock = MagicMock()
    mock.text = text
    mock.status_code = status
    mock.raise_for_status = MagicMock()
    if status >= 400:
        from requests.exceptions import HTTPError
        mock.raise_for_status.side_effect = HTTPError('error')
    return mock


class TestParse:
    def test_basic_parse(self):
        csv_text = 'A,B,C,D\n1,2,3,4\n5,6,7,8\n'
        with patch('requests.get', return_value=_mock_response(csv_text)):
            result = parse('http://example.com', REQUIRED, IGNORED)
        assert result == [['1', '2'], ['5', '6']]

    def test_columns_reordered(self):
        # B appears before A in the CSV header — values should still map correctly
        csv_text = 'C,B,A,D\nalpha,beta,gamma,delta\n'
        with patch('requests.get', return_value=_mock_response(csv_text)):
            result = parse('http://example.com', REQUIRED, IGNORED)
        assert result == [['gamma', 'beta']]

    def test_http_error_raises(self):
        with patch('requests.get', side_effect=Exception('network error')):
            with pytest.raises(DataException, match='Failed to read data'):
                parse('http://example.com', REQUIRED, IGNORED)

    def test_empty_csv_raises(self):
        with patch('requests.get', return_value=_mock_response('')):
            with pytest.raises(DataException, match='Missing CSV headers'):
                parse('http://example.com', REQUIRED, IGNORED)

    def test_unknown_header_raises(self):
        csv_text = 'A,B,UNKNOWN\n1,2,3\n'
        with patch('requests.get', return_value=_mock_response(csv_text)):
            with pytest.raises(DataException, match='Unrecognised header'):
                parse('http://example.com', REQUIRED, IGNORED)

    def test_missing_required_header_raises(self):
        csv_text = 'A,C,D\n1,2,3\n'
        with patch('requests.get', return_value=_mock_response(csv_text)):
            with pytest.raises(DataException, match='Missing required header'):
                parse('http://example.com', REQUIRED, IGNORED)

    def test_column_count_mismatch_raises(self):
        csv_text = 'A,B,C\n1,2\n'
        with patch('requests.get', return_value=_mock_response(csv_text)):
            with pytest.raises(DataException, match='Column count does not match'):
                parse('http://example.com', REQUIRED, ['C'])

    def test_empty_data_rows(self):
        csv_text = 'A,B,C\n'
        with patch('requests.get', return_value=_mock_response(csv_text)):
            result = parse('http://example.com', REQUIRED, ['C'])
        assert result == []
