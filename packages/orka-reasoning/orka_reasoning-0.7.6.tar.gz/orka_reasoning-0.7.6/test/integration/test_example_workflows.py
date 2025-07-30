"""
Integration tests using real YAML workflow examples.
Tests actual OrKa configurations with mocked external services.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from orka.orchestrator import Orchestrator


class TestExampleWorkflows:
    """Test real workflow examples with proper mocking."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up all necessary mocks for external services."""
        with patch("redis.from_url") as mock_redis, patch(
            "orka.agents.llm_agents.client",
        ) as mock_openai, patch("orka.tools.search_tools.DDGS") as mock_ddg:
            # Mock Redis
            mock_redis.return_value = MagicMock()

            # Mock OpenAI responses
            def create_openai_response(content="Test response"):
                response = MagicMock()
                response.choices = [MagicMock()]
                response.choices[0].message.content = content
                response.usage.total_tokens = 100
                response.usage.prompt_tokens = 80
                response.usage.completion_tokens = 20
                return response

            mock_openai.chat.completions.create.return_value = create_openai_response()

            # Mock DuckDuckGo search
            mock_ddg_instance = MagicMock()
            mock_ddg_instance.text.return_value = [
                MagicMock(title="Test Result", body="Test search result", href="http://test.com"),
            ]
            mock_ddg.return_value = mock_ddg_instance

            yield {
                "redis": mock_redis,
                "openai": mock_openai,
                "ddg": mock_ddg,
            }

    def test_basic_example_workflow(self, setup_mocks):
        """Test the basic example.yml workflow - fork/join with classification."""
        example_path = Path("examples/example.yml")
        assert example_path.exists(), "example.yml not found"

        # Create orchestrator with real config
        orchestrator = Orchestrator(str(example_path))

        # Verify orchestrator structure
        assert orchestrator.orchestrator_cfg["id"] == "orka-ui"
        assert orchestrator.orchestrator_cfg["strategy"] == "parallel"

        # Verify agents were created
        expected_agents = [
            "fork_2",
            "duckduckgo_4",
            "openai-classification_5",
            "join_1",
            "openai-binary_6",
            "router_7",
        ]
        for agent_id in expected_agents:
            assert agent_id in orchestrator.agents, f"Agent {agent_id} not found"

        # Test agent types
        assert orchestrator.agents["fork_2"].__class__.__name__ == "ForkNode"
        assert orchestrator.agents["duckduckgo_4"].__class__.__name__ == "DuckDuckGoTool"
        assert (
            orchestrator.agents["openai-classification_5"].__class__.__name__
            == "OpenAIClassificationAgent"
        )

    def test_complex_flow_workflow_structure(self, setup_mocks):
        """Test the complex_flow.yml workflow - temporal analysis with search."""
        complex_path = Path("examples/complex_flow.yml")
        assert complex_path.exists(), "complex_flow.yml not found"

        # Create orchestrator
        orchestrator = Orchestrator(str(complex_path))

        # Verify complex workflow structure
        assert orchestrator.orchestrator_cfg["strategy"] == "parallel"

        # Verify all agents exist
        expected_agents = [
            "detect_change",
            "fork_temporal",
            "generate_before_query",
            "generate_after_query",
            "search_before",
            "search_after",
            "join_paths",
            "synthesize_timeline_answer",
        ]
        for agent_id in expected_agents:
            assert agent_id in orchestrator.agents, f"Agent {agent_id} not found"

        # Verify fork node has correct targets
        fork_agent = orchestrator.agents["fork_temporal"]
        assert hasattr(fork_agent, "targets")

    def test_basic_memory_workflow_structure(self, setup_mocks):
        """Test the basic_memory.yml workflow - memory operations."""
        memory_path = Path("examples/basic_memory.yml")
        assert memory_path.exists(), "basic_memory.yml not found"

        # Create orchestrator
        orchestrator = Orchestrator(str(memory_path))

        # Verify memory agents exist
        memory_agents = ["memory-read_0", "memory-write_final"]
        for agent_id in memory_agents:
            assert agent_id in orchestrator.agents, f"Memory agent {agent_id} not found"

        # Verify other key agents
        key_agents = ["openai-answer_2", "fork_3", "join_9", "openai-binary_10", "router_11"]
        for agent_id in key_agents:
            assert agent_id in orchestrator.agents, f"Key agent {agent_id} not found"

    def test_failover_workflow_structure(self, setup_mocks):
        """Test the failover.yml workflow - error handling."""
        failover_path = Path("examples/failover.yml")
        assert failover_path.exists(), "failover.yml not found"

        # Create orchestrator
        orchestrator = Orchestrator(str(failover_path))

        # Verify decision-tree strategy
        assert orchestrator.orchestrator_cfg["strategy"] == "decision-tree"

        # Verify failover agents exist
        failover_agents = ["test_failover", "test_failover2"]
        for agent_id in failover_agents:
            assert agent_id in orchestrator.agents, f"Failover agent {agent_id} not found"

        # Verify other agents
        other_agents = ["answer_9", "need_answer", "router_answer"]
        for agent_id in other_agents:
            assert agent_id in orchestrator.agents, f"Agent {agent_id} not found"

    def test_agent_dependencies_basic_example(self, setup_mocks):
        """Test that agent dependencies are properly configured in basic example."""
        example_path = Path("examples/example.yml")
        orchestrator = Orchestrator(str(example_path))

        # Test specific dependency relationships
        join_agent = orchestrator.agents["join_1"]
        router_agent = orchestrator.agents["router_7"]

        # Verify join agent has the right group_id
        assert hasattr(join_agent, "group_id")

        # Verify router has decision key
        assert hasattr(router_agent, "decision_key") or hasattr(router_agent, "params")

    def test_memory_namespace_configuration(self, setup_mocks):
        """Test memory namespace configuration in memory workflow."""
        memory_path = Path("examples/basic_memory.yml")
        orchestrator = Orchestrator(str(memory_path))

        # Check that memory agents have namespace
        memory_read = orchestrator.agents["memory-read_0"]
        memory_write = orchestrator.agents["memory-write_final"]

        # Both should be memory-related nodes
        assert hasattr(memory_read, "namespace") or hasattr(memory_read, "node_id")
        assert hasattr(memory_write, "namespace") or hasattr(memory_write, "node_id")

    def test_search_integration_configuration(self, setup_mocks):
        """Test DuckDuckGo search integration in complex flow."""
        complex_path = Path("examples/complex_flow.yml")
        orchestrator = Orchestrator(str(complex_path))

        # Verify search agents exist and are configured
        search_agents = ["search_before", "search_after"]
        for agent_id in search_agents:
            agent = orchestrator.agents[agent_id]
            assert agent.__class__.__name__ == "DuckDuckGoTool"
            assert hasattr(agent, "prompt") or hasattr(agent, "tool_id")

    def test_classification_options_configuration(self, setup_mocks):
        """Test classification agent options are properly configured."""
        example_path = Path("examples/example.yml")
        orchestrator = Orchestrator(str(example_path))

        # Check classification agent
        classifier = orchestrator.agents["openai-classification_5"]
        assert classifier.__class__.__name__ == "OpenAIClassificationAgent"

        # Verify it has params configured (where options are stored)
        assert hasattr(classifier, "params")

    def test_router_mapping_configuration(self, setup_mocks):
        """Test router mapping configuration in basic example."""
        example_path = Path("examples/example.yml")
        orchestrator = Orchestrator(str(example_path))

        # Check router configuration
        router = orchestrator.agents["router_7"]
        assert router.__class__.__name__ == "RouterNode"

        # Router should have routing configuration
        assert hasattr(router, "routing_map") or hasattr(router, "params")

    def test_fork_targets_configuration(self, setup_mocks):
        """Test fork node targets are properly configured."""
        example_path = Path("examples/example.yml")
        orchestrator = Orchestrator(str(example_path))

        # Check fork configuration
        fork = orchestrator.agents["fork_2"]
        assert fork.__class__.__name__ == "ForkNode"

        # Fork should have targets configured
        assert hasattr(fork, "targets")

    def test_workflow_config_validation(self, setup_mocks):
        """Test that all example workflows pass validation."""
        example_files = [
            "examples/example.yml",
            "examples/complex_flow.yml",
            "examples/basic_memory.yml",
            "examples/failover.yml",
        ]

        for example_file in example_files:
            if Path(example_file).exists():
                # Should not raise an exception
                orchestrator = Orchestrator(example_file)
                assert orchestrator is not None
                assert len(orchestrator.agents) > 0

    def test_mixed_agent_types_integration(self, setup_mocks):
        """Test that mixed agent types work together in complex workflows."""
        complex_path = Path("examples/complex_flow.yml")
        orchestrator = Orchestrator(str(complex_path))

        # Verify we have different types of agents working together
        agent_types = set()
        for agent in orchestrator.agents.values():
            agent_types.add(agent.__class__.__name__)

        # Should have multiple different agent types
        assert len(agent_types) >= 3, f"Expected multiple agent types, got: {agent_types}"

        # Should include both OpenAI and search agents
        assert any("OpenAI" in agent_type for agent_type in agent_types)
        assert any("DuckDuckGo" in agent_type for agent_type in agent_types)
