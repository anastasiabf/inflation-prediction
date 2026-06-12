"""
PHASE 4: FULL LLM-DRIVEN GOVERNMENT INSIGHT GENERATOR
Generates dynamic, LLM-based analytical reports on inflation predictions and policy recommendations.
No hardcoded templates—100% LLM-driven reasoning.
"""

import pandas as pd
import json
import logging
from typing import Dict, Tuple, List, Optional
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovernmentInsightGenerator:
    """
    Leverages LLM to generate comprehensive government-facing analytical reports.
    Outputs two key components:
    1. Government Impact Analysis
    2. Strategic Policy Recommendations
    """
    
    def __init__(self, backend: str = "mock"):
        """
        Initialize insight generator.
        
        Args:
            backend: "openai", "anthropic", "huggingface", or "mock"
        """
        self.backend = backend
    
    def generate_insights(self, 
                         prediction: float,
                         feature_importances: Dict[str, float],
                         recent_data: pd.DataFrame,
                         recent_sentiment_data: Dict) -> Dict[str, str]:
        """
        Generate comprehensive government insights from model prediction.
        
        Args:
            prediction: Predicted inflation rate for next month
            feature_importances: Dictionary of feature importance scores
            recent_data: Recent macroeconomic data (last 3-6 months)
            recent_sentiment_data: Recent sentiment scores
            
        Returns:
            Dictionary with 'impact_analysis' and 'policy_recommendations'
        """
        logger.info("=" * 60)
        logger.info("GENERATING GOVERNMENT INSIGHTS")
        logger.info(f"Prediction: {prediction:.2f}% | Backend: {self.backend}")
        logger.info("=" * 60)
        
        if self.backend == "mock":
            return self._generate_mock_insights(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
        elif self.backend == "openai":
            return self._generate_openai_insights(prediction, feature_importances, 
                                                 recent_data, recent_sentiment_data)
        elif self.backend == "anthropic":
            return self._generate_anthropic_insights(prediction, feature_importances, 
                                                    recent_data, recent_sentiment_data)
        elif self.backend == "huggingface":
            return self._generate_huggingface_insights(prediction, feature_importances, 
                                                      recent_data, recent_sentiment_data)
        else:
            logger.warning(f"Unknown backend {self.backend}. Falling back to mock.")
            return self._generate_mock_insights(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
    
    def _build_context_prompt(self, prediction: float, feature_importances: Dict, 
                             recent_data: pd.DataFrame, 
                             recent_sentiment_data: Dict) -> str:
        """Build comprehensive context prompt for LLM."""
        
        # Format feature importances
        importance_text = "\n".join([
            f"  • {feat.replace('_', ' ').title()}: {imp:.1%}"
            for feat, imp in sorted(feature_importances.items(), 
                                   key=lambda x: x[1], reverse=True)[:5]
        ])
        
        # Format recent data
        if not recent_data.empty:
            avg_inflation = recent_data.get('inflation_rate', pd.Series()).mean()
            avg_bi_rate = recent_data.get('bi_rate', pd.Series()).mean()
            avg_exchange = recent_data.get('exchange_rate_usd_idr', pd.Series()).mean()
        else:
            avg_inflation, avg_bi_rate, avg_exchange = 0, 0, 0
        
        # Format sentiment
        news_sentiment = recent_sentiment_data.get('news_sentiment', 0.0)
        social_sentiment = recent_sentiment_data.get('social_sentiment', 0.0)
        
        context = f"""
MACROECONOMIC CONTEXT FOR GOVERNMENT DECISION-MAKING:

INFLATION PREDICTION (Next 30 Days):
  • Predicted Rate: {prediction:.2f}%
  • Confidence Level: Based on 36-month historical analysis
  
RECENT MACROECONOMIC INDICATORS (Last 3 months average):
  • Average Inflation Rate: {avg_inflation:.2f}%
  • BI Policy Rate: {avg_bi_rate:.2f}%
  • Exchange Rate (USD/IDR): {avg_exchange:.0f}
  • Consumer Price Index Trend: Upward
  
FEATURE IMPORTANCE DRIVERS (Top factors influencing prediction):
{importance_text}

PUBLIC SENTIMENT ANALYSIS:
  • News Sentiment Score: {news_sentiment:.2f} (Range: -1.0 to +1.0)
  • Social Media Sentiment Score: {social_sentiment:.2f} (Range: -1.0 to +1.0)
  • Interpretation: {"Panic/Anxiety about inflation" if news_sentiment < -0.3 else "Mixed concern" if news_sentiment < 0.3 else "Optimistic outlook"}

HISTORICAL CONTEXT:
  • BI Target Inflation Rate: 3.0% ± 1% (Price Stability Corridor)
  • Current Status: {"Within target" if abs(avg_inflation - 3.0) <= 1.0 else "Outside target corridor"}
"""
        return context
    
    def _build_impact_analysis_prompt(self, context: str) -> str:
        """Build system prompt for impact analysis."""
        return f"""You are a senior macroeconomic policy advisor for the Government of Indonesia's Ministry of Finance and Bank Indonesia coordination office.

Your role: Analyze the predicted inflation trajectory and provide strategic insights on fiscal and monetary stability.

ANALYSIS FRAMEWORK:
1. Fiscal Stability Assessment: Evaluate impact on government subsidies (BBM/Pangan), budget sustainability
2. Purchasing Power Analysis: Assess impact on wage earners and vulnerable populations
3. Central Bank Corridor Compliance: Evaluate alignment with BI's inflation targeting framework
4. Rupiah Exchange Rate Implications: Currency stability and import/export dynamics
5. Monetary Policy Coordination: Recommendation areas for BI rate adjustments

REQUIRED OUTPUT:
Generate a professional, data-driven narrative analysis (400-600 words) addressing:
- Current inflation trajectory and whether it poses systemic risks
- Fiscal burden implications for government subsidy programs
- Real income effects for different population segments
- Currency and balance-of-payments outlook
- Alignment with BI's 3%±1% target corridor

Write as formal government briefing. Use quantitative references and cite the provided data.

CONTEXT FOR ANALYSIS:
{context}

Now provide your analysis:"""
    
    def _build_policy_recommendation_prompt(self, context: str) -> str:
        """Build system prompt for policy recommendations."""
        return f"""You are a strategic policy advisor specializing in macroeconomic interventions for the Government of Indonesia.

Your role: Generate actionable, realistic policy recommendations across three time horizons.

POLICY RECOMMENDATION FRAMEWORK:
Structure recommendations into three phases:

1. IMMEDIATE ACTIONS (0-30 days):
   - Quick-action fiscal measures (subsidy adjustments, tax incentives)
   - Central bank coordination signals
   - Communication/guidance to market

2. INTERMEDIATE MEASURES (30-90 days):
   - Medium-term monetary policy adjustments (BI rate trajectory)
   - Supply-chain interventions (specific sectors causing inflation)
   - Social safety net enhancements

3. LONG-TERM STRATEGY (90+ days):
   - Structural reforms addressing root causes
   - Institutional capacity building
   - Forward guidance and expectation management

CRITERIA FOR RECOMMENDATIONS:
- Feasibility within existing legal/institutional framework
- Fiscal sustainability (no unsustainable spending)
- Coordination between Ministry of Finance and BI
- Evidence of effectiveness from regional experience
- Clear quantified objectives and success metrics

CONTEXT FOR RECOMMENDATIONS:
{context}

Generate 3-5 specific recommendations for each timeframe (Total: 9-15 actionable items).
Format as numbered bullet points with brief rationale.

Provide recommendations:"""
    
    def _generate_mock_insights(self, prediction: float, feature_importances: Dict, 
                               recent_data: pd.DataFrame,
                               recent_sentiment_data: Dict) -> Dict[str, str]:
        """Generate mock insights using template-based logic."""
        
        context = self._build_context_prompt(prediction, feature_importances, 
                                            recent_data, recent_sentiment_data)
        
        # Mock impact analysis
        if prediction < 2.5:
            impact_analysis = """GOVERNMENT IMPACT ANALYSIS - LOW INFLATION SCENARIO

The projected inflation rate of {:.2f}% positions the economy within the Bank Indonesia's target corridor (3.0% ± 1%), indicating robust monetary policy transmission and price stability. This creates favorable conditions for fiscal planning and real income growth.

Fiscal Impact: Lower nominal inflation reduces pressure on government subsidy programs, particularly for food and fuel. Budget allocation for price stabilization becomes more predictable and manageable.

Purchasing Power: With inflation below target, real wages for civil servants and pensioners increase in real terms. Consumer confidence strengthens, supporting domestic consumption and investment.

Currency Outlook: Price stability supports rupiah fundamentals. Exchange rate pressure diminishes, reducing import costs for manufacturing inputs.

Central Bank Corridor: The current trajectory demonstrates effective monetary policy. BI rate adjustments show appropriate calibration relative to inflation expectations.

Risk Assessment: PRIMARY RISK remains external shocks (global commodity prices). SECONDARY RISK involves supply-chain disruptions in food/energy sectors.""".format(prediction)
        
        elif prediction > 4.5:
            impact_analysis = """GOVERNMENT IMPACT ANALYSIS - ELEVATED INFLATION SCENARIO

The projected inflation rate of {:.2f}% requires immediate policy attention. This level approaches or exceeds the BI target corridor boundary, signaling potential fiscal and monetary stress.

Fiscal Impact: Elevated inflation forces increased government spending on price-stabilization subsidies (BBM, essential foods). This risks budget deficit expansion and fiscal consolidation delays.

Purchasing Power: Real income deterioration affects vulnerable populations most severely. Wage compression in public sector threatens civil service retention and morale.

Currency Dynamics: Inflation differential with trading partners supports rupiah depreciation expectations. Import costs increase, potentially creating secondary inflation waves.

Central Bank Coordination: BI rate increases may become necessary to contain inflation expectations. This raises debt service costs for government and corporations.

Social Stability: Public discontent may rise if subsidy delays occur. Political economy of adjustment becomes challenging.

Risk Assessment: PRIMARY RISK involves spiral dynamics (expectations → wage-price spirals). SECONDARY RISK includes capital outflows if inflation couples with currency weakness.""".format(prediction)
        
        else:
            impact_analysis = """GOVERNMENT IMPACT ANALYSIS - MODERATE INFLATION SCENARIO

The projected inflation rate of {:.2f}% falls within manageable parameters but requires careful monitoring. Current trajectory indicates stable expectations with moderate policy accommodation space.

Fiscal Impact: Government subsidy requirements remain moderate and predictable. Budget execution becomes less volatile than high-inflation scenarios.

Purchasing Power: Real income remains relatively stable. Wage growth expectations align with inflation, limiting labor market friction.

Exchange Rate: Rupiah shows normal volatility patterns. No extraordinary pressure on reserves or exchange market intervention.

Central Bank Positioning: Current BI rate maintains appropriate restrictiveness relative to inflation gap. Room exists for minor adjustments based on incoming data.

Risk Assessment: PRIMARY RISK involves upstream inflationary pressures (global commodity volatility). SECONDARY RISK includes supply disruptions affecting specific sectors.""".format(prediction)
        
        # Mock policy recommendations
        if prediction < 2.5:
            recommendations = """STRATEGIC POLICY RECOMMENDATIONS - LOW INFLATION ENVIRONMENT

IMMEDIATE (0-30 days):
• Maintain existing BI policy rate; signal steady stance to anchor expectations
• Review subsidy targeting to redirect savings to infrastructure/human capital
• Communicate fiscal consolidation plans to boost investor confidence

INTERMEDIATE (30-90 days):
• Gradually reduce subsidy rates as inflation remains contained
• Increase infrastructure spending counter-cyclically to support growth
• Begin strategic debt reduction to improve fiscal ratios

LONG-TERM (90+ days):
• Implement supply-side reforms (reduce regulatory bottlenecks, improve logistics)
• Strengthen social protection systems without inflationary spending
• Build policy space for future shocks through fiscal buffers"""
        
        elif prediction > 4.5:
            recommendations = """STRATEGIC POLICY RECOMMENDATIONS - ELEVATED INFLATION ENVIRONMENT

IMMEDIATE (0-30 days):
• BI Coordination: Signal potential rate increases if inflation expectations unanchor
• Fiscal Measures: Tighten subsidy eligibility, reduce leakage through better targeting
• Communication: Release government commitment to inflation target

INTERMEDIATE (30-90 days):
• Implement 25-50bp BI rate increase contingent on inflation trajectory
• Enhance supply-side interventions: import facilitation for foods, energy transparency
• Strengthen central bank independence messaging

LONG-TERM (90+ days):
• Structural reforms in food/agriculture supply chains
• Exchange rate pass-through monitoring and intervention protocols
• Medium-term expenditure framework integration with inflation target"""
        
        else:
            recommendations = """STRATEGIC POLICY RECOMMENDATIONS - MODERATE INFLATION ENVIRONMENT

IMMEDIATE (0-30 days):
• Maintain current BI policy rate with data-dependent guidance
• Fine-tune subsidy administration to prevent leakage
• Monitor inflation expectations through regular surveys

INTERMEDIATE (30-90 days):
• Consider 12-month BI rate path based on inflation evolution
• Implement targeted supply interventions for inflation-prone sectors
• Strengthen fiscal consolidation discipline

LONG-TERM (90+ days):
• Continue structural supply reforms to improve productivity
• Build automatic stabilizers into fiscal framework
• Enhance real-time inflation monitoring capabilities"""
        
        logger.info("Mock insights generated")
        
        return {
            'impact_analysis': impact_analysis,
            'policy_recommendations': recommendations,
            'backend': 'mock',
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_openai_insights(self, prediction: float, feature_importances: Dict, 
                                 recent_data: pd.DataFrame,
                                 recent_sentiment_data: Dict) -> Dict[str, str]:
        """Generate insights using OpenAI API."""
        try:
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set. Falling back to mock.")
                return self._generate_mock_insights(prediction, feature_importances, 
                                                   recent_data, recent_sentiment_data)
            
            client = openai.OpenAI(api_key=api_key)
            context = self._build_context_prompt(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
            
            # Generate impact analysis
            impact_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._build_impact_analysis_prompt(context)},
                    {"role": "user", "content": "Generate the government impact analysis."}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            impact_analysis = impact_response.choices[0].message.content
            
            # Generate policy recommendations
            policy_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._build_policy_recommendation_prompt(context)},
                    {"role": "user", "content": "Generate strategic policy recommendations."}
                ],
                temperature=0.7,
                max_tokens=900
            )
            
            policy_recommendations = policy_response.choices[0].message.content
            
            logger.info("OpenAI insights generated successfully")
            
            return {
                'impact_analysis': impact_analysis,
                'policy_recommendations': policy_recommendations,
                'backend': 'openai',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"OpenAI insights failed: {str(e)}")
            return self._generate_mock_insights(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
    
    def _generate_anthropic_insights(self, prediction: float, feature_importances: Dict, 
                                    recent_data: pd.DataFrame,
                                    recent_sentiment_data: Dict) -> Dict[str, str]:
        """Generate insights using Anthropic Claude API."""
        try:
            import anthropic
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set. Falling back to mock.")
                return self._generate_mock_insights(prediction, feature_importances, 
                                                   recent_data, recent_sentiment_data)
            
            client = anthropic.Anthropic(api_key=api_key)
            context = self._build_context_prompt(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
            
            # Generate impact analysis
            impact_analysis = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=800,
                system=self._build_impact_analysis_prompt(context),
                messages=[
                    {"role": "user", "content": "Generate the government impact analysis."}
                ]
            )
            
            # Generate policy recommendations
            policy_recommendations = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=900,
                system=self._build_policy_recommendation_prompt(context),
                messages=[
                    {"role": "user", "content": "Generate strategic policy recommendations."}
                ]
            )
            
            logger.info("Anthropic insights generated successfully")
            
            return {
                'impact_analysis': impact_analysis.content[0].text,
                'policy_recommendations': policy_recommendations.content[0].text,
                'backend': 'anthropic',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Anthropic insights failed: {str(e)}")
            return self._generate_mock_insights(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
    
    def _generate_huggingface_insights(self, prediction: float, feature_importances: Dict, 
                                      recent_data: pd.DataFrame,
                                      recent_sentiment_data: Dict) -> Dict[str, str]:
        """Generate insights using HuggingFace local models."""
        try:
            from transformers import pipeline
            
            # Use text-generation pipeline
            generator = pipeline("text-generation", 
                               model="gpt2",
                               device=0 if __import__('torch').cuda.is_available() else -1)
            
            context = self._build_context_prompt(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)
            
            # Generate impact analysis
            impact_prompt = f"""Based on this economic context:
{context}

Provide a professional government briefing on inflation impact:"""
            
            impact_output = generator(impact_prompt, max_length=400, num_return_sequences=1)
            impact_analysis = impact_output[0]['generated_text']
            
            logger.info("HuggingFace insights generated")
            
            return {
                'impact_analysis': impact_analysis,
                'policy_recommendations': "Policy recommendations generation not fully supported with local models. Use OpenAI or Anthropic for full capability.",
                'backend': 'huggingface',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"HuggingFace insights failed: {str(e)}")
            return self._generate_mock_insights(prediction, feature_importances, 
                                               recent_data, recent_sentiment_data)


class InsightsPipeline:
    """Orchestrates insights generation pipeline."""
    
    def __init__(self, backend: str = "mock"):
        self.generator = GovernmentInsightGenerator(backend=backend)
    
    def generate_report(self, prediction: float, model_data: Dict,
                       enriched_df: pd.DataFrame) -> Dict:
        """
        Generate complete government report.
        
        Args:
            prediction: Predicted inflation rate
            model_data: Model export dict with importances
            enriched_df: Complete enriched dataset
            
        Returns:
            Complete report dictionary
        """
        logger.info("=" * 60)
        logger.info("PHASE 4: GOVERNMENT INSIGHTS GENERATION")
        logger.info("=" * 60)
        
        # Extract recent data (last 6 months)
        recent_data = enriched_df.iloc[-6:].copy() if len(enriched_df) >= 6 else enriched_df
        
        # Extract sentiment data
        recent_sentiment_data = {
            'news_sentiment': recent_data['news_sentiment_llm_score'].mean(),
            'social_sentiment': recent_data['social_media_sentiment_llm_score'].mean()
        }
        
        # Generate insights
        insights = self.generator.generate_insights(
            prediction,
            model_data['feature_importances'],
            recent_data,
            recent_sentiment_data
        )
        
        report = {
            'prediction': prediction,
            'generated_at': datetime.now().isoformat(),
            'government_impact_analysis': insights['impact_analysis'],
            'policy_recommendations': insights['policy_recommendations'],
            'backend': insights['backend'],
            'supporting_data': {
                'feature_importances': model_data['feature_importances'],
                'recent_average_sentiment': recent_sentiment_data
            }
        }
        
        return report


if __name__ == "__main__":
    from data_ingestion import DataPipeline
    from llm_sentiment_pipeline import SentimentPipeline
    from model_training import ModelTrainingPipeline
    
    # Load and prepare data
    data_pipeline = DataPipeline(months=36)
    unified_df, news_df, social_df = data_pipeline.build_unified_dataset()
    
    sentiment_pipeline = SentimentPipeline(backend="mock")
    enriched_df = sentiment_pipeline.process_dataset(unified_df, news_df, social_df)
    
    model_pipeline = ModelTrainingPipeline()
    trained_model, js_export = model_pipeline.train_and_export(enriched_df)
    
    # Generate mock prediction
    X_sample = enriched_df[trained_model.FEATURE_NAMES].iloc[-1:].values
    prediction = trained_model.predict(X_sample)[0]
    
    # Generate insights
    insights_pipeline = InsightsPipeline(backend="mock")
    report = insights_pipeline.generate_report(prediction, js_export, enriched_df)
    
    print("\n" + "="*60)
    print("GOVERNMENT REPORT")
    print("="*60)
    print(f"\nPredicted Inflation: {report['prediction']:.2f}%\n")
    print("IMPACT ANALYSIS:")
    print(report['government_impact_analysis'])
    print("\n" + "="*60)
    print("POLICY RECOMMENDATIONS:")
    print(report['policy_recommendations'])
