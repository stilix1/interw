from io import StringIO
from unittest.mock import patch
from src.interv.main import ReportGenerator

import pytest

from src.interv.main import ReportGenerator, EmployeeData, calculate_salary, sorting_data


def test_generate_average_hourly_rate_report_valid(capfd):
    sample_data = [
        {'id': '1', 'email': 'a@example.com', 'name': 'Alice', 'department': 'Sales', 'hours_worked': '160',
         'hourly_rate': '50'},
        {'id': '2', 'email': 'b@example.com', 'name': 'Bob', 'department': 'Sales', 'hours_worked': '150',
         'hourly_rate': '70'}
    ]
    report = ReportGenerator(sample_data)
    report.generate_average_hourly_rate_report()

    out, _ = capfd.readouterr()
    assert "Department: Sales" in out
    assert "Average Hourly Rate: 60.00" in out


def test_generate_average_hourly_rate_report_empty_values(capfd):
    sample_data = [
        {'id': '1', 'email': 'a@example.com', 'name': 'Alice', 'department': 'HR',
         'hours_worked': '160', 'hourly_rate': 'notanumber'},
        {'id': '2', 'email': 'b@example.com', 'name': 'Bob', 'department': 'HR',
         'hours_worked': '150', 'hourly_rate': ''}
    ]
    report = ReportGenerator(sample_data)
    report.generate_average_hourly_rate_report()

    out, _ = capfd.readouterr()
    assert "Department: HR" in out
    assert "No data available for average hourly rate." in out


def test_get_available_reports():
    data = []
    report = ReportGenerator(data)
    reports = report.get_available_reports()
    assert 'payout' in reports
    assert 'average_hourly_rate' in reports


def test_run_report_invalid_type():
    report = ReportGenerator([])
    with pytest.raises(ValueError) as excinfo:
        report.run_report('invalid')
    assert "Неверный тип отчета" in str(excinfo.value)


# Тест одного файла
def test_generate_payout_report_single_file():
    data1 = [
        {'id': '1', 'email': 'alice@example.com', 'name': 'Alice Johnson', 'department': 'Marketing',
         'hours_worked': '160', 'hourly_rate': '50'},
        {'id': '2', 'email': 'bob@example.com', 'name': 'Bob Smith', 'department': 'Design', 'hours_worked': '150',
         'hourly_rate': '40'},
        {'id': '3', 'email': 'carol@example.com', 'name': 'Carol Williams', 'department': 'Design',
         'hours_worked': '170', 'hourly_rate': '60'}
    ]

    sorted_data = sorting_data(data1)  # Сортировка
    report_generator = ReportGenerator(sorted_data)

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        report_generator.run_report('payout')  # генерация отчета
        output = mock_stdout.getvalue()

    # проверяем, что отчет содержит все нужные данные
    assert "Department: Marketing" in output
    assert "Alice Johnson" in output
    assert "Bob Smith" in output
    assert "Carol Williams" in output
    assert "Salary" in output
    assert "8000" in output
    assert "6000" in output
    assert "10200" in output


# Тест двух файлов
def test_generate_payout_report_multiple_files():
    data1 = [
        {'id': '1', 'email': 'alice@example.com', 'name': 'Alice Johnson', 'department': 'Marketing',
         'hours_worked': '160', 'hourly_rate': '50'},
        {'id': '2', 'email': 'bob@example.com', 'name': 'Bob Smith', 'department': 'Design', 'hours_worked': '150',
         'hourly_rate': '40'},
        {'id': '3', 'email': 'carol@example.com', 'name': 'Carol Williams', 'department': 'Design',
         'hours_worked': '170', 'hourly_rate': '60'}
    ]
    data2 = [
        {'id': '101', 'email': 'grace@example.com', 'name': 'Grace Lee', 'department': 'HR', 'hours_worked': '160',
         'hourly_rate': '45'},
        {'id': '102', 'email': 'henry@example.com', 'name': 'Henry Martin', 'department': 'Marketing',
         'hours_worked': '150', 'hourly_rate': '35'},
        {'id': '103', 'email': 'ivy@example.com', 'name': 'Ivy Clark', 'department': 'HR', 'hours_worked': '158',
         'hourly_rate': '38'}
    ]

    combined_data = data1 + data2  # Комбинируем данные из двух файлов
    sorted_data = sorting_data(combined_data)
    report_generator = ReportGenerator(sorted_data)

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        report_generator.run_report('payout')  # Генерируем отчет
        output = mock_stdout.getvalue()

    # Проверяем, что отчет содержит все нужные департаменты и данные
    assert "Department: Marketing" in output
    assert "Alice Johnson" in output
    assert "Henry Martin" in output
    assert "Salary" in output
    assert "8000" in output
    assert "5250" in output
    assert "6000" in output
    assert "10200" in output
    assert "HR" in output
    assert "7200" in output
    assert "6004" in output
