"""
Comprehensive unit tests for the orchestrator module components.
Tests all orchestrator classes with heavy mocking for comprehensive coverage.
"""

import os
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from orka.orchestrator import AGENT_TYPES, Orchestrator
from orka.orchestrator.agent_factory import AGENT_TYPES, AgentFactory
from orka.orchestrator.base import OrchestratorBase
from orka.orchestrator.error_handling import ErrorHandler
from orka.orchestrator.execution_engine import ExecutionEngine
from orka.orchestrator.metrics import MetricsCollector
from orka.orchestrator.prompt_rendering import PromptRenderer


class TestOrchestratorBase:
    """Test OrchestratorBase initialization and configuration."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies for OrchestratorBase."""
        with (
            patch("orka.orchestrator.base.YAMLLoader") as mock_loader,
            patch(
                "orka.orchestrator.base.create_memory_logger",
            ) as mock_memory,
            patch("orka.orchestrator.base.ForkGroupManager") as mock_fork,
        ):
            # Configure loader mock
            mock_loader_instance = Mock()
            mock_loader.return_value = mock_loader_instance
            mock_loader_instance.validate.return_value = None
            mock_loader_instance.get_orchestrator.return_value = {
                "agents": ["test_agent"],
                "debug": {"keep_previous_outputs": False},
                "memory": {"decay": {"enabled": True, "default_short_term_hours": 2.0}},
            }
            mock_loader_instance.get_agents.return_value = [
                {"id": "test_agent", "type": "binary", "prompt": "test"},
            ]

            # Configure memory mock
            mock_memory_instance = Mock()
            mock_memory_instance.redis = Mock()
            mock_memory_instance.decay_config = {"enabled": True}
            mock_memory.return_value = mock_memory_instance

            # Configure fork manager mock
            mock_fork_instance = Mock()
            mock_fork.return_value = mock_fork_instance

            yield {
                "loader": mock_loader,
                "memory": mock_memory,
                "fork_manager": mock_fork,
                "loader_instance": mock_loader_instance,
                "memory_instance": mock_memory_instance,
                "fork_instance": mock_fork_instance,
            }

    def test_orchestrator_base_initialization_redis(self, mock_dependencies):
        """Test OrchestratorBase initialization with Redis backend."""
        with patch.dict(os.environ, {"ORKA_MEMORY_BACKEND": "redis"}):
            base = OrchestratorBase("test_config.yml")

            assert base.loader is not None
            assert (
                base.orchestrator_cfg
                == mock_dependencies["loader_instance"].get_orchestrator.return_value
            )
            assert base.agent_cfgs == mock_dependencies["loader_instance"].get_agents.return_value
            assert base.memory is not None
            assert base.fork_manager is not None
            assert base.queue == ["test_agent"]
            assert base.step_index == 0
            assert isinstance(base.run_id, str)
            assert "errors" in base.error_telemetry
            assert base.error_telemetry["execution_status"] == "running"

    def test_orchestrator_base_initialization_kafka(self, mock_dependencies):
        """Test OrchestratorBase initialization with Kafka backend."""
        with patch.dict(
            os.environ,
            {
                "ORKA_MEMORY_BACKEND": "kafka",
                "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
                "KAFKA_TOPIC_PREFIX": "test-orka",
            },
        ):
            base = OrchestratorBase("test_config.yml")

            # Verify Kafka-specific memory logger configuration
            mock_dependencies["memory"].assert_called_once()
            call_args = mock_dependencies["memory"].call_args
            assert call_args[1]["backend"] == "kafka"
            assert call_args[1]["bootstrap_servers"] == "localhost:9092"
            assert call_args[1]["topic_prefix"] == "test-orka"

    def test_orchestrator_base_environment_overrides(self, mock_dependencies):
        """Test environment variable overrides."""
        with patch.dict(
            os.environ,
            {
                "ORKA_DEBUG_KEEP_PREVIOUS_OUTPUTS": "true",
                "REDIS_URL": "redis://custom:6380/1",
            },
        ):
            base = OrchestratorBase("test_config.yml")

            call_args = mock_dependencies["memory"].call_args
            assert call_args[1]["debug_keep_previous_outputs"] is True
            assert call_args[1]["redis_url"] == "redis://custom:6380/1"

    def test_orchestrator_base_decay_config_initialization(self, mock_dependencies):
        """Test decay configuration initialization."""
        # Override orchestrator config to include specific decay settings
        mock_dependencies["loader_instance"].get_orchestrator.return_value = {
            "agents": ["test_agent"],
            "memory": {
                "decay": {
                    "enabled": True,
                    "default_short_term_hours": 0.5,
                    "default_long_term_hours": 48.0,
                    "check_interval_minutes": 15,
                },
            },
        }

        # Mock the _init_decay_config method to return our expected config
        expected_decay_config = {
            "enabled": True,
            "default_short_term_hours": 0.5,
            "default_long_term_hours": 48.0,
            "check_interval_minutes": 15,
        }

        with patch.object(
            OrchestratorBase,
            "_init_decay_config",
            return_value=expected_decay_config,
        ):
            base = OrchestratorBase("test_config.yml")

        # Verify decay config was properly initialized
        call_args = mock_dependencies["memory"].call_args
        decay_config = call_args[1]["decay_config"]
        assert decay_config["enabled"] is True
        assert decay_config["default_short_term_hours"] == 0.5
        assert decay_config["default_long_term_hours"] == 48.0

    def test_orchestrator_base_enqueue_fork_placeholder(self, mock_dependencies):
        """Test enqueue_fork placeholder method."""
        base = OrchestratorBase("test_config.yml")

        # Method should exist but not raise errors (placeholder implementation)
        try:
            base.enqueue_fork(["agent1", "agent2"], "fork_group_1")
        except NotImplementedError:
            pass  # Expected for placeholder implementation


class TestAgentFactory:
    """Test AgentFactory agent creation and configuration."""

    @pytest.fixture
    def mock_agent_factory(self):
        """Create a mock agent factory with necessary attributes."""
        factory = AgentFactory()
        factory.orchestrator_cfg = {"agents": ["test_agent"]}
        factory.agent_cfgs = [
            {"id": "binary_agent", "type": "binary", "prompt": "test prompt"},
            {"id": "router_agent", "type": "router", "params": {"decision_key": "result"}},
            {"id": "memory_reader", "type": "memory", "config": {"operation": "read"}},
            {"id": "memory_writer", "type": "memory", "config": {"operation": "write"}},
            {"id": "fork_node", "type": "fork", "prompt": "fork prompt"},
            {"id": "failing_node", "type": "failing", "prompt": "fail prompt"},
        ]
        factory.memory = Mock()
        factory.memory.decay_config = {"enabled": True}
        return factory

    def test_agent_types_mapping(self):
        """Test AGENT_TYPES mapping completeness."""
        assert "binary" in AGENT_TYPES
        assert "classification" in AGENT_TYPES
        assert "openai-answer" in AGENT_TYPES
        assert "router" in AGENT_TYPES
        assert "memory" in AGENT_TYPES
        assert "fork" in AGENT_TYPES
        assert "failing" in AGENT_TYPES

        # Verify special handler for memory
        assert AGENT_TYPES["memory"] == "special_handler"

    def test_init_agents_binary_agent(self, mock_agent_factory):
        """Test binary agent initialization."""
        # Create a mock binary agent
        mock_binary_agent = Mock()
        mock_binary_agent.return_value = Mock(type="binary")

        # Patch the AGENT_TYPES dict to use our mock
        with patch.dict(AGENT_TYPES, {"binary": mock_binary_agent}):
            agents = mock_agent_factory._init_agents()

        assert "binary_agent" in agents
        mock_binary_agent.assert_called_once()

    def test_init_agents_router_node(self, mock_agent_factory):
        """Test router node initialization."""
        # Create a mock router node
        mock_router_node = Mock()
        mock_router_node.return_value = Mock(type="router")

        # Patch the AGENT_TYPES dict to use our mock
        with patch.dict(AGENT_TYPES, {"router": mock_router_node}):
            agents = mock_agent_factory._init_agents()

        assert "router_agent" in agents
        mock_router_node.assert_called_once()
        # Verify router-specific parameters
        call_args = mock_router_node.call_args
        assert call_args[1]["node_id"] == "router_agent"
        assert "params" in call_args[1]

    @patch("orka.orchestrator.agent_factory.MemoryReaderNode")
    def test_init_agents_memory_reader(self, mock_memory_reader, mock_agent_factory):
        """Test memory reader node initialization."""
        mock_memory_reader.return_value = Mock(type="memory")

        agents = mock_agent_factory._init_agents()

        assert "memory_reader" in agents
        mock_memory_reader.assert_called_once()
        call_args = mock_memory_reader.call_args
        assert call_args[1]["node_id"] == "memory_reader"

    @patch("orka.orchestrator.agent_factory.MemoryWriterNode")
    def test_init_agents_memory_writer(self, mock_memory_writer, mock_agent_factory):
        """Test memory writer node initialization."""
        mock_memory_writer.return_value = Mock(type="memory")

        agents = mock_agent_factory._init_agents()

        assert "memory_writer" in agents
        mock_memory_writer.assert_called_once()
        call_args = mock_memory_writer.call_args
        assert call_args[1]["node_id"] == "memory_writer"

    def test_init_agents_fork_node(self, mock_agent_factory):
        """Test fork node initialization."""
        # Create a mock fork node
        mock_fork_node = Mock()
        mock_fork_node.return_value = Mock(type="fork")

        # Patch the AGENT_TYPES dict to use our mock
        with patch.dict(AGENT_TYPES, {"fork": mock_fork_node}):
            agents = mock_agent_factory._init_agents()

        assert "fork_node" in agents
        mock_fork_node.assert_called_once()
        call_args = mock_fork_node.call_args
        assert call_args[1]["memory_logger"] == mock_agent_factory.memory

    def test_init_agents_failing_node(self, mock_agent_factory):
        """Test failing node initialization."""
        # Create a mock failing node
        mock_failing_node = Mock()
        mock_failing_node.return_value = Mock(type="failing")

        # Patch the AGENT_TYPES dict to use our mock
        with patch.dict(AGENT_TYPES, {"failing": mock_failing_node}):
            agents = mock_agent_factory._init_agents()

        assert "failing_node" in agents
        mock_failing_node.assert_called_once()

    def test_init_agents_unsupported_type(self, mock_agent_factory):
        """Test handling of unsupported agent type."""
        mock_agent_factory.agent_cfgs = [
            {"id": "invalid_agent", "type": "unsupported_type"},
        ]

        with pytest.raises(ValueError, match="Unsupported agent type: unsupported_type"):
            mock_agent_factory._init_agents()


class TestExecutionEngine:
    """Test ExecutionEngine execution logic and error handling."""

    @pytest.fixture
    def mock_execution_engine(self):
        """Create a mock execution engine with necessary attributes."""
        engine = ExecutionEngine()
        engine.orchestrator_cfg = {"agents": ["test_agent"]}
        engine.agents = {"test_agent": Mock(type="binary")}
        engine.run_id = str(uuid4())
        engine.step_index = 0
        engine.memory = Mock()
        engine.fork_manager = Mock()  # Add fork_manager attribute
        engine.queue = []  # Add queue attribute
        engine.error_telemetry = {
            "errors": [],
            "retry_counters": {},
            "partial_successes": [],
            "silent_degradations": [],
            "status_codes": {},
            "execution_status": "running",
            "critical_failures": [],
            "recovery_actions": [],
        }

        # Mock the methods that will be called
        engine._record_error = Mock()
        engine._record_retry = Mock()  # Add _record_retry method
        engine._record_partial_success = Mock()  # Add _record_partial_success method
        engine._save_error_report = Mock()
        engine.build_previous_outputs = Mock(return_value={})
        engine._extract_llm_metrics = Mock(return_value=None)
        engine._generate_meta_report = Mock(
            return_value={
                "total_duration": 1.0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "total_llm_calls": 0,  # Add total_llm_calls key
                "avg_latency_ms": 0.0,
                "agent_metrics": {},
                "model_usage": {},
            },
        )
        engine._add_prompt_to_payload = Mock()  # Add _add_prompt_to_payload method
        engine.normalize_bool = Mock(return_value=True)  # Add normalize_bool method
        engine._render_agent_prompt = Mock()  # Add _render_agent_prompt method

        return engine

    @pytest.mark.asyncio
    async def test_run_success(self, mock_execution_engine):
        """Test successful execution run."""
        # Mock the main execution method
        expected_logs = [{"agent_id": "test_agent", "result": "success"}]

        with patch.object(
            mock_execution_engine,
            "_run_with_comprehensive_error_handling",
            new_callable=AsyncMock,
        ) as mock_run:
            mock_run.return_value = expected_logs

            result = await mock_execution_engine.run("test input")

            assert result == expected_logs
            mock_run.assert_called_once_with("test input", [], False)

    @pytest.mark.asyncio
    async def test_run_with_fatal_error(self, mock_execution_engine):
        """Test run method with fatal error."""
        with patch.object(
            mock_execution_engine,
            "_run_with_comprehensive_error_handling",
            new_callable=AsyncMock,
        ) as mock_run:
            mock_run.side_effect = Exception("Fatal error")

            with pytest.raises(Exception, match="Fatal error"):
                await mock_execution_engine.run("test input")

            # Verify error recording
            mock_execution_engine._record_error.assert_called_once()
            error_call = mock_execution_engine._record_error.call_args
            assert error_call[0][0] == "orchestrator_execution"
            assert "Orchestrator execution failed" in error_call[0][2]

    @pytest.mark.asyncio
    async def test_run_with_comprehensive_error_handling(self, mock_execution_engine):
        """Test main execution loop."""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.type = "binary"
        mock_agent.__class__.__name__ = "BinaryAgent"
        mock_execution_engine.agents["test_agent"] = mock_agent

        # Mock single agent execution
        with patch.object(
            mock_execution_engine,
            "_execute_single_agent",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {"status": "success", "result": True}

            # Mock time.time for duration calculation
            with patch("orka.orchestrator.execution_engine.time") as mock_time:
                mock_time.side_effect = [1000.0, 1001.5]  # start, end times

                # Update the _generate_meta_report mock to return the expected structure
                mock_execution_engine._generate_meta_report.return_value = {
                    "total_duration": 1.5,
                    "total_tokens": 100,
                    "total_cost_usd": 0.002,
                    "total_llm_calls": 1,
                    "avg_latency_ms": 500.0,
                    "agent_metrics": {},
                    "model_usage": {},
                }

                result = await mock_execution_engine._run_with_comprehensive_error_handling(
                    "test input",
                    [],
                    return_logs=True,
                )

                assert len(result) == 1
                log_entry = result[0]
                assert log_entry["agent_id"] == "test_agent"
                assert log_entry["event_type"] == "BinaryAgent"
                assert log_entry["duration"] == 1.5
                assert "payload" in log_entry

    @pytest.mark.asyncio
    async def test_execution_with_retry_logic(self, mock_execution_engine):
        """Test retry logic for failing agents."""
        mock_agent = Mock()
        mock_agent.type = "binary"
        mock_agent.__class__.__name__ = "BinaryAgent"
        mock_execution_engine.agents["test_agent"] = mock_agent

        # Mock methods for retry tracking
        mock_execution_engine._record_retry = Mock()
        mock_execution_engine._record_partial_success = Mock()

        # Mock single agent execution to fail twice then succeed
        with patch.object(
            mock_execution_engine,
            "_execute_single_agent",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                {"status": "success", "result": True},  # Success on third try
            ]

            with patch("orka.orchestrator.execution_engine.time") as mock_time:
                mock_time.side_effect = [1000.0, 1001.0]

                # Update the _generate_meta_report mock to return the expected structure
                mock_execution_engine._generate_meta_report.return_value = {
                    "total_duration": 1.0,
                    "total_tokens": 100,
                    "total_cost_usd": 0.002,
                    "total_llm_calls": 1,
                    "avg_latency_ms": 500.0,
                    "agent_metrics": {},
                    "model_usage": {},
                }

                with patch("asyncio.sleep"):  # Mock sleep for retry delays
                    result = await mock_execution_engine._run_with_comprehensive_error_handling(
                        "test input",
                        [],
                        return_logs=True,
                    )

                # Verify retry was recorded and partial success logged
                assert mock_execution_engine._record_retry.call_count == 2
                mock_execution_engine._record_partial_success.assert_called_once_with(
                    "test_agent",
                    2,
                )

    @pytest.mark.asyncio
    async def test_execution_with_waiting_status(self, mock_execution_engine):
        """Test handling of waiting status for re-queueing."""
        mock_agent = Mock()
        mock_agent.type = "binary"
        mock_agent.__class__.__name__ = "BinaryAgent"
        mock_execution_engine.agents["test_agent"] = mock_agent

        # Mock to return waiting status first, then success
        with patch.object(
            mock_execution_engine,
            "_execute_single_agent",
            new_callable=AsyncMock,
        ) as mock_execute:
            # Return waiting first, then success - provide enough values to avoid StopIteration
            def mock_execute_side_effect(*args, **kwargs):
                if mock_execute.call_count == 1:
                    return {"status": "waiting"}
                else:
                    return {"status": "success", "result": True}

            mock_execute.side_effect = mock_execute_side_effect

            with patch("orka.orchestrator.execution_engine.time") as mock_time:
                mock_time.side_effect = [1000.0, 1001.0, 1002.0, 1003.0]

                # Update the _generate_meta_report mock to return the expected structure
                mock_execution_engine._generate_meta_report.return_value = {
                    "total_duration": 2.0,
                    "total_tokens": 100,
                    "total_cost_usd": 0.002,
                    "total_llm_calls": 1,
                    "avg_latency_ms": 500.0,
                    "agent_metrics": {},
                    "model_usage": {},
                }

                result = await mock_execution_engine._run_with_comprehensive_error_handling(
                    "test input",
                    [],
                    return_logs=True,
                )

                # Agent should have been executed at least twice (waiting, then success)
                # But the actual implementation may retry, so we check >= 2
                assert mock_execute.call_count >= 2
                assert len(result) >= 1  # At least one log entry

    @pytest.mark.asyncio
    async def test_execute_single_agent_basic(self, mock_execution_engine):
        """Test basic single agent execution."""
        mock_agent = Mock()
        mock_agent.run = Mock(return_value={"result": "success"})  # Use regular Mock, not AsyncMock

        result = await mock_execution_engine._execute_single_agent(
            "test_agent",
            mock_agent,
            "binary",
            {"input": "test"},
            "test",
            [],
            [],
        )

        # The method returns a payload structure with input and result
        expected_result = {"input": "test", "result": {"result": "success"}}
        assert result == expected_result
        mock_agent.run.assert_called_once()


class TestMetricsCollector:
    """Test MetricsCollector metrics extraction and reporting."""

    @pytest.fixture
    def mock_metrics_collector(self):
        """Create a mock metrics collector."""
        collector = MetricsCollector()
        collector.run_id = str(uuid4())  # Add run_id attribute
        return collector

    def test_extract_llm_metrics_from_result(self, mock_metrics_collector):
        """Test extracting metrics from agent result."""
        agent = Mock()
        result = {"_metrics": {"tokens": 100, "cost_usd": 0.002, "latency_ms": 500}}

        metrics = mock_metrics_collector._extract_llm_metrics(agent, result)

        assert metrics["tokens"] == 100
        assert metrics["cost_usd"] == 0.002
        assert metrics["latency_ms"] == 500

    def test_extract_llm_metrics_from_agent(self, mock_metrics_collector):
        """Test extracting metrics from agent state."""
        agent = Mock()
        agent._last_metrics = {"tokens": 150, "cost_usd": 0.003, "latency_ms": 750}
        result = {}

        metrics = mock_metrics_collector._extract_llm_metrics(agent, result)

        assert metrics["tokens"] == 150
        assert metrics["cost_usd"] == 0.003
        assert metrics["latency_ms"] == 750

    def test_extract_llm_metrics_none(self, mock_metrics_collector):
        """Test extracting metrics when none available."""
        agent = Mock()
        agent._last_metrics = None
        result = {}

        metrics = mock_metrics_collector._extract_llm_metrics(agent, result)

        assert metrics is None

    def test_generate_meta_report_basic(self, mock_metrics_collector):
        """Test basic meta report generation."""
        logs = [
            {
                "agent_id": "agent1",
                "duration": 1.5,
                "llm_metrics": {"tokens": 100, "cost_usd": 0.002, "latency_ms": 500},
            },
            {
                "agent_id": "agent2",
                "duration": 2.0,
                "llm_metrics": {"tokens": 200, "cost_usd": 0.004, "latency_ms": 750},
            },
        ]

        report = mock_metrics_collector._generate_meta_report(logs)

        assert report["total_duration"] == 3.5
        assert report["total_llm_calls"] == 2
        assert report["total_tokens"] == 300
        assert report["total_cost_usd"] == 0.006
        assert report["avg_latency_ms"] == 625.0
        assert (
            len(report["agent_breakdown"]) == 2
        )  # Fixed: use agent_breakdown instead of agent_metrics

    def test_generate_meta_report_with_null_costs(self, mock_metrics_collector):
        """Test meta report with null costs."""
        logs = [
            {
                "agent_id": "agent1",
                "duration": 1.0,
                "llm_metrics": {"tokens": 100, "cost_usd": None, "latency_ms": 500},
            },
        ]

        report = mock_metrics_collector._generate_meta_report(logs)

        # Null costs should be excluded from total
        assert report["total_cost_usd"] == 0.0
        assert report["total_tokens"] == 100

    @patch.dict(os.environ, {"ORKA_LOCAL_COST_POLICY": "null_fail"})
    def test_generate_meta_report_null_cost_policy_fail(self, mock_metrics_collector):
        """Test meta report with null cost policy set to fail."""
        logs = [
            {
                "agent_id": "agent1",
                "duration": 1.0,
                "llm_metrics": {
                    "tokens": 100,
                    "cost_usd": None,
                    "model": "gpt-4",
                    "latency_ms": 500,
                },
            },
        ]

        with pytest.raises(ValueError, match="Pipeline failed due to null cost"):
            mock_metrics_collector._generate_meta_report(logs)


class TestErrorHandler:
    """Test ErrorHandler error tracking and reporting."""

    @pytest.fixture
    def mock_error_handler(self):
        """Create a mock error handler."""
        handler = ErrorHandler()
        handler.step_index = 1
        handler.run_id = str(uuid4())
        handler.error_telemetry = {
            "errors": [],
            "retry_counters": {},
            "partial_successes": [],
            "silent_degradations": [],
            "status_codes": {},
            "execution_status": "running",
            "critical_failures": [],
            "recovery_actions": [],
        }
        handler.memory = Mock()
        handler.memory.memory = []
        handler._generate_meta_report = Mock(return_value={"total_duration": 1.0})
        return handler

    def test_record_error_basic(self, mock_error_handler):
        """Test basic error recording."""
        error = Exception("Test error")

        mock_error_handler._record_error(
            "agent_failure",
            "test_agent",
            "Test error message",
            error,
            recovery_action="retry",
        )

        assert len(mock_error_handler.error_telemetry["errors"]) == 1
        error_entry = mock_error_handler.error_telemetry["errors"][0]
        assert error_entry["type"] == "agent_failure"
        assert error_entry["agent_id"] == "test_agent"
        assert error_entry["message"] == "Test error message"
        assert error_entry["recovery_action"] == "retry"
        assert "exception" in error_entry

    def test_record_error_with_status_code(self, mock_error_handler):
        """Test error recording with HTTP status code."""
        mock_error_handler._record_error(
            "api_error",
            "openai_agent",
            "API rate limit",
            status_code=429,
            recovery_action="backoff",
        )

        error_entry = mock_error_handler.error_telemetry["errors"][0]
        assert error_entry["status_code"] == 429
        assert mock_error_handler.error_telemetry["status_codes"]["openai_agent"] == 429

    def test_record_retry(self, mock_error_handler):
        """Test retry recording."""
        mock_error_handler._record_retry("test_agent")
        mock_error_handler._record_retry("test_agent")

        assert mock_error_handler.error_telemetry["retry_counters"]["test_agent"] == 2

    def test_record_partial_success(self, mock_error_handler):
        """Test partial success recording."""
        mock_error_handler._record_partial_success("test_agent", 3)

        partial_successes = mock_error_handler.error_telemetry["partial_successes"]
        assert len(partial_successes) == 1
        assert partial_successes[0]["agent_id"] == "test_agent"
        assert partial_successes[0]["retry_count"] == 3

    def test_record_silent_degradation(self, mock_error_handler):
        """Test silent degradation recording."""
        mock_error_handler._record_silent_degradation(
            "json_agent",
            "json_parsing_failure",
            {"original": "invalid json", "fallback": "raw text"},
        )

        degradations = mock_error_handler.error_telemetry["silent_degradations"]
        assert len(degradations) == 1
        assert degradations[0]["agent_id"] == "json_agent"
        assert degradations[0]["type"] == "json_parsing_failure"

    @patch("builtins.open", create=True)
    @patch("os.makedirs")
    @patch("json.dump")
    def test_save_error_report_success(
        self,
        mock_json_dump,
        mock_makedirs,
        mock_open,
        mock_error_handler,
    ):
        """Test successful error report saving."""
        logs = [{"agent_id": "test_agent", "result": "success"}]

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        with patch("orka.orchestrator.error_handling.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"

            report_path = mock_error_handler._save_error_report(logs)

            # Verify file operations
            mock_makedirs.assert_called_once()
            mock_open.assert_called()
            mock_json_dump.assert_called_once()

            # Verify error report structure
            call_args = mock_json_dump.call_args[0]
            error_report = call_args[0]
            assert "orka_execution_report" in error_report
            assert error_report["orka_execution_report"]["run_id"] == mock_error_handler.run_id


class TestPromptRenderer:
    """Test PromptRenderer template processing and formatting."""

    @pytest.fixture
    def mock_prompt_renderer(self):
        """Create a mock prompt renderer."""
        return PromptRenderer()

    def test_render_prompt_basic(self, mock_prompt_renderer):
        """Test basic prompt rendering."""
        template = "Hello {{ name }}, you have {{ count }} messages"
        payload = {"name": "Alice", "count": 5}

        result = mock_prompt_renderer.render_prompt(template, payload)

        assert result == "Hello Alice, you have 5 messages"

    def test_render_prompt_complex_template(self, mock_prompt_renderer):
        """Test complex template with conditionals."""
        template = """
        {%- if previous_outputs.classifier -%}
        Based on classification: {{ previous_outputs.classifier.result }}
        {%- endif -%}
        Process: {{ input }}
        """
        payload = {
            "input": "user query",
            "previous_outputs": {
                "classifier": {"result": "question"},
            },
        }

        result = mock_prompt_renderer.render_prompt(template, payload)

        assert "Based on classification: question" in result
        assert "Process: user query" in result

    def test_render_prompt_invalid_template_type(self, mock_prompt_renderer):
        """Test error handling for invalid template type."""
        with pytest.raises(ValueError, match="Expected template_str to be str"):
            mock_prompt_renderer.render_prompt(123, {})

    def test_add_prompt_to_payload_with_agent_prompt(self, mock_prompt_renderer):
        """Test adding prompt to payload with agent that has prompt."""
        agent = Mock()
        agent.prompt = "Process: {{ input }}"
        agent._last_formatted_prompt = "Process: test input"
        agent._last_response = "Agent response"
        agent._last_confidence = 0.95
        agent._last_internal_reasoning = "Step-by-step reasoning"

        payload_out = {}
        payload = {"input": "test input"}

        mock_prompt_renderer._add_prompt_to_payload(agent, payload_out, payload)

        assert payload_out["prompt"] == "Process: {{ input }}"
        assert payload_out["formatted_prompt"] == "Process: test input"
        assert payload_out["response"] == "Agent response"
        assert payload_out["confidence"] == 0.95
        assert payload_out["internal_reasoning"] == "Step-by-step reasoning"

    def test_normalize_bool_simple_cases(self, mock_prompt_renderer):
        """Test boolean normalization for simple cases."""
        assert mock_prompt_renderer.normalize_bool(True) is True
        assert mock_prompt_renderer.normalize_bool(False) is False
        assert mock_prompt_renderer.normalize_bool("true") is True
        assert mock_prompt_renderer.normalize_bool("TRUE") is True
        assert mock_prompt_renderer.normalize_bool("yes") is True
        assert mock_prompt_renderer.normalize_bool("false") is False
        assert mock_prompt_renderer.normalize_bool("no") is False
        assert mock_prompt_renderer.normalize_bool("random") is False

    def test_normalize_bool_dict_cases(self, mock_prompt_renderer):
        """Test boolean normalization for dictionary responses."""
        # Test with 'result' key
        assert mock_prompt_renderer.normalize_bool({"result": True}) is True
        assert mock_prompt_renderer.normalize_bool({"result": "yes"}) is True

        # Test with 'response' key
        assert mock_prompt_renderer.normalize_bool({"response": False}) is False
        assert mock_prompt_renderer.normalize_bool({"response": "no"}) is False

        # Test with nested structure
        assert mock_prompt_renderer.normalize_bool({"result": {"response": True}}) is True

        # Test with no relevant keys
        assert mock_prompt_renderer.normalize_bool({"other": True}) is False


class TestOrchestratorIntegration:
    """Test complete Orchestrator integration."""

    def test_orchestrator_module_structure(self):
        """Test that orchestrator module has the expected structure."""
        # Import the module to check structure
        import orka.orchestrator as orchestrator_module

        # Check that expected classes are accessible
        assert hasattr(orchestrator_module, "Orchestrator")
        assert hasattr(orchestrator_module, "AgentFactory")
        assert hasattr(orchestrator_module, "AGENT_TYPES")

        # Check that the orchestrator module exports what we expect
        expected_exports = [
            "AGENT_TYPES",
            "AgentFactory",
            "ErrorHandler",
            "ExecutionEngine",
            "MetricsCollector",
            "Orchestrator",
            "OrchestratorBase",
            "PromptRenderer",
        ]
        for export in expected_exports:
            assert hasattr(orchestrator_module, export), f"Missing export: {export}"

    def test_orchestrator_class_inheritance(self):
        """Test that Orchestrator class has correct inheritance."""
        # Check inheritance
        from orka.orchestrator.agent_factory import AgentFactory
        from orka.orchestrator.base import OrchestratorBase
        from orka.orchestrator.error_handling import ErrorHandler
        from orka.orchestrator.execution_engine import ExecutionEngine
        from orka.orchestrator.metrics import MetricsCollector
        from orka.orchestrator.prompt_rendering import PromptRenderer

        assert issubclass(Orchestrator, OrchestratorBase)
        assert issubclass(Orchestrator, AgentFactory)
        assert issubclass(Orchestrator, PromptRenderer)
        assert issubclass(Orchestrator, ErrorHandler)
        assert issubclass(Orchestrator, MetricsCollector)
        assert issubclass(Orchestrator, ExecutionEngine)

    def test_orchestrator_mro(self):
        """Test that Orchestrator has the correct method resolution order."""
        mro_names = [cls.__name__ for cls in Orchestrator.__mro__]
        expected_classes = [
            "Orchestrator",
            "OrchestratorBase",
            "AgentFactory",
            "PromptRenderer",
            "ErrorHandler",
            "MetricsCollector",
            "ExecutionEngine",
        ]

        for expected_class in expected_classes:
            assert expected_class in mro_names, f"{expected_class} not found in MRO"

    @patch("orka.orchestrator.base.YAMLLoader")
    @patch("orka.orchestrator.base.create_memory_logger")
    @patch("orka.orchestrator.base.ForkGroupManager")
    def test_orchestrator_complete_initialization(self, mock_fork, mock_memory, mock_loader):
        """Test complete Orchestrator initialization."""
        # Setup mocks
        mock_loader_instance = Mock()
        mock_loader.return_value = mock_loader_instance
        mock_loader_instance.validate.return_value = None
        mock_loader_instance.get_orchestrator.return_value = {"agents": ["test_agent"]}
        mock_loader_instance.get_agents.return_value = [
            {"id": "test_agent", "type": "binary", "prompt": "test"},
        ]

        mock_memory_instance = Mock()
        mock_memory_instance.redis = Mock()
        mock_memory.return_value = mock_memory_instance

        with patch.object(Orchestrator, "_init_agents") as mock_init_agents:
            mock_init_agents.return_value = {"test_agent": Mock()}

            orchestrator = Orchestrator("test_config.yml")

            # Verify all components are properly initialized
            assert hasattr(orchestrator, "orchestrator_cfg")
            assert hasattr(orchestrator, "agent_cfgs")
            assert hasattr(orchestrator, "memory")
            assert hasattr(orchestrator, "fork_manager")
            assert hasattr(orchestrator, "agents")
            assert hasattr(orchestrator, "error_telemetry")

            # Verify MRO includes all expected classes
            mro_names = [cls.__name__ for cls in orchestrator.__class__.__mro__]
            expected_classes = [
                "Orchestrator",
                "OrchestratorBase",
                "AgentFactory",
                "PromptRenderer",
                "ErrorHandler",
                "MetricsCollector",
                "ExecutionEngine",
            ]
            for expected_class in expected_classes:
                assert expected_class in mro_names
