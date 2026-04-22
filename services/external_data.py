import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()


def _safe_get_json(url: str, params: Dict[str, Any], timeout: int = 8) -> Dict[str, Any]:
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


def validate_email(email: str, enabled: bool = True) -> Dict[str, Any]:
    result = {"provider": "local", "deliverability": "unknown", "is_valid_format": "@" in email}
    api_key = os.getenv("ABSTRACT_API_KEY")
    if not enabled or not api_key:
        return result

    data = _safe_get_json(
        "https://emailvalidation.abstractapi.com/v1/",
        {"api_key": api_key, "email": email},
    )
    if data:
        result = {
            "provider": "abstract",
            "deliverability": data.get("deliverability", "unknown"),
            "is_valid_format": bool(data.get("is_valid_format", {}).get("value")),
            "is_free_email": bool(data.get("is_free_email", {}).get("value")),
            "quality_score": data.get("quality_score"),
        }
    return result


def validate_phone(phone: str, enabled: bool = True) -> Dict[str, Any]:
    digits_only = "".join(ch for ch in phone if ch.isdigit())
    result = {
        "provider": "local",
        "is_valid_format": len(digits_only) >= 10,
        "country": "unknown",
    }
    api_key = os.getenv("NUMVERIFY_API_KEY")
    if not enabled or not api_key:
        return result

    data = _safe_get_json(
        "http://apilayer.net/api/validate",
        {"access_key": api_key, "number": phone, "country_code": "IN", "format": 1},
    )
    if data:
        result = {
            "provider": "numverify",
            "is_valid_format": bool(data.get("valid")),
            "country": data.get("country_name", "unknown"),
            "carrier": data.get("carrier"),
            "line_type": data.get("line_type"),
        }
    return result


def get_macro_signals(enabled: bool = True) -> Dict[str, Any]:
    signals = {
        "provider": "local",
        "federal_funds_rate": None,
        "inflation_proxy": None,
        "market_note": "No external macro data configured",
        "risk_adjustment": 0,
    }

    if not enabled:
        return signals

    fred_key = os.getenv("FRED_API_KEY")
    alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if fred_key:
        fed = _safe_get_json(
            "https://api.stlouisfed.org/fred/series/observations",
            {
                "series_id": "FEDFUNDS",
                "api_key": fred_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            },
        )
        cpi = _safe_get_json(
            "https://api.stlouisfed.org/fred/series/observations",
            {
                "series_id": "CPIAUCSL",
                "api_key": fred_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 2,
            },
        )

        observations = fed.get("observations", [])
        cpi_observations = cpi.get("observations", [])
        if observations:
            try:
                fed_rate = float(observations[0]["value"])
                signals["federal_funds_rate"] = fed_rate
                signals["provider"] = "fred"
                if fed_rate >= 5:
                    signals["risk_adjustment"] += 4
            except (KeyError, TypeError, ValueError):
                pass

        if len(cpi_observations) >= 2:
            try:
                latest = float(cpi_observations[0]["value"])
                previous = float(cpi_observations[1]["value"])
                monthly_change = ((latest - previous) / previous) * 100 if previous else 0
                signals["inflation_proxy"] = round(monthly_change, 3)
                if monthly_change > 0.4:
                    signals["risk_adjustment"] += 2
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                pass

    if alpha_key:
        market = _safe_get_json(
            "https://www.alphavantage.co/query",
            {"function": "GLOBAL_QUOTE", "symbol": "SPY", "apikey": alpha_key},
        )
        quote = market.get("Global Quote", {})
        change_percent = (quote.get("10. change percent") or "").replace("%", "").strip()
        try:
            change_value = abs(float(change_percent))
            signals["market_volatility_percent"] = change_value
            signals["provider"] = "fred+alphavantage" if signals["provider"] == "fred" else "alphavantage"
            if change_value >= 2:
                signals["risk_adjustment"] += 1
        except ValueError:
            pass

    if signals["risk_adjustment"] == 0:
        signals["market_note"] = "Macro conditions are neutral"
    else:
        signals["market_note"] = "Macro conditions slightly tightened the risk view"

    return signals
