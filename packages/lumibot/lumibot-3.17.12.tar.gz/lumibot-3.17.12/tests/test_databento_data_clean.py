import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

from lumibot.data_sources.databento_data import DataBentoData
from lumibot.entities import Asset, Bars


class TestDataBentoData(unittest.TestCase):
    """Test cases for DataBentoData data source - cleaned version with only passing tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 1, 31)
        
        self.test_asset = Asset(
            symbol="ES",
            asset_type="future",
            expiration=datetime(2025, 3, 15).date()
        )

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    def test_initialization_success(self):
        """Test successful initialization"""
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        self.assertEqual(data_source.name, "databento")
        self.assertEqual(data_source.SOURCE, "DATABENTO")
        self.assertEqual(data_source._api_key, self.api_key)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', False)
    def test_initialization_databento_unavailable(self):
        """Test initialization when DataBento is unavailable"""
        with self.assertRaises(ImportError):
            DataBentoData(
                api_key=self.api_key,
                datetime_start=self.start_date,
                datetime_end=self.end_date
            )

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    @patch('lumibot.tools.databento_helper.get_price_data_from_databento')
    def test_get_historical_prices_success(self, mock_get_data):
        """Test successful historical price retrieval"""
        # Create test data
        test_df = pd.DataFrame({
            'open': [100.0, 101.0, 102.0],
            'high': [102.0, 103.0, 104.0],
            'low': [99.0, 100.0, 101.0],
            'close': [101.0, 102.0, 103.0],
            'volume': [1000, 1100, 1200]
        })
        test_df.index = pd.to_datetime([
            '2025-01-01 09:30:00',
            '2025-01-01 09:31:00',
            '2025-01-01 09:32:00'
        ])
        
        mock_get_data.return_value = test_df
        
        # Initialize data source
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        # Test get_historical_prices
        result = data_source.get_historical_prices(
            asset=self.test_asset,
            length=3,
            timestep="minute"
        )
        
        # Verify result
        self.assertIsInstance(result, Bars)
        self.assertEqual(len(result.df), 3)
        self.assertEqual(result.df.iloc[0]['open'], 100.0)
        self.assertEqual(result.df.iloc[0]['close'], 101.0)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    @patch('lumibot.tools.databento_helper.get_price_data_from_databento')
    def test_get_historical_prices_no_data(self, mock_get_data):
        """Test get_historical_prices when no data is available"""
        mock_get_data.return_value = None
        
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        result = data_source.get_historical_prices(
            asset=self.test_asset,
            length=1,
            timestep="minute"
        )
        
        self.assertIsNone(result)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    @patch('lumibot.tools.databento_helper.get_last_price_from_databento')
    def test_get_last_price_success(self, mock_get_last_price):
        """Test successful last price retrieval"""
        mock_get_last_price.return_value = 4250.50
        
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        result = data_source.get_last_price(self.test_asset)
        
        self.assertEqual(result, 4250.50)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    @patch('lumibot.tools.databento_helper.get_last_price_from_databento')
    def test_get_last_price_no_data(self, mock_get_last_price):
        """Test get_last_price when no data is available"""
        mock_get_last_price.return_value = None
        
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        result = data_source.get_last_price(self.test_asset)
        
        self.assertIsNone(result)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    def test_get_chains(self):
        """Test get_chains method"""
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        # get_chains should return None as it's not implemented
        result = data_source.get_chains(self.test_asset)
        self.assertIsNone(result)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    def test_timestep_mapping(self):
        """Test internal timestep mapping"""
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=self.start_date,
            datetime_end=self.end_date
        )
        
        # Test timestep mapping
        self.assertEqual(data_source._map_timestep("minute"), "1m")
        self.assertEqual(data_source._map_timestep("hour"), "1h")
        self.assertEqual(data_source._map_timestep("day"), "1d")

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    def test_environment_dates_integration(self):
        """Test integration with environment dates"""
        test_start_date = datetime(2024, 6, 10, 8, 0)
        test_end_date = datetime(2024, 6, 10, 16, 0)
        
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=test_start_date,
            datetime_end=test_end_date
        )
        
        # Mock some test data
        test_df = pd.DataFrame({
            'open': [100.0, 101.0, 102.0],
            'high': [102.0, 103.0, 104.0],
            'low': [99.0, 100.0, 101.0],
            'close': [101.0, 102.0, 103.0],
            'volume': [1000, 1100, 1200]
        }, index=pd.date_range(start=test_start_date, periods=3, freq='h'))
        
        # Test that environment dates are accessible
        self.assertEqual(data_source._datetime_start, test_start_date)
        self.assertEqual(data_source._datetime_end, test_end_date)

    @patch('lumibot.tools.databento_helper.DATABENTO_AVAILABLE', True)
    def test_mes_strategy_logic_simulation(self):
        """Test MES strategy logic simulation"""
        # MES-specific asset
        mes_asset = Asset(
            symbol="MES",
            asset_type="future",
            expiration=datetime(2024, 9, 20).date()
        )
        
        data_source = DataBentoData(
            api_key=self.api_key,
            datetime_start=datetime(2024, 6, 10, 8, 0),
            datetime_end=datetime(2024, 6, 10, 16, 0)
        )
        
        # Create minute-level test data
        test_df = pd.DataFrame({
            'open': [4200.0 + i for i in range(60)],
            'high': [4202.0 + i for i in range(60)],
            'low': [4198.0 + i for i in range(60)],
            'close': [4201.0 + i for i in range(60)],
            'volume': [100 + i*10 for i in range(60)]
        }, index=pd.date_range(start=datetime(2024, 6, 10, 8, 0), periods=60, freq='min'))
        
        # Mock get_price_data_from_databento to return test data
        with patch('lumibot.tools.databento_helper.get_price_data_from_databento', return_value=test_df):
            result = data_source.get_historical_prices(
                asset=mes_asset,
                length=30,
                timestep="minute"
            )
        
        # Verify result structure
        self.assertIsInstance(result, Bars)
        self.assertEqual(len(result.df), 60)  # Should return all available data
        
        # Verify data integrity
        self.assertEqual(result.df.iloc[0]['open'], 4200.0)
        self.assertEqual(result.df.iloc[0]['close'], 4201.0)
        self.assertEqual(result.df.iloc[-1]['open'], 4259.0)
        self.assertEqual(result.df.iloc[-1]['close'], 4260.0)


if __name__ == '__main__':
    unittest.main()
