"""Tests for dashboard/config_generator.py - configuration generation."""

import pytest

from dashboard.config_generator import (
    escape_python_string,
    format_client_section,
    generate_vars_py,
    sanitize_client_id,
    validate_client_data,
)


# ---------------------------------------------------------------------------
# TestSanitizeClientId
# ---------------------------------------------------------------------------
class TestSanitizeClientId:
    """Test client name to Python identifier conversion."""

    def test_spaces_replaced_with_underscores(self):
        assert sanitize_client_id("Acme Corp") == "acme_corp"

    def test_hyphens_replaced_with_underscores(self):
        assert sanitize_client_id("Red-Hat") == "red_hat"

    def test_special_chars_removed(self):
        assert sanitize_client_id("Client@#$%Inc.") == "clientinc"

    def test_leading_digit_prefixed(self):
        result = sanitize_client_id("3M Company")
        assert result.startswith("_")
        assert result == "_3m_company"

    def test_length_capped_at_64(self):
        long_name = "A" * 100
        result = sanitize_client_id(long_name)
        assert len(result) <= 64

    def test_lowercase_conversion(self):
        assert sanitize_client_id("IBM") == "ibm"

    def test_multiple_spaces_collapsed(self):
        assert sanitize_client_id("Some   Big   Company") == "some_big_company"

    def test_empty_string(self):
        result = sanitize_client_id("")
        assert result == ""


# ---------------------------------------------------------------------------
# TestValidateClientData
# ---------------------------------------------------------------------------
class TestValidateClientData:
    """Test single client configuration validation."""

    def _make_client(self, **overrides):
        base = {
            "id": "test_client",
            "name": "Test Client",
            "folder": "https://drive.google.com/drive/folders/1ABC123",
            "industry": "technology",
            "subsegments": "cloud, AI",
        }
        base.update(overrides)
        return base

    def test_valid_data_passes(self):
        valid, error = validate_client_data(self._make_client())
        assert valid is True
        assert error == ""

    def test_missing_required_field(self):
        client = self._make_client()
        del client["name"]
        valid, error = validate_client_data(client)
        assert valid is False
        assert "name" in error.lower() or "Missing" in error

    def test_empty_id_rejected(self):
        valid, error = validate_client_data(self._make_client(id=""))
        assert valid is False

    def test_empty_name_rejected(self):
        valid, error = validate_client_data(self._make_client(name=""))
        assert valid is False

    def test_empty_folder_rejected(self):
        valid, error = validate_client_data(self._make_client(folder=""))
        assert valid is False

    def test_empty_industry_allowed(self):
        valid, _ = validate_client_data(self._make_client(industry=""))
        assert valid is True

    def test_empty_subsegments_allowed(self):
        valid, _ = validate_client_data(self._make_client(subsegments=""))
        assert valid is True

    def test_invalid_id_format(self):
        valid, error = validate_client_data(self._make_client(id="UPPER_CASE"))
        assert valid is False
        assert "identifier" in error.lower() or "must be" in error.lower()

    def test_invalid_drive_url(self):
        valid, error = validate_client_data(
            self._make_client(folder="https://drive.google.com/invalid_url")
        )
        assert valid is False
        assert "Drive URL" in error or "Invalid" in error

    def test_local_folder_accepted(self):
        valid, _ = validate_client_data(self._make_client(folder="/path/to/local"))
        assert valid is True


# ---------------------------------------------------------------------------
# TestGenerateVarsPy
# ---------------------------------------------------------------------------
class TestGenerateVarsPy:
    """Test full vars.py generation."""

    def _make_clients(self):
        return [
            {
                "id": "test_client",
                "name": "Test Client Corp",
                "folder": "https://drive.google.com/drive/folders/1ABC123",
                "industry": "technology",
                "subsegments": "cloud, AI",
            }
        ]

    def test_produces_valid_python(self):
        content = generate_vars_py(self._make_clients())
        # Should compile without errors
        compile(content, "<test>", "exec")

    def test_contains_client_list(self):
        content = generate_vars_py(self._make_clients())
        assert '"test_client"' in content
        assert "clients = [" in content

    def test_contains_client_variables(self):
        content = generate_vars_py(self._make_clients())
        assert 'test_client_name = "Test Client Corp"' in content
        assert 'test_client_industry = "technology"' in content

    def test_duplicate_ids_rejected(self):
        clients = self._make_clients() * 2  # Duplicate
        with pytest.raises(ValueError, match="Duplicate"):
            generate_vars_py(clients)

    def test_validation_errors_raised(self):
        invalid = [{"id": "", "name": "", "folder": "", "industry": "", "subsegments": ""}]
        with pytest.raises(ValueError, match="Validation"):
            generate_vars_py(invalid)

    def test_multiple_clients(self):
        clients = [
            {
                "id": "client_a",
                "name": "Client A",
                "folder": "/local/a",
                "industry": "tech",
                "subsegments": "cloud",
            },
            {
                "id": "client_b",
                "name": "Client B",
                "folder": "/local/b",
                "industry": "finance",
                "subsegments": "banking",
            },
        ]
        content = generate_vars_py(clients)
        compile(content, "<test>", "exec")
        assert '"client_a"' in content
        assert '"client_b"' in content


# ---------------------------------------------------------------------------
# TestEscapePythonString
# ---------------------------------------------------------------------------
class TestEscapePythonString:
    """Test string escaping for safe Python code generation."""

    def test_quotes_escaped(self):
        assert escape_python_string('say "hello"') == 'say \\"hello\\"'

    def test_backslashes_escaped(self):
        assert escape_python_string("path\\to\\file") == "path\\\\to\\\\file"

    def test_plain_string_unchanged(self):
        assert escape_python_string("hello world") == "hello world"
