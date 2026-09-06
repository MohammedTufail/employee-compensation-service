import pytest

from utils.errors import AppError
from utils.validation import parse_id_param, validate_create_employee, validate_update_employee

VALID_BODY = {
    "firstName": "Ada",
    "lastName": "Lovelace",
    "departmentId": 1,
    "salary": 900000,
    "hireDate": "2023-01-15",
}


class TestValidateCreateEmployee:
    def test_accepts_valid_payload_without_bonus_defaults_to_none(self):
        result = validate_create_employee(VALID_BODY)
        assert result["bonus"] is None
        assert result["first_name"] == "Ada"

    def test_accepts_explicit_bonus(self):
        result = validate_create_employee({**VALID_BODY, "bonus": 50000})
        assert result["bonus"] == 50000

    def test_rejects_missing_first_name(self):
        body = {k: v for k, v in VALID_BODY.items() if k != "firstName"}
        with pytest.raises(AppError):
            validate_create_employee(body)

    def test_rejects_negative_salary(self):
        with pytest.raises(AppError):
            validate_create_employee({**VALID_BODY, "salary": -1})

    def test_rejects_malformed_hire_date(self):
        with pytest.raises(AppError):
            validate_create_employee({**VALID_BODY, "hireDate": "15-01-2023"})

    def test_rejects_negative_bonus(self):
        with pytest.raises(AppError):
            validate_create_employee({**VALID_BODY, "bonus": -500})


class TestValidateUpdateEmployee:
    def test_accepts_partial_update_with_only_bonus(self):
        result = validate_update_employee({"bonus": 25000})
        assert result == {"bonus": 25000}

    def test_allows_explicitly_clearing_bonus_to_none(self):
        result = validate_update_employee({"bonus": None})
        assert result["bonus"] is None

    def test_rejects_empty_update_body(self):
        with pytest.raises(AppError):
            validate_update_employee({})

    def test_rejects_invalid_field_type(self):
        with pytest.raises(AppError):
            validate_update_employee({"salary": "a lot"})


class TestParseIdParam:
    def test_parses_valid_positive_integer_string(self):
        assert parse_id_param("42") == 42

    @pytest.mark.parametrize("raw", ["0", "-3", "abc", None])
    def test_rejects_zero_negatives_and_non_numeric_values(self, raw):
        with pytest.raises(AppError):
            parse_id_param(raw)
