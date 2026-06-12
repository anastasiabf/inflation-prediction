"""
MAIN ORCHESTRATOR: Complete End-to-End Pipeline Execution
Orchestrates all 5 phases and generates the final interactive dashboard.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Import all phase modules
from .data_ingestion import DataPipeline as DataIngestionPipeline
from .llm_sentiment_pipeline import SentimentPipeline
from .model_training import ModelTrainingPipeline
from .llm_government_insights import InsightsPipeline
from .html_factory import HTMLFactoryPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class InflationPredictionOrchestrator:
    """
    Master orchestrator for complete AI-driven inflation prediction system.
    Executes all 5 phases sequentially and produces final dashboard.
    """
    
    def __init__(self, months: int = 36, llm_backend: str = "mock", 
                 output_dir: str = "."):
        """
        Initialize orchestrator.
        
        Args:
            months: Historical months to process
            llm_backend: "openai", "anthropic", "huggingface", or "mock"
            output_dir: Output directory for results
        """
        self.months = months
        self.llm_backend = llm_backend
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Tracking
        self.execution_log = {
            'start_time': datetime.now().isoformat(),
            'phases': {}
        }
    
    def execute(self) -> dict:
        """
        Execute complete pipeline.
        
        Returns:
            Dictionary with execution summary
        """
        logger.info("=" * 80)
        logger.info("INFLATION PREDICTION SYSTEM - COMPLETE PIPELINE EXECUTION")
        logger.info("=" * 80)
        logger.info(f"Configuration: months={self.months}, llm_backend={self.llm_backend}")
        logger.info("")
        
        try:
            # PHASE 1: DATA INGESTION
            unified_df, news_df, social_df = self._execute_phase_1()
            
            # PHASE 2: LLM SENTIMENT ANALYSIS
            enriched_df = self._execute_phase_2(unified_df, news_df, social_df)
            
            # PHASE 3: RANDOM FOREST MODELING
            trained_model, model_data = self._execute_phase_3(enriched_df)
            
            # Generate prediction for next month
            X_sample = enriched_df[trained_model.FEATURE_NAMES].iloc[-1:].values
            prediction = trained_model.predict(X_sample)[0]
            logger.info(f"Next month inflation prediction: {prediction:.2f}%")
            
            # PHASE 4: LLM GOVERNMENT INSIGHTS
            report = self._execute_phase_4(prediction, model_data, enriched_df)
            
            # PHASE 5: HTML DASHBOARD GENERATION
            dashboard_path = self._execute_phase_5(prediction, enriched_df, 
                                                   model_data, report)
            
            # Finalize
            self.execution_log['end_time'] = datetime.now().isoformat()
            self.execution_log['success'] = True
            self.execution_log['dashboard_path'] = str(dashboard_path)
            self.execution_log['prediction'] = prediction
            
            self._print_summary(dashboard_path, prediction)
            self._save_execution_log()
            
            return {
                'success': True,
                'dashboard': str(dashboard_path),
                'prediction': prediction,
                'model_accuracy': model_data['training_metrics']['r2']
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            self.execution_log['success'] = False
            self.execution_log['error'] = str(e)
            self._save_execution_log()
            raise
    
    def _execute_phase_1(self):
        """Execute Phase 1: Data Ingestion."""
        logger.info("")
        logger.info("PHASE 1: SPECIFIC DATA INGESTION ENGINE")
        logger.info("-" * 80)
        
        try:
            pipeline = DataIngestionPipeline(months=self.months)
            unified_df, news_df, social_df = pipeline.build_unified_dataset()
            
            # Save datasets
            unified_df.to_csv(self.output_dir / 'unified_dataset.csv')
            news_df.to_csv(self.output_dir / 'news_batches.csv')
            social_df.to_csv(self.output_dir / 'social_media_batches.csv')
            
            self.execution_log['phases']['phase_1'] = {
                'status': 'completed',
                'unified_df_shape': unified_df.shape,
                'date_range': f"{unified_df.index.min()} to {unified_df.index.max()}"
            }
            
            logger.info("✓ Phase 1 completed successfully")
            return unified_df, news_df, social_df
            
        except Exception as e:
            logger.error(f"Phase 1 failed: {str(e)}")
            self.execution_log['phases']['phase_1'] = {'status': 'failed', 'error': str(e)}
            raise
    
    def _execute_phase_2(self, unified_df, news_df, social_df):
        """Execute Phase 2: LLM Sentiment Analysis."""
        logger.info("")
        logger.info("PHASE 2: FULL LLM-DRIVEN SENTIMENT ANALYSIS PIPELINE")
        logger.info("-" * 80)
        
        try:
            sentiment_pipeline = SentimentPipeline(backend=self.llm_backend)
            enriched_df = sentiment_pipeline.process_dataset(unified_df, news_df, social_df)
            
            # Save enriched dataset
            enriched_df.to_csv(self.output_dir / 'enriched_dataset.csv')
            
            # Log sentiment stats
            news_sent = enriched_df['news_sentiment_llm_score'].mean()
            social_sent = enriched_df['social_media_sentiment_llm_score'].mean()
            
            self.execution_log['phases']['phase_2'] = {
                'status': 'completed',
                'backend': self.llm_backend,
                'avg_news_sentiment': float(news_sent),
                'avg_social_sentiment': float(social_sent)
            }
            
            logger.info("✓ Phase 2 completed successfully")
            return enriched_df
            
        except Exception as e:
            logger.error(f"Phase 2 failed: {str(e)}")
            self.execution_log['phases']['phase_2'] = {'status': 'failed', 'error': str(e)}
            raise
    
    def _execute_phase_3(self, enriched_df):
        """Execute Phase 3: Random Forest Modeling."""
        logger.info("")
        logger.info("PHASE 3: RANDOM FOREST MODELING & FORMULA EXPORT")
        logger.info("-" * 80)
        
        try:
            model_pipeline = ModelTrainingPipeline()
            trained_model, model_data = model_pipeline.train_and_export(enriched_df)
            
            # Save model export
            with open(self.output_dir / 'model_export.json', 'w') as f:
                json.dump(model_data, f, indent=2)
            
            self.execution_log['phases']['phase_3'] = {
                'status': 'completed',
                'model_type': 'random_forest',
                'n_estimators': model_data['n_estimators'],
                'r2_score': float(model_data['training_metrics']['r2']),
                'rmse': float(model_data['training_metrics']['rmse']),
                'mae': float(model_data['training_metrics']['mae'])
            }
            
            logger.info("✓ Phase 3 completed successfully")
            return trained_model, model_data
            
        except Exception as e:
            logger.error(f"Phase 3 failed: {str(e)}")
            self.execution_log['phases']['phase_3'] = {'status': 'failed', 'error': str(e)}
            raise
    
    def _execute_phase_4(self, prediction: float, model_data: dict, enriched_df):
        """Execute Phase 4: LLM Government Insights."""
        logger.info("")
        logger.info("PHASE 4: FULL LLM-DRIVEN GOVERNMENT INSIGHT GENERATOR")
        logger.info("-" * 80)
        
        try:
            insights_pipeline = InsightsPipeline(backend=self.llm_backend)
            report = insights_pipeline.generate_report(prediction, model_data, enriched_df)
            
            # Save report
            with open(self.output_dir / 'government_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Save report text
            with open(self.output_dir / 'government_report.txt', 'w', encoding='utf-8') as f:
                f.write(f"INFLATION PREDICTION: {prediction:.2f}%\n")
                f.write(f"Generated: {report['generated_at']}\n")
                f.write("=" * 80 + "\n\n")
                f.write("GOVERNMENT IMPACT ANALYSIS:\n")
                f.write("-" * 80 + "\n")
                f.write(report['government_impact_analysis'] + "\n\n")
                f.write("POLICY RECOMMENDATIONS:\n")
                f.write("-" * 80 + "\n")
                f.write(report['policy_recommendations'] + "\n")
            
            self.execution_log['phases']['phase_4'] = {
                'status': 'completed',
                'backend': report['backend'],
                'prediction': float(prediction)
            }
            
            logger.info("✓ Phase 4 completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Phase 4 failed: {str(e)}")
            self.execution_log['phases']['phase_4'] = {'status': 'failed', 'error': str(e)}
            raise
    
    def _execute_phase_5(self, prediction: float, enriched_df, 
                        model_data: dict, report: dict) -> Path:
        """Execute Phase 5: HTML Dashboard Generation."""
        logger.info("")
        logger.info("PHASE 5: STANDALONE HTML FACTORY WITH JS SIMULATION ENGINE")
        logger.info("-" * 80)
        
        try:
            dashboard_path = self.output_dir / 'index.html'
            
            html_pipeline = HTMLFactoryPipeline()
            html_pipeline.generate_dashboard(
                prediction,
                enriched_df,
                model_data,
                report,
                output_path=str(dashboard_path)
            )
            
            self.execution_log['phases']['phase_5'] = {
                'status': 'completed',
                'output_path': str(dashboard_path),
                'file_size_kb': dashboard_path.stat().st_size / 1024
            }
            
            logger.info("✓ Phase 5 completed successfully")
            return dashboard_path
            
        except Exception as e:
            logger.error(f"Phase 5 failed: {str(e)}")
            self.execution_log['phases']['phase_5'] = {'status': 'failed', 'error': str(e)}
            raise
    
    def _print_summary(self, dashboard_path: Path, prediction: float):
        """Print execution summary."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Status: ✓ SUCCESS")
        logger.info(f"Next Month Inflation Prediction: {prediction:.2f}%")
        logger.info(f"Dashboard Location: {dashboard_path}")
        logger.info(f"Dashboard Size: {dashboard_path.stat().st_size / 1024:.1f} KB")
        logger.info("")
        logger.info("OUTPUT FILES GENERATED:")
        logger.info("  • index.html - Interactive dashboard (OPEN THIS IN BROWSER)")
        logger.info("  • unified_dataset.csv - Complete feature dataset")
        logger.info("  • enriched_dataset.csv - Dataset with sentiment scores")
        logger.info("  • model_export.json - Model coefficients & metadata")
        logger.info("  • government_report.json - Structured government analysis")
        logger.info("  • government_report.txt - Text version of report")
        logger.info("  • execution_log.json - Complete execution trace")
        logger.info("")
        logger.info("NEXT STEPS:")
        logger.info(f"  1. Open {dashboard_path} in your web browser")
        logger.info("  2. Review the inflation prediction and key drivers")
        logger.info("  3. Use the simulation panel to test policy scenarios")
        logger.info("  4. Review government impact analysis and recommendations")
        logger.info("=" * 80)
    
    def _save_execution_log(self):
        """Save execution log as JSON."""
        log_path = self.output_dir / 'execution_log.json'
        with open(log_path, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
        logger.info(f"Execution log saved: {log_path}")


def main():
    """Main entry point."""
    
    # Configuration
    MONTHS = 36  # Historical months to process
    LLM_BACKEND = "mock"  # Options: "openai", "anthropic", "huggingface", "mock"
    OUTPUT_DIR = Path.cwd() / "inflation_prediction_output"
    
    # Execute
    orchestrator = InflationPredictionOrchestrator(
        months=MONTHS,
        llm_backend=LLM_BACKEND,
        output_dir=OUTPUT_DIR
    )
    
    result = orchestrator.execute()
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
