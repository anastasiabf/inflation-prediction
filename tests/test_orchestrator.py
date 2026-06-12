"""
Unit tests for Inflation Prediction System
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.unit
def test_imports():
    """Test that all modules can be imported"""
    try:
        from inflation_prediction import data_ingestion
        from inflation_prediction import llm_sentiment_pipeline
        from inflation_prediction import model_training
        from inflation_prediction import llm_government_insights
        from inflation_prediction import html_factory
        from inflation_prediction import main_orchestrator
        
        assert data_ingestion is not None
        assert llm_sentiment_pipeline is not None
        assert model_training is not None
        assert llm_government_insights is not None
        assert html_factory is not None
        assert main_orchestrator is not None
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


@pytest.mark.unit
def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    from inflation_prediction.main_orchestrator import InflationPredictionOrchestrator
    
    orchestrator = InflationPredictionOrchestrator(
        months=12,
        llm_backend="mock",
        output_dir="/tmp/test"
    )
    
    assert orchestrator.months == 12
    assert orchestrator.llm_backend == "mock"


@pytest.mark.integration
@pytest.mark.slow
def test_full_pipeline():
    """Test complete pipeline execution"""
    pytest.skip("Full pipeline test - run manually with make run-mock")
