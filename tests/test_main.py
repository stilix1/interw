import os
import pytest
from src.interv.main import main


def test_main_payout_report(capfd):
    # Пути к CSV-файлам
    base_dir = os.path.dirname(__file__)
    csv_dir = os.path.join(base_dir, '../csv')

    files = [
        os.path.join(csv_dir, 'data1.csv'),
        os.path.join(csv_dir, 'data2.csv'),
        os.path.join(csv_dir, 'data3.csv'),
        os.path.join(csv_dir, 'workers.csv')
    ]

    # Запуск основного скрипта с типом отчета
    main(files, 'payout')

    # Читаем вывод
    out, err = capfd.readouterr()

    assert 'Department:' in out
    assert 'Salary' in out
    assert 'ID' in out
    assert 'Name' in out
