import argparse
import os
import json  # доп.функционал и показ маштабируемости, для простоты использовал внешний модуль
from typing import List, Dict


def sorting_data(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """сортировка по ID"""
    sorted_data = sorted(data, key=lambda x: int(x['id']))
    ordered_data = []
    standard_field_order = ['id', 'email', 'name', 'department', 'hours_worked', 'hourly_rate']

    for row in sorted_data:
        ordered_row = {key: row.get(key, '') for key in standard_field_order}
        ordered_data.append(ordered_row)
    return ordered_data


def standardize_headers(headers: List[str]) -> Dict[str, str]:
    """стандартизация заголовков"""
    field_mapping = {
        'id': ['id', 'identifier', 'emp_id', 'employee_id'],
        'email': ['email', 'e-mail', 'mail', 'contact'],
        'name': ['name', 'full_name', 'employee_name'],
        'department': ['department', 'dept', 'team'],
        'hours_worked': ['hours_worked', 'hours', 'work_hours'],
        'hourly_rate': ['hourly_rate', 'rate', 'salary', 'wage', 'hour_rate']
    }

    standardized_headers = {}
    for header in headers:
        header = header.lower()
        for standard_field, keywords in field_mapping.items():
            if any(keyword in header for keyword in keywords):
                standardized_headers[standard_field] = header
                break
    return standardized_headers


def calculate_salary(row: Dict[str, str]) -> float:
    """расчет зп"""
    return int(row['hours_worked']) * int(row['hourly_rate'])


class EmployeeData:
    def __init__(self, files: List[str]):
        self.files = files
        self.data = []

    def validate_files(self):
        """проверка существования файлов"""
        invalid_files = [file for file in self.files if not os.path.exists(file)]
        if invalid_files:
            raise FileNotFoundError(f"Следующие файлы не найдены: {', '.join(invalid_files)}")

    def read_and_standardize_csv(self, file_path: str) -> List[Dict[str, str]]:
        """чтение и стандартизация данных из CSV"""
        with open(file_path, 'r') as file:
            lines = file.readlines()

        raw_headers = lines[0].strip().split(',')
        headers_mapping = standardize_headers(raw_headers)

        data = []
        for line in lines[1:]:
            values = line.strip().split(',')
            row_dict = {}
            for i, value in enumerate(values):
                for standard_key, original_header in headers_mapping.items():
                    if raw_headers[i].lower() == original_header.lower():
                        row_dict[standard_key] = value

            for key in ['id', 'email', 'name', 'department', 'hours_worked', 'hourly_rate']:
                if key not in row_dict:
                    row_dict[key] = ''
            data.append(row_dict)

        return data

    def read_and_standardize_json(self, file_path: str) -> List[Dict[str, str]]:
        """чтение и стандартизация данных из JSON"""
        with open(file_path, 'r') as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError(f"Файл {file_path} должен содержать список объектов JSON.")

        headers = list(records[0].keys())
        headers_mapping = standardize_headers(headers)

        data = []
        for item in records:
            row_dict = {}
            for standard_key, original_header in headers_mapping.items():
                row_dict[standard_key] = str(item.get(original_header, ''))
            for key in ['id', 'email', 'name', 'department', 'hours_worked', 'hourly_rate']:
                if key not in row_dict:
                    row_dict[key] = ''
            data.append(row_dict)

        return data

    def process_multiple_files(self) -> List[Dict[str, str]]:
        """обработка CSV и JSON файлов"""
        all_data = []
        for file in self.files:
            ext = os.path.splitext(file)[-1].lower()
            if ext == '.csv':
                data = self.read_and_standardize_csv(file)
            elif ext == '.json':
                data = self.read_and_standardize_json(file)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file}")
            all_data.extend(data)
        return all_data

    def group_by(self, data: List[Dict[str, str]], key: str) -> Dict[str, List[Dict[str, str]]]:
        """группировка данных по ключу"""
        grouped_data = {}
        for row in data:
            group_value = row[key]
            if group_value not in grouped_data:
                grouped_data[group_value] = []
            grouped_data[group_value].append(row)
        return grouped_data


class ReportGenerator:
    def __init__(self, data: List[Dict[str, str]]):
        self.data = data
        self.employee_data = EmployeeData([])

        self.available_reports = {
            'payout': self.generate_payout_report,
            'average_hourly_rate': self.generate_average_hourly_rate_report
        }

    def get_available_reports(self) -> List[str]:
        return list(self.available_reports.keys())

    def run_report(self, report_type: str) -> None:
        report_func = self.available_reports.get(report_type)
        if report_func:
            report_func()
        else:
            raise ValueError(f"Неверный тип отчета: '{report_type}'. "
                             f"Доступные отчеты: {', '.join(self.get_available_reports())}")

    def generate_payout_report(self):
        grouped_data = self.employee_data.group_by(self.data, 'department')
        for department, rows in grouped_data.items():
            print(f"Department: {department}")
            print('-' * 150)
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Hours Worked':<15} {'Hourly Rate':<15} {'Salary':<10}")
            print('-' * 105)
            for row in sorted(rows, key=lambda x: int(x['id'])):
                salary = calculate_salary(row)
                print(f"{row['id']:<5} {row['name']:<25} {row['email']:<25} "
                      f"{row['hours_worked']:<15} {row['hourly_rate']:<15} {salary:<10}")
            print('\n' + '-' * 150 + '\n')

    def generate_average_hourly_rate_report(self):
        """генерация отчета по средней почасовой ставке"""
        grouped_data = self.employee_data.group_by(self.data, 'department')
        for department, rows in grouped_data.items():
            print(f"Department: {department}")
            print('-' * 150)
            hourly_rates = []
            for row in rows:
                try:
                    rate = float(row['hourly_rate'])
                    hourly_rates.append(rate)
                except (ValueError, TypeError):
                    continue
            if hourly_rates:
                average_rate = sum(hourly_rates) / len(hourly_rates)
                print(f"Average Hourly Rate: {average_rate:.2f}")
            else:
                print("No data available for average hourly rate.")
            print('-' * 150 + '\n')


def main(files: List[str], report_type: str) -> None:
    try:
        employee_data = EmployeeData(files)
        employee_data.validate_files()
        all_data = employee_data.process_multiple_files()
        sorted_data = sorting_data(all_data)

        report_generator = ReportGenerator(sorted_data)
        report_generator.run_report(report_type)
    except Exception as e:
        print(f"\n Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Скрипт для генерации отчетов по CSV/JSON")
    parser.add_argument('files', metavar='F', type=str, nargs='+', help="Список файлов")
    parser.add_argument('--report', type=str, required=True,
                        help="Тип отчета (например, 'payout', 'average_hourly_rate')")
    args = parser.parse_args()
    main(args.files, args.report)
