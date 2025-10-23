"""
Unit tests for llms.py service functions.
Tests LLM creation, invocation, and interaction recording.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import base64
from io import BytesIO
from PIL import Image

from app.services.llms import (
    downsample_image_base64,
    create_openai_request_wrapper,
    create_llm,
    get_default_llm,
    invoke_llm,
    invoke_llm_with_image,
    record_llm_interaction,
    invoke_llm_with_images,
)


class TestLLMServices:
    """Test suite for LLM service functions."""

    @patch("app.services.llms.settings")
    def test_downsample_image_base64_no_downsampling_needed(self, mock_settings):
        """Test image downsampling when image is already small enough."""
        mock_settings.VISION_IMAGE_MAX_DIMENSION = 512

        # Create a small test image
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()

        result = downsample_image_base64(img_b64, 512)

        # Should return original image since it's small
        assert result == img_b64

    @patch("app.services.llms.settings")
    def test_downsample_image_base64_with_downsampling(self, mock_settings):
        """Test image downsampling when image exceeds max dimension."""
        mock_settings.VISION_IMAGE_MAX_DIMENSION = 100

        # Create a large test image
        img = Image.new("RGB", (400, 300), color="blue")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()

        result = downsample_image_base64(img_b64, 100)

        # Should return different base64 (downsampled image)
        assert result != img_b64
        assert isinstance(result, str)

        # Decode and verify dimensions
        decoded = base64.b64decode(result)
        downsampled_img = Image.open(BytesIO(decoded))
        assert downsampled_img.size[0] <= 100
        assert downsampled_img.size[1] <= 100

    def test_downsample_image_base64_invalid_input(self):
        """Test image downsampling with invalid base64 input."""
        result = downsample_image_base64("invalid_base64!")
        # Should return original invalid input
        assert result == "invalid_base64!"

    @patch("PIL.Image")
    def test_downsample_image_base64_pil_not_available(self, mock_image):
        """Test image downsampling when PIL is not available."""
        mock_image.open.side_effect = ImportError("PIL not available")

        img_b64 = "fake_image_data"
        result = downsample_image_base64(img_b64)

        # Should return original image
        assert result == img_b64

    @patch("app.services.llms.openai_request_queue")
    def test_create_openai_request_wrapper(self, mock_queue):
        """Test OpenAI request wrapper creation."""
        mock_formatted_text = "test formatted text"
        mock_model_class = "gpt-4"

        result = create_openai_request_wrapper(mock_formatted_text, mock_model_class)

        # Should return a callable function
        assert callable(result)

    @patch("app.services.llms.ChatOpenAI")
    @patch("app.services.llms.ChatBedrock")
    @patch("app.services.llms.ChatOllama")
    @patch("app.services.llms.Replicate")
    def test_create_llm_openai(
        self, mock_replicate, mock_ollama, mock_bedrock, mock_openai
    ):
        """Test LLM creation for OpenAI provider."""
        mock_instance = Mock()
        mock_openai.return_value = mock_instance

        result = create_llm("openai", "gpt-4", api_key="test_key")

        mock_openai.assert_called_once()
        assert result == mock_instance

    @patch("app.services.llms.ChatOpenAI")
    @patch("app.services.llms.ChatBedrock")
    @patch("app.services.llms.ChatOllama")
    @patch("app.services.llms.Replicate")
    def test_create_llm_bedrock(
        self, mock_replicate, mock_ollama, mock_bedrock, mock_openai
    ):
        """Test LLM creation for AWS Bedrock provider."""
        mock_instance = Mock()
        mock_bedrock.return_value = mock_instance

        result = create_llm(
            "aws", "anthropic.claude-v2", additional_params={"region": "us-east-1"}
        )

        mock_bedrock.assert_called_once()
        assert result is not None  # BedrockWrapper instance

    @patch("app.services.llms.ChatOpenAI")
    @patch("app.services.llms.ChatBedrock")
    @patch("app.services.llms.ChatOllama")
    @patch("app.services.llms.Replicate")
    def test_create_llm_ollama(
        self, mock_replicate, mock_ollama, mock_bedrock, mock_openai
    ):
        """Test LLM creation for Ollama provider."""
        mock_instance = Mock()
        mock_ollama.return_value = mock_instance

        result = create_llm(
            "ollama",
            "llama2",
            additional_params={"OLLAMA_BASE_URL": "http://localhost:11434"},
        )

        mock_ollama.assert_called_once()
        assert result == mock_instance

    @patch("app.services.llms.ChatOpenAI")
    @patch("app.services.llms.ChatBedrock")
    @patch("app.services.llms.ChatOllama")
    @patch("app.services.llms.ReplicateWrapper")
    def test_create_llm_replicate(
        self, mock_replicate_wrapper, mock_ollama, mock_bedrock, mock_openai
    ):
        """Test LLM creation for Replicate provider."""
        mock_instance = Mock()
        mock_replicate_wrapper.return_value = mock_instance

        result = create_llm(
            "replicate",
            "meta/llama-2-70b-chat",
            additional_params={"api_token": "test_token"},
        )

        mock_replicate_wrapper.assert_called_once()
        assert result is not None  # ReplicateWrapper instance

    def test_create_llm_invalid_provider(self):
        """Test LLM creation with invalid provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm("invalid_provider", "model_name")

    @patch("app.services.llms.select")
    @patch("app.services.llms.Session")
    def test_get_default_llm_success(self, mock_session_class, mock_select):
        """Test getting default LLM for user."""
        # Mock database session and query
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_user = Mock()
        mock_user.id = 1
        mock_user.default_llm = None  # User has no default LLM set

        mock_session.get.return_value = mock_user

        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_session.get.return_value = mock_user

        # Mock system defaults
        mock_system_model = Mock()
        mock_system_model.provider.value = "openai"
        mock_system_model.model_id = "gpt-4"
        mock_system_model.name = "GPT-4"
        mock_session.exec.return_value.all.return_value = [mock_system_model]

        with patch("app.services.llms.settings") as mock_settings:
            mock_settings.llm_providers = ["openai"]
            with patch("app.services.llms.create_llm") as mock_create_llm:
                mock_create_llm.return_value = Mock()
                result = get_default_llm(mock_session, mock_user)

                mock_create_llm.assert_called_once_with(
                    provider=mock_system_model.provider,
                    model_id="gpt-4",
                    temperature=0.0,
                )
                assert result is not None

    @patch("app.services.llms.select")
    @patch("app.services.llms.Session")
    def test_get_default_llm_no_model(self, mock_session_class, mock_select):
        """Test getting default LLM when no model is configured."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_user = Mock()
        mock_user.id = 1
        mock_user.default_llm = None
        mock_session.get.return_value = mock_user

        # Mock empty system defaults
        mock_session.exec.return_value.all.return_value = []

        with patch("app.services.llms.settings") as mock_settings:
            mock_settings.llm_providers = ["openai"]
            with pytest.raises(ValueError, match="No default LLM available"):
                get_default_llm(mock_session, mock_user)

    @patch("app.services.llms.global_rate_limiter")
    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_success(self, mock_execute, mock_rate_limiter):
        """Test successful LLM invocation."""
        mock_rate_limiter.wait_for_capacity.return_value = True
        mock_execute.return_value = Mock(content="Test response")
        mock_llm = Mock()

        result = invoke_llm(mock_llm, "Test prompt")

        assert result == "Test response"
        mock_execute.assert_called_once()

    @patch("app.services.llms.global_rate_limiter")
    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_variables(self, mock_execute, mock_rate_limiter):
        """Test LLM invocation with template variables."""
        mock_rate_limiter.wait_for_capacity.return_value = True
        mock_execute.return_value = Mock(content="Hello World")
        mock_llm = Mock()

        result = invoke_llm(mock_llm, "Hello {name}", {"name": "World"})

        assert result == "Hello World"
        mock_execute.assert_called_once()

    @patch("app.services.llms.global_rate_limiter")
    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_error(self, mock_execute, mock_rate_limiter):
        """Test LLM invocation error handling."""
        mock_rate_limiter.wait_for_capacity.return_value = True
        mock_execute.side_effect = Exception("API Error")
        mock_llm = Mock()

        with pytest.raises(Exception):
            invoke_llm(mock_llm, "Test prompt")

    @patch("app.services.llms.HumanMessage")
    @patch("app.services.llms.downsample_image_base64")
    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_image_success(
        self, mock_execute, mock_downsample, mock_human_message
    ):
        """Test LLM invocation with image."""
        mock_execute.return_value = Mock(content="Image description")
        mock_downsample.return_value = "downsampled_image"
        mock_message_instance = Mock()
        mock_human_message.return_value = mock_message_instance

        result = invoke_llm_with_image(
            Mock(), "Describe this image", image_base64="base64_image_data"
        )

        assert result == "Image description"
        mock_execute.assert_called_once()

    @patch("app.services.llms.HumanMessage")
    @patch("app.services.llms.downsample_image_base64")
    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_image_error(
        self, mock_execute, mock_downsample, mock_human_message
    ):
        """Test LLM invocation with image error handling."""
        mock_execute.side_effect = Exception("Vision API Error")
        mock_downsample.return_value = "downsampled_image"
        mock_message_instance = Mock()
        mock_human_message.return_value = mock_message_instance

        result = invoke_llm_with_image(
            Mock(), "Describe this image", image_base64="base64_image_data"
        )

        assert "Error processing image" in result
        mock_execute.assert_called_once()

    @patch("app.services.llms.Session")
    @patch("app.services.llms.LlmInteraction")
    def test_record_llm_interaction_success(
        self, mock_interaction_class, mock_session_class
    ):
        """Test recording LLM interaction in database."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_interaction = Mock()
        mock_interaction_class.return_value = mock_interaction

        record_llm_interaction(
            session=mock_session,
            user_id=1,
            functionality="chat",
            input_data="Test prompt",
            output_data="Test response",
            metadata={"model": "gpt-4", "tokens_used": 100},
        )

        mock_session.add.assert_called_once_with(mock_interaction)
        mock_session.commit.assert_called_once()

    @patch("app.services.llms.Session")
    @patch("app.services.llms.LlmInteraction")
    def test_record_llm_interaction_error(
        self, mock_interaction_class, mock_session_class
    ):
        """Test LLM interaction recording error handling."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.commit.side_effect = Exception("Database error")

        # The function should handle database errors gracefully (not implemented yet)
        # For now, it raises exceptions
        with pytest.raises(Exception):
            record_llm_interaction(
                session=mock_session,
                user_id=1,
                functionality="chat",
                input_data="Test prompt",
                output_data="Test response",
                metadata={"model": "gpt-4", "tokens_used": 100},
            )

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_images_multiple(self, mock_execute):
        """Test invoking LLM with multiple images."""
        mock_response = Mock()
        mock_response.content = "Combined response"
        mock_execute.return_value = mock_response

        mock_llm = Mock()
        images = ["image1.jpg", "image2.jpg"]
        result = invoke_llm_with_images(
            mock_llm, "Describe these images", variables=None, images_list=images
        )

        assert result == "Combined response"
        assert mock_execute.call_count == 1

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_images_single(self, mock_execute):
        """Test invoking LLM with single image."""
        mock_response = Mock()
        mock_response.content = "Single image response"
        mock_execute.return_value = mock_response

        mock_llm = Mock()
        images = ["image1.jpg"]
        result = invoke_llm_with_images(
            mock_llm, "Describe this image", variables=None, images_list=images
        )

        assert result == "Single image response"
        assert mock_execute.call_count == 1

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_images_no_images(self, mock_execute):
        """Test invoking LLM with no images (fallback to text-only)."""
        mock_response = Mock()
        mock_response.content = "Text response"
        mock_execute.return_value = mock_response

        mock_llm = Mock()
        result = invoke_llm_with_images(
            mock_llm, "Test prompt", variables=None, images_list=[]
        )

        assert result == "Text response"
        mock_execute.assert_called_once()

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_invoke_llm_with_images_error(self, mock_execute):
        """Test error handling in multi-image LLM invocation."""
        mock_execute.side_effect = Exception("Failed to process images")

        mock_llm = Mock()
        images = ["image1.jpg", "image2.jpg"]
        result = invoke_llm_with_images(
            mock_llm, "Describe these images", variables=None, images_list=images
        )

        assert "Error processing multiple images" in result
