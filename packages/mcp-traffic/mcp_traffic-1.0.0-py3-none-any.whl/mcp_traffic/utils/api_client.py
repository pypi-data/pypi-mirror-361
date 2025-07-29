"""
ODPT API Client for MCP Traffic

Handles communication with the ODPT (Open Data Platform for Transportation) API
"""

import time
import logging
from typing import Dict, List, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ODPTClient:
    """Client for ODPT API interactions"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ODPT API client
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.odpt_config = config.get("odpt_api", {})
        self.base_url = self.odpt_config.get("base_url")
        self.api_key = self.odpt_config.get("api_key")
        self.rate_limit = self.odpt_config.get("rate_limit", 100)
        self.timeout = self.odpt_config.get("timeout", 30)
        
        self.logger = logging.getLogger(__name__)
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60.0 / self.rate_limit  # seconds between requests
        
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def _make_request(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the ODPT API
        
        Args:
            action: API action to call
            params: Additional parameters for the request
            
        Returns:
            JSON response from the API
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response is invalid
        """
        self._rate_limit()
        
        url = f"{self.base_url.rstrip('/')}/{action}"
        
        request_params = {
            "acl:consumerKey": self.api_key
        }
        
        if params:
            request_params.update(params)
            
        self.logger.debug(f"Making request to {url} with params: {request_params}")
        
        try:
            response = self.session.get(
                url, 
                params=request_params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                raise ValueError(f"Unexpected content type: {content_type}")
                
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid response: {str(e)}")
            raise
            
    def get_catalog(self) -> Dict[str, Any]:
        """Get API catalog information
        
        Returns:
            Catalog data from the API
        """
        self.logger.info("Fetching API catalog")
        return self._make_request("package_list")
        
    def get_package_info(self, package_id: str) -> Dict[str, Any]:
        """Get information about a specific package
        
        Args:
            package_id: ID of the package to retrieve
            
        Returns:
            Package information
        """
        self.logger.info(f"Fetching package info for: {package_id}")
        return self._make_request("package_show", {"id": package_id})
        
    def get_data(self, data_type: str, **filters) -> List[Dict[str, Any]]:
        """Get data of a specific type
        
        Args:
            data_type: Type of data to retrieve (e.g., 'odpt:Train')
            **filters: Additional filters to apply
            
        Returns:
            List of data items
        """
        self.logger.info(f"Fetching data for type: {data_type}")
        
        params = {"rdf:type": data_type}
        params.update(filters)
        
        try:
            response = self._make_request("datastore_search", params)
            
            # Handle different response formats
            if isinstance(response, dict):
                if "result" in response and "records" in response["result"]:
                    return response["result"]["records"]
                elif "records" in response:
                    return response["records"]
                else:
                    return [response]  # Single item response
            elif isinstance(response, list):
                return response
            else:
                self.logger.warning(f"Unexpected response format for {data_type}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to fetch data for {data_type}: {str(e)}")
            return []
            
    def get_train_data(self, operator: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get train data with optional operator filter
        
        Args:
            operator: Optional operator to filter by
            
        Returns:
            List of train data
        """
        filters = {}
        if operator:
            filters["odpt:operator"] = operator
            
        return self.get_data("odpt:Train", **filters)
        
    def get_train_information(self, railway: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get train information with optional railway filter
        
        Args:
            railway: Optional railway to filter by
            
        Returns:
            List of train information
        """
        filters = {}
        if railway:
            filters["odpt:railway"] = railway
            
        return self.get_data("odpt:TrainInformation", **filters)
        
    def get_station_data(self, operator: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get station data with optional operator filter
        
        Args:
            operator: Optional operator to filter by
            
        Returns:
            List of station data
        """
        filters = {}
        if operator:
            filters["odpt:operator"] = operator
            
        return self.get_data("odpt:Station", **filters)
        
    def get_bus_data(self, operator: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get bus data with optional operator filter
        
        Args:
            operator: Optional operator to filter by
            
        Returns:
            List of bus data
        """
        filters = {}
        if operator:
            filters["odpt:operator"] = operator
            
        return self.get_data("odpt:Bus", **filters)
        
    def get_railway_data(self, operator: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get railway data with optional operator filter
        
        Args:
            operator: Optional operator to filter by
            
        Returns:
            List of railway data
        """
        filters = {}
        if operator:
            filters["odpt:operator"] = operator
            
        return self.get_data("odpt:Railway", **filters)
        
    def test_connection(self) -> bool:
        """Test API connection and authentication
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.logger.info("Testing API connection")
            catalog = self.get_catalog()
            
            if catalog and (isinstance(catalog, dict) or isinstance(catalog, list)):
                self.logger.info("API connection test successful")
                return True
            else:
                self.logger.error("API connection test failed: Invalid response")
                return False
                
        except Exception as e:
            self.logger.error(f"API connection test failed: {str(e)}")
            return False
            
    def get_available_operators(self) -> List[str]:
        """Get list of available operators
        
        Returns:
            List of operator IDs
        """
        try:
            # Get railway data to find operators
            railways = self.get_railway_data()
            operators = set()
            
            for railway in railways:
                if "odpt:operator" in railway:
                    operators.add(railway["odpt:operator"])
                    
            return sorted(list(operators))
            
        except Exception as e:
            self.logger.error(f"Failed to get operators: {str(e)}")
            return []
            
    def get_health_status(self) -> Dict[str, Any]:
        """Get API health status
        
        Returns:
            Dictionary with health status information
        """
        start_time = time.time()
        
        try:
            # Test basic connectivity
            catalog = self.get_catalog()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_seconds": round(response_time, 3),
                "api_accessible": True,
                "catalog_items": len(catalog) if isinstance(catalog, list) else 1
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return {
                "status": "unhealthy",
                "response_time_seconds": round(response_time, 3),
                "api_accessible": False,
                "error": str(e)
            }
            
    def __str__(self) -> str:
        """String representation of the client"""
        return f"ODPTClient(base_url={self.base_url}, rate_limit={self.rate_limit})"
        
    def __repr__(self) -> str:
        """Detailed string representation"""
        return self.__str__()
