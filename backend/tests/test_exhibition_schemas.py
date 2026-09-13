from datetime import date

import pytest
from app.schemas.exhibition import ExhibitionCreate
from pydantic import ValidationError


def test_exhibition_create_rejects_invalid_date_range():
    with pytest.raises(ValidationError):
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição da exposição",
            start_date=date(2026, 9, 20),
            end_date=date(2026, 9, 10),
        )


def test_exhibition_create_accepts_valid_date_range():
    exhibition = ExhibitionCreate(
        title="Exposiçao Teste",
        description="Descrição da exposiçao",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 20),
    )

    assert exhibition.start_date == date(2026, 9, 10)
    assert exhibition.end_date == date(2026, 9, 20)


def test_exhibition_create_accepts_none_dates():
    exhibition = ExhibitionCreate(
        title="Exposição Teste",
        description="Descrição da exposição",
    )

    assert exhibition.start_date is None
    assert exhibition.end_date is None


def test_exhibition_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        ExhibitionCreate(
            title="",
            description="Descrição da exposiçao",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 20),
        )


def test_exhibition_create_rejects_empty_description():
    with pytest.raises(ValidationError):
        ExhibitionCreate(
            title="Exposiçao Teste",
            description="",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 20),
        )


def test_exhibition_create_rejects_longer_title():
    with pytest.raises(ValidationError):
        ExhibitionCreate(
            title="a" * 151,
            description="descrição teste",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 20),
        )
