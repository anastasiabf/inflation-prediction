"""
PHASE 1: SPECIFIC DATA INGESTION ENGINE
Handles web scraping from Bank Indonesia, yfinance integration, and mocked data layers
for a unified monthly temporal index.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BIInflationScraper:
    """
    Scrapes historical inflation data from Bank Indonesia's official statistics portal.
    """
    
    def __init__(self):
        self.url = "https://www.bi.go.id/id/statistik/indikator/data-inflasi.aspx"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_inflation_table(self) -> pd.DataFrame:
        """
        Parse the BI inflation webpage to extract historical monthly inflation data.
        Fallback to synthetic data if scraping fails (production resilience).
        """
        try:
            logger.info(f"Attempting to scrape from {self.url}...")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for tables containing inflation data
            tables = soup.find_all('table')
            inflation_data = []
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            # Try to parse date and inflation value
                            date_str = cells[0].text.strip()
                            inflation_val = cells[1].text.strip()
                            
                            # Attempt parsing
                            if self._is_valid_inflation_row(date_str, inflation_val):
                                inflation_data.append({
                                    'date': date_str,
                                    'inflation': float(inflation_val.replace(',', '.'))
                                })
                        except (ValueError, IndexError):
                            continue
            
            if inflation_data:
                logger.info(f"Successfully scraped {len(inflation_data)} inflation records")
                return self._prepare_dataframe(inflation_data)
            else:
                logger.warning("No inflation data found in table. Using synthetic data.")
                return self._generate_synthetic_inflation()
                
        except Exception as e:
            logger.warning(f"Scraping failed ({str(e)}). Falling back to synthetic data.")
            return self._generate_synthetic_inflation()
    
    def _is_valid_inflation_row(self, date_str: str, value_str: str) -> bool:
        """Validate if row contains valid date and inflation value."""
        try:
            float(value_str.replace(',', '.'))
            # Check if date string contains month/year patterns
            return any(month in date_str.lower() for month in 
                      ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
                       'juli', 'agustus', 'september', 'oktober', 'november', 'desember',
                       'january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december'])
        except:
            return False
    
    def _prepare_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Convert scraped data to standardized DataFrame."""
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.sort_values('date').drop_duplicates(subset=['date'])
        df.set_index('date', inplace=True)
        return df
    
    def _generate_synthetic_inflation(self) -> pd.DataFrame:
        """Generate realistic synthetic inflation data (36 months)."""
        logger.info("Generating synthetic inflation data")
        dates = pd.date_range(end=datetime.now(), periods=36, freq='MS')
        # Realistic Indonesian inflation patterns: 2.5-5.5% range
        inflation_rates = np.random.normal(loc=3.8, scale=0.8, size=len(dates))
        inflation_rates = np.clip(inflation_rates, 1.5, 6.5)
        
        return pd.DataFrame({
            'inflation': inflation_rates
        }, index=pd.DatetimeIndex(dates, name='date'))


class ExchangeRateCollector:
    """Integrates Yahoo Finance to pull USD/IDR historical data."""
    
    @staticmethod
    def fetch_monthly_usd_idr(months: int = 36) -> pd.DataFrame:
        """
        Fetch USD/IDR exchange rates and aggregate to monthly means.
        
        Args:
            months: Number of months of historical data
            
        Returns:
            DataFrame with monthly mean exchange rates
        """
        try:
            logger.info("Fetching USD/IDR exchange rates from Yahoo Finance...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Fetch daily data
            data = yf.download('USDIDX=X', start=start_date, end=end_date, progress=False)
            
            if data.empty:
                # Fallback to EURJPY or synthetic
                logger.warning("USD/IDR not available. Using synthetic data.")
                return ExchangeRateCollector._generate_synthetic_exchange_rates(months)
            
            # Resample to monthly mean of closing prices
            monthly_data = data['Close'].resample('MS').mean()
            return pd.DataFrame({
                'exchange_rate_usd_idr': monthly_data
            })
            
        except Exception as e:
            logger.warning(f"Yahoo Finance fetch failed ({str(e)}). Using synthetic data.")
            return ExchangeRateCollector._generate_synthetic_exchange_rates(months)
    
    @staticmethod
    def _generate_synthetic_exchange_rates(months: int) -> pd.DataFrame:
        """Generate realistic IDR exchange rates (Rp 15.000 - Rp 16.500)."""
        dates = pd.date_range(end=datetime.now(), periods=months, freq='MS')
        # Realistic IDR rates around 15.500 with some volatility
        rates = np.random.normal(loc=15500, scale=300, size=len(dates))
        rates = np.clip(rates, 14500, 17000)
        
        return pd.DataFrame({
            'exchange_rate_usd_idr': rates
        }, index=pd.DatetimeIndex(dates, name='date'))


class MacroeconomicDataCollector:
    """
    Collects BI Rate, IHK, news text, and social media text using open/mocked sources.
    All data is aligned to monthly cadence.
    """
    
    @staticmethod
    def fetch_bi_rate(months: int = 36) -> pd.DataFrame:
        """
        Fetch or mock BI Rate data (Policy Rate).
        Current BI Rate typically 5-7.5%.
        """
        logger.info("Generating BI Rate data")
        dates = pd.date_range(end=datetime.now(), periods=months, freq='MS')
        # Realistic BI policy rates (5.0% - 7.5%)
        rates = np.random.normal(loc=6.0, scale=0.5, size=len(dates))
        rates = np.clip(rates, 4.5, 8.0)
        
        return pd.DataFrame({
            'bi_rate': rates
        }, index=pd.DatetimeIndex(dates, name='date'))
    
    @staticmethod
    def fetch_ihk_index(months: int = 36) -> pd.DataFrame:
        """
        Fetch or mock Consumer Price Index (IHK).
        IHK typically ranges 100-120 with upward trends.
        """
        logger.info("Generating IHK (Consumer Price Index) data")
        dates = pd.date_range(end=datetime.now(), periods=months, freq='MS')
        # IHK base=100, upward trending
        base_ihk = 110
        trend = np.linspace(0, 5, len(dates))
        noise = np.random.normal(0, 1, len(dates))
        ihk_values = base_ihk + trend + noise
        
        return pd.DataFrame({
            'ihk_index': ihk_values
        }, index=pd.DatetimeIndex(dates, name='date'))
    
    @staticmethod
    def generate_news_text_batches(months: int = 36) -> pd.DataFrame:
        """
        Generate realistic news text snippets batched by month.
        In production, these would be scraped from CNN Indonesia, Detik, Kontan, etc.
        """
        logger.info("Generating monthly news text batches")
        dates = pd.date_range(end=datetime.now(), periods=months, freq='MS')
        
        news_templates = [
            "Bank Indonesia maintains policy rate at {}% amid inflation concerns.",
            "Rupiah weakens to {} IDR/USD as global uncertainty persists.",
            "Consumer spending rises {} points, boosting economic growth outlook.",
            "Food prices surge amid supply chain disruptions.",
            "Government announces new subsidy programs to stabilize prices.",
            "Inflation expectations remain elevated according to latest survey.",
            "BI Deputy Governor signals potential rate adjustment next month.",
            "Trade deficit widens to $1.2B, pressuring rupiah valuation.",
            "Worker wages increase {} percent effective next month.",
            "Central bank holds rates steady, signaling data-dependent approach."
        ]
        
        news_data = []
        for date in dates:
            # 3-5 news snippets per month
            num_snippets = np.random.randint(3, 6)
            snippets = [np.random.choice(news_templates) for _ in range(num_snippets)]
            combined_text = " ".join(snippets)
            
            news_data.append({
                'date': date,
                'news_text': combined_text
            })
        
        df = pd.DataFrame(news_data)
        df.set_index('date', inplace=True)
        return df
    
    @staticmethod
    def generate_social_media_text_batches(months: int = 36) -> pd.DataFrame:
        """
        Generate realistic social media text (Twitter/X-like snippets).
        In production, scraped from Twitter API, Reddit, local forums.
        """
        logger.info("Generating monthly social media text batches")
        dates = pd.date_range(end=datetime.now(), periods=months, freq='MS')
        
        social_templates = [
            "Harga minyak goreng naik lagi! Kapan turun? #inflation #mahal",
            "Gaji tidak kunjung naik tapi harga semua membumbung #ekonomi",
            "Bank Indonesia harus potong suku bunga untuk selamatkan UMKM!",
            "Rupiah melemah lagi hari ini. Resesi sudah di depan mata.",
            "Beras mahal, telur mahal, bensin mahal. Negara bagaimana?",
            "Pemerintah harus berani turun harga kebutuhan pokok.",
            "Harapan ekonomi membaik dengan proyek infrastruktur baru.",
            "Pasar saham naik konsisten, sinyal pemulihan ekonomi kuat.",
            "Investasi asing masuk terus, kepercayaan pada ekonomi RI bagus.",
            "Pengangguran masih tinggi meski GDP tumbuh. Unemployment trap?"
        ]
        
        social_data = []
        for date in dates:
            # 5-10 social media posts per month
            num_posts = np.random.randint(5, 11)
            posts = [np.random.choice(social_templates) for _ in range(num_posts)]
            combined_text = " | ".join(posts)
            
            social_data.append({
                'date': date,
                'social_media_text': combined_text
            })
        
        df = pd.DataFrame(social_data)
        df.set_index('date', inplace=True)
        return df


class DataPipeline:
    """
    Orchestrates all data collection and merges into unified monthly dataset.
    """
    
    def __init__(self, months: int = 36):
        self.months = months
        self.inflation_scraper = BIInflationScraper()
        self.exchange_collector = ExchangeRateCollector()
        self.macro_collector = MacroeconomicDataCollector()
    
    def build_unified_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Build complete unified dataset with aligned monthly index.

        Returns:
            - unified_df: Complete feature matrix
            - news_df: News text batches
            - social_df: Social media text batches
        """
        logger.info("=" * 60)
        logger.info("BUILDING UNIFIED MONTHLY DATASET")
        logger.info("=" * 60)

        # Collect all data sources
        inflation_df = self.inflation_scraper.scrape_inflation_table()
        exchange_df = self.exchange_collector.fetch_monthly_usd_idr(self.months)
        bi_rate_df = self.macro_collector.fetch_bi_rate(self.months)
        ihk_df = self.macro_collector.fetch_ihk_index(self.months)
        news_df = self.macro_collector.generate_news_text_batches(self.months)
        social_df = self.macro_collector.generate_social_media_text_batches(self.months)

        # Normalize all indices to month-start (avoids time-component mismatches
        # when each collector generates dates independently)
        def normalize_index(df):
            df = df.copy()
            df.index = df.index.normalize()  # strip time component
            df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d'))  # ensure consistent
            df = df[~df.index.duplicated(keep='first')]  # remove any duplicate months
            return df

        inflation_df = normalize_index(inflation_df)
        exchange_df = normalize_index(exchange_df)
        bi_rate_df = normalize_index(bi_rate_df)
        ihk_df = normalize_index(ihk_df)
        news_df = normalize_index(news_df)
        social_df = normalize_index(social_df)

        # Align all to monthly cadence using inner join (only months with all data)
        unified_df = pd.concat([
            inflation_df.rename(columns={'inflation': 'inflation_rate'}),
            exchange_df,
            bi_rate_df,
            ihk_df,
            news_df,
            social_df
        ], axis=1, join='inner')

        # Drop any remaining duplicate index entries
        unified_df = unified_df[~unified_df.index.duplicated(keep='first')]

        # Sort by date
        unified_df = unified_df.sort_index()

        logger.info(f"Unified dataset shape: {unified_df.shape}")
        logger.info(f"Date range: {unified_df.index.min()} to {unified_df.index.max()}")
        logger.info(f"Columns: {list(unified_df.columns)}")
        logger.info(f"Unique months: {len(unified_df)}")

        return unified_df, news_df, social_df
    
    def export_to_json(self, df: pd.DataFrame, output_path: str):
        """Export dataset to JSON for downstream processing."""
        df_reset = df.reset_index()
        df_reset['date'] = df_reset['date'].astype(str)
        
        with open(output_path, 'w') as f:
            json.dump(df_reset.to_dict('records'), f, indent=2)
        
        logger.info(f"Exported data to {output_path}")


if __name__ == "__main__":
    pipeline = DataPipeline(months=36)
    unified_df, news_df, social_df = pipeline.build_unified_dataset()
    
    # Export for inspection
    unified_df.to_csv('/tmp/inflation_unified_data.csv')
    pipeline.export_to_json(unified_df, '/tmp/inflation_unified_data.json')
    
    print("\nSample of unified dataset:")
    print(unified_df.head())
    print(f"\nDataset Info:\n{unified_df.info()}")
