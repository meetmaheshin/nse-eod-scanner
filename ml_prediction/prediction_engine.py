#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML-Based Stock Prediction Engine
---------------------------------
Analyzes historical scanner signals and builds a machine learning model
to predict tomorrow's potential winning trades with confidence scores.

Features:
- Tracks historical performance of scanner recommendations
- Builds ML model using historical data
- Generates tomorrow's predictions with probability scores
- Calculates win rate, average return, and confidence metrics

Requirements:
    pip install pandas numpy scikit-learn yfinance

Usage:
    python prediction_engine.py
"""

import os
import json
import logging
import warnings
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
except ImportError:
    raise SystemExit("Please install scikit-learn: pip install scikit-learn")

try:
    import yfinance as yf
except ImportError:
    raise SystemExit("Please install yfinance: pip install yfinance")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('prediction_engine.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
OUTPUT_DIR = Path('eod_scanner_output')
MODELS_DIR = Path('ml_models')
MODELS_DIR.mkdir(exist_ok=True)

PERFORMANCE_TRACKING_FILE = 'performance_history.csv'
MODEL_FILE = MODELS_DIR / 'prediction_model.pkl'
SCALER_FILE = MODELS_DIR / 'scaler.pkl'

# Prediction thresholds
MIN_TRAINING_SAMPLES = 50  # Minimum historical samples needed
CONFIDENCE_THRESHOLD = 0.6  # 60% minimum confidence
TARGET_RETURN_PCT = 2.0  # 2% return target for next day


class PredictionEngine:
    """ML-based prediction engine for stock movements"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.performance_data = None
        
    def collect_historical_data(self, days_back: int = 60) -> pd.DataFrame:
        """Collect historical scanner signals and their next-day performance"""
        logger.info(f"Collecting historical data from last {days_back} days...")
        
        # Find all historical signal files
        long_files = sorted(OUTPUT_DIR.glob('long_candidates_*.csv'))
        short_files = sorted(OUTPUT_DIR.glob('short_candidates_*.csv'))
        all_signals_files = sorted(OUTPUT_DIR.glob('all_signals_*.csv'))
        
        if not all_signals_files:
            logger.warning("No historical signal files found!")
            return pd.DataFrame()
        
        historical_data = []
        
        # Process each signal file
        for signal_file in all_signals_files[-days_back:]:
            try:
                # Extract date from filename: all_signals_2025-10-30_0935.csv
                filename = signal_file.stem
                date_part = '_'.join(filename.split('_')[2:])  # 2025-10-30_0935
                signal_date = datetime.strptime(date_part.split('_')[0], '%Y-%m-%d')
                
                # Read signals
                df = pd.read_csv(signal_file)
                
                # Get next trading day performance for each symbol
                for _, row in df.iterrows():
                    symbol = row['symbol']
                    close_price = row.get('close', 0)
                    
                    if close_price == 0:
                        continue
                    
                    # Fetch next day's data
                    next_day_perf = self.get_next_day_performance(
                        symbol, 
                        signal_date, 
                        close_price
                    )
                    
                    if next_day_perf is not None:
                        # Combine signal features with performance
                        record = {
                            'date': signal_date,
                            'symbol': symbol,
                            'signal_close': close_price,
                            **{k: row.get(k, 0) for k in [
                                'score_long', 'score_short', 'rsi14', 'atr14',
                                'vol_ratio', 'cpr_width_pct', 'macd_value',
                                'bb_position', 'risk_reward_ratio', 'ibs',
                                'twenty_high_break', 'twenty_low_break',
                                'macd_bullish', 'macd_bearish', 'narrow_cpr',
                                'bb_squeeze', 'vol_surge', 'trend_long', 'trend_short'
                            ]},
                            **next_day_perf
                        }
                        historical_data.append(record)
                        
            except Exception as e:
                logger.warning(f"Error processing {signal_file}: {e}")
                continue
        
        if historical_data:
            df = pd.DataFrame(historical_data)
            logger.info(f"Collected {len(df)} historical records")
            # Save for future reference
            df.to_csv(PERFORMANCE_TRACKING_FILE, index=False)
            return df
        else:
            logger.warning("No historical data collected")
            return pd.DataFrame()
    
    def get_next_day_performance(self, symbol: str, signal_date: datetime, 
                                 entry_price: float) -> Optional[Dict]:
        """Get next trading day's performance for a symbol"""
        try:
            # Fetch data for next few days
            start_date = signal_date
            end_date = signal_date + timedelta(days=5)
            
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(start=start_date, end=end_date)
            
            if len(hist) < 2:
                return None
            
            # Get next day's data (first day after signal date)
            next_day = hist.iloc[1]  # Next trading day
            
            next_high = next_day['High']
            next_low = next_day['Low']
            next_close = next_day['Close']
            
            # Calculate returns
            high_return = ((next_high - entry_price) / entry_price) * 100
            low_return = ((next_low - entry_price) / entry_price) * 100
            close_return = ((next_close - entry_price) / entry_price) * 100
            
            # Define success criteria
            hit_target = high_return >= TARGET_RETURN_PCT  # Long target
            hit_stop = low_return <= -1.0  # 1% stop loss
            
            return {
                'next_high': next_high,
                'next_low': next_low,
                'next_close': next_close,
                'high_return_pct': high_return,
                'low_return_pct': low_return,
                'close_return_pct': close_return,
                'hit_target': 1 if hit_target else 0,
                'hit_stop': 1 if hit_stop else 0,
                'profitable': 1 if close_return > 0 else 0
            }
            
        except Exception as e:
            logger.debug(f"Could not fetch next day data for {symbol}: {e}")
            return None
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for ML model"""
        
        # Feature columns (technical indicators + flags)
        feature_cols = [
            'score_long', 'score_short', 'rsi14', 'atr14', 'vol_ratio',
            'cpr_width_pct', 'macd_value', 'bb_position', 'risk_reward_ratio',
            'ibs', 'twenty_high_break', 'twenty_low_break', 'macd_bullish',
            'macd_bearish', 'narrow_cpr', 'bb_squeeze', 'vol_surge',
            'trend_long', 'trend_short'
        ]
        
        # Convert boolean columns to int
        bool_cols = [
            'twenty_high_break', 'twenty_low_break', 'macd_bullish',
            'macd_bearish', 'narrow_cpr', 'bb_squeeze', 'vol_surge',
            'trend_long', 'trend_short'
        ]
        
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # Fill missing values
        df[feature_cols] = df[feature_cols].fillna(0)
        
        X = df[feature_cols]
        y = df['profitable']  # Target: 1 if next day was profitable, 0 otherwise
        
        self.feature_columns = feature_cols
        
        return X, y
    
    def train_model(self, min_samples: int = MIN_TRAINING_SAMPLES):
        """Train ML model on historical data"""
        logger.info("Training prediction model...")
        
        # Load or collect historical data
        if Path(PERFORMANCE_TRACKING_FILE).exists():
            logger.info(f"Loading existing performance data from {PERFORMANCE_TRACKING_FILE}")
            df = pd.read_csv(PERFORMANCE_TRACKING_FILE)
        else:
            df = self.collect_historical_data()
        
        if len(df) < min_samples:
            logger.warning(f"Insufficient data for training. Need {min_samples}, have {len(df)}")
            logger.info("Run scanner for more days to collect historical performance data")
            return False
        
        self.performance_data = df
        
        # Prepare features
        X, y = self.prepare_features(df)
        
        logger.info(f"Training with {len(X)} samples")
        logger.info(f"Profitable trades: {y.sum()} ({y.mean()*100:.1f}%)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model (Random Forest + Gradient Boosting)
        logger.info("Training Random Forest classifier...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        rf_model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = rf_model.predict(X_test_scaled)
        y_proba = rf_model.predict_proba(X_test_scaled)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model Accuracy: {accuracy*100:.2f}%")
        logger.info("\nClassification Report:")
        logger.info("\n" + classification_report(y_test, y_pred, 
                                                 target_names=['Loss', 'Profit']))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\nTop 10 Important Features:")
        logger.info("\n" + str(feature_importance.head(10)))
        
        # Save model
        self.model = rf_model
        joblib.dump(self.model, MODEL_FILE)
        joblib.dump(self.scaler, SCALER_FILE)
        logger.info(f"Model saved to {MODEL_FILE}")
        
        return True
    
    def load_model(self):
        """Load pre-trained model"""
        if MODEL_FILE.exists() and SCALER_FILE.exists():
            logger.info("Loading pre-trained model...")
            self.model = joblib.load(MODEL_FILE)
            self.scaler = joblib.load(SCALER_FILE)
            
            # Load feature columns from a saved config
            if Path(PERFORMANCE_TRACKING_FILE).exists():
                df = pd.read_csv(PERFORMANCE_TRACKING_FILE, nrows=1)
                self.feature_columns = [
                    'score_long', 'score_short', 'rsi14', 'atr14', 'vol_ratio',
                    'cpr_width_pct', 'macd_value', 'bb_position', 'risk_reward_ratio',
                    'ibs', 'twenty_high_break', 'twenty_low_break', 'macd_bullish',
                    'macd_bearish', 'narrow_cpr', 'bb_squeeze', 'vol_surge',
                    'trend_long', 'trend_short'
                ]
            return True
        else:
            logger.warning("No pre-trained model found. Please train first.")
            return False
    
    def predict_tomorrow(self, signals_file: Optional[str] = None) -> pd.DataFrame:
        """Generate predictions for tomorrow based on today's signals"""
        logger.info("Generating tomorrow's predictions...")
        
        # Load model if not loaded
        if self.model is None:
            if not self.load_model():
                logger.error("Model not available. Train first with: train_model()")
                return pd.DataFrame()
        
        # Find latest signals file if not provided
        if signals_file is None:
            signal_files = sorted(OUTPUT_DIR.glob('all_signals_*.csv'))
            if not signal_files:
                logger.error("No signal files found!")
                return pd.DataFrame()
            signals_file = signal_files[-1]
            logger.info(f"Using latest signals: {signals_file.name}")
        
        # Read signals
        df = pd.read_csv(signals_file)
        
        # Prepare features
        feature_data = df[self.feature_columns].fillna(0)
        
        # Convert boolean columns
        bool_cols = [
            'twenty_high_break', 'twenty_low_break', 'macd_bullish',
            'macd_bearish', 'narrow_cpr', 'bb_squeeze', 'vol_surge',
            'trend_long', 'trend_short'
        ]
        for col in bool_cols:
            if col in feature_data.columns:
                feature_data[col] = feature_data[col].astype(int)
        
        # Scale features
        X_scaled = self.scaler.transform(feature_data)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        # Add predictions to dataframe
        df['prediction'] = predictions
        df['confidence_profit'] = probabilities[:, 1]  # Probability of profit
        df['confidence_loss'] = probabilities[:, 0]    # Probability of loss
        
        # Calculate prediction score (0-100)
        df['prediction_score'] = (df['confidence_profit'] * 100).round(1)
        
        # Add recommendation
        df['recommendation'] = df.apply(
            lambda row: 'STRONG BUY' if row['prediction'] == 1 and row['confidence_profit'] >= 0.75
            else 'BUY' if row['prediction'] == 1 and row['confidence_profit'] >= CONFIDENCE_THRESHOLD
            else 'HOLD' if row['prediction'] == 1
            else 'AVOID',
            axis=1
        )
        
        # Add expected return estimate (rough estimate based on historical avg)
        if self.performance_data is not None:
            avg_return = self.performance_data[
                self.performance_data['profitable'] == 1
            ]['close_return_pct'].mean()
            df['expected_return_pct'] = df['prediction'].apply(
                lambda x: round(avg_return, 2) if x == 1 else 0
            )
        else:
            df['expected_return_pct'] = 0
        
        # Sort by confidence
        df = df.sort_values('prediction_score', ascending=False)
        
        return df
    
    def generate_prediction_report(self, predictions: pd.DataFrame, 
                                   output_file: str = 'tomorrow_predictions.csv'):
        """Generate formatted prediction report"""
        
        if predictions.empty:
            logger.warning("No predictions to report")
            return
        
        # Filter high-confidence predictions
        high_conf = predictions[predictions['confidence_profit'] >= CONFIDENCE_THRESHOLD]
        
        logger.info(f"\n{'='*80}")
        logger.info(f"TOMORROW'S PREDICTIONS - {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"{'='*80}")
        logger.info(f"Total Signals Analyzed: {len(predictions)}")
        logger.info(f"High Confidence Predictions (≥{CONFIDENCE_THRESHOLD*100:.0f}%): {len(high_conf)}")
        logger.info(f"{'='*80}\n")
        
        if len(high_conf) > 0:
            logger.info("🎯 TOP PREDICTIONS FOR TOMORROW:\n")
            
            # Top 10 predictions
            top_picks = high_conf.head(10)
            
            for idx, (_, row) in enumerate(top_picks.iterrows(), 1):
                logger.info(f"{idx}. {row['symbol']} - {row['recommendation']}")
                logger.info(f"   Prediction Score: {row['prediction_score']:.1f}%")
                logger.info(f"   Expected Return: ~{row['expected_return_pct']:.2f}%")
                logger.info(f"   Technical Score: Long={row['score_long']}, Short={row['score_short']}")
                logger.info(f"   RSI: {row['rsi14']:.1f}, IBS: {row['ibs']:.3f}")
                logger.info(f"   Risk Level: {row.get('risk_level', 'N/A')}")
                logger.info("")
        
        # Save predictions
        output_path = OUTPUT_DIR / output_file
        predictions.to_csv(output_path, index=False)
        logger.info(f"Full predictions saved to: {output_path}")
        
        # Also save just the top predictions
        if len(high_conf) > 0:
            top_output = OUTPUT_DIR / f"top_predictions_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
            high_conf.to_csv(top_output, index=False)
            logger.info(f"Top predictions saved to: {top_output}")


def main():
    """Main execution"""
    engine = PredictionEngine()
    
    # Check if model exists
    if not MODEL_FILE.exists():
        logger.info("No model found. Starting training process...")
        logger.info("This will analyze historical scanner data and train ML model.")
        logger.info("Note: This requires historical data from multiple scanner runs.")
        
        success = engine.train_model()
        if not success:
            logger.error("Training failed. Please run scanner for more days to collect data.")
            return
    
    # Generate predictions
    predictions = engine.predict_tomorrow()
    
    if not predictions.empty:
        engine.generate_prediction_report(predictions)
        logger.info("\n✅ Predictions generated successfully!")
        logger.info("Check the eod_scanner_output folder for results.")
    else:
        logger.error("Failed to generate predictions")


if __name__ == "__main__":
    main()
