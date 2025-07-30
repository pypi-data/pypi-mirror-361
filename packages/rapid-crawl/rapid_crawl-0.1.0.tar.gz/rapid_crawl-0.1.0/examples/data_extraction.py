#!/usr/bin/env python3
"""
Data extraction examples using RapidCrawl.

This example demonstrates how to:
- Extract structured data from web pages
- Use CSS selectors and schemas
- Process and validate extracted data
- Save data in various formats
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import RapidCrawlError


def extract_with_schema():
    """Extract data using a predefined schema."""
    print("=== Extract with Schema Example ===\n")
    
    app = RapidCrawlApp()
    
    # Define extraction schema for a blog post
    blog_schema = [
        {"name": "title", "selector": "h1"},
        {"name": "author", "selector": ".author-name"},
        {"name": "date", "selector": "time", "attribute": "datetime"},
        {"name": "content", "selector": ".post-content"},
        {"name": "tags", "selector": ".tag", "type": "array"},
        {"name": "comments_count", "selector": ".comments-count", "type": "number"}
    ]
    
    url = "https://example.com/blog/post"
    print(f"Extracting data from {url}...")
    
    result = app.extract(url, schema=blog_schema)
    
    if result.success and result.structured_data:
        print("\nExtracted data:")
        for field, value in result.structured_data.items():
            if isinstance(value, list):
                print(f"  {field}: {', '.join(map(str, value))}")
            else:
                print(f"  {field}: {value}")
    else:
        print(f"Extraction failed: {result.error}")


def extract_product_data():
    """Extract e-commerce product data."""
    print("\n=== Extract Product Data Example ===\n")
    
    app = RapidCrawlApp()
    
    # Product extraction schema
    product_schema = [
        {"name": "name", "selector": "h1.product-title"},
        {"name": "price", "selector": ".price-now", "type": "number", "regex": r"[\d.]+"},
        {"name": "original_price", "selector": ".price-was", "type": "number", "regex": r"[\d.]+"},
        {"name": "rating", "selector": ".rating", "type": "number"},
        {"name": "reviews_count", "selector": ".reviews-count", "type": "number", "regex": r"\d+"},
        {"name": "availability", "selector": ".availability-status"},
        {"name": "description", "selector": ".product-description"},
        {"name": "images", "selector": ".product-image img", "attribute": "src", "type": "array"},
        {"name": "features", "selector": ".feature-list li", "type": "array"}
    ]
    
    # Extract from multiple product URLs
    product_urls = [
        "https://shop.example.com/product/laptop-1",
        "https://shop.example.com/product/laptop-2",
        "https://shop.example.com/product/laptop-3"
    ]
    
    products = []
    for url in product_urls:
        print(f"Extracting from {url}...")
        
        try:
            result = app.extract(url, schema=product_schema)
            
            if result.success and result.structured_data:
                product = result.structured_data
                product["url"] = url
                product["extracted_at"] = datetime.now().isoformat()
                
                # Calculate discount if prices available
                if product.get("price") and product.get("original_price"):
                    discount = (1 - product["price"] / product["original_price"]) * 100
                    product["discount_percent"] = round(discount, 2)
                
                products.append(product)
                print(f"  ✓ Extracted: {product.get('name', 'Unknown')}")
            else:
                print(f"  ✗ Failed to extract")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save products
    if products:
        # Save as JSON
        with open("products.json", "w") as f:
            json.dump(products, f, indent=2)
        
        # Save as CSV
        with open("products.csv", "w", newline="") as f:
            if products:
                writer = csv.DictWriter(f, fieldnames=products[0].keys())
                writer.writeheader()
                writer.writerows(products)
        
        print(f"\nExtracted {len(products)} products")
        print("Saved to products.json and products.csv")


def extract_table_data():
    """Extract data from HTML tables."""
    print("\n=== Extract Table Data Example ===\n")
    
    app = RapidCrawlApp()
    
    # Schema for extracting table data
    table_schema = [
        {
            "name": "stock_data",
            "selector": "table.stock-prices",
            "type": "table",
            "columns": [
                {"name": "symbol", "selector": "td:nth-child(1)"},
                {"name": "price", "selector": "td:nth-child(2)", "type": "number"},
                {"name": "change", "selector": "td:nth-child(3)", "type": "number"},
                {"name": "volume", "selector": "td:nth-child(4)", "type": "number"}
            ]
        }
    ]
    
    # Note: This is a conceptual example
    # Real implementation would need custom table parsing
    
    print("Extracting stock market data...")
    
    # Alternative approach using multiple selectors
    stock_schema = [
        {"name": "symbols", "selector": "table.stock-prices td:nth-child(1)", "type": "array"},
        {"name": "prices", "selector": "table.stock-prices td:nth-child(2)", "type": "array"},
        {"name": "changes", "selector": "table.stock-prices td:nth-child(3)", "type": "array"},
        {"name": "volumes", "selector": "table.stock-prices td:nth-child(4)", "type": "array"}
    ]
    
    result = app.extract("https://finance.example.com/stocks", schema=stock_schema)
    
    if result.success and result.structured_data:
        data = result.structured_data
        
        # Combine arrays into table format
        if all(key in data for key in ["symbols", "prices", "changes", "volumes"]):
            stocks = []
            for i in range(len(data["symbols"])):
                stocks.append({
                    "symbol": data["symbols"][i] if i < len(data["symbols"]) else "",
                    "price": data["prices"][i] if i < len(data["prices"]) else 0,
                    "change": data["changes"][i] if i < len(data["changes"]) else 0,
                    "volume": data["volumes"][i] if i < len(data["volumes"]) else 0
                })
            
            print(f"\nExtracted {len(stocks)} stocks")
            for stock in stocks[:5]:  # Show first 5
                print(f"  {stock['symbol']}: ${stock['price']} ({stock['change']}%)")


def batch_extraction():
    """Extract data from multiple pages efficiently."""
    print("\n=== Batch Extraction Example ===\n")
    
    app = RapidCrawlApp()
    
    # News article schema
    article_schema = [
        {"name": "headline", "selector": "h1"},
        {"name": "author", "selector": ".byline"},
        {"name": "publish_date", "selector": "time", "attribute": "datetime"},
        {"name": "summary", "selector": ".article-summary"},
        {"name": "content", "selector": ".article-content"},
        {"name": "category", "selector": ".category-tag"},
        {"name": "related_links", "selector": ".related-articles a", "attribute": "href", "type": "array"}
    ]
    
    # URLs to extract from
    article_urls = [
        "https://news.example.com/article-1",
        "https://news.example.com/article-2",
        "https://news.example.com/article-3",
        "https://news.example.com/article-4",
        "https://news.example.com/article-5"
    ]
    
    print(f"Extracting from {len(article_urls)} articles...")
    
    # Batch extraction
    results = app.extract(article_urls, schema=article_schema)
    
    articles = []
    for i, result in enumerate(results):
        if result.success and result.structured_data:
            article = result.structured_data
            article["url"] = article_urls[i]
            articles.append(article)
            print(f"  ✓ {article.get('headline', 'Unknown headline')}")
        else:
            print(f"  ✗ Failed: {article_urls[i]}")
    
    # Analyze extracted data
    if articles:
        print(f"\nSuccessfully extracted {len(articles)} articles")
        
        # Group by category
        by_category = {}
        for article in articles:
            category = article.get("category", "Uncategorized")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(article)
        
        print("\nArticles by category:")
        for category, items in by_category.items():
            print(f"  {category}: {len(items)} articles")


def extract_with_validation():
    """Extract and validate data."""
    print("\n=== Extract with Validation Example ===\n")
    
    app = RapidCrawlApp()
    
    # Schema with validation requirements
    contact_schema = [
        {"name": "company_name", "selector": "h1.company-name", "required": True},
        {"name": "email", "selector": ".contact-email", "required": True},
        {"name": "phone", "selector": ".contact-phone"},
        {"name": "address", "selector": ".contact-address"},
        {"name": "social_links", "selector": ".social-links a", "attribute": "href", "type": "array"}
    ]
    
    url = "https://example.com/contact"
    print(f"Extracting contact information from {url}...")
    
    result = app.extract(url, schema=contact_schema)
    
    if result.success and result.structured_data:
        data = result.structured_data
        
        # Validate extracted data
        errors = []
        
        # Check required fields
        if not data.get("company_name"):
            errors.append("Company name is required")
        
        if not data.get("email"):
            errors.append("Email is required")
        elif "@" not in data.get("email", ""):
            errors.append("Invalid email format")
        
        # Validate phone format
        if data.get("phone"):
            import re
            phone_pattern = r"[\d\s\-\+\(\)]+"
            if not re.match(phone_pattern, data["phone"]):
                errors.append("Invalid phone format")
        
        # Validate social links
        if data.get("social_links"):
            valid_social = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com"]
            for link in data["social_links"]:
                if not any(social in link for social in valid_social):
                    errors.append(f"Unknown social platform: {link}")
        
        if errors:
            print("\nValidation errors:")
            for error in errors:
                print(f"  ✗ {error}")
        else:
            print("\n✓ All data validated successfully!")
            
            # Save validated data
            with open("contact_info.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Saved to contact_info.json")


def extract_with_transformation():
    """Extract and transform data."""
    print("\n=== Extract with Transformation Example ===\n")
    
    app = RapidCrawlApp()
    
    # Recipe extraction schema
    recipe_schema = [
        {"name": "title", "selector": "h1.recipe-title"},
        {"name": "prep_time", "selector": ".prep-time", "regex": r"\d+"},
        {"name": "cook_time", "selector": ".cook-time", "regex": r"\d+"},
        {"name": "servings", "selector": ".servings", "type": "number", "regex": r"\d+"},
        {"name": "ingredients", "selector": ".ingredient", "type": "array"},
        {"name": "instructions", "selector": ".instruction", "type": "array"},
        {"name": "nutrition", "selector": ".nutrition-item", "type": "array"}
    ]
    
    url = "https://recipes.example.com/chocolate-cake"
    print(f"Extracting recipe from {url}...")
    
    result = app.extract(url, schema=recipe_schema)
    
    if result.success and result.structured_data:
        recipe = result.structured_data
        
        # Transform the data
        transformed = {
            "title": recipe.get("title", "Unknown Recipe"),
            "total_time": int(recipe.get("prep_time", 0)) + int(recipe.get("cook_time", 0)),
            "servings": recipe.get("servings", 1),
            "ingredients_count": len(recipe.get("ingredients", [])),
            "steps_count": len(recipe.get("instructions", [])),
            "difficulty": "Easy" if len(recipe.get("instructions", [])) < 10 else "Medium"
        }
        
        # Parse nutrition info
        nutrition_dict = {}
        for item in recipe.get("nutrition", []):
            if ":" in item:
                key, value = item.split(":", 1)
                nutrition_dict[key.strip()] = value.strip()
        transformed["nutrition"] = nutrition_dict
        
        # Create shopping list
        shopping_list = []
        for ingredient in recipe.get("ingredients", []):
            # Simple parsing - in reality would be more complex
            parts = ingredient.split()
            if len(parts) >= 2:
                amount = parts[0]
                item = " ".join(parts[1:])
                shopping_list.append({"amount": amount, "item": item})
        transformed["shopping_list"] = shopping_list
        
        print("\nTransformed recipe data:")
        print(json.dumps(transformed, indent=2))
        
        # Save recipe
        with open("recipe_transformed.json", "w") as f:
            json.dump(transformed, f, indent=2)
        print("\nSaved to recipe_transformed.json")


if __name__ == "__main__":
    try:
        # Run all examples
        extract_with_schema()
        extract_product_data()
        extract_table_data()
        batch_extraction()
        extract_with_validation()
        extract_with_transformation()
        
        print("\n✓ All extraction examples completed!")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")