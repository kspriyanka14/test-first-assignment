import datetime
from typing import Dict, List, Optional

class CurrencyConverter:
    def __init__(self):
        # Initialize with fixed exchange rates
        self.exchange_rates = {
            ("USD", "EUR"): 0.91,
            ("USD", "GBP"): 0.77,
            ("EUR", "USD"): 1.10,
            ("GBP", "USD"): 1.30,
        }
        self.conversion_history = {}
    
    def get_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get the exchange rate between two currencies."""
        if not isinstance(from_currency, str) or not isinstance(to_currency, str):
            raise ValueError("Currency codes must be strings")
            
        if from_currency == to_currency:
            return 1.0
            
        if (from_currency, to_currency) in self.exchange_rates:
            return self.exchange_rates[(from_currency, to_currency)]
        
        # Try to calculate via USD if direct rate not available
        if from_currency != "USD" and to_currency != "USD":
            # First convert from_currency to USD
            if (from_currency, "USD") in self.exchange_rates:
                from_to_usd = self.exchange_rates[(from_currency, "USD")]
            elif ("USD", from_currency) in self.exchange_rates:
                from_to_usd = 1.0 / self.exchange_rates[("USD", from_currency)]
            else:
                raise ValueError(f"No exchange rate found for {from_currency} to USD")
                
            # Then convert USD to to_currency
            if ("USD", to_currency) in self.exchange_rates:
                usd_to_to = self.exchange_rates[("USD", to_currency)]
            elif (to_currency, "USD") in self.exchange_rates:
                usd_to_to = 1.0 / self.exchange_rates[(to_currency, "USD")]
            else:
                raise ValueError(f"No exchange rate found for USD to {to_currency}")
                
            # Calculate cross rate
            return from_to_usd * usd_to_to
        
        # If we reach here, we don't have a valid rate
        raise ValueError(f"No exchange rate found for {from_currency} to {to_currency}")
    
    def convert(self, amount: float, from_currency: str, to_currency: str,
                user_id: Optional[str] = None) -> Dict:
        """Convert an amount from one currency to another."""
        # Validate inputs
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Get exchange rate and calculate converted amount
        rate = self.get_rate(from_currency, to_currency)
        converted_amount = amount * rate
        
        # Create result object
        result = {
            "original_amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": converted_amount,
            "exchange_rate": rate,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save to history if user_id provided
        if user_id:
            if user_id not in self.conversion_history:
                self.conversion_history[user_id] = []
            self.conversion_history[user_id].append(result)
        
        return result
    
    def get_user_history(self, user_id: str) -> List[Dict]:
        """Get conversion history for a user."""
        return self.conversion_history.get(user_id, [])
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of currencies that have exchange rates."""
        currencies = set()
        
        for from_curr, to_curr in self.exchange_rates.keys():
            currencies.add(from_curr)
            currencies.add(to_curr)
            
        return sorted(list(currencies))
    
    def clear_user_history(self, user_id: str) -> bool:
        """Clear conversion history for a user."""
        if user_id in self.conversion_history:
            self.conversion_history[user_id] = []
            return True
        return False
    
    def format_result(self, result: Dict, decimal_places: int = 2) -> str:
        """Format a conversion result as a readable string."""
        original = result["original_amount"]
        converted = result["converted_amount"]
        from_curr = result["from_currency"]
        to_curr = result["to_currency"]
        rate = result["exchange_rate"]
        
        return (f"{original:.{decimal_places}f} {from_curr} = "
                f"{converted:.{decimal_places}f} {to_curr} "
                f"(rate: {rate:.{decimal_places}f})")
                
    def update_exchange_rate(self, from_currency: str, to_currency: str, 
                             rate: float) -> bool:
        """Update the exchange rate between two currencies."""
        # Validate inputs
        if not isinstance(from_currency, str) or not isinstance(to_currency, str):
            return False
            
        if rate <= 0:
            return False
            
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Update rate
        self.exchange_rates[(from_currency, to_currency)] = rate
        return True