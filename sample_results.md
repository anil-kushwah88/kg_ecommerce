# Sample Results (offline rule-based planner)

## 1. Which products from brand Zenith are supplied by vendor Sunrise Traders?
**Graph query:** `{"return_type": "Product", "filters": [{"type": "Brand", "name": "Zenith"}, {"type": "Vendor", "name": "Sunrise Traders"}]}`

**Retrieved:** Product:Wireless Earbuds Pro, Product:Bluetooth Speaker Mini

**Answer:** Found 2 result(s):
- Product: Wireless Earbuds Pro
- Product: Bluetooth Speaker Mini

## 2. Which customers bought products from brand Lumo?
**Graph query:** `{"return_type": "Customer", "filters": [{"type": "Brand", "name": "Lumo"}]}`

**Retrieved:** Customer:Rahul Sharma, Customer:Priya Verma

**Answer:** Found 2 result(s):
- Customer: Rahul Sharma
- Customer: Priya Verma

## 3. List all products in the Electronics category with their vendors.
**Graph query:** `{"return_type": "Product", "filters": [{"type": "Category", "name": "Electronics"}]}`

**Retrieved:** Product:Wireless Earbuds Pro, Product:Smart Watch Active, Product:Bluetooth Speaker Mini

**Answer:** Found 3 result(s):
- Product: Wireless Earbuds Pro
- Product: Smart Watch Active
- Product: Bluetooth Speaker Mini

## 4. Which vendors supply products in the Grocery category?
**Graph query:** `{"return_type": "Vendor", "filters": [{"type": "Category", "name": "Grocery"}]}`

**Retrieved:** Vendor:GreenLeaf Supplies

**Answer:** Found 1 result(s):
- Vendor: GreenLeaf Supplies

## 5. Which orders contain products supplied by Metro Wholesale?
**Graph query:** `{"return_type": "Order", "filters": [{"type": "Vendor", "name": "Metro Wholesale"}]}`

**Retrieved:** Order:O3, Order:O4, Order:O7, Order:O8

**Answer:** Found 4 result(s):
- Order: O3
- Order: O4
- Order: O7
- Order: O8

## 6. What is linked to banana in the knowledge graph?
**Graph query:** `{"return_type": "ANY", "filters": [{"type": "Keyword", "name": "banana"}]}`

**Retrieved:** Brand:FreshFarm, Category:Grocery, Vendor:GreenLeaf Supplies, Product:Organic Oats 1kg, Product:Cold Pressed Peanut Butter

**Answer:** Found 5 result(s):
- Brand: FreshFarm
- Category: Grocery
- Vendor: GreenLeaf Supplies
- Product: Organic Oats 1kg
- Product: Cold Pressed Peanut Butter

## 7. Which products have the banana keyword?
**Graph query:** `{"return_type": "Product", "filters": [{"type": "Keyword", "name": "banana"}]}`

**Retrieved:** Product:Organic Oats 1kg, Product:Cold Pressed Peanut Butter

**Answer:** Found 2 result(s):
- Product: Organic Oats 1kg
- Product: Cold Pressed Peanut Butter
