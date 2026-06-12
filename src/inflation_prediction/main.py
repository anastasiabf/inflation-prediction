"""
Entry point for Inflation Prediction System CLI
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from inflation_prediction.main_orchestrator import InflationPredictionOrchestrator


def main():
    """Run the inflation prediction pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI-driven Inflation Prediction System"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=36,
        help="Historical months to process (default: 36)"
    )
    parser.add_argument(
        "--backend",
        choices=["openai", "anthropic", "huggingface", "mock"],
        default="mock",
        help="LLM backend to use (default: mock)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="inflation_prediction_output",
        help="Output directory for results"
    )
    
    args = parser.parse_args()
    
    # Run orchestrator
    orchestrator = InflationPredictionOrchestrator(
        months=args.months,
        llm_backend=args.backend,
        output_dir=args.output
    )
    
    orchestrator.execute()


if __name__ == "__main__":
    main()
