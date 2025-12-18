"""Grocy API client for stock operations."""
import requests
from typing import Optional, Dict, Any
from config import Config


class GrocyAPI:
    """Client for interacting with Grocy API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.host
        self.api_key = config.api_key
        self.session = requests.Session()
        self.session.headers.update({
            'GROCY-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make GET request to Grocy API."""
        try:
            url = f"{self.base_url}/api/{endpoint}"
            response = self.session.get(url, timeout=10)
            
            # Check for errors
            if response.status_code == 500:
                # Server error - don't spam console, just return None
                return None
            elif response.status_code == 404:
                # Not found - this is normal for missing products
                return None
            elif response.status_code == 400:
                # Bad request - query syntax might be wrong, try next method
                return None
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Only print errors that aren't expected (400, 404, 500)
            status_code = e.response.status_code if hasattr(e, 'response') else None
            if status_code not in [400, 404, 500]:
                print(f"API GET error ({status_code}): {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"API GET error: {e}")
            return None
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make POST request to Grocy API."""
        try:
            url = f"{self.base_url}/api/{endpoint}"
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API POST error: {e}")
            return None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product information by barcode/EAN."""
        print(f"🔍 Searching for barcode: {barcode}")
        
        # Method 1: Use Grocy's query API with correct syntax
        # Grocy API v3 uses: query[]=field=value format
        try:
            # URL encode the barcode properly
            encoded_barcode = requests.utils.quote(barcode, safe='')
            endpoint = f"objects/products?query[]=barcode={encoded_barcode}"
            print(f"  Trying endpoint: {endpoint}")
            products = self._get(endpoint)
            
            if products:
                print(f"  Response: {type(products)} with {len(products) if isinstance(products, list) else 'N/A'} items")
                if isinstance(products, list) and len(products) > 0:
                    print(f"  ✓ Found product via query API: {products[0].get('name', 'Unknown')}")
                    return products[0]
                elif isinstance(products, dict):
                    # Sometimes API returns a single object instead of list
                    print(f"  ✓ Found product (single object): {products.get('name', 'Unknown')}")
                    return products
        except Exception as e:
            print(f"  ✗ Query API error: {e}")
        
        # Method 2: Try alternative query format with URL encoding
        try:
            encoded_barcode = requests.utils.quote(barcode, safe='')
            endpoint = f"objects/products?query[]=barcode%3D{encoded_barcode}"
            print(f"  Trying alternative endpoint: {endpoint}")
            products = self._get(endpoint)
            
            if products:
                print(f"  Response: {type(products)} with {len(products) if isinstance(products, list) else 'N/A'} items")
                if isinstance(products, list) and len(products) > 0:
                    print(f"  ✓ Found product via alternative query: {products[0].get('name', 'Unknown')}")
                    return products[0]
                elif isinstance(products, dict):
                    print(f"  ✓ Found product (single object): {products.get('name', 'Unknown')}")
                    return products
        except Exception as e:
            print(f"  ✗ Alternative query error: {e}")
        
        # Method 3: Get all products and filter client-side (most reliable fallback)
        print("  Trying client-side search (fetching all products)...")
        try:
            all_products = self._get("objects/products")
            if all_products and isinstance(all_products, list):
                print(f"  Fetched {len(all_products)} products, searching for barcode...")
                
                # Debug: Show structure of first product
                if len(all_products) > 0:
                    print(f"  Sample product structure (first product):")
                    sample = all_products[0]
                    print(f"    Keys: {list(sample.keys())}")
                    if 'barcode' in sample:
                        print(f"    barcode field: {sample.get('barcode')} (type: {type(sample.get('barcode'))})")
                    if 'barcodes' in sample:
                        print(f"    barcodes field: {sample.get('barcodes')} (type: {type(sample.get('barcodes'))})")
                
                found_count = 0
                for product in all_products:
                    product_id = product.get('id')
                    product_name = product.get('name', 'Unknown')
                    
                    # Check multiple possible barcode fields
                    product_barcode = product.get('barcode')
                    product_barcodes = product.get('barcodes')  # Plural form
                    
                    # Also try to get barcodes from stock/products endpoint
                    if product_id:
                        try:
                            stock_info = self._get(f"stock/products/{product_id}")
                            if stock_info:
                                stock_barcode = stock_info.get('barcode')
                                if stock_barcode:
                                    if str(stock_barcode).strip() == str(barcode).strip():
                                        print(f"  ✓ Found product via stock info: {product_name}")
                                        print(f"    Stock barcode: {stock_barcode}")
                                        return product
                        except:
                            pass
                    
                    # Check barcode field (can be string, list, or None)
                    if product_barcode:
                        found_count += 1
                        # Handle different barcode formats
                        if isinstance(product_barcode, list):
                            # Multiple barcodes - check if our barcode is in the list
                            if any(str(bc).strip() == str(barcode).strip() for bc in product_barcode):
                                print(f"  ✓ Found product via client-side search: {product_name}")
                                print(f"    Product barcodes: {product_barcode}")
                                return product
                        else:
                            # Single barcode - compare as strings
                            if str(product_barcode).strip() == str(barcode).strip():
                                print(f"  ✓ Found product via client-side search: {product_name}")
                                print(f"    Product barcode: {product_barcode}")
                                return product
                    
                    # Check barcodes (plural) field
                    if product_barcodes:
                        found_count += 1
                        if isinstance(product_barcodes, list):
                            if any(str(bc).strip() == str(barcode).strip() for bc in product_barcodes):
                                print(f"  ✓ Found product via barcodes field: {product_name}")
                                print(f"    Product barcodes: {product_barcodes}")
                                return product
                
                print(f"  ✗ Barcode not found. Checked {found_count} products with barcode fields.")
                
                # Try alternative: Get barcodes from objects/product_barcodes endpoint
                print("  Trying product_barcodes endpoint...")
                try:
                    all_barcodes = self._get("objects/product_barcodes")
                    if all_barcodes and isinstance(all_barcodes, list):
                        print(f"  Found {len(all_barcodes)} barcode entries")
                        for barcode_entry in all_barcodes:
                            entry_barcode = barcode_entry.get('barcode')
                            if entry_barcode and str(entry_barcode).strip() == str(barcode).strip():
                                product_id = barcode_entry.get('product_id')
                                if product_id:
                                    print(f"  ✓ Found barcode in product_barcodes table!")
                                    print(f"    Product ID: {product_id}, Barcode: {entry_barcode}")
                                    return self.get_product_by_id(product_id)
                except Exception as e:
                    print(f"  ✗ product_barcodes endpoint error: {e}")
                
            else:
                print(f"  ✗ Could not fetch products list")
        except Exception as e:
            print(f"  ✗ Client-side search error: {e}")
        
        print(f"  ✗ Barcode '{barcode}' not found in Grocy")
        return None
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product information by ID."""
        return self._get(f"objects/products/{product_id}")
    
    def search_products(self, search_term: str = None) -> list:
        """Search for products by name. If no search_term provided, returns first 10 products."""
        try:
            # Get all products
            all_products = self._get("objects/products")
            if all_products and isinstance(all_products, list):
                if search_term:
                    # Filter products that match the search term
                    search_lower = search_term.lower()
                    matches = [
                        p for p in all_products
                        if search_lower in p.get('name', '').lower()
                    ]
                    return matches[:10]  # Return top 10 matches
                else:
                    # Return first 10 products if no search term
                    return all_products[:10]
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_recent_products(self, limit: int = 10) -> list:
        """Get recent products (first N products)."""
        return self.search_products()[:limit]
    
    def get_product_picture_url(self, product_id: int, picture_file_name: str) -> Optional[str]:
        """Get product picture URL."""
        if not picture_file_name:
            return None
        
        # Try multiple possible URL formats
        # Format 1: Standard API endpoint
        url1 = f"{self.base_url}/api/files/productpictures/{picture_file_name}"
        
        # Format 2: Direct file path (some Grocy versions)
        url2 = f"{self.base_url}/api/files/productpictures/{product_id}/{picture_file_name}"
        
        # Format 3: Without /api/ prefix
        url3 = f"{self.base_url}/files/productpictures/{picture_file_name}"
        
        # Format 4: With product ID in path
        url4 = f"{self.base_url}/files/productpictures/{product_id}/{picture_file_name}"
        
        print(f"  Trying image URLs:")
        print(f"    1: {url1}")
        print(f"    2: {url2}")
        print(f"    3: {url3}")
        print(f"    4: {url4}")
        
        # Return the first format (most common), but we'll try all in the UI
        return url1
    
    def get_stock(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get current stock information for a product."""
        # Try the stock/products/{id} endpoint first
        stock = self._get(f"stock/products/{product_id}")
        
        if stock:
            print(f"  Stock info for product {product_id}:")
            print(f"    Type: {type(stock)}")
            if isinstance(stock, dict):
                print(f"    Keys: {list(stock.keys())}")
                print(f"    Amount: {stock.get('amount', 'N/A')}")
                print(f"    Stock amount: {stock.get('stock_amount', 'N/A')}")
                print(f"    Full response: {stock}")
            elif isinstance(stock, list):
                print(f"    List length: {len(stock)}")
                if len(stock) > 0:
                    print(f"    First item keys: {list(stock[0].keys()) if isinstance(stock[0], dict) else 'N/A'}")
        else:
            # Try alternative endpoint: stock/entries
            print(f"  Trying alternative stock endpoint...")
            all_stock = self._get("stock/entries")
            if all_stock and isinstance(all_stock, list):
                # Find stock entries for this product
                product_stock = [s for s in all_stock if s.get('product_id') == product_id]
                if product_stock:
                    total_amount = sum(entry.get('amount', 0) for entry in product_stock)
                    print(f"  Found {len(product_stock)} stock entries, total: {total_amount}")
                    return {'amount': total_amount, 'entries': product_stock}
            
            print(f"  ✗ Could not get stock info for product {product_id}")
        
        return stock
    
    def add_to_stock(self, product_id: int, amount: float = 1.0, 
                    best_before_date: Optional[str] = None,
                    transaction_type: str = "purchase") -> Optional[Dict[str, Any]]:
        """Add stock to a product."""
        print(f"  Adding {amount} to stock for product {product_id}")
        data = {
            "amount": amount,
            "transaction_type": transaction_type
        }
        if best_before_date:
            data["best_before_date"] = best_before_date
        
        result = self._post(f"stock/products/{product_id}/add", data)
        if result:
            print(f"  ✓ Add stock result: {result}")
        else:
            print(f"  ✗ Add stock failed")
        return result
    
    def deduct_from_stock(self, product_id: int, amount: float = 1.0,
                          transaction_type: str = "consume") -> Optional[Dict[str, Any]]:
        """Deduct stock from a product."""
        data = {
            "amount": amount,
            "transaction_type": transaction_type
        }
        return self._post(f"stock/products/{product_id}/consume", data)
    
    def open_product(self, product_id: int, amount: float = 1.0) -> Optional[Dict[str, Any]]:
        """Open a product package (mark as opened without fully consuming)."""
        # In Grocy, "open" is done via consume endpoint with opened=True
        # This marks the product as opened but doesn't consume the full amount
        data = {
            "amount": amount,
            "transaction_type": "consume",
            "opened": True
        }
        return self._post(f"stock/products/{product_id}/consume", data)
    
    def get_product_groups(self) -> list:
        """Get all product groups from Grocy."""
        try:
            groups = self._get("objects/product_groups")
            if groups and isinstance(groups, list):
                # Sort by name
                return sorted(groups, key=lambda x: x.get('name', ''))
            return []
        except Exception as e:
            print(f"Error getting product groups: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test connection to Grocy API."""
        try:
            result = self._get("system/info")
            return result is not None
        except Exception:
            return False

