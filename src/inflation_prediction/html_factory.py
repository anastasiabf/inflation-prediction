"""
PHASE 5: STANDALONE HTML FACTORY WITH JS SIMULATION ENGINE
Generates index.html with Tailwind CSS, Chart.js, and interactive simulation sliders.
"""

import json
import logging
from typing import Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTMLFactory:
    """
    Factory for generating standalone index.html dashboard.
    Embeds all data, visualizations, and simulation logic.
    """
    
    def __init__(self):
        self.theme_color = "#1e3a8a"  # Deep Corporate Blue
    
    def generate_html(self, prediction: float, historical_data: Dict,
                     model_export: Dict, report: Dict) -> str:
        """
        Generate complete standalone HTML dashboard.
        
        Args:
            prediction: Predicted inflation rate
            historical_data: Historical inflation time series
            model_export: Model coefficients and metadata
            report: Government insights report
            
        Returns:
            Complete HTML string
        """
        logger.info("Generating standalone HTML dashboard...")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indonesia Inflation Prediction Dashboard</title>
    
    <!-- Tailwind CSS via CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Chart.js via CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- Custom Tailwind Config -->
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'corporate': '#1e3a8a',
                        'corporate-light': '#3b82f6',
                        'corporate-dark': '#0f172a'
                    }}
                }}
            }}
        }};
    </script>
    
    <style>
        body {{
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        }}
        
        .hero-gradient {{
            background: linear-gradient(135deg, {self.theme_color} 0%, #2563eb 100%);
        }}
        
        .card-shadow {{
            box-shadow: 0 4px 20px rgba(30, 58, 138, 0.1);
        }}
        
        .metric-badge {{
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 24px;
            text-align: center;
        }}
        
        .metric-green {{
            background-color: #ecfdf5;
            color: #065f46;
        }}
        
        .metric-red {{
            background-color: #fef2f2;
            color: #7f1d1d;
        }}
        
        .metric-yellow {{
            background-color: #fefce8;
            color: #78350f;
        }}
        
        .slider-container {{
            position: relative;
            padding: 20px;
            background: white;
            border-radius: 12px;
            margin-bottom: 16px;
        }}
        
        input[type='range'] {{
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: linear-gradient(to right, #10b981, #eab308, #ef4444);
            outline: none;
            -webkit-appearance: none;
        }}
        
        input[type='range']::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: {self.theme_color};
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}
        
        input[type='range']::-moz-range-thumb {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: {self.theme_color};
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}
        
        .report-section {{
            background: white;
            border-left: 4px solid {self.theme_color};
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}
        
        .report-title {{
            font-size: 20px;
            font-weight: 700;
            color: {self.theme_color};
            margin-bottom: 12px;
        }}
        
        .report-text {{
            font-size: 15px;
            line-height: 1.6;
            color: #374151;
        }}
    </style>
</head>
<body class="font-sans">
    <!-- Header -->
    <div class="hero-gradient text-white">
        <div class="max-w-7xl mx-auto px-6 py-16">
            <h1 class="text-5xl font-bold mb-2">Indonesia Inflation Prediction System</h1>
            <p class="text-xl text-blue-100">AI-Driven Macroeconomic Intelligence & Policy Simulation</p>
            <p class="text-sm text-blue-200 mt-4">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <!-- Main Container -->
    <div class="max-w-7xl mx-auto px-6 py-12">
        
        <!-- Key Metrics Section -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div class="card-shadow bg-white p-6 rounded-lg">
                <p class="text-gray-600 text-sm mb-2">PREDICTED INFLATION</p>
                <div class="metric-badge" id="predictionBadge" style="color: {self._get_color_for_value(prediction)}; background-color: {self._get_bg_color_for_value(prediction)};">
                    {prediction:.2f}%
                </div>
                <p class="text-center text-xs text-gray-500 mt-3">Next 30 Days</p>
            </div>
            
            <div class="card-shadow bg-white p-6 rounded-lg">
                <p class="text-gray-600 text-sm mb-2">MODEL ACCURACY (R²)</p>
                <div class="metric-badge metric-yellow">
                    {model_export['training_metrics']['r2']:.1%}
                </div>
                <p class="text-center text-xs text-gray-500 mt-3">Validation Score</p>
            </div>
            
            <div class="card-shadow bg-white p-6 rounded-lg">
                <p class="text-gray-600 text-sm mb-2">PREDICTION ERROR (RMSE)</p>
                <div class="metric-badge metric-yellow">
                    ±{model_export['training_metrics']['rmse']:.2f}%
                </div>
                <p class="text-center text-xs text-gray-500 mt-3">Confidence Interval</p>
            </div>
        </div>
        
        <!-- Historical vs Predicted Chart -->
        <div class="card-shadow bg-white p-8 rounded-lg mb-12">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">Inflation Trajectory: Historical vs Predicted</h2>
            <div class="chart-container">
                <canvas id="inflationChart"></canvas>
            </div>
        </div>
        
        <!-- Feature Importance -->
        <div class="card-shadow bg-white p-8 rounded-lg mb-12">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">Key Drivers (Feature Importance)</h2>
            <div class="chart-container">
                <canvas id="featureImportanceChart"></canvas>
            </div>
            <div class="mt-6 text-sm text-gray-600">
                <p><strong>Top Factors Influencing Next Month's Inflation:</strong></p>
                <ul class="mt-3 space-y-2">
{self._render_importance_list(model_export['feature_importance_ranking'])}
                </ul>
            </div>
        </div>
        
        <!-- Interactive Simulation Panel -->
        <div class="card-shadow bg-white p-8 rounded-lg mb-12">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">What-If Scenario Simulator</h2>
            <p class="text-gray-600 mb-8">Adjust variables below to simulate inflation scenarios and test policy interventions.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <div class="slider-container">
                        <label class="block text-sm font-semibold text-gray-700 mb-2">BI Policy Rate (%)</label>
                        <input type="range" id="sliderBIRate" min="0" max="10" step="0.1" value="6.0" 
                               oninput="updateSimulation()" class="w-full">
                        <div class="flex justify-between text-xs text-gray-500 mt-2">
                            <span>0%</span>
                            <span id="valueBIRate" class="font-semibold text-corporate">6.00%</span>
                            <span>10%</span>
                        </div>
                    </div>
                    
                    <div class="slider-container">
                        <label class="block text-sm font-semibold text-gray-700 mb-2">USD/IDR Exchange Rate</label>
                        <input type="range" id="sliderExchange" min="14000" max="18000" step="50" value="15500" 
                               oninput="updateSimulation()" class="w-full">
                        <div class="flex justify-between text-xs text-gray-500 mt-2">
                            <span>Rp 14.000</span>
                            <span id="valueExchange" class="font-semibold text-corporate">Rp 15.500</span>
                            <span>Rp 18.000</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class="slider-container">
                        <label class="block text-sm font-semibold text-gray-700 mb-2">News Sentiment Score</label>
                        <input type="range" id="sliderNewsSentiment" min="-1" max="1" step="0.05" value="0" 
                               oninput="updateSimulation()" class="w-full">
                        <div class="flex justify-between text-xs text-gray-500 mt-2">
                            <span>Panic (-1)</span>
                            <span id="valueNewsSentiment" class="font-semibold text-corporate">0.00</span>
                            <span>Optimism (+1)</span>
                        </div>
                    </div>
                    
                    <div class="slider-container">
                        <label class="block text-sm font-semibold text-gray-700 mb-2">Social Media Sentiment Score</label>
                        <input type="range" id="sliderSocialSentiment" min="-1" max="1" step="0.05" value="0" 
                               oninput="updateSimulation()" class="w-full">
                        <div class="flex justify-between text-xs text-gray-500 mt-2">
                            <span>Panic (-1)</span>
                            <span id="valueSocialSentiment" class="font-semibold text-corporate">0.00</span>
                            <span>Optimism (+1)</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Simulation Result -->
            <div class="mt-12 bg-gradient-to-r from-gray-50 to-blue-50 p-8 rounded-lg">
                <p class="text-gray-700 text-sm mb-3">SIMULATED INFLATION OUTCOME</p>
                <div class="metric-badge" id="simulationResult" style="color: #065f46; background-color: #ecfdf5;">
                    --
                </div>
                <p class="text-center text-gray-600 text-sm mt-4">Adjust sliders above to see real-time prediction updates</p>
            </div>
        </div>
        
        <!-- Government Impact Analysis -->
        <div class="report-section">
            <div class="report-title">Government Impact Analysis</div>
            <div class="report-text">
{self._format_text_for_html(report['government_impact_analysis'])}
            </div>
        </div>
        
        <!-- Policy Recommendations -->
        <div class="report-section">
            <div class="report-title">Strategic Policy Recommendations</div>
            <div class="report-text">
{self._format_text_for_html(report['policy_recommendations'])}
            </div>
        </div>
        
        <!-- Footer -->
        <div class="bg-corporate text-white text-center py-8 rounded-lg mt-12">
            <p class="text-sm">
                <strong>Disclaimer:</strong> This prediction system is based on machine learning models trained on historical data. 
                Actual inflation outcomes may differ significantly due to unforeseen macroeconomic shocks, policy changes, or 
                external events. This tool is designed for strategic analysis and policy simulation only.
            </p>
            <p class="text-xs mt-4 text-blue-200">
                System: AI-Driven Inflation Prediction v1.0 | Model: Random Forest Regressor | Backend: LLM-Enhanced Analysis
            </p>
        </div>
    </div>
    
    <!-- Data Embedded in Script -->
    <script>
        // Historical data for chart
        const historicalData = {json.dumps(historical_data)};
        
        // Model export data
        const modelExport = {json.dumps(model_export)};
        
        // Feature ranges for normalization
        const featureRanges = {json.dumps(model_export['feature_ranges'])};
        
        // Prediction function (extracted from model)
        function predictInflation(features) {{
            let prediction = {model_export['linear_approximation']['intercept']};
{self._render_js_coefficients(model_export['linear_approximation']['coefficients'])}
            return Math.max(0, Math.min(10, prediction));
        }}
        
        // Slider update handler
        function updateSimulation() {{
            const biRate = parseFloat(document.getElementById('sliderBIRate').value);
            const exchangeRate = parseFloat(document.getElementById('sliderExchange').value);
            const newsSentiment = parseFloat(document.getElementById('sliderNewsSentiment').value);
            const socialSentiment = parseFloat(document.getElementById('sliderSocialSentiment').value);
            
            // Update display values
            document.getElementById('valueBIRate').textContent = biRate.toFixed(2) + '%';
            document.getElementById('valueExchange').textContent = 'Rp ' + exchangeRate.toLocaleString();
            document.getElementById('valueNewsSentiment').textContent = newsSentiment.toFixed(2);
            document.getElementById('valueSocialSentiment').textContent = socialSentiment.toFixed(2);
            
            // Create feature vector (in same order as model)
            const features = {{
                'inflation_rate': {prediction},  // Use last known inflation as baseline
                'bi_rate': biRate,
                'exchange_rate_usd_idr': exchangeRate,
                'ihk_index': 112,  // Typical IHK value
                'news_sentiment_llm_score': newsSentiment,
                'social_media_sentiment_llm_score': socialSentiment
            }};
            
            // Predict
            const simulatedInflation = predictInflation(features);
            
            // Update badge with color
            const badge = document.getElementById('simulationResult');
            badge.textContent = simulatedInflation.toFixed(2) + '%';
            
            // Color coding
            if (simulatedInflation < 2.5) {{
                badge.style.color = '#065f46';
                badge.style.backgroundColor = '#ecfdf5';
            }} else if (simulatedInflation < 4.0) {{
                badge.style.color = '#78350f';
                badge.style.backgroundColor = '#fefce8';
            }} else {{
                badge.style.color = '#7f1d1d';
                badge.style.backgroundColor = '#fef2f2';
            }}
        }}
        
        // Initialize charts when page loads
        window.addEventListener('load', function() {{
            initializeCharts();
            updateSimulation();
        }});
        
        function initializeCharts() {{
            // Inflation historical vs predicted chart
            const ctx1 = document.getElementById('inflationChart').getContext('2d');
            const dates = historicalData.dates;
            const inflationValues = historicalData.values;
            
            // Add prediction point
            dates.push(dates[dates.length - 1] + ' (Pred)');
            inflationValues.push({prediction});
            
            new Chart(ctx1, {{
                type: 'line',
                data: {{
                    labels: dates,
                    datasets: [
                        {{
                            label: 'Historical Inflation',
                            data: inflationValues.slice(0, -1),
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: '#3b82f6'
                        }},
                        {{
                            label: 'Predicted Inflation',
                            data: Array(inflationValues.length - 2).fill(null).concat([inflationValues[inflationValues.length - 2], {prediction}]),
                            borderColor: '#ef4444',
                            borderDash: [5, 5],
                            borderWidth: 2,
                            pointRadius: 5,
                            pointBackgroundColor: '#ef4444'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 8,
                            title: {{
                                display: true,
                                text: 'Inflation Rate (%)'
                            }}
                        }}
                    }}
                }}
            }});
            
            // Feature importance chart
            const ctx2 = document.getElementById('featureImportanceChart').getContext('2d');
            const featureNames = modelExport.feature_importance_ranking.map(f => f.feature.replace(/_/g, ' '));
            const importances = modelExport.feature_importance_ranking.map(f => (f.importance * 100).toFixed(1));
            
            new Chart(ctx2, {{
                type: 'barHorizontal',
                data: {{
                    labels: featureNames,
                    datasets: [
                        {{
                            label: 'Feature Importance (%)',
                            data: importances,
                            backgroundColor: ['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe'],
                            borderRadius: 6
                        }}
                    ]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>"""
        
        return html
    
    def _get_color_for_value(self, value: float) -> str:
        """Get text color based on inflation value."""
        if value < 2.5:
            return "#065f46"
        elif value < 4.0:
            return "#78350f"
        else:
            return "#7f1d1d"
    
    def _get_bg_color_for_value(self, value: float) -> str:
        """Get background color based on inflation value."""
        if value < 2.5:
            return "#ecfdf5"  # Light green
        elif value < 4.0:
            return "#fefce8"  # Light yellow
        else:
            return "#fef2f2"  # Light red
    
    def _render_importance_list(self, importance_ranking: list) -> str:
        """Render feature importance list as HTML."""
        html_items = []
        for i, item in enumerate(importance_ranking[:6], 1):
            feature_name = item['feature'].replace('_', ' ').title()
            importance_pct = item['importance'] * 100
            html_items.append(f"<li>{i}. <strong>{feature_name}</strong>: {importance_pct:.1f}%</li>")
        return "\n".join(html_items)
    
    def _render_js_coefficients(self, coefficients: Dict[str, float]) -> str:
        """Render coefficients as JavaScript lines."""
        lines = []
        for fname, coef in coefficients.items():
            js_var = fname.lower().replace(' ', '_')
            lines.append(f"            prediction += {coef:.6f} * features['{js_var}'];")
        return "\n".join(lines)
    
    def _format_text_for_html(self, text: str) -> str:
        """Convert text to HTML paragraphs, preserving structure."""
        # Split by double newlines for paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        
        for para in paragraphs:
            # Check if paragraph starts with bullet or number
            if para.strip().startswith('•') or para.strip().startswith('-'):
                # Convert to HTML list
                items = [line.strip().lstrip('•').lstrip('-').strip() 
                        for line in para.split('\n') if line.strip()]
                html_paragraphs.append('<ul class="list-disc list-inside space-y-2">')
                for item in items:
                    html_paragraphs.append(f'<li>{item}</li>')
                html_paragraphs.append('</ul>')
            elif para.strip() and any(para.strip()[0].isdigit() and para.strip()[1] in '.):' 
                                    for _ in [None]):
                # Numbered list
                items = [line.strip() for line in para.split('\n') 
                        if line.strip() and not line.strip()[0].isdigit()]
                if items:
                    html_paragraphs.append('<ol class="list-decimal list-inside space-y-2">')
                    for item in items:
                        html_paragraphs.append(f'<li>{item}</li>')
                    html_paragraphs.append('</ol>')
            elif para.strip():
                html_paragraphs.append(f'<p class="mb-3">{para.strip()}</p>')
        
        return '\n'.join(html_paragraphs)


class HTMLFactoryPipeline:
    """Orchestrates HTML generation."""
    
    def generate_dashboard(self, prediction: float, enriched_df, 
                          model_data: Dict, report: Dict, 
                          output_path: str = "index.html"):
        """
        Generate and save complete dashboard.
        
        Args:
            prediction: Predicted inflation
            enriched_df: Dataset
            model_data: Model export dictionary
            report: Government report
            output_path: Where to save HTML
        """
        logger.info("=" * 60)
        logger.info("PHASE 5: GENERATING STANDALONE HTML DASHBOARD")
        logger.info("=" * 60)
        
        # Prepare historical data for chart
        recent_inflation = enriched_df['inflation_rate'].tail(12)
        historical_data = {
            'dates': [d.strftime('%Y-%m') for d in recent_inflation.index],
            'values': recent_inflation.values.tolist()
        }
        
        # Generate HTML
        factory = HTMLFactory()
        html_content = factory.generate_html(
            prediction,
            historical_data,
            model_data,
            report
        )
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Dashboard generated successfully: {output_path}")
        logger.info(f"File size: {len(html_content) / 1024:.1f} KB")
        
        return output_path


if __name__ == "__main__":
    from data_ingestion import DataPipeline
    from llm_sentiment_pipeline import SentimentPipeline
    from model_training import ModelTrainingPipeline
    from llm_government_insights import InsightsPipeline
    
    # Load and process data
    data_pipeline = DataPipeline(months=36)
    unified_df, news_df, social_df = data_pipeline.build_unified_dataset()
    
    sentiment_pipeline = SentimentPipeline(backend="mock")
    enriched_df = sentiment_pipeline.process_dataset(unified_df, news_df, social_df)
    
    model_pipeline = ModelTrainingPipeline()
    trained_model, model_data = model_pipeline.train_and_export(enriched_df)
    
    # Generate prediction
    X_sample = enriched_df[trained_model.FEATURE_NAMES].iloc[-1:].values
    prediction = trained_model.predict(X_sample)[0]
    
    # Generate report
    insights_pipeline = InsightsPipeline(backend="mock")
    report = insights_pipeline.generate_report(prediction, model_data, enriched_df)
    
    # Generate dashboard
    html_pipeline = HTMLFactoryPipeline()
    output_file = html_pipeline.generate_dashboard(
        prediction,
        enriched_df,
        model_data,
        report,
        output_path="index.html"
    )
    
    print(f"\n✓ Dashboard generated: {output_file}")
    print("Open in web browser to interact with simulation!")
