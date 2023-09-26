import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.tix import Tree

# Create a connection to the SQLite database (or create a new one if it doesn't exist)
conn = sqlite3.connect('inventory.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store product information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL,
        quantity INTEGER
    )
''')

def add_product():
    name = name_entry.get()
    description = desc_entry.get()
    price = price_entry.get()
    quantity = quantity_entry.get()
    
    cursor.execute('''
        INSERT INTO products (name, description, price, quantity)
        VALUES (?, ?, ?, ?)
    ''', (name, description, price, quantity))
    conn.commit()
    
    # Show a success message
    messagebox.showinfo("Success", "Product added successfully.")
    
    # Clear the form entries
    clear_entries()

def view_products():
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    # Clear the treeview widget
    for row in products_tree.get_children():
        products_tree.delete(row)
    
    for product in products:
        products_tree.insert('', 'end', values=product)

def clear_entries():
    name_entry.delete(0, 'end')
    desc_entry.delete(0, 'end')
    price_entry.delete(0, 'end')
    quantity_entry.delete(0, 'end')

def save_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            cursor.execute('SELECT * FROM products')
            products = cursor.fetchall()
            for product in products:
                file.write(f"ID: {product[0]}\n")
                file.write(f"Name: {product[1]}\n")
                file.write(f"Description: {product[2]}\n")
                file.write(f"Price: {product[3]}\n")
                file.write(f"Quantity: {product[4]}\n")
                file.write("\n")
        messagebox.showinfo("Success", "Data saved to file.")

def load_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            # Clear existing data from the database
            cursor.execute('DELETE FROM products')
            conn.commit()

            with open(file_path, 'r') as file:
                product_data = []
                current_product = {}
                for line in file:
                    line = line.strip()
                    if line:
                        key, value = line.split(': ', 1)
                        current_product[key] = value
                    else:
                        if current_product:
                            name = current_product.get('Name', '')
                            description = current_product.get('Description', '')
                            price = float(current_product.get('Price', '0.0'))
                            quantity = int(current_product.get('Quantity', '0'))
                            product_data.append((name, description, price, quantity))
                            current_product = {}

                if current_product:
                    name = current_product.get('Name', '')
                    description = current_product.get('Description', '')
                    price = float(current_product.get('Price', '0.0'))
                    quantity = int(current_product.get('Quantity', '0'))
                    product_data.append((name, description, price, quantity))

                # Insert the loaded data into the database
                cursor.executemany('''
                    INSERT INTO products (name, description, price, quantity)
                    VALUES (?, ?, ?, ?)
                ''', product_data)
                conn.commit()

            # Show a success message
            messagebox.showinfo("Success", "Data loaded from file.")

            # Refresh the product list
            view_products()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create a function to update a product
def update_product():
    selected_item = products_tree.selection()
    if selected_item:
        selected_item = selected_item[0]
        new_name = name_entry.get()
        new_description = desc_entry.get()
        new_price = price_entry.get()
        new_quantity = quantity_entry.get()
        
        cursor.execute('''
            UPDATE products
            SET name=?, description=?, price=?, quantity=?
            WHERE id=?
        ''', (new_name, new_description, new_price, new_quantity, selected_item))
        conn.commit()
        
        # Show a success message
        messagebox.showinfo("Success", "Product updated successfully.")
        
        # Clear the form entries and refresh the product list
        clear_entries()
        view_products()
    else:
        messagebox.showwarning("Warning", "Please select a product to update.")

# Create a function to delete a product
def delete_product():
    selected_item = products_tree.selection()
    if selected_item:
        selected_item = selected_item[0]
        cursor.execute('DELETE FROM products WHERE id=?', (selected_item,))
        conn.commit()
        
        # Show a success message
        messagebox.showinfo("Success", "Product deleted successfully.")
        
        # Refresh the product list
        view_products()
    else:
        messagebox.showwarning("Warning", "Please select a product to delete.")

# Create a function to search for products
def search_products():
    search_term = search_entry.get()
    cursor.execute('SELECT * FROM products WHERE name LIKE ? OR description LIKE ?', ('%' + search_term + '%', '%' + search_term + '%'))
    products = cursor.fetchall()
    
    # Clear the treeview widget
    for row in products_tree.get_children():
        products_tree.delete(row)
    
    for product in products:
        products_tree.insert('', 'end', values=product)

# Create a function to sort products by a column
def sort_products(column_index):
    products = [(Tree.item(item)['values'], item) for item in products_tree.get_children()]
    products.sort(key=lambda x: x[0][column_index])
    
    # Clear the treeview widget
    for row in products_tree.get_children():
        products_tree.delete(row)
    
    for product, item in products:
        products_tree.insert('', 'end', values=product, iid=item)

# Create a function to calculate the total value of all products
def calculate_total_value():
    cursor.execute('SELECT SUM(price * quantity) FROM products')
    total_value = cursor.fetchone()[0]
    if total_value is not None:
        status_label.config(text=f"Total Value: ${total_value:.2f}")
    else:
        status_label.config(text="Total Value: $0.00")

# Create a function to generate and display a bill
def generate_bill():
    selected_items = products_tree.selection()
    
    if not selected_items:
        messagebox.showwarning("Warning", "Please select products to include in the bill.")
        return
    
    bill_content = "Bill Details:\n"
    total_price = 0.0
    
    for item in selected_items:
        product = products_tree.item(item)['values']
        product_id, name, description, price, quantity = product
        total_price += (price * quantity)
        
        bill_content += f"Product ID: {product_id}\n"
        bill_content += f"Name: {name}\n"
        bill_content += f"Description: {description}\n"
        bill_content += f"Price: {price:.2f}\n"
        bill_content += f"Quantity: {quantity}\n"
        bill_content += "-----------------------------------\n"
    
    bill_content += f"Total Price: {total_price:.2f}\n"
    
    # Display the bill content in a message box
    messagebox.showinfo("Bill Details", bill_content)

# Create the main application window
root = tk.Tk()
root.title("Inventory Management System")
root.geometry("1000x600")  # Adjust the window size
root.resizable(True, True)  # Disable window resizing

# Set a background color for the entire UI
root.configure(bg="#f2f2f2")

# Create labels and entry widgets for product details
font_style = ("Arial", 12)

name_label = ttk.Label(root, text="Name:", font=font_style, background="#f2f2f2")
name_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

name_entry = ttk.Entry(root, font=font_style, width=40)
name_entry.grid(row=0, column=1, padx=20, pady=(20, 10))

desc_label = ttk.Label(root, text="Description:", font=font_style, background="#f2f2f2")
desc_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

desc_entry = ttk.Entry(root, font=font_style, width=40)
desc_entry.grid(row=1, column=1, padx=20, pady=10)

price_label = ttk.Label(root, text="Price:", font=font_style, background="#f2f2f2")
price_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

price_entry = ttk.Entry(root, font=font_style, width=40)
price_entry.grid(row=2, column=1, padx=20, pady=10)

quantity_label = ttk.Label(root, text="Quantity:", font=font_style, background="#f2f2f2")
quantity_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

quantity_entry = ttk.Entry(root, font=font_style, width=40)
quantity_entry.grid(row=3, column=1, padx=20, pady=10)

# Create a frame for product management buttons (Add, Update, Delete)
product_buttons_frame = ttk.Frame(root)
product_buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)

add_button = ttk.Button(product_buttons_frame, text="Add Product", command=add_product, style="TButton")
add_button.grid(row=0, column=0, padx=5)

update_button = ttk.Button(product_buttons_frame, text="Update Product", command=update_product, style="TButton")
update_button.grid(row=0, column=1, padx=5)

delete_button = ttk.Button(product_buttons_frame, text="Delete Product", command=delete_product, style="TButton")
delete_button.grid(row=0, column=2, padx=5)

# Create a frame for data management buttons (View, Save, Load)
data_buttons_frame = ttk.Frame(root)
data_buttons_frame.grid(row=7, column=0, columnspan=2, pady=20)

view_button = ttk.Button(data_buttons_frame, text="View Products", command=view_products, style="TButton")
view_button.grid(row=0, column=0, padx=5)

clear_button = ttk.Button(data_buttons_frame, text="Clear Entries", command=clear_entries, style="TButton")
clear_button.grid(row=0, column=1, padx=5)

save_button = ttk.Button(data_buttons_frame, text="Save to File", command=save_to_file, style="TButton")
save_button.grid(row=0, column=2, padx=5)

load_button = ttk.Button(data_buttons_frame, text="Load from File", command=load_from_file, style="TButton")
load_button.grid(row=0, column=3, padx=5)

# Create a button for printing the bill
print_bill_button = ttk.Button(data_buttons_frame, text="Print Bill", command=generate_bill, style="TButton")
print_bill_button.grid(row=0, column=4, padx=5)

# Create labels and entry field for searching products
search_label = ttk.Label(root, text="Search Products:", font=font_style, background="#f2f2f2")
search_label.grid(row=11, column=0, padx=20, pady=10, sticky="w")

search_entry = ttk.Entry(root, font=font_style, width=40)
search_entry.grid(row=11, column=1, padx=20, pady=10)

search_button = ttk.Button(root, text="Search", command=search_products, style="TButton")
search_button.grid(row=12, column=0, columnspan=2, pady=10)

# Create a status label
status_label = ttk.Label(root, text="", foreground="green", background="#f2f2f2", font=("Arial", 12))
status_label.grid(row=13, column=0, columnspan=2, pady=10)

# Create a treeview widget to display products with improved styling and vertical scrollbar
products_tree = ttk.Treeview(root, columns=("ID", "Name", "Description", "Price", "Quantity"), show="headings")
products_tree.heading("#1", text="ID")
products_tree.heading("#2", text="Name")
products_tree.heading("#3", text="Description")
products_tree.heading("#4", text="Price")
products_tree.heading("#5", text="Quantity")

# Create a vertical scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=products_tree.yview)
scrollbar.grid(row=14, column=2, sticky="ns")
products_tree.configure(yscrollcommand=scrollbar.set)

products_tree.grid(row=14, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

# Configure grid weights to make the treeview expandable
root.grid_rowconfigure(14, weight=1)
root.grid_columnconfigure(1, weight=1)

# Start the main event loop
root.mainloop()
