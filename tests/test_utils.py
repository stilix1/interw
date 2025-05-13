from typing import List, Dict
from src.interv.main import calculate_salary, sorting_data, standardize_headers


def test_calculate_salary() -> None:
    """тест на расчет зп"""
    row: Dict[str, str] = {'hours_worked': '150', 'hourly_rate': '20'}
    expected_salary: float = 3000
    assert calculate_salary(row) == expected_salary


def test_sorting_data() -> None:
    """тест на сортировку данных по id"""
    unsorted_data: List[Dict[str, str, str, str, str, str]] = [
        {'id': '12222', 'email': 'ryan.wood@example.com', 'name': 'Ryan Wood', 'department': 'Engineering',
         'hours_worked': '173', 'hourly_rate': '60'},
        {'id': '1', 'email': 'alice@example.com', 'name': 'Alice Johnson', 'department': 'Marketing',
         'hours_worked': '160', 'hourly_rate': '50'},
        {'id': '2', 'email': 'bob@example.com', 'name': 'Bob Smith', 'department': 'Design',
         'hours_worked': '150', 'hourly_rate': '40'}

    ]
    sorted_data = sorting_data(unsorted_data)
    assert [row['id'] for row in sorted_data] == ['1', '2', '12222']


def test_standardize_headers():
    headers = ['Emp_ID', 'Mail', 'Full_Name', 'Dept', 'Hours', 'Wage']
    result = standardize_headers(headers)
    expected = {
        'id': 'emp_id',
        'email': 'mail',
        'name': 'full_name',
        'department': 'dept',
        'hours_worked': 'hours',
        'hourly_rate': 'wage'
    }
    assert result == expected
