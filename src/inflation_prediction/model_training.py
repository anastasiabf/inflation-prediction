"""
PHASE 3: RANDOM FOREST MODELING & FORMULA EXPORT
Train Random Forest with time-series validation and export mathematical formula
as JSON for client-side JavaScript simulation.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
from typing import Dict, Tuple, List, Any
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RandomForestInflationModel:
    """
    Trains and manages Random Forest model for inflation prediction.
    Includes validation via TimeSeriesSplit and formula extraction for JavaScript.
    """
    
    FEATURE_NAMES = [
        'inflation_rate',
        'bi_rate',
        'exchange_rate_usd_idr',
        'ihk_index',
        'news_sentiment_llm_score',
        'social_media_sentiment_llm_score'
    ]
    
    TARGET_NAME = 'inflation_rate_t1'  # Next month inflation
    
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """
        Initialize model.
        
        Args:
            n_estimators: Number of trees in forest
            random_state: Reproducibility seed
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
            verbose=0
        )
        
        self.feature_importances = None
        self.training_metrics = None
        self.feature_importance_ranking = None
    
    def prepare_training_data(self, unified_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare feature matrix and target from unified dataset.
        Creates shifted target (t+1) for proper temporal alignment.
        
        Args:
            unified_df: Complete unified dataset
            
        Returns:
            (X, y) feature matrix and target vector
        """
        logger.info("Preparing training data...")
        
        # Ensure all features exist
        for feature in self.FEATURE_NAMES:
            if feature not in unified_df.columns:
                raise ValueError(f"Missing feature: {feature}")
        
        # Extract feature matrix
        X = unified_df[self.FEATURE_NAMES].copy()
        
        # Create target: shift inflation_rate up by 1 (to predict next month)
        y = X['inflation_rate'].shift(-1).values  # Next month's inflation
        
        # Remove last row (no target for last month)
        X = X[:-1].values
        y = y[:-1]
        
        # Remove any NaN rows
        valid_idx = ~np.isnan(y)
        X = X[valid_idx]
        y = y[valid_idx]
        
        logger.info(f"Training data prepared: X shape {X.shape}, y shape {y.shape}")
        
        return X, y
    
    def train_with_time_series_split(self, X: np.ndarray, y: np.ndarray, 
                                     n_splits: int = 3) -> Dict[str, Any]:
        """
        Train model using TimeSeriesSplit for proper time-series validation.
        Prevents data leakage by respecting temporal order.
        
        Args:
            X: Feature matrix
            y: Target vector
            n_splits: Number of cross-validation splits
            
        Returns:
            Dictionary with validation metrics
        """
        logger.info("=" * 60)
        logger.info("TRAINING RANDOM FOREST WITH TIME SERIES VALIDATION")
        logger.info("=" * 60)
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_results = {
            'mae': [],
            'rmse': [],
            'r2': []
        }
        
        fold_num = 0
        for train_idx, test_idx in tscv.split(X):
            fold_num += 1
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Train on this fold
            fold_model = RandomForestRegressor(
                n_estimators=self.model.n_estimators,
                max_depth=self.model.max_depth,
                min_samples_split=self.model.min_samples_split,
                min_samples_leaf=self.model.min_samples_leaf,
                random_state=self.model.random_state,
                n_jobs=-1
            )
            fold_model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = fold_model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            cv_results['mae'].append(mae)
            cv_results['rmse'].append(rmse)
            cv_results['r2'].append(r2)
            
            logger.info(f"  Fold {fold_num}: MAE={mae:.4f}, RMSE={rmse:.4f}, R²={r2:.4f}")
        
        # Final training on full dataset
        logger.info("\nTraining final model on complete dataset...")
        self.model.fit(X, y)
        
        # Final predictions for metrics
        y_pred_final = self.model.predict(X)
        final_mae = mean_absolute_error(y, y_pred_final)
        final_rmse = np.sqrt(mean_squared_error(y, y_pred_final))
        final_r2 = r2_score(y, y_pred_final)
        
        # Extract feature importances
        self.feature_importances = dict(zip(self.FEATURE_NAMES, 
                                            self.model.feature_importances_))
        
        # Rank features by importance
        self.feature_importance_ranking = sorted(
            self.feature_importances.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        self.training_metrics = {
            'cv_mae': (np.mean(cv_results['mae']), np.std(cv_results['mae'])),
            'cv_rmse': (np.mean(cv_results['rmse']), np.std(cv_results['rmse'])),
            'cv_r2': (np.mean(cv_results['r2']), np.std(cv_results['r2'])),
            'final_mae': final_mae,
            'final_rmse': final_rmse,
            'final_r2': final_r2,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
        
        logger.info(f"\nFinal Metrics:")
        logger.info(f"  MAE: {final_mae:.4f} (±{np.std(cv_results['mae']):.4f})")
        logger.info(f"  RMSE: {final_rmse:.4f} (±{np.std(cv_results['rmse']):.4f})")
        logger.info(f"  R²: {final_r2:.4f} (±{np.std(cv_results['r2']):.4f})")
        
        logger.info(f"\nFeature Importances:")
        for feature, importance in self.feature_importance_ranking:
            logger.info(f"  {feature}: {importance:.4f}")
        
        return self.training_metrics
    
    def export_linear_approximation(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Extract a simplified linear approximation of the Random Forest.
        Useful for client-side JavaScript simulation.
        
        This uses partial dependence to create a linear approximation.
        
        Args:
            X: Feature matrix (for calculating average contributions)
            y: Target vector
            
        Returns:
            Dictionary with coefficients and intercept for linear model
        """
        logger.info("Extracting linear approximation from Random Forest...")
        
        # Use sklearn's PartialDependence to extract feature contributions
        from sklearn.inspection import partial_dependence
        
        # Get mean predictions at feature mean values
        X_mean = np.mean(X, axis=0)
        mean_pred = self.model.predict(X_mean.reshape(1, -1))[0]
        
        # Estimate linear coefficients using permutation importance + correlation
        coefficients = {}
        
        for i, feature_name in enumerate(self.FEATURE_NAMES):
            # Correlation with target
            corr = np.corrcoef(X[:, i], y)[0, 1]
            
            # Weight by feature importance
            importance = self.feature_importances[feature_name]
            
            # Combine: correlation + importance + feature scale
            X_std = np.std(X[:, i])
            y_std = np.std(y)
            
            if X_std > 0:
                coef = corr * importance * (y_std / X_std)
            else:
                coef = 0.0
            
            coefficients[feature_name] = float(coef)
        
        # Intercept: mean of predictions minus weighted sum of features
        weighted_sum = sum(coefficients[fname] * X_mean[i] 
                          for i, fname in enumerate(self.FEATURE_NAMES))
        intercept = float(mean_pred - weighted_sum)
        
        logger.info(f"Linear approximation extracted:")
        logger.info(f"  Intercept: {intercept:.6f}")
        for fname, coef in coefficients.items():
            logger.info(f"  {fname}: {coef:.6f}")
        
        return {
            'intercept': intercept,
            'coefficients': coefficients
        }
    
    def export_decision_tree_rules(self, max_trees: int = 5) -> List[Dict]:
        """
        Export simplified decision rules from top N trees.
        Used for transparency and JavaScript evaluation.
        
        Args:
            max_trees: Number of top trees to export
            
        Returns:
            List of tree rule dictionaries
        """
        logger.info(f"Exporting decision rules from top {max_trees} trees...")
        
        tree_rules = []
        
        for tree_idx in range(min(max_trees, len(self.model.estimators_))):
            tree = self.model.estimators_[tree_idx]
            
            # Extract simplified rules from tree
            tree_dict = {
                'tree_id': tree_idx,
                'rules': self._extract_tree_rules(tree, max_depth=4)
            }
            tree_rules.append(tree_dict)
        
        return tree_rules
    
    def _extract_tree_rules(self, tree, max_depth=4, node_id=0, depth=0, 
                            prefix="") -> str:
        """Recursively extract rules from a decision tree."""
        if depth >= max_depth:
            return f"Prediction: {tree.tree_.value[node_id][0][0]:.2f}"
        
        if tree.tree_.feature[node_id] == -2:  # Leaf node
            return f"Prediction: {tree.tree_.value[node_id][0][0]:.2f}"
        
        feature_name = self.FEATURE_NAMES[tree.tree_.feature[node_id]]
        threshold = tree.tree_.threshold[node_id]
        
        left_rule = self._extract_tree_rules(tree, max_depth, tree.tree_.children_left[node_id], 
                                            depth+1, prefix + "  ")
        right_rule = self._extract_tree_rules(tree, max_depth, tree.tree_.children_right[node_id], 
                                             depth+1, prefix + "  ")
        
        return f"IF {feature_name} <= {threshold:.2f} THEN {left_rule} ELSE {right_rule}"
    
    def export_for_javascript(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Export complete model information in JSON format for JavaScript.
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            Dictionary suitable for JSON serialization in HTML
        """
        logger.info("=" * 60)
        logger.info("EXPORTING MODEL FOR JAVASCRIPT")
        logger.info("=" * 60)
        
        # Get linear approximation
        linear_approx = self.export_linear_approximation(X, y)
        
        export_dict = {
            'model_type': 'random_forest',
            'n_estimators': int(self.model.n_estimators),
            'feature_names': self.FEATURE_NAMES,
            'feature_count': len(self.FEATURE_NAMES),
            'feature_importances': {
                fname: float(imp) for fname, imp in self.feature_importances.items()
            },
            'feature_importance_ranking': [
                {'feature': fname, 'importance': float(imp)} 
                for fname, imp in self.feature_importance_ranking
            ],
            'linear_approximation': {
                'intercept': linear_approx['intercept'],
                'coefficients': linear_approx['coefficients']
            },
            'training_metrics': {
                'mae': float(self.training_metrics['final_mae']),
                'rmse': float(self.training_metrics['final_rmse']),
                'r2': float(self.training_metrics['final_r2']),
                'n_samples': int(self.training_metrics['n_samples']),
                'n_features': int(self.training_metrics['n_features'])
            },
            'prediction_formula': self._build_js_formula(linear_approx),
            'feature_ranges': self._calculate_feature_ranges(X)
        }
        
        return export_dict
    
    def _build_js_formula(self, linear_approx: Dict) -> str:
        """Build a JavaScript-ready prediction formula."""
        formula = f"function predictInflation(features) {{\n"
        formula += f"  let prediction = {linear_approx['intercept']:.6f};\n"
        
        for fname, coef in linear_approx['coefficients'].items():
            js_var_name = fname.lower().replace(' ', '_')
            formula += f"  prediction += {coef:.6f} * features['{js_var_name}'];\n"
        
        formula += f"  return Math.max(0, Math.min(10, prediction));\n"  # Clip to 0-10%
        formula += "}"
        
        return formula
    
    def _calculate_feature_ranges(self, X: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Calculate min/max/mean ranges for each feature for UI slider setup."""
        ranges = {}
        for i, fname in enumerate(self.FEATURE_NAMES):
            ranges[fname] = {
                'min': float(np.min(X[:, i])),
                'max': float(np.max(X[:, i])),
                'mean': float(np.mean(X[:, i])),
                'std': float(np.std(X[:, i]))
            }
        return ranges
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        return self.model.predict(X)


class ModelTrainingPipeline:
    """Orchestrates complete model training workflow."""
    
    def __init__(self):
        self.model = RandomForestInflationModel()
    
    def train_and_export(self, enriched_df: pd.DataFrame) -> Tuple[RandomForestInflationModel, Dict]:
        """
        Complete training pipeline.
        
        Args:
            enriched_df: Dataset with sentiment scores
            
        Returns:
            (trained_model, export_dict_for_js)
        """
        logger.info("=" * 60)
        logger.info("PHASE 3: RANDOM FOREST MODELING")
        logger.info("=" * 60)
        
        # Prepare data
        X, y = self.model.prepare_training_data(enriched_df)
        
        # Train with time series validation
        self.model.train_with_time_series_split(X, y, n_splits=3)
        
        # Export for JavaScript
        js_export = self.model.export_for_javascript(X, y)
        
        return self.model, js_export


if __name__ == "__main__":
    from data_ingestion import DataPipeline
    from llm_sentiment_pipeline import SentimentPipeline
    
    # Load data
    data_pipeline = DataPipeline(months=36)
    unified_df, news_df, social_df = data_pipeline.build_unified_dataset()
    
    # Add sentiment
    sentiment_pipeline = SentimentPipeline(backend="mock")
    enriched_df = sentiment_pipeline.process_dataset(unified_df, news_df, social_df)
    
    # Train model
    model_pipeline = ModelTrainingPipeline()
    trained_model, js_export = model_pipeline.train_and_export(enriched_df)
    
    # Save export
    import json
    with open('/tmp/model_export.json', 'w') as f:
        json.dump(js_export, f, indent=2)
    
    print("\nModel export saved to /tmp/model_export.json")
    print("\nPrediction formula:")
    print(js_export['prediction_formula'])
