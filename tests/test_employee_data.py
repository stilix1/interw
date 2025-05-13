import os
import pytest
from src.interv.main import EmployeeData


def test_validate_files_success(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("id,email\n1,test@example.com")
    employee = EmployeeData([str(test_file)])
    employee.validate_files()  # не должно выбросить исключение


def test_validate_files_failure():
    """Тест: файл не существует — должна быть ошибка"""
    with pytest.raises(FileNotFoundError):
        EmployeeData(["nonexistent.csv"]).validate_files()


def test_validate_files_with_missing_file():
    """Тест: файл не существует — должна быть ошибка с правильным сообщением"""
    data = EmployeeData(["nonexistent.csv"])
    with pytest.raises(FileNotFoundError) as exc_info:
        data.validate_files()
    assert "не найдены" in str(exc_info.value)  # проверка, что в сообщении есть нужный текст


def test_group_by():
    data = [
        {'department': 'HR', 'id': '1'},
        {'department': 'HR', 'id': '2'},
        {'department': 'IT', 'id': '3'}
    ]
    result = EmployeeData([]).group_by(data, 'department')
    assert list(result.keys()) == ['HR', 'IT']
    assert len(result['HR']) == 2


def test_read_and_standardize_csv_missing_headers(tmp_path):
    content = "name,dept\n" \
              "Charlie,IT\n"

    file_path = tmp_path / "missing_headers.csv"
    file_path.write_text(content)

    emp_data = EmployeeData([str(file_path)])
    result = emp_data.read_and_standardize_csv(str(file_path))

    assert result == [{
        'id': '',
        'email': '',
        'name': 'Charlie',
        'department': 'IT',
        'hours_worked': '',
        'hourly_rate': ''
    }]


def test_read_and_standardize_csv_only_headers(tmp_path):
    content = "name,email,department,hours_worked,hourly_rate,id\n"

    file_path = tmp_path / "only_headers.csv"
    file_path.write_text(content)

    emp_data = EmployeeData([str(file_path)])
    result = emp_data.read_and_standardize_csv(str(file_path))

    assert result == []


def test_read_and_standardize_csv_incomplete_row(tmp_path):
    content = "name,email,department,hours_worked,hourly_rate,id\n" \
              "Dana,d@example.com,Finance,170,,4\n" \
              "Eve\n"

    file_path = tmp_path / "incomplete_row.csv"
    file_path.write_text(content)

    emp_data = EmployeeData([str(file_path)])
    result = emp_data.read_and_standardize_csv(str(file_path))

    assert result[0]['name'] == 'Dana'
    assert result[0]['hourly_rate'] == ''  # отсутствует
    assert result[1]['name'] == 'Eve'      # только одно поле найдено
    assert result[1]['email'] == ''        # остальные — пустые


import os
from src.interv.main import EmployeeData

def test_read_and_standardize_csv(tmp_path):
    # создаем временный CSV-файл
    content = "full_name,mail,dept,hours,rate,emp_id\n" \
              "Alice,a@example.com,Sales,160,50,1\n" \
              "Bob,b@example.com,HR,150,60,2\n"

    file_path = tmp_path / "test.csv"
    file_path.write_text(content)

    emp_data = EmployeeData([str(file_path)])
    result = emp_data.read_and_standardize_csv(str(file_path))

    expected = [
        {
            'id': '1',
            'email': 'a@example.com',
            'name': 'Alice',
            'department': 'Sales',
            'hours_worked': '160',
            'hourly_rate': '50',
        },
        {
            'id': '2',
            'email': 'b@example.com',
            'name': 'Bob',
            'department': 'HR',
            'hours_worked': '150',
            'hourly_rate': '60',
        }
    ]

    assert result == expected


def test_process_multiple_csv(tmp_path):
    file1 = tmp_path / "file1.csv"
    file1.write_text("name,department,hourly_rate,hours_worked,id,email\n"
                     "Alice,HR,50,160,1,alice@example.com\n")

    file2 = tmp_path / "file2.csv"
    file2.write_text("name,department,hourly_rate,hours_worked,id,email\n"
                     "Bob,IT,60,170,2,bob@example.com\n")

    emp_data = EmployeeData([str(file1), str(file2)])
    result = emp_data.process_multiple_csv()

    assert len(result) == 2
    assert result[0]['name'] == 'Alice'
    assert result[1]['name'] == 'Bob'


def test_group_by_department():
    input_data = [
        {'id': '1', 'name': 'Alice', 'email': '', 'department': 'HR', 'hours_worked': '160', 'hourly_rate': '50'},
        {'id': '2', 'name': 'Bob', 'email': '', 'department': 'IT', 'hours_worked': '170', 'hourly_rate': '60'},
        {'id': '3', 'name': 'Charlie', 'email': '', 'department': 'HR', 'hours_worked': '150', 'hourly_rate': '55'},
    ]

    emp_data = EmployeeData([])
    grouped = emp_data.group_by(input_data, 'department')

    assert list(grouped.keys()) == ['HR', 'IT']
    assert len(grouped['HR']) == 2
    assert grouped['HR'][0]['name'] == 'Alice'
    assert grouped['HR'][1]['name'] == 'Charlie'
    assert grouped['IT'][0]['name'] == 'Bob'
