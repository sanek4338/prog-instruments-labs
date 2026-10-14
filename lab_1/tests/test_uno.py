"""Тесты для модуля uno."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from uno import find_incorrect_birthdates, is_valid_real_date


@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("01.01.2000", True),
        ("29.02.2024", True),
        ("29.02.2023", False),   # не високосный
        ("31.04.2020", False),   # апреля 31 нет
        ("32.01.2000", False),
        ("00.01.2000", False),
        ("01.13.2000", False),
        ("01-01-2000", False),   # дефис не допускается
        ("01/01/2000", False),   # слэш не допускается
        ("1899.01.2000", False),
        ("01.01.2100", False),
        (" 01.01.2000 ", True),  # пробелы по краям допускаются
    ],
)
def test_is_valid_real_date(date_str: str, expected: bool) -> None:
    assert is_valid_real_date(date_str) is expected


def test_find_incorrect_birthdates_splits_profiles() -> None:
    """Проверяем, что анкеты корректно делятся на правильные и неправильные."""
    text = (
        "1)\n"
        "Фамилия: Иванов\n"
        "Дата рождения: 15.03.1990\n"
        "\n"
        "2)\n"
        "Фамилия: Петров\n"
        "Дата рождения: 32.13.2000\n"
        "\n"
        "3)\n"
        "Фамилия: Сидоров\n"
        "Дата рождения: 29.02.2020\n"
    )

    incorrect, correct = find_incorrect_birthdates(text)

    assert len(incorrect) == 1, "Должна быть одна некорректная анкета"
    assert len(correct) == 2, "Должны быть две корректные анкеты"
    assert "Петров" in incorrect[0]
    assert "Иванов" in correct[0]
    assert "Сидоров" in correct[1]


def test_script_runs_and_creates_output(tmp_path: Path) -> None:
    """Проверяем, что скрипт запускается и создаёт непустой файл."""
    lab_dir = Path(__file__).parent.parent
    input_file = lab_dir / "data.txt"
    output_file = tmp_path / "result.txt"

    result = subprocess.run(
        [
            sys.executable,
            str(lab_dir / "uno.py"),
            str(input_file),
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Скрипт упал: {result.stderr}"
    assert output_file.exists(), "Выходной файл не создан"
    assert output_file.stat().st_size > 0, "Выходной файл пуст"


def test_output_contains_profiles(tmp_path: Path) -> None:
    """Проверяем, что в результат попали анкеты с корректными датами."""
    lab_dir = Path(__file__).parent.parent
    input_file = lab_dir / "data.txt"
    output_file = tmp_path / "result.txt"

    subprocess.run(
        [
            sys.executable,
            str(lab_dir / "uno.py"),
            str(input_file),
            str(output_file),
        ],
        check=True,
    )

    content = output_file.read_text(encoding="utf-8")
    assert "Дата рождения" in content, "В выводе нет анкет с датами рождения"
