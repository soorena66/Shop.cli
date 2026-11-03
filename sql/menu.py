from shop import Shop

def print_table(headers, rows):
    if not rows:
        print("\n[THERE IS NO ANY THING TO SHOW]")
        return
    
  
    str_rows = [[str(item) for item in row] for row in rows]
    
   
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(val))
            
    format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])
    separator = "-+-".join(["-" * w for w in col_widths])
    
    print("\n" + format_str.format(*headers))
    print(separator)
    for row in str_rows:
        print(format_str.format(*row))
    print()
def select_user(shop):
    keyword = input("Search user (name/phone) to select: ")
    users = shop.search_users(keyword)
    if not users:
        print("No user found.")
        return None
    print_table(["ID", "Name", "Family", "Phone", "Email"], users)
    try:
        return int(input("Enter User ID from list: "))
    except ValueError:
        return None

def select_product(shop):
    keyword = input("Search product (Name/Category/Brand): ")
    products = shop.search_products(keyword)
    if not products:
        print("No products found.")
        return None
    
    print("\n--- [Products List] ---")
    for p in products:
        print(f"ID: {p['id']} | Name: {p['name']} | Category: {p['category']} | Brand: {p['brand']} | Price: {p['price']} | Stock: {p['stock']}")
    print("-" * 50)
    
    try:
        return int(input("Enter the product ID from the list above: "))
    except ValueError:
        print("Invalid selection.")
        return None


def select_product_by_category(shop):
    categories = shop.get_categories()
    if not categories:
        print("No categories or products available.")
        return None
    
    print("\n--- [Available Categories] ---")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    print("0. Back")
    
    try:
        choice = int(input("Enter the category number: "))
        if choice == 0: 
            return None
        selected_cat = categories[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None
    
    products = shop.get_products_by_category(selected_cat)
    if not products:
        print("No products found in this category.")
        return None
    
    print(f"\n--- [Products in '{selected_cat}'] ---")
    for p in products:
        print(f"ID: {p['id']} | Name: {p['name']} | Brand: {p['brand']} | Price: {p['price']} | Stock: {p['stock']}")
    print("-" * 50)
    
    try:
        return int(input("Enter the product ID from the list above: "))
    except ValueError:
        print("Invalid selection.")
        return None

    
def manage_user_addresses(shop, uid):
    while True:
        print("\n--- [Address Management] ---")
        addrs = shop.get_user_addresses(uid)
        print_table(["ID", "User ID", "City", "Detail", "Postal Code"], addrs)
        print("1-Add | 2-Edit | 3-Delete | 0-Back")
        ch = input("Selection: ")
        if ch == '1':
            shop.add_address(uid, input("City: "), input("Detail: "), input("Postal Code: "))
        elif ch == '2':
            aid = int(input("Address ID to edit: "))
            shop.update_address(aid, input("New City: "), input("New Detail: "), input("New Postal Code: "))
        elif ch == '3':
            aid = int(input("Address ID to delete: "))
            shop.delete_address(aid)
            print("Address deleted successfully.")
        elif ch == '0': break

def manage_users(shop):
    while True:
        print("\n--- [Users Management] ---")
        print("1-List | 2-Add | 3-Manage Addresses | 4-Search | 5-Edit | 6-Delete | 0-Back")
        ch = input("Selection: ")
        if ch == '1': 
            print_table(["ID", "Name", "Family", "Phone", "Email"], shop.get_all_users())
        elif ch == '2': 
            shop.add_user(input("Name: "), input("Family: "), input("Phone: "), input("Email: "))
        elif ch == '3':
            uid = select_user(shop)
            if uid and shop.get_user(uid): manage_user_addresses(shop, uid)
        elif ch == '4':
            keyword = input("Enter keyword to search: ")
            print_table(["ID", "Name", "Family", "Phone", "Email"], shop.search_users(keyword))
        elif ch == '5':
            uid = select_user(shop)
            if uid:
                user = shop.get_user(uid)
                shop.update_user(uid, 
                                 input(f"Name [{user[1]}]: ") or user[1], 
                                 input(f"Family [{user[2]}]: ") or user[2], 
                                 input(f"Phone [{user[3]}]: ") or user[3], 
                                 input(f"Email [{user[4]}]: ") or user[4])
                print("User updated successfully.")
        elif ch == '6':
            uid = select_user(shop)
            if uid:
                confirm = input(f"Are you sure you want to delete user ID {uid}? (y/n): ")
                if confirm.lower() == 'y':
                    if shop.delete_user(uid):
                        print("User archived successfully (Soft Delete).")
        elif ch == '0': break

def manage_products(shop):
    while True:
        print("\n--- [Product Management] ---")
        print("1-List All | 2-Add | 3-Update | 4-Delete | 5-Low Stock | 6-Browse by Category | 0-Back")
        ch = input("Selection: ")
        if ch == '1': 
            print_table(["ID", "Name", "Category", "Brand", "Price", "Stock"], shop.get_all_products())
        elif ch == '2': 
            shop.add_product(input("Name: "), input("Category: "), input("Brand: "), float(input("Price: ")), int(input("Stock: ")))
        elif ch == '3':
         
            pid = select_product(shop)
            if pid:
                prod = shop.get_product(pid)
                if prod:
                    shop.update_product(
                        pid, 
                        input(f"New Name [{prod[1]}]: ") or prod[1], 
                        input(f"New Category [{prod[2]}]: ") or prod[2], 
                        input(f"New Brand [{prod[3]}]: ") or prod[3], 
                        float(input(f"New Price [{prod[4]}]: ") or prod[4]), 
                        int(input(f"New Stock [{prod[5]}]: ") or prod[5])
                    )
                    print("Product updated successfully.")
        elif ch == '4': 
            
            pid = select_product(shop)
            if pid:
                confirm = input(f"Are you sure you want to delete product ID {pid}? (y/n): ")
                if confirm.lower() == 'y':
                    shop.delete_product(pid)
                    print("Product deleted successfully.")
        elif ch == '5': 
            print_table(["ID", "Name", "Category", "Brand", "Price", "Stock"], shop.get_low_stock())
        elif ch == '6':
            categories = shop.get_categories()
            if not categories:
                print("No categories found.")
                continue
            print("\n--- Categories ---")
            for i, cat in enumerate(categories, 1): print(f"{i}. {cat}")
            try:
                c_idx = int(input("Select category number: "))
                selected_cat = categories[c_idx - 1]
                print_table(["ID", "Name", "Category", "Brand", "Price", "Stock"], shop.get_products_by_category(selected_cat))
            except (ValueError, IndexError):
                print("Invalid selection.")
        elif ch == '0': break

def main():
    shop = Shop()
    while True:
        print("\n=== FOROOSHGAH MVP SYSTEM ===")
        print("1-Users | 2-Products | 3-Process Order | 4-Show Invoice | 0-Exit")
        ch = input("Selection: ")
        if ch == '1': manage_users(shop)
        elif ch == '2': manage_products(shop)
        elif ch == '3': 
            uid = select_user(shop)
            if uid:
                print("\n--- Select Product via Category ---")
                pid = select_product_by_category(shop)
                if pid:
                    qty = int(input("Quantity: "))
                    shop.add_order(uid, pid, qty)
                    shop.update_stock(pid, -qty)
                    print("Order saved and stock updated successfully.")
        elif ch == '4':
            uid = select_user(shop)
            if uid:
                items = shop.get_user_invoice(uid)
                print_table(["Product", "Qty", "Price", "Total"], items)
                print(f"\nGRAND TOTAL: {shop.get_invoice_total(uid)}")
        elif ch == '0': break

if __name__ == "__main__": main()
