import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average with proper error handling"""
    try:
        if period <= 0:
            raise ValueError("Period must be positive")
        if len(data) < period:
            raise ValueError(f"Data length ({len(data)}) must be >= period ({period})")
        
        # Use min_periods=1 for more flexibility, but proper SMA starts at min_periods=period
        result = data.rolling(window=period, min_periods=1).mean()
        return pd.Series(result)
    except Exception as e:
        raise ValueError(f"SMA calculation failed: {str(e)}")


def calculate_ema(data: pd.Series, period: int, alpha: Optional[float] = None) -> pd.Series:
    """Calculate Exponential Moving Average with proper error handling"""
    try:
        if period <= 0:
            raise ValueError("Period must be positive")
        if alpha is None:
            alpha = 2.0 / (period + 1)
        if not 0 < alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")
            
        result = data.ewm(alpha=alpha, adjust=False, min_periods=1).mean()
        return pd.Series(result)
    except Exception as e:
        raise ValueError(f"EMA calculation failed: {str(e)}")


def calculate_dma(data: pd.Series, period: int) -> pd.Series:
    """Calculate Double Moving Average (EMA of EMA) with proper error handling"""
    try:
        ema1 = calculate_ema(data, period)
        return calculate_ema(ema1, period)
    except Exception as e:
        raise ValueError(f"DMA calculation failed: {str(e)}")


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index with proper error handling"""
    try:
        if period <= 0:
            raise ValueError("RSI period must be positive")
        if len(data) < period + 1:
            raise ValueError(f"Data length ({len(data)}) must be > period ({period}) for RSI calculation")
        
        # Calculate price changes
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate rolling averages
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        
        # Handle division by zero cases
        rs = np.where(avg_loss == 0, np.inf, avg_gain / avg_loss)
        rsi = 100 - (100 / (1 + rs))
        
        # Handle edge cases
        rsi = np.where(np.isinf(rs), 100, rsi)
        rsi = np.where((avg_gain == 0) & (avg_loss > 0), 0, rsi)
        
        return pd.Series(rsi, index=data.index)
        
    except Exception as e:
        raise ValueError(f"RSI calculation failed: {str(e)}")


def calculate_macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        # Validation
        if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
            raise ValueError("All MACD periods must be positive")
        if fast_period >= slow_period:
            raise ValueError(f"Fast period ({fast_period}) must be less than slow period ({slow_period})")
        if len(data) < slow_period:
            raise ValueError(f"Data length ({len(data)}) must be >= slow period ({slow_period})")
        
        # Calculate EMAs
        ema_fast = calculate_ema(data, fast_period)
        ema_slow = calculate_ema(data, slow_period)
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = calculate_ema(macd_line, signal_period)
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
        
    except Exception as e:
        raise ValueError(f"MACD calculation failed: {str(e)}")


def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
    """Calculate Bollinger Bands"""
    try:
        # Validation
        if period <= 0:
            raise ValueError("Bollinger Bands period must be positive")
        if std_dev <= 0:
            raise ValueError("Standard deviation multiplier must be positive")
        if len(data) < period:
            raise ValueError(f"Data length ({len(data)}) must be >= period ({period})")
        
        # Calculate middle line (SMA)
        sma = calculate_sma(data, period)
        
        # Calculate standard deviation
        std = data.rolling(window=period, min_periods=1).std()
        
        # Calculate bands
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
        
    except Exception as e:
        raise ValueError(f"Bollinger Bands calculation failed: {str(e)}")


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Dict[str, pd.Series]:
    """Calculate SuperTrend indicator"""
    try:
        if len(df) < period:
            raise ValueError(f"Insufficient data: need at least {period} candles, got {len(df)}")
        
        high = df['high'].copy()
        low = df['low'].copy()
        close = df['close'].copy()
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = tr.rolling(window=period, min_periods=1).mean()
        
        # Calculate basic upper and lower bands
        hl2 = (high + low) / 2
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        # Initialize final bands and SuperTrend series
        final_upper_band = pd.Series(index=df.index, dtype=float)
        final_lower_band = pd.Series(index=df.index, dtype=float)
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        
        # Calculate SuperTrend values
        for i in range(len(df)):
            if i < period:
                final_upper_band.iloc[i] = np.nan
                final_lower_band.iloc[i] = np.nan
                supertrend.iloc[i] = np.nan
                direction.iloc[i] = np.nan
            elif i == period:
                final_upper_band.iloc[i] = upper_band.iloc[i]
                final_lower_band.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
                supertrend.iloc[i] = final_lower_band.iloc[i]
            else:
                # Final upper band
                if pd.notna(upper_band.iloc[i]) and pd.notna(final_upper_band.iloc[i-1]):
                    final_upper_band.iloc[i] = (upper_band.iloc[i] 
                                               if (upper_band.iloc[i] < final_upper_band.iloc[i-1]) 
                                               or (close.iloc[i-1] > final_upper_band.iloc[i-1]) 
                                               else final_upper_band.iloc[i-1])
                else:
                    final_upper_band.iloc[i] = upper_band.iloc[i]
                
                # Final lower band
                if pd.notna(lower_band.iloc[i]) and pd.notna(final_lower_band.iloc[i-1]):
                    final_lower_band.iloc[i] = (lower_band.iloc[i] 
                                               if (lower_band.iloc[i] > final_lower_band.iloc[i-1]) 
                                               or (close.iloc[i-1] < final_lower_band.iloc[i-1]) 
                                               else final_lower_band.iloc[i-1])
                else:
                    final_lower_band.iloc[i] = lower_band.iloc[i]
                
                # SuperTrend and direction calculation
                if pd.notna(supertrend.iloc[i-1]) and pd.notna(final_upper_band.iloc[i]) and pd.notna(final_lower_band.iloc[i]):
                    if (supertrend.iloc[i-1] == final_upper_band.iloc[i-1] and 
                        close.iloc[i] <= final_upper_band.iloc[i]):
                        direction.iloc[i] = -1
                        supertrend.iloc[i] = final_upper_band.iloc[i]
                    elif (supertrend.iloc[i-1] == final_upper_band.iloc[i-1] and 
                          close.iloc[i] > final_upper_band.iloc[i]):
                        direction.iloc[i] = 1
                        supertrend.iloc[i] = final_lower_band.iloc[i]
                    elif (supertrend.iloc[i-1] == final_lower_band.iloc[i-1] and 
                          close.iloc[i] >= final_lower_band.iloc[i]):
                        direction.iloc[i] = 1
                        supertrend.iloc[i] = final_lower_band.iloc[i]
                    elif (supertrend.iloc[i-1] == final_lower_band.iloc[i-1] and 
                          close.iloc[i] < final_lower_band.iloc[i]):
                        direction.iloc[i] = -1
                        supertrend.iloc[i] = final_upper_band.iloc[i]
                    else:
                        direction.iloc[i] = direction.iloc[i-1]
                        supertrend.iloc[i] = supertrend.iloc[i-1]
                else:
                    direction.iloc[i] = 1
                    supertrend.iloc[i] = final_lower_band.iloc[i]
        
        return {
            'supertrend': supertrend,
            'direction': direction,
            'upper_band': final_upper_band,
            'lower_band': final_lower_band
        }
        
    except Exception as e:
        raise ValueError(f"SuperTrend calculation failed: {str(e)}")


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Calculate Volume Weighted Average Price"""
    try:
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        volume_price = typical_price * df['volume']
        cumulative_volume_price = volume_price.cumsum()
        cumulative_volume = df['volume'].cumsum()
        
        vwap = cumulative_volume_price / cumulative_volume
        return vwap
    except Exception as e:
        raise ValueError(f"VWAP calculation failed: {str(e)}")


def find_pivot_points(df: pd.DataFrame, window: int = 5) -> Dict[str, list]:
    """Find pivot highs and lows for support/resistance"""
    try:
        highs = df['high']
        lows = df['low']
        
        pivot_highs = []
        pivot_lows = []
        
        for i in range(window, len(df) - window):
            # Check for pivot high
            if all(highs.iloc[i] >= highs.iloc[i-j] for j in range(1, window+1)) and \
               all(highs.iloc[i] >= highs.iloc[i+j] for j in range(1, window+1)):
                pivot_highs.append({
                    'index': i,
                    'timestamp': df.iloc[i]['timestamp'],
                    'price': highs.iloc[i],
                    'type': 'resistance'
                })
            
            # Check for pivot low
            if all(lows.iloc[i] <= lows.iloc[i-j] for j in range(1, window+1)) and \
               all(lows.iloc[i] <= lows.iloc[i+j] for j in range(1, window+1)):
                pivot_lows.append({
                    'index': i,
                    'timestamp': df.iloc[i]['timestamp'],
                    'price': lows.iloc[i],
                    'type': 'support'
                })
        
        return {
            'pivot_highs': pivot_highs,
            'pivot_lows': pivot_lows
        }
    except Exception as e:
        raise ValueError(f"Pivot points calculation failed: {str(e)}")


def calculate_pivot_points_standard(high: float, low: float, close: float) -> Dict[str, float]:
    """Calculate standard pivot points"""
    try:
        pivot = (high + low + close) / 3
        
        return {
            'pivot': pivot,
            'r1': 2 * pivot - low,
            'r2': pivot + (high - low),
            'r3': high + 2 * (pivot - low),
            's1': 2 * pivot - high,
            's2': pivot - (high - low),
            's3': low - 2 * (high - pivot)
        }
    except Exception as e:
        raise ValueError(f"Standard pivot points calculation failed: {str(e)}")


def calculate_pivot_points_fibonacci(high: float, low: float, close: float) -> Dict[str, float]:
    """Calculate Fibonacci pivot points"""
    try:
        pivot = (high + low + close) / 3
        range_val = high - low
        
        return {
            'pivot': pivot,
            'r1': pivot + 0.382 * range_val,
            'r2': pivot + 0.618 * range_val,
            'r3': pivot + range_val,
            's1': pivot - 0.382 * range_val,
            's2': pivot - 0.618 * range_val,
            's3': pivot - range_val
        }
    except Exception as e:
        raise ValueError(f"Fibonacci pivot points calculation failed: {str(e)}")


def calculate_pivot_points_camarilla(high: float, low: float, close: float) -> Dict[str, float]:
    """Calculate Camarilla pivot points"""
    try:
        range_val = high - low
        
        return {
            'r1': close + (range_val * 1.1 / 12),
            'r2': close + (range_val * 1.1 / 6),
            'r3': close + (range_val * 1.1 / 4),
            'r4': close + (range_val * 1.1 / 2),
            's1': close - (range_val * 1.1 / 12),
            's2': close - (range_val * 1.1 / 6),
            's3': close - (range_val * 1.1 / 4),
            's4': close - (range_val * 1.1 / 2)
        }
    except Exception as e:
        raise ValueError(f"Camarilla pivot points calculation failed: {str(e)}")


def add_rsi_signals(df: pd.DataFrame, rsi_col: str = 'rsi') -> pd.DataFrame:
    """Add RSI signals to dataframe"""
    df[f'{rsi_col}_signal'] = df[rsi_col].apply(
        lambda x: "overbought" if x > 70 else ("oversold" if x < 30 else "neutral")
    )
    return df


def add_macd_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Add MACD signals to dataframe"""
    df["macd_crossover"] = ((df["macd"] > df["macd_signal"]) & 
                           (df["macd"].shift(1) <= df["macd_signal"].shift(1))).astype(int)
    df["macd_crossunder"] = ((df["macd"] < df["macd_signal"]) & 
                            (df["macd"].shift(1) >= df["macd_signal"].shift(1))).astype(int)
    return df


def add_bollinger_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Add Bollinger Bands signals to dataframe"""
    df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
    df["bb_squeeze"] = ((df["bb_upper"] - df["bb_lower"]) / df["bb_middle"] < 0.1).astype(int)
    return df


def add_supertrend_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Add SuperTrend signals to dataframe"""
    df["trend_signal"] = df["st_direction"].apply(
        lambda x: "bullish" if x == 1 else ("bearish" if x == -1 else "unknown")
    )
    return df


def add_vwap_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Add VWAP signals to dataframe"""
    df["vwap_signal"] = (df["close"] > df["vwap"]).apply(
        lambda x: "above_vwap" if x else "below_vwap"
    )
    return df 