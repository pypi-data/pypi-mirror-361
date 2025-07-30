"""
Comprehensive unit tests for the main orchestrator.py module.
Tests the Orchestrator class composition and initialization.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest
import yaml

from orka.orchestrator import Orchestrator


class TestOrchestrator:
    """Test suite for the main Orchestrator class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary YAML config file
        self.temp_config = {
            "orchestrator": {
                "memory_backend": "file",
                "memory_logger_config": {
                    "file_path": "/tmp/test_memory.json",
                },
            },
            "agents": [
                {
                    "id": "test_agent",
                    "type": "openai",
                    "prompt": "Test prompt",
                    "api_key": "test_key",
                },
            ],
        }

        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml")
        yaml.dump(self.temp_config, self.temp_file)
        self.temp_file.close()
        self.config_path = self.temp_file.name

    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.config_path)
        except FileNotFoundError:
            pass

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    def test_orchestrator_inheritance_chain(self, mock_base_init):
        """Test that Orchestrator properly inherits from all mixin classes."""
        mock_base_init.return_value = None

        # Test inheritance chain
        assert hasattr(Orchestrator, "__mro__")
        mro = Orchestrator.__mro__

        # Verify all expected classes are in the MRO
        class_names = [cls.__name__ for cls in mro]

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
            assert expected_class in class_names, f"{expected_class} not found in MRO"

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_initialization_success(self, mock_init_agents, mock_base_init):
        """Test successful orchestrator initialization."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {"test_agent": Mock()}

        orchestrator = Orchestrator(self.config_path)

        # Verify base initialization was called
        mock_base_init.assert_called_once_with(self.config_path)

        # Verify agent initialization was called
        mock_init_agents.assert_called_once()

        # Verify agents attribute is set
        assert hasattr(orchestrator, "agents")
        assert "test_agent" in orchestrator.agents

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_initialization_with_empty_agents(self, mock_init_agents, mock_base_init):
        """Test orchestrator initialization with empty agents list."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {}

        orchestrator = Orchestrator(self.config_path)

        assert orchestrator.agents == {}

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_initialization_with_multiple_agents(
        self,
        mock_init_agents,
        mock_base_init,
    ):
        """Test orchestrator initialization with multiple agents."""
        mock_base_init.return_value = None
        mock_agents = {
            "agent1": Mock(),
            "agent2": Mock(),
            "agent3": Mock(),
        }
        mock_init_agents.return_value = mock_agents

        orchestrator = Orchestrator(self.config_path)

        assert len(orchestrator.agents) == 3
        assert "agent1" in orchestrator.agents
        assert "agent2" in orchestrator.agents
        assert "agent3" in orchestrator.agents

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_methods_available(self, mock_init_agents, mock_base_init):
        """Test that all expected methods are available from mixins."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {}

        orchestrator = Orchestrator(self.config_path)

        # Methods that should be inherited from mixins
        expected_methods = [
            "_init_agents",  # From AgentFactory
        ]

        for method in expected_methods:
            assert hasattr(orchestrator, method), f"Method {method} not found"

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_docstring_and_attributes(self, mock_init_agents, mock_base_init):
        """Test orchestrator class attributes and documentation."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {}

        # Test class has proper docstring
        assert Orchestrator.__doc__ is not None
        assert "core engine" in Orchestrator.__doc__

        # Test class module
        assert Orchestrator.__module__ == "orka.orchestrator"

    @patch("orka.orchestrator.OrchestratorBase.__init__", side_effect=Exception("Base init error"))
    def test_orchestrator_initialization_base_error(self, mock_base_init):
        """Test orchestrator initialization when base init fails."""
        with pytest.raises(Exception, match="Base init error"):
            Orchestrator(self.config_path)

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents", side_effect=Exception("Agent init error"))
    def test_orchestrator_initialization_agent_error(self, mock_init_agents, mock_base_init):
        """Test orchestrator initialization when agent init fails."""
        mock_base_init.return_value = None

        with pytest.raises(Exception, match="Agent init error"):
            Orchestrator(self.config_path)

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_config_path_handling(self, mock_init_agents, mock_base_init):
        """Test that config path is properly passed to base class."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {}

        config_path = "/path/to/config.yml"
        Orchestrator(config_path)

        # Verify the config path was passed to the base class
        mock_base_init.assert_called_once_with(config_path)

    def test_orchestrator_class_composition(self):
        """Test the multiple inheritance composition structure."""
        # Test that the class properly inherits from all expected base classes
        bases = Orchestrator.__bases__
        base_names = [base.__name__ for base in bases]

        expected_bases = [
            "OrchestratorBase",
            "AgentFactory",
            "PromptRenderer",
            "ErrorHandler",
            "MetricsCollector",
            "ExecutionEngine",
        ]

        for expected_base in expected_bases:
            assert expected_base in base_names, f"Expected base class {expected_base} not found"

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_super_call_behavior(self, mock_init_agents, mock_base_init):
        """Test that super().__init__ properly calls the base class."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {}

        Orchestrator(self.config_path)

        # Verify super().__init__ was called correctly
        mock_base_init.assert_called_once()

    @patch("orka.orchestrator.OrchestratorBase.__init__")
    @patch.object(Orchestrator, "_init_agents")
    def test_orchestrator_logging_setup(self, mock_init_agents, mock_base_init):
        """Test that logging is properly set up."""
        mock_base_init.return_value = None
        mock_init_agents.return_value = {}

        # Access logger from the actual orchestrator module file
        import importlib.util
        import os

        # Import the actual orchestrator.py file directly
        spec = importlib.util.spec_from_file_location(
            "orka.orchestrator",
            os.path.join(os.path.dirname(__file__), "../../orka/orchestrator.py"),
        )
        orch_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orch_module)

        assert hasattr(orch_module, "logger")
        logger = orch_module.logger
        assert logger is not None
        assert logger.name == "orka.orchestrator"

        Orchestrator(self.config_path)
