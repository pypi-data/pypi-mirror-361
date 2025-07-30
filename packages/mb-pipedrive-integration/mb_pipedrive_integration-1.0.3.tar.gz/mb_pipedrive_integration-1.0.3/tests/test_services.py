import json
import pytest
import responses
import requests
from unittest.mock import patch

from mb_pipedrive_integration.services import PipedriveService
from mb_pipedrive_integration.dataclasses import (
    PipedriveConfig,
    PersonData,
    DealData,
)
from mb_pipedrive_integration.exceptions import (
    PipedriveAPIError,
    PipedriveNetworkError,
    PipedriveConfigError,
)


class TestPipedriveService:
    """Test individual PipedriveService methods"""

    def test_service_initialization_with_config(self):
        """Test service initialization with provided config"""
        config = PipedriveConfig(domain="test", api_token="token")
        service = PipedriveService(config)

        assert service.config == config
        assert service.base_url == "https://test.pipedrive.com/v1"

    @patch("mb_pipedrive_integration.services.PipedriveConfig.from_django_settings")
    def test_service_initialization_django_fallback(self, mock_django_config):
        """Test service initialization falling back to Django settings"""
        mock_config = PipedriveConfig(domain="django", api_token="django-token")
        mock_django_config.return_value = mock_config

        service = PipedriveService()

        assert service.config == mock_config
        mock_django_config.assert_called_once()

    @patch("mb_pipedrive_integration.services.PipedriveConfig.from_django_settings")
    @patch("mb_pipedrive_integration.services.PipedriveConfig.from_env")
    def test_service_initialization_env_fallback(self, mock_env_config, mock_django_config):
        """Test service initialization falling back to environment"""
        mock_django_config.side_effect = PipedriveConfigError("Django not available")
        mock_config = PipedriveConfig(domain="env", api_token="env-token")
        mock_env_config.return_value = mock_config

        service = PipedriveService()

        assert service.config == mock_config
        mock_django_config.assert_called_once()
        mock_env_config.assert_called_once()

    @responses.activate
    def test_make_request_get_success(self, mock_service):
        """Test successful GET request"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/test",
            json={"success": True, "data": {"test": "value"}},
            status=200,
        )

        result = mock_service._make_request("GET", "test")

        assert result is not None
        assert result["success"] is True
        assert result["data"]["test"] == "value"

    @responses.activate
    def test_make_request_post_success(self, mock_service):
        """Test successful POST request"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/test",
            json={"success": True, "data": {"id": 123}},
            status=200,
        )

        test_data = {"name": "Test"}
        result = mock_service._make_request("POST", "test", test_data)

        assert result is not None
        assert result["data"]["id"] == 123

    @responses.activate
    def test_make_request_api_failure(self, mock_service):
        """Test API request with success=false"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/test",
            json={"success": False, "error": "API Error"},
            status=200,
        )

        result = mock_service._make_request("GET", "test")
        assert result is None

    @responses.activate
    def test_make_request_http_error(self, mock_service):
        """Test API request with HTTP error status"""
        responses.add(
            responses.GET, f"{mock_service.base_url}/test", json={"error": "Not found"}, status=404
        )

        # The enhanced service should raise an exception for HTTP errors
        with pytest.raises(PipedriveAPIError) as exc_info:
            mock_service._make_request("GET", "test")

        assert exc_info.value.status_code == 404
        assert "HTTP 404" in str(exc_info.value)

    @responses.activate
    def test_create_person_minimal(self, mock_service):
        """Test creating person with minimal data"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/persons",
            json={"success": True, "data": {"id": 123, "name": "Test Person"}},
            status=200,
        )

        result = mock_service.create_person("Test Person")

        assert result is not None
        assert result["id"] == 123

        # Verify request data
        request_body = responses.calls[0].request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")
        request_data = json.loads(request_body)

        assert request_data["name"] == "Test Person"
        assert "email" not in request_data

    @responses.activate
    def test_create_person_with_all_data(self, mock_service):
        """Test creating person with all data"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/persons",
            json={"success": True, "data": {"id": 124}},
            status=200,
        )

        result = mock_service.create_person(
            name="Full Person",
            email="full@example.com",
            phone="123-456-7890",
            tags=["Tag1", "Tag2"],
        )

        assert result is not None

        # Verify request data includes all fields
        request_body = responses.calls[0].request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")
        request_data = json.loads(request_body)

        assert request_data["name"] == "Full Person"
        assert request_data["email"] == "full@example.com"
        assert request_data["phone"] == "123-456-7890"
        assert "Tag1" in request_data["label"]  # Custom tags
        assert "Tag2" in request_data["label"]

    @responses.activate
    def test_find_person_by_email_found(self, mock_service):
        """Test finding person by email when found"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/persons/search",
            json={
                "success": True,
                "data": {
                    "items": [
                        {
                            "item": {
                                "id": 123,
                                "name": "Found Person",
                                "emails": [{"value": "found@example.com"}],
                            }
                        }
                    ]
                },
            },
            status=200,
        )

        result = mock_service.find_person_by_email("found@example.com")

        assert result is not None
        assert result["id"] == 123
        assert result["name"] == "Found Person"

    @responses.activate
    def test_find_person_by_email_not_found(self, mock_service):
        """Test finding person by email when not found"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/persons/search",
            json={"success": True, "data": {"items": []}},
            status=200,
        )

        result = mock_service.find_person_by_email("notfound@example.com")
        assert result is None

    @responses.activate
    def test_create_organization(self, mock_service):
        """Test organization creation"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/organizations",
            json={"success": True, "data": {"id": 456, "name": "Test Org"}},
            status=200,
        )

        result = mock_service.create_organization("Test Org")

        assert result is not None
        assert result["id"] == 456
        assert result["name"] == "Test Org"

    @responses.activate
    def test_find_organization_by_name(self, mock_service):
        """Test finding organization by name"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations/search",
            json={"success": True, "data": {"items": [{"item": {"id": 456, "name": "Found Org"}}]}},
            status=200,
        )

        result = mock_service.find_organization_by_name("Found Org")

        assert result is not None
        assert result["id"] == 456
        assert result["name"] == "Found Org"

    @responses.activate
    def test_update_deal_stage(self, mock_service):
        """Test updating deal stage"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": True, "data": {"id": 123, "stage_id": 5}},
            status=200,
        )

        result = mock_service.update_deal_stage(123, "5")
        assert result is True

    @responses.activate
    def test_update_deal_stage_failure(self, mock_service):
        """Test updating deal stage failure"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": False, "error": "Deal not found"},
            status=404,
        )

        result = mock_service.update_deal_stage(123, "5")
        assert result is False

    @responses.activate
    def test_close_deal_won(self, mock_service):
        """Test closing deal as won"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": True, "data": {"id": 123, "status": "won"}},
            status=200,
        )

        result = mock_service.close_deal(123, "won")
        assert result is True

    @responses.activate
    def test_close_deal_lost(self, mock_service):
        """Test closing deal as lost"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": True, "data": {"id": 123, "status": "lost"}},
            status=200,
        )

        result = mock_service.close_deal(123, "lost")
        assert result is True

    @responses.activate
    def test_add_deal_notes(self, mock_service):
        """Test adding notes to a deal"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/notes",
            json={"success": True, "data": {"id": 999}},
            status=200,
        )

        deal_data = DealData(
            title="Test Deal",
            folder_number=12345,
            folder_id="abc-123",
            tenant=PersonData(name="John Tenant", email="tenant@example.com"),
            property_address="123 Test Street",
        )

        result = mock_service._add_deal_notes(123, deal_data)
        assert result is True

        # Verify note content includes relevant information
        request_body = responses.calls[0].request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")
        request_data = json.loads(request_body)

        assert request_data["deal_id"] == 123
        assert "Folder Number: 12345" in request_data["content"]
        assert "Tenant: John Tenant" in request_data["content"]
        assert "Property Address: 123 Test Street" in request_data["content"]

    def test_network_error_handling(self, mock_service):
        """Test handling of network errors"""
        # Mock requests.get to raise ConnectionError
        with patch(
            "requests.get", side_effect=requests.exceptions.ConnectionError("Network unreachable")
        ):
            with pytest.raises(PipedriveNetworkError) as exc_info:
                mock_service._make_request("GET", "test")

            assert "Network unreachable" in str(exc_info.value)
            assert exc_info.value.retry_count == 3  # max_retries

    def test_timeout_handling(self, mock_service):
        """Test handling of request timeouts"""
        # Mock requests.get to raise Timeout
        with patch("requests.get", side_effect=requests.exceptions.Timeout("Request timeout")):
            with pytest.raises(PipedriveNetworkError) as exc_info:
                mock_service._make_request("GET", "test")

            assert "timeout" in str(exc_info.value).lower()
            assert exc_info.value.retry_count == 3  # max_retries

    @responses.activate
    def test_add_deal_tags_success(self, mock_service):
        """Test adding tags to a deal successfully"""
        deal_id = 123
        tags = ["INQUILINO", "ASESOR INMOBILIARIO"]

        # Mock getting current deal (no existing tags)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": None  # No existing tags
                }
            },
            status=200
        )

        # Mock updating deal with tags
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,ASESOR INMOBILIARIO"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, tags)

        assert result is True
        assert len(responses.calls) == 2  # GET + PUT

        # Verify the PUT request data
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))
        assert request_data["label"] == "INQUILINO,ASESOR INMOBILIARIO"


    @responses.activate
    def test_add_deal_tags_with_existing_tags(self, mock_service):
        """Test adding tags to a deal that already has tags"""
        deal_id = 123
        new_tags = ["PROPIETARIO"]

        # Mock getting current deal (with existing tags)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG"
                }
            },
            status=200
        )

        # Mock updating deal with combined tags
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG,PROPIETARIO"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, new_tags)

        assert result is True

        # Verify the PUT request includes both existing and new tags
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        # Should contain all tags (order might vary due to set operation)
        label_tags = set(request_data["label"].split(","))
        expected_tags = {"INQUILINO", "EXISTING_TAG", "PROPIETARIO"}
        assert label_tags == expected_tags


    @responses.activate
    def test_add_deal_tags_duplicate_prevention(self, mock_service):
        """Test that duplicate tags are not added"""
        deal_id = 123
        duplicate_tags = ["INQUILINO", "EXISTING_TAG"]  # INQUILINO already exists

        # Mock getting current deal (with existing tags)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG"
                }
            },
            status=200
        )

        # Mock updating deal (should be the same tags)
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, duplicate_tags)

        assert result is True

        # Verify no duplicate tags in the request
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        label_tags = request_data["label"].split(",")
        # Should have only 2 unique tags, not 4
        assert len(set(label_tags)) == 2


    @responses.activate
    def test_add_deal_tags_empty_list(self, mock_service):
        """Test adding empty tag list"""
        deal_id = 123
        empty_tags = []

        result = mock_service.add_deal_tags(deal_id, empty_tags)

        assert result is True
        assert len(responses.calls) == 0  # No API calls should be made


    @responses.activate
    def test_add_deal_tags_get_deal_failure(self, mock_service):
        """Test failure when getting current deal info"""
        deal_id = 123
        tags = ["INQUILINO"]

        # Mock failed GET request
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={"success": False, "error": "Deal not found"},
            status=404
        )

        result = mock_service.add_deal_tags(deal_id, tags)

        assert result is False
        assert len(responses.calls) == 1  # Only GET call, no PUT


    @responses.activate
    def test_add_deal_tags_update_failure(self, mock_service):
        """Test failure when updating deal with tags"""
        deal_id = 123
        tags = ["INQUILINO"]

        # Mock successful GET
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": None
                }
            },
            status=200
        )

        # Mock failed PUT
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={"success": False, "error": "Update failed"},
            status=400
        )

        result = mock_service.add_deal_tags(deal_id, tags)

        assert result is False
        assert len(responses.calls) == 2  # GET + PUT


    @responses.activate
    def test_add_deal_tags_with_string_labels(self, mock_service):
        """Test handling existing labels as string (comma-separated)"""
        deal_id = 123
        new_tags = ["NEW_TAG"]

        # Mock getting current deal with string labels
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "TAG1,TAG2, TAG3 "  # Note spaces and formatting
                }
            },
            status=200
        )

        # Mock updating deal
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "TAG1,TAG2,TAG3,NEW_TAG"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, new_tags)

        assert result is True

        # Verify the request properly handles the string parsing
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        label_tags = set(request_data["label"].split(","))
        expected_tags = {"TAG1", "TAG2", "TAG3", "NEW_TAG"}
        assert label_tags == expected_tags
