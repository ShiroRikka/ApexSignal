"""Abstract base class for data fetchers."""

from abc import ABC, abstractmethod


class DataFetcher(ABC):
    """Abstract base class for data fetchers."""

    @abstractmethod
    def fetch_and_store(self, stock_code, days_back):
        """Fetch and store data.
        
        Args:
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        pass