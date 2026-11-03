from SHOP_ORM import ShopManager

def select_product(shop):
    keyword = input("Search product (Name/Category/Brand): ")
    products = shop.search_products(keyword)
    if not products:
        print("No products found.")
        return None
    
    print("\n--- [Products List] ---")
    for p in products:
        print(f"ID: {p['id']} | Name: {p['name']} | Category: {p['category']} | Brand: {p['brand']} | Price: {p['price']} | Stock: {p['stock']}")
    print("-" * 60)
    
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
    print("-" * 60)
    
    try:
        return int(input("Enter the product ID from the list above: "))
    except ValueError:
        print("Invalid selection.")
        return None

def run_user_dashboard(shop, user):
    while True:
        print(f"\n--- User Dashboard (Logged in as: {user['username']}) ---")
        
        
        print("1. Search & View Products")
        print("2. Browse by Category")
        

        if user['is_admin']:
            print("3. [Admin] Add Product")
            print("4. [Admin] Update Product Stock")
            print("5. [Admin] Deactivate User (Soft Delete)")
            
        print("0. Logout")
        
        sub_choice = input("Select an option: ")
        
        if sub_choice == '1':
            pid = select_product(shop)
            if pid:
                print(f"Selected Product ID: {pid}")
        elif sub_choice == '2':
            pid = select_product_by_category(shop)
            if pid:
                print(f"Selected Product ID: {pid}")
        elif sub_choice == '3' and user['is_admin']:
            name = input("Product Name: ")
            category = input("Category: ")
            brand = input("Brand: ")
            price = float(input("Price: "))
            stock = int(input("Stock: "))
            shop.add_product(name, category, brand, price, stock)
            print("Product added successfully.")
        elif sub_choice == '4' and user['is_admin']:
            pid = select_product(shop)
            if pid:
                new_stock = int(input("Enter new stock value: "))
                if shop.update_product_stock(pid, new_stock):
                    print("Stock updated successfully.")
                else:
                    print("Product not found.")
        elif sub_choice == '5' and user['is_admin']:
            uid = int(input("Enter User ID to deactivate: "))
            if shop.soft_delete_user(uid):
                print("User deactivated successfully.")
            else:
                print("User not found.")
        elif sub_choice == '0':
            print("Logging out...")
            break
        else:
            print("Invalid option.")


def main():
    shop = ShopManager()
    
    while True:
        print("\n=== Forooshgah System ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            username = input("Username: ")
            password = input("Password: ")
            user = shop.login_user(username, password)
            
            if not user:
                print("Login failed or account inactive.")
            else:
                print(f"Welcome back, {user['username']}!")
                run_user_dashboard(shop, user) 
                
        elif choice == '2':
            username = input("Choose Username: ")
            password = input("Choose Password: ")
            is_admin = input("Is admin? (y/n): ").lower() == 'y'
            
            if shop.register_user(username, password, is_admin):
                print("Registration successful! Logging you in automatically...")
                user = shop.login_user(username, password)
                if user:
                    print(f"Welcome, {user['username']}!")
                    run_user_dashboard(shop, user)  
            else:
                print("Username already exists.")
                
        elif choice == '3':
            print("Exiting Forooshgah. Goodbye!")
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
