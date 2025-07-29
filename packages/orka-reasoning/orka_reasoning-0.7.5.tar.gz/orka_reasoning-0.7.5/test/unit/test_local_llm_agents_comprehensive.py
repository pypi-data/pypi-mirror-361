"""
Comprehensive unit tests for the local_llm_agents.py module.
Tests LocalLLMAgent and the _count_tokens utility function.
"""

from unittest.mock import Mock, patch

from orka.agents.local_llm_agents import LocalLLMAgent, _count_tokens


class TestCountTokensFunction:
    """Test suite for the _count_tokens utility function."""

    def test_count_tokens_empty_text(self):
        """Test token counting with empty text."""
        assert _count_tokens("") == 0
        assert _count_tokens(None) == 0

    def test_count_tokens_non_string(self):
        """Test token counting with non-string input."""
        assert _count_tokens(123) == 0
        assert _count_tokens([]) == 0
        assert _count_tokens({}) == 0

    def test_count_tokens_without_tiktoken(self):
        """Test token counting when tiktoken is not available."""
        with patch("builtins.__import__", side_effect=ImportError("No module named 'tiktoken'")):
            result = _count_tokens("Hello world test")
            # Should use character-based estimation (len // 4)
            expected = max(1, len("Hello world test") // 4)
            assert result == expected

    def test_count_tokens_long_text_fallback(self):
        """Test token counting with long text using fallback."""
        long_text = "This is a very long text " * 100
        # Without tiktoken, should use character estimation
        with patch("builtins.__import__", side_effect=ImportError()):
            result = _count_tokens(long_text)
            expected = max(1, len(long_text) // 4)
            assert result == expected


class TestLocalLLMAgent:
    """Test suite for the LocalLLMAgent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_params = {
            "model": "llama3.2:latest",
            "model_url": "http://localhost:11434/api/generate",
            "provider": "ollama",
            "temperature": 0.7,
        }
        self.agent = LocalLLMAgent(
            agent_id="test_llm_agent",
            prompt="Test prompt: {{ input }}",
            queue=[],  # Required by LegacyBaseAgent
            **self.test_params,
        )

    def test_initialization(self):
        """Test LocalLLMAgent initialization."""
        assert self.agent.agent_id == "test_llm_agent"
        assert self.agent.prompt == "Test prompt: {{ input }}"
        assert self.agent.params == self.test_params

    def test_initialization_with_defaults(self):
        """Test initialization with minimal parameters."""
        agent = LocalLLMAgent(agent_id="simple_agent", prompt=None, queue=[])

        assert agent.agent_id == "simple_agent"
        assert agent.prompt is None
        assert isinstance(agent.params, dict)

    @patch("orka.agents.local_llm_agents._count_tokens")
    @patch("time.time")
    def test_run_with_string_input(self, mock_time, mock_count_tokens):
        """Test run method with string input."""
        mock_time.side_effect = [1000.0, 1000.5]  # 500ms latency
        mock_count_tokens.side_effect = [10, 15, 25]  # prompt, completion, total

        with patch.object(self.agent, "_call_ollama", return_value="Mock response"):
            result = self.agent.run("Test input")

            assert isinstance(result, dict)
            assert "response" in result
            assert "_metrics" in result
            assert result["_metrics"]["latency_ms"] == 500
            assert result["_metrics"]["model"] == "llama3.2:latest"
            assert result["_metrics"]["provider"] == "ollama"

    @patch("orka.agents.local_llm_agents._count_tokens")
    @patch("time.time")
    def test_run_with_dict_input(self, mock_time, mock_count_tokens):
        """Test run method with dictionary input."""
        mock_time.side_effect = [1000.0, 1001.0]  # 1000ms latency
        mock_count_tokens.side_effect = [20, 30, 50]

        input_data = {
            "input": "Test content",
            "model": "custom_model",
            "temperature": 0.9,
        }

        with patch.object(self.agent, "_call_ollama", return_value="Custom response"):
            result = self.agent.run(input_data)

            assert isinstance(result, dict)
            assert result["_metrics"]["model"] == "custom_model"
            assert result["_metrics"]["latency_ms"] == 1000

    @patch("orka.agents.local_llm_agents._count_tokens")
    def test_run_with_lm_studio_provider(self, mock_count_tokens):
        """Test run method with LM Studio provider."""
        mock_count_tokens.return_value = 10

        self.agent.params["provider"] = "lm_studio"
        self.agent.params["model_url"] = "http://localhost:1234"

        with patch.object(self.agent, "_call_lm_studio", return_value="LM Studio response"):
            with patch("time.time", side_effect=[1000.0, 1000.2]):
                result = self.agent.run("Test input")

                assert result["_metrics"]["provider"] == "lm_studio"

    @patch("orka.agents.local_llm_agents._count_tokens")
    def test_run_with_openai_compatible_provider(self, mock_count_tokens):
        """Test run method with OpenAI-compatible provider."""
        mock_count_tokens.return_value = 10

        self.agent.params["provider"] = "openai_compatible"
        self.agent.params["model_url"] = "http://localhost:8000"

        with patch.object(self.agent, "_call_openai_compatible", return_value="OpenAI response"):
            with patch("time.time", side_effect=[1000.0, 1000.3]):
                result = self.agent.run("Test input")

                assert result["_metrics"]["provider"] == "openai_compatible"

    def test_run_parse_llm_json_response_success(self):
        """Test run method with successful JSON parsing."""
        mock_response = '```json\n{"response": "Parsed response", "confidence": "0.95"}\n```'

        with patch.object(self.agent, "_call_ollama", return_value=mock_response):
            with patch("time.time", side_effect=[1000.0, 1000.1]):
                with patch("orka.agents.local_llm_agents._count_tokens", return_value=10):
                    result = self.agent.run("Test input")

                    assert result["response"] == "Parsed response"
                    assert result["confidence"] == "0.95"

    def test_run_parse_llm_json_response_failure(self):
        """Test run method with failed JSON parsing."""
        mock_response = "Invalid JSON response"

        with patch.object(self.agent, "_call_ollama", return_value=mock_response):
            with patch("time.time", side_effect=[1000.0, 1000.1]):
                with patch("orka.agents.local_llm_agents._count_tokens", return_value=10):
                    result = self.agent.run("Test input")

                    assert result["response"] == "Invalid JSON response"
                    assert (
                        result["internal_reasoning"]
                        == "Could not parse as JSON, using raw response"
                    )

    def test_run_with_exception(self):
        """Test run method when an exception occurs."""
        with patch.object(self.agent, "_call_ollama", side_effect=Exception("LLM error")):
            with patch("time.time", side_effect=[1000.0, 1000.1]):
                with patch("orka.agents.local_llm_agents._count_tokens", return_value=10):
                    result = self.agent.run("Test input")

                    assert "[LocalLLMAgent error: LLM error]" in result["response"]
                    assert result["confidence"] == "0.0"
                    assert result["_metrics"]["error"] is True

    def test_build_prompt_simple(self):
        """Test build_prompt with simple template replacement."""
        result = self.agent.build_prompt("test input", "Input: {{ input }}")
        assert result == "Input: test input"

    def test_build_prompt_with_none_template(self):
        """Test build_prompt with None template."""
        result = self.agent.build_prompt("test input", None)
        assert result == "Test prompt: test input"  # Uses agent's prompt template

    def test_build_prompt_with_previous_outputs(self):
        """Test build_prompt with previous outputs context."""
        template = "Input: {{ input }}, Previous: {{ previous_outputs.agent1 }}"
        context = {
            "previous_outputs": {"agent1": "previous result"},
        }

        with patch("jinja2.Template") as mock_template_class:
            mock_template = Mock()
            mock_template.render.return_value = "Rendered template"
            mock_template_class.return_value = mock_template

            result = self.agent.build_prompt("test input", template, context)

            assert result == "Rendered template"
            mock_template.render.assert_called_once()

    def test_build_prompt_jinja2_fallback(self):
        """Test build_prompt fallback when Jinja2 fails."""
        template = "Input: {{ input }}, Previous: {{ previous_outputs.agent1 }}"
        context = {
            "previous_outputs": {"agent1": "previous result"},
        }

        with patch("jinja2.Template", side_effect=Exception("Jinja2 error")):
            result = self.agent.build_prompt("test input", template, context)

            # Should fall back to manual replacement
            assert "test input" in result

    def test_build_prompt_manual_previous_outputs(self):
        """Test build_prompt with manual previous outputs replacement."""
        template = "Input: {{ input }}, Prev: {{ previous_outputs.agent1 }}"
        context = {
            "previous_outputs": {"agent1": "result1"},
        }

        with patch("jinja2.Template", side_effect=ImportError("No jinja2")):
            result = self.agent.build_prompt("test input", template, context)

            # Should replace manually
            assert "test input" in result
            assert "result1" in result

    def test_call_ollama_success(self):
        """Test _call_ollama method."""
        mock_response = {
            "response": "Ollama test response",
        }

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = self.agent._call_ollama(
                "http://localhost:11434/api/generate",
                "llama3.2",
                "Test prompt",
                0.7,
            )

            assert result == "Ollama test response"

            # Verify request payload
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["model"] == "llama3.2"
            assert payload["prompt"] == "Test prompt"
            assert payload["options"]["temperature"] == 0.7
            assert payload["stream"] is False

    def test_call_ollama_empty_response(self):
        """Test _call_ollama with empty response."""
        mock_response = {"response": ""}

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = self.agent._call_ollama("http://localhost:11434", "model", "prompt", 0.5)

            assert result == ""

    def test_call_lm_studio_success(self):
        """Test _call_lm_studio method."""
        mock_response = {
            "choices": [
                {"message": {"content": "LM Studio response"}},
            ],
        }

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = self.agent._call_lm_studio(
                "http://localhost:1234",
                "local_model",
                "Test prompt",
                0.8,
            )

            assert result == "LM Studio response"

            # Verify URL formatting
            call_args = mock_post.call_args
            url = call_args[0][0]
            assert url.endswith("/v1/chat/completions")

            # Verify payload
            payload = call_args[1]["json"]
            assert payload["model"] == "local_model"
            assert payload["messages"][0]["content"] == "Test prompt"
            assert payload["temperature"] == 0.8

    def test_call_lm_studio_url_formatting(self):
        """Test _call_lm_studio URL formatting variations."""
        mock_response = {"choices": [{"message": {"content": "response"}}]}

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            # Test URL with trailing slash
            self.agent._call_lm_studio("http://localhost:1234/", "model", "prompt", 0.5)
            call_url = mock_post.call_args[0][0]
            assert call_url == "http://localhost:1234/v1/chat/completions"

            # Test URL without trailing slash
            self.agent._call_lm_studio("http://localhost:1234", "model", "prompt", 0.5)
            call_url = mock_post.call_args[0][0]
            assert call_url == "http://localhost:1234/v1/chat/completions"

    def test_call_openai_compatible_success(self):
        """Test _call_openai_compatible method."""
        mock_response = {
            "choices": [
                {"message": {"content": "OpenAI compatible response"}},
            ],
        }

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = self.agent._call_openai_compatible(
                "http://localhost:8000/v1/chat/completions",
                "custom_model",
                "Test prompt",
                0.9,
            )

            assert result == "OpenAI compatible response"

            # Verify payload structure
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["model"] == "custom_model"
            assert payload["messages"][0]["role"] == "user"
            assert payload["messages"][0]["content"] == "Test prompt"
            assert payload["temperature"] == 0.9
            assert payload["stream"] is False

    def test_provider_method_selection(self):
        """Test correct provider method selection."""
        test_cases = [
            ("ollama", "_call_ollama"),
            ("lm_studio", "_call_lm_studio"),
            ("openai_compatible", "_call_openai_compatible"),
            ("unknown", "_call_ollama"),  # Default fallback
        ]

        for provider, expected_method in test_cases:
            self.agent.params["provider"] = provider

            with patch.object(self.agent, "_call_ollama", return_value="ollama"):
                with patch.object(self.agent, "_call_lm_studio", return_value="lm_studio"):
                    with patch.object(self.agent, "_call_openai_compatible", return_value="openai"):
                        with patch("time.time", side_effect=[1000.0, 1000.1]):
                            with patch(
                                "orka.agents.local_llm_agents._count_tokens",
                                return_value=10,
                            ):
                                result = self.agent.run("test")

                                if provider == "ollama" or provider == "unknown":
                                    assert "ollama" in str(result)
                                elif provider == "lm_studio":
                                    assert "lm_studio" in str(result)
                                elif provider == "openai_compatible":
                                    assert "openai" in str(result)

    def test_complex_input_handling(self):
        """Test handling of complex input data structures."""
        complex_input = {
            "input": "Complex test",
            "metadata": {"type": "test", "priority": "high"},
            "previous_outputs": {"agent1": "result1"},
        }

        with patch.object(self.agent, "_call_ollama", return_value="Complex response"):
            with patch("time.time", side_effect=[1000.0, 1000.1]):
                with patch("orka.agents.local_llm_agents._count_tokens", return_value=10):
                    result = self.agent.run(complex_input)

                    assert isinstance(result, dict)
                    assert "response" in result
                    assert "formatted_prompt" in result

    def test_self_evaluation_prompt_inclusion(self):
        """Test that self-evaluation instructions are included in prompts."""
        with patch.object(self.agent, "_call_ollama", return_value="Response") as mock_call:
            with patch("time.time", side_effect=[1000.0, 1000.1]):
                with patch("orka.agents.local_llm_agents._count_tokens", return_value=10):
                    self.agent.run("Test input")

                    # Verify self-evaluation instructions were added to prompt
                    call_args = mock_call.call_args[0]
                    full_prompt = call_args[2]  # prompt parameter

                    assert "CRITICAL INSTRUCTIONS" in full_prompt
                    assert "valid JSON" in full_prompt
                    assert "confidence" in full_prompt
