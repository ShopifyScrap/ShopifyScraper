#!/usr/bin/env python3
"""
Shopify Product Scraper
Extrait les produits d'une boutique Shopify et les exporte en CSV.
"""

import sys
import csv
import json
import urllib.parse
from typing import List, Dict
import requests
from requests.exceptions import RequestException

def get_store_domain(url: str) -> str:
    """Extrait et normalise le domaine Shopify de l'URL."""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc or parsed.path
    return domain

def fetch_products(domain: str) -> List[Dict]:
    """Récupère tous les produits via l'API Shopify."""
    products = []
    page = 1
    while True:
        try:
            url = f"https://{domain}/products.json?page={page}&limit=250"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('products'):
                break
                
            products.extend(data['products'])
            page += 1
            
        except RequestException as e:
            print(f"Erreur lors de la récupération des produits: {e}")
            break
            
    return products

def format_product_data(products: List[Dict]) -> List[Dict]:
    """Formate les données des produits pour l'export CSV."""
    formatted_products = []
    
    for product in products:
        # Gestion des variantes
        for variant in product.get('variants', []):
            formatted_product = {
                'ID': variant.get('id'),
                'Title': f"{product.get('title')} - {variant.get('title')}" if variant.get('title') != 'Default Title' else product.get('title'),
                'Description': product.get('body_html', ''),
                'Vendor': product.get('vendor', ''),
                'Product Type': product.get('product_type', ''),
                'Price': variant.get('price', ''),
                'Compare at Price': variant.get('compare_at_price', ''),
                'SKU': variant.get('sku', ''),
                'Barcode': variant.get('barcode', ''),
                'Tags': ', '.join(product.get('tags', [])),
                'Published': product.get('published_at') is not None
            }
            formatted_products.append(formatted_product)
            
    return formatted_products

def export_to_csv(products: List[Dict], filename: str = 'products.csv'):
    """Exporte les produits dans un fichier CSV."""
    if not products:
        print("Aucun produit à exporter.")
        return
        
    fieldnames = products[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        print(f"{len(products)} produits exportés dans {filename}")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier CSV: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python shopify_scraper.py <shopify_url>")
        sys.exit(1)

    url = sys.argv[1]
    domain = get_store_domain(url)
    
    print(f"Récupération des produits depuis {domain}...")
    products = fetch_products(domain)
    
    if products:
        formatted_products = format_product_data(products)
        export_to_csv(formatted_products)
    else:
        print("Aucun produit trouvé.")

if __name__ == "__main__":
    main() 