import os
import time
from typing import Optional, Dict, List, Annotated, Literal, Union, cast, Sequence
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ..helper import groww_login
from ..indicator_helper import (
    calculate_sma,
    calculate_ema,
    calculate_dma,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_supertrend,
    calculate_vwap,
    find_pivot_points,
    calculate_pivot_points_standard,
    calculate_pivot_points_fibonacci,
    calculate_pivot_points_camarilla,
    add_rsi_signals,
    add_macd_signals,
    add_bollinger_signals,
    add_supertrend_signals,
    add_vwap_signals,
)
import pandas as pd

groww = groww_login()

mcp = FastMCP(
    name="Groww Technical Indicators MCP Server",
    instructions="A Groww MCP Server for calculating comprehensive technical indicators on market data",
)


def get_time_range(period_value: int, period_unit: str) -> tuple[str, str]:
    """Calculate start and end time based on period"""
    end_time = datetime.now()
    
    if period_unit == "days":
        start_time = end_time - timedelta(days=period_value)
    elif period_unit == "weeks":
        start_time = end_time - timedelta(weeks=period_value)
    elif period_unit == "months":
        start_time = end_time - timedelta(days=period_value * 30)  # Approximate
    elif period_unit == "hours":
        start_time = end_time - timedelta(hours=period_value)
    else:
        raise ValueError(f"Invalid period_unit: {period_unit}")
    
    return start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S")


def get_appropriate_interval(period_value: int, period_unit: str) -> int:
    """Get appropriate interval based on time period"""
    if period_unit == "hours":
        return 5 if period_value < 24 else 60  # Fixed: 24 hours should use 60-minute intervals
    elif period_unit == "days":
        if period_value <= 1:
            return 5
        elif period_value <= 7:
            return 60
        elif period_value <= 30:
            return 1440
        else:
            return 1440
    elif period_unit == "weeks":
        return 1440 if period_value <= 12 else 10080
    elif period_unit == "months":
        return 1440 if period_value <= 6 else 10080
    else:
        return 1440





def calculate_indicators(df: pd.DataFrame, indicators: Sequence[str], params: Dict) -> pd.DataFrame:
    """Calculate specified technical indicators"""
    # Check if this is index data (volume is null for all rows)
    is_index_data = df["volume"].isna().sum() == len(df)
    
    for indicator in indicators:
        try:
            if indicator == "sma":
                df["sma"] = calculate_sma(cast(pd.Series, df["close"]), params.get("sma_period", 20))
            
            elif indicator == "ema":
                df["ema"] = calculate_ema(cast(pd.Series, df["close"]), params.get("ema_period", 20))
            
            elif indicator == "dma":
                df["dma"] = calculate_dma(cast(pd.Series, df["close"]), params.get("dma_period", 20))
            
            elif indicator == "rsi":
                df["rsi"] = calculate_rsi(cast(pd.Series, df["close"]), params.get("rsi_period", 14))
                df = add_rsi_signals(df)
            
            elif indicator == "macd":
                macd_data = calculate_macd(
                    cast(pd.Series, df["close"]), 
                    params.get("macd_fast", 12), 
                    params.get("macd_slow", 26), 
                    params.get("macd_signal", 9)
                )
                df["macd"] = macd_data["macd"]
                df["macd_signal"] = macd_data["signal"]
                df["macd_histogram"] = macd_data["histogram"]
                df = add_macd_signals(df)
            
            elif indicator == "bollinger":
                bb_data = calculate_bollinger_bands(
                    cast(pd.Series, df["close"]), 
                    params.get("bb_period", 20), 
                    params.get("bb_std", 2.0)
                )
                df["bb_upper"] = bb_data["upper"]
                df["bb_middle"] = bb_data["middle"]
                df["bb_lower"] = bb_data["lower"]
                df = add_bollinger_signals(df)
            
            elif indicator == "supertrend":
                st_data = calculate_supertrend(
                    df, 
                    params.get("st_period", 10), 
                    params.get("st_multiplier", 3.0)
                )
                df["supertrend"] = st_data["supertrend"]
                df["st_direction"] = st_data["direction"]
                df["st_upper_band"] = st_data["upper_band"]
                df["st_lower_band"] = st_data["lower_band"]
                df = add_supertrend_signals(df)
            
            elif indicator == "vwap":
                if is_index_data:
                    print(f"Warning: VWAP calculation skipped for index data (volume is null)")
                    df["vwap"] = None
                else:
                    df["vwap"] = calculate_vwap(df)
                    df = add_vwap_signals(df)
            
            elif indicator == "pivot_points":
                pivot_data = find_pivot_points(df, params.get("pivot_window", 5))
                df.attrs["pivot_points"] = pivot_data
        
        except Exception as e:
            # Log error but continue with other indicators
            print(f"Error calculating {indicator}: {str(e)}")
    
    return df


@mcp.tool()
def calculate_technical_indicators(
    trading_symbol: Annotated[
        str,
        Field(
            description="Trading Symbol of the instrument (e.g., 'RELIANCE', 'NIFTY')"
        ),
    ],
    period_value: Annotated[
        int,
        Field(
            description="Number of time periods to analyze (e.g., 30 for 30 days, 12 for 12 weeks)"
        ),
    ],
    period_unit: Annotated[
        Literal["hours", "days", "weeks", "months"],
        Field(
            description="Time unit for the period (hours, days, weeks, months)"
        ),
    ] = "days",
    indicators: Annotated[
        List[Literal["sma", "ema", "dma", "rsi", "macd", "bollinger", "supertrend", "vwap", "pivot_points"]],
        Field(
            description="List of technical indicators to calculate"
        ),
    ] = ["sma", "ema", "rsi"],
    # SMA/EMA Parameters
    sma_period: Annotated[int, Field(description="SMA period")] = 20,
    ema_period: Annotated[int, Field(description="EMA period")] = 20,
    dma_period: Annotated[int, Field(description="DMA period")] = 20,
    # RSI Parameters
    rsi_period: Annotated[int, Field(description="RSI period")] = 14,
    # MACD Parameters
    macd_fast: Annotated[int, Field(description="MACD fast period")] = 12,
    macd_slow: Annotated[int, Field(description="MACD slow period")] = 26,
    macd_signal: Annotated[int, Field(description="MACD signal period")] = 9,
    # Bollinger Bands Parameters
    bb_period: Annotated[int, Field(description="Bollinger Bands period")] = 20,
    bb_std: Annotated[float, Field(description="Bollinger Bands std deviation")] = 2.0,
    # SuperTrend Parameters
    st_period: Annotated[int, Field(description="SuperTrend ATR period")] = 10,
    st_multiplier: Annotated[float, Field(description="SuperTrend multiplier")] = 3.0,
    # Pivot Points Parameters
    pivot_window: Annotated[int, Field(description="Pivot points window")] = 5,
    # Trading Parameters
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
    interval_override: Annotated[
        Optional[int],
        Field(description="Override automatic interval selection (minutes)")
    ] = None,
) -> dict:
    """
    Calculate multiple technical indicators for historical data over a specified time period.
    
    This tool automatically selects appropriate time intervals based on the period requested
    and calculates the specified technical indicators.

    Use this tool when the user asks about:
    - "Calculate RSI and MACD for RELIANCE over last 30 days"
    - "Show me moving averages for NIFTY for past 3 months"
    - "Get technical indicators for TCS last week"
    - "Calculate all indicators for HDFC for 2 weeks"
    - "Show me SuperTrend and Bollinger Bands for last month"
    - "Get pivot points for RELIANCE daily data"
    - "Calculate VWAP for intraday analysis"
    - "Show me RSI signals for past 60 days"
    - "Get MACD crossover signals for last 3 weeks"
    - "Calculate technical analysis for portfolio stocks"

    Available Indicators:
    - sma: Simple Moving Average
    - ema: Exponential Moving Average  
    - dma: Double Moving Average
    - rsi: Relative Strength Index (with overbought/oversold signals)
    - macd: MACD with signal line and histogram
    - bollinger: Bollinger Bands with squeeze detection
    - supertrend: SuperTrend with trend direction
    - vwap: Volume Weighted Average Price
    - pivot_points: Support/Resistance levels

    Time Period Examples:
    - 24 hours: Recent intraday data
    - 7 days: Weekly analysis
    - 30 days: Monthly trend analysis
    - 12 weeks: Quarterly analysis
    - 6 months: Medium-term analysis

    limitations in time-range and interval:
    | Candle Interval | Max Duration per Request | Historical Data Available |
    | :--- | :--- | :--- |
    | **1 min** | 7 days | Last 3 months |
    | **5 min** | 15 days | Last 3 months |
    | **10 min** | 30 days | Last 3 months |
    | **1 hour (60 min)** | 150 days | Last 3 months |
    | **4 hours (240 min)**| 365 days | Last 3 months |
    | **1 day (1440 min)** | 1080 days (~3 years) | Full history |
    | **1 week (10080 min)**| No Limit | Full history |
    """
    try:
        # Validate inputs
        if not trading_symbol or not trading_symbol.strip():
            return {"error": "Trading symbol is required"}
        
        if period_value <= 0:
            return {"error": "Period value must be positive"}
        
        if not indicators:
            return {"error": "At least one indicator must be specified"}
        
        # Calculate time range
        start_time, end_time = get_time_range(period_value, period_unit)
        
        # Get appropriate interval
        interval = interval_override or get_appropriate_interval(period_value, period_unit)
        
        # Fetch historical data
        response = groww.get_historical_candle_data(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
            start_time=start_time,
            end_time=end_time,
            interval_in_minutes=interval,
        )
        
        # Check if response contains candles
        if not response.get("candles") or len(response["candles"]) == 0:
            return {
                "error": f"No historical data found for {trading_symbol} in the specified time range",
                "time_range": f"{start_time} to {end_time}",
                "interval": interval
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(response["candles"])
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        
        # Convert timestamp
        df["timestamp"] = (
            pd.to_datetime(df["timestamp"], unit="s", utc=True)
            .dt.tz_convert("Asia/Kolkata")
            .dt.tz_localize(None)
        )
        
        # Check data quality before processing
        # For indices like NIFTY, volume might be null, so check if volume is completely null
        volume_null_count = df["volume"].isna().sum()
        is_index_data = volume_null_count == len(df)  # All volume values are null
        
        if is_index_data:
            # For index data, only validate OHLC data (volume is not meaningful)
            core_data_df = df[["timestamp", "open", "high", "low", "close"]]
            valid_core_candles = len(core_data_df.dropna())
        else:
            # For stock data, validate OHLCV data
            core_data_df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            valid_core_candles = len(core_data_df.dropna())
        
        # Always generate NaN analysis for debugging
        nan_info = {}
        for col in ["timestamp", "open", "high", "low", "close", "volume"]:
            nan_count = df[col].isna().sum()
            nan_info[f"{col}_nan_count"] = nan_count
        
        # Add data type info to debug
        nan_info["is_index_data"] = is_index_data
        nan_info["validation_columns"] = "OHLC only" if is_index_data else "OHLCV"
        
        # Add debugging info to understand data quality issues
        if valid_core_candles == 0:
            if is_index_data:
                error_msg = f"All {len(df)} candles have NaN values in core OHLC data (index data, volume excluded)"
                message = "Core OHLC data contains NaN values. This might be an API data quality issue for index data."
            else:
                error_msg = f"All {len(df)} candles have NaN values in core OHLCV data"
                message = "Core OHLCV data contains NaN values. This might be an API data quality issue for stock data."
            
            return {
                "error": error_msg,
                "debug_info": {
                    "trading_symbol": trading_symbol,
                    "exchange": exchange,
                    "segment": segment,
                    "start_time": start_time,
                    "end_time": end_time,
                    "interval_in_minutes": interval,
                    "original_candles": len(df),
                    "processed_candles": valid_core_candles,
                    "nan_analysis": nan_info,
                    "first_few_rows": df.head(3).to_dict(orient="records"),
                    "message": message
                }
            }
        
        # Validate sufficient data for moving averages
        max_period_needed = max(
            sma_period if "sma" in indicators else 0,
            ema_period if "ema" in indicators else 0,
            dma_period if "dma" in indicators else 0,
            macd_slow if "macd" in indicators else 0,
            bb_period if "bollinger" in indicators else 0
        )
        
        if valid_core_candles < max_period_needed:
            data_type = "index data (OHLC)" if is_index_data else "stock data (OHLCV)"
            return {
                "error": f"Insufficient data for moving averages calculation. Need at least {max_period_needed} candles but got valid data for {valid_core_candles} candles after processing ({data_type}).",
                "debug_info": {
                    "trading_symbol": trading_symbol,
                    "exchange": exchange,
                    "segment": segment,
                    "start_time": start_time,
                    "end_time": end_time,
                    "interval_in_minutes": interval,
                    "sma_period": sma_period,
                    "ema_period": ema_period,
                    "dma_period": dma_period,
                    "original_candles": len(df),
                    "processed_candles": valid_core_candles,
                    "required_candles": max_period_needed,
                    "nan_analysis": nan_info,
                    "first_few_rows": df.head(3).to_dict(orient="records"),
                    "message": f"Moving averages calculation requires sufficient historical data for {data_type}. Try using a longer time period or daily intervals."
                }
            }
        
        # Prepare parameters
        params = {
            "sma_period": sma_period,
            "ema_period": ema_period,
            "dma_period": dma_period,
            "rsi_period": rsi_period,
            "macd_fast": macd_fast,
            "macd_slow": macd_slow,
            "macd_signal": macd_signal,
            "bb_period": bb_period,
            "bb_std": bb_std,
            "st_period": st_period,
            "st_multiplier": st_multiplier,
            "pivot_window": pivot_window,
        }
        
        # Calculate indicators
        df = calculate_indicators(df, indicators, params)
        
        # Extract pivot points if calculated
        pivot_points = df.attrs.get("pivot_points", {})
        


        
        # Prepare response
        response["technical_indicators"] = {
            "requested_indicators": indicators,
            "parameters": params,
            "time_period": {
                "value": period_value,
                "unit": period_unit,
                "start_time": start_time,
                "end_time": end_time,
                "interval_minutes": interval
            },
            "data_quality": {
                "total_candles": len(df),
                "valid_candles": valid_core_candles,
                "data_completeness": f"{valid_core_candles/len(df)*100:.1f}%"
            }
        }
        
        # Add pivot points to response if calculated
        if pivot_points:
            response["technical_indicators"]["pivot_points"] = pivot_points
        

        
        # Convert DataFrame to records
        response["candles"] = df.to_dict(orient="records")
        
        return response
        
    except Exception as e:
        return {
            "error": f"Failed to calculate technical indicators: {str(e)}",
            "debug_info": {
                "trading_symbol": trading_symbol,
                "period_value": period_value,
                "period_unit": period_unit,
                "indicators": indicators,
                "exchange": exchange,
                "segment": segment
            }
        }


@mcp.tool()
def calculate_pivot_points_levels(
    trading_symbol: Annotated[
        str,
        Field(
            description="Trading Symbol of the instrument (e.g., 'RELIANCE', 'NIFTY')"
        ),
    ],
    period_value: Annotated[
        int,
        Field(
            description="Number of time periods to analyze"
        ),
    ],
    period_unit: Annotated[
        Literal["days", "weeks", "months"],
        Field(
            description="Time unit for the period"
        ),
    ] = "days",
    pivot_type: Annotated[
        Literal["standard", "fibonacci", "camarilla"],
        Field(
            description="Type of pivot points calculation"
        ),
    ] = "standard",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Calculate pivot points (Standard, Fibonacci, or Camarilla) for historical data.
    
    Use this tool when the user asks about:
    - "Calculate pivot points for RELIANCE last 30 days"
    - "Show me daily pivot levels for NIFTY"
    - "Get Fibonacci pivot points for last week"
    - "Calculate Camarilla levels for TCS monthly"
    - "Show me support resistance levels"
    """
    try:
        # Calculate time range
        start_time, end_time = get_time_range(period_value, period_unit)
        
        # Get appropriate interval (prefer daily for pivot points)
        interval = 1440  # Daily intervals for pivot points
        
        # Fetch historical data
        response = groww.get_historical_candle_data(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
            start_time=start_time,
            end_time=end_time,
            interval_in_minutes=interval,
        )
        
        # Check if response contains candles
        if not response.get("candles") or len(response["candles"]) == 0:
            return {
                "error": f"No historical data found for {trading_symbol} in the specified time range"
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(response["candles"])
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        
        # Convert timestamp
        df["timestamp"] = (
            pd.to_datetime(df["timestamp"], unit="s", utc=True)
            .dt.tz_convert("Asia/Kolkata")
            .dt.tz_localize(None)
        )
        
        # Calculate pivot points for each day
        pivot_points_list = []
        
        for _, row in df.iterrows():
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])
            
            if pivot_type == "standard":
                pivots = calculate_pivot_points_standard(high, low, close)
            elif pivot_type == "fibonacci":
                pivots = calculate_pivot_points_fibonacci(high, low, close)
            elif pivot_type == "camarilla":
                pivots = calculate_pivot_points_camarilla(high, low, close)
            else:
                return {"error": f"Unknown pivot type: {pivot_type}"}
            
            pivot_points_list.append({
                "timestamp": row["timestamp"],
                "high": high,
                "low": low,
                "close": close,
                "pivots": pivots
            })
        
        # Add pivot points data to response
        response["pivot_points"] = {
            "type": pivot_type,
            "time_period": {
                "value": period_value,
                "unit": period_unit,
                "start_time": start_time,
                "end_time": end_time
            },
            "data": pivot_points_list
        }
        
        response["candles"] = df.to_dict(orient="records")
        
        return response
        
    except Exception as e:
        return {
            "error": f"Failed to calculate pivot points: {str(e)}",
            "debug_info": {
                "trading_symbol": trading_symbol,
                "period_value": period_value,
                "period_unit": period_unit,
                "pivot_type": pivot_type
            }
        }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8894)