from woocommerce import API
import json
import tkinter as tk
from tkinter import ttk, messagebox
import concurrent.futures
import requests
import os
import time
import threading
from tkinter.font import Font
from tkinter import PhotoImage

# WooCommerce API settings
saved_settings_path = "woocommerce_settings.json"

def load_saved_settings():
    if os.path.exists(saved_settings_path):
        with open(saved_settings_path, 'r') as file:
            return json.load(file)
    return {
        "url": "https://yourstore.com",
        "consumer_key": "your_consumer_key",
        "consumer_secret": "your_consumer_secret"
    }

def save_settings(settings):
    with open(saved_settings_path, 'w') as file:
        json.dump(settings, file)

settings = load_saved_settings()

wcapi = API(
    url=settings["url"],
    consumer_key=settings["consumer_key"],
    consumer_secret=settings["consumer_secret"],
    version="wc/v3",
    timeout=10  # Increase the timeout to handle slow responses
)

# Get all products
def get_products(log_widget):
    products = []
    page = 1
    retries = 3
    while True:
        try:
            response = wcapi.get("products", params={"per_page": 100, "page": page})
            response.raise_for_status()
            page_products = response.json()
            if not page_products:
                break
            products.extend(page_products)
            page += 1
        except Exception as e:
            if retries > 0:
                retries -= 1
                log_widget.insert(tk.END, f"Error retrieving products: {e}. Retrying...\n")
                log_widget.see(tk.END)
                time.sleep(5)  # Wait before retrying
            else:
                log_widget.insert(tk.END, f"Error retrieving products after retries: {e}\n")
                log_widget.see(tk.END)
                break
    return products

# Get product fields
def get_available_fields(log_widget):
    products = get_products(log_widget)
    if products:
        return list(products[0].keys())
    return []

# Update products concurrently
def update_products(selected_field, new_value, log_widget, progress_var):
    products = get_products(log_widget)
    total_products = len(products)
    progress_var.set(0)

    def update_product(product):
        product_id = product['id']
        data = {
            selected_field: new_value
        }
        retries = 3
        while retries > 0:
            try:
                response = wcapi.put(f"products/{product_id}", data)
                response.raise_for_status()
                log_widget.insert(tk.END, f"Product with ID {product_id} updated successfully.\n")
                log_widget.see(tk.END)
                break
            except Exception as e:
                retries -= 1
                log_widget.insert(tk.END, f"Error updating product with ID {product_id}: {e}. Retrying...\n")
                log_widget.see(tk.END)
                time.sleep(3)
        progress_var.set(progress_var.get() + (1 / total_products) * 100)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(update_product, products))

# Download product images
def download_product_images(log_widget, progress_var):
    products = get_products(log_widget)
    os.makedirs("product_images", exist_ok=True)
    total_products = len(products)
    progress_var.set(0)

    def download_image(product):
        if 'images' in product and product['images']:
            image_url = product['images'][0]['src']
            image_name = f"product_images/{product['name'].replace('/', '_')}.jpg"
            retries = 3
            while retries > 0:
                try:
                    img_data = requests.get(image_url, timeout=10).content
                    with open(image_name, 'wb') as handler:
                        handler.write(img_data)
                    log_widget.insert(tk.END, f"Image for product '{product['name']}' downloaded successfully.\n")
                    log_widget.see(tk.END)
                    break
                except Exception as e:
                    retries -= 1
                    log_widget.insert(tk.END, f"Error downloading image for product '{product['name']}': {e}. Retrying...\n")
                    log_widget.see(tk.END)
                    time.sleep(3)
        progress_var.set(progress_var.get() + (1 / total_products) * 100)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(download_image, products))

# GUI using Tkinter
def create_gui(available_fields):
    root = tk.Tk()
    root.title("WooCommerce Product Update")
    root.geometry("800x700")
    root.resizable(False, False)
    root.configure(bg='#f8f9fa')
    
    # Header Frame
    header_frame = ttk.Frame(root)
    header_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
    header_label = ttk.Label(header_frame, text="WooCommerce Bulk Product Update Tool", font=("Helvetica", 18, "bold"))
    header_label.pack(pady=5)

    # Sidebar Frame for actions
    sidebar_frame = ttk.Frame(root)
    sidebar_frame.grid(row=1, column=2, rowspan=7, padx=10, pady=10, sticky='ns')

    # URL Entry
    url_label = ttk.Label(root, text="Store URL:", font=("Helvetica", 10, "bold"), background='#f8f9fa')
    url_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
    url_entry = ttk.Entry(root, width=50)
    url_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
    url_entry.insert(0, settings["url"])

    # Consumer Key Entry
    key_label = ttk.Label(root, text="Consumer Key:", font=("Helvetica", 10, "bold"), background='#f8f9fa')
    key_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
    key_entry = ttk.Entry(root, width=50)
    key_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
    key_entry.insert(0, settings["consumer_key"])

    # Consumer Secret Entry
    secret_label = ttk.Label(root, text="Consumer Secret:", font=("Helvetica", 10, "bold"), background='#f8f9fa')
    secret_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
    secret_entry = ttk.Entry(root, width=50, show="*")
    secret_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
    secret_entry.insert(0, settings["consumer_secret"])

    # Save settings button
    def on_save_settings():
        settings["url"] = url_entry.get()
        settings["consumer_key"] = key_entry.get()
        settings["consumer_secret"] = secret_entry.get()
        save_settings(settings)
        messagebox.showinfo("Success", "Settings saved successfully.")
    
    save_settings_button = ttk.Button(sidebar_frame, text="Save Settings", command=on_save_settings)
    save_settings_button.pack(pady=10, fill='x')

    # Field selection
    field_label = ttk.Label(root, text="Select Field:", font=("Helvetica", 10, "bold"), background='#f8f9fa')
    field_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')
    field_combobox = ttk.Combobox(root, values=available_fields, state="readonly")
    field_combobox.grid(row=4, column=1, padx=10, pady=10, sticky='w')

    # New value - dynamic input based on selected field
    value_label = ttk.Label(root, text="New Value:", font=("Helvetica", 10, "bold"), background='#f8f9fa')
    value_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')
    value_entry = ttk.Entry(root)
    value_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
    

    def on_field_select(event):
        selected_field = field_combobox.get()
        value_entry.grid_forget()
        if selected_field == "price":
            value_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
            value_entry.delete(0, tk.END)
            value_entry.insert(0, "Enter new price (e.g., 19.99)")
        elif selected_field == "stock_quantity":
            value_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
            value_entry.delete(0, tk.END)
            value_entry.insert(0, "Enter stock quantity (e.g., 50)")
        elif selected_field == "categories":
            value_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
            value_entry.delete(0, tk.END)
            value_entry.insert(0, "Enter category IDs (comma-separated, e.g., 1,2,3)")
        else:
            value_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
            value_entry.delete(0, tk.END)
            value_entry.insert(0, "Enter new value")

    field_combobox.bind("<<ComboboxSelected>>", on_field_select)

    # Log output
    log_frame = ttk.LabelFrame(root, text="Log Output", padding=(10, 10))
    log_frame.grid(row=9, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    log_text = tk.Text(log_frame, height=15, width=80, wrap='word', state='disabled', bg='#ffffff', fg='#000000')
    log_text.pack(fill='both', expand=True)

    # Progress bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=10, column=0, columnspan=3, padx=10, pady=10, sticky='we')

    # Update button
    def on_update_click():
        selected_field = field_combobox.get()
        new_value = value_entry.get()
        if not selected_field or not new_value:
            messagebox.showerror("Error", "Please fill in all fields.")
        else:
            log_text.config(state='normal')
            threading.Thread(target=lambda: update_products(selected_field, new_value, log_text, progress_var), daemon=True).start()
            log_text.config(state='disabled')
            messagebox.showinfo("Success", "Update process started. Check logs for progress.")
    
    update_button = ttk.Button(sidebar_frame, text="Update Products", command=on_update_click)
    update_button.pack(pady=10, fill='x')

    # Download images button
    def on_download_images_click():
        log_text.config(state='normal')
        threading.Thread(target=lambda: download_product_images(log_text, progress_var), daemon=True).start()
        log_text.config(state='disabled')
        messagebox.showinfo("Success", "Download process started. Check logs for progress.")

    download_images_button = ttk.Button(sidebar_frame, text="Download Images", command=on_download_images_click)
    download_images_button.pack(pady=10, fill='x')

    # Count products button
    def on_count_products():
        products = get_products(log_text)
        messagebox.showinfo("Product Count", f"Total Products: {len(products)}")

    count_products_button = ttk.Button(sidebar_frame, text="Count Products", command=on_count_products)
    count_products_button.pack(pady=10, fill='x')

    root.mainloop()

if __name__ == '__main__':
    log_text_placeholder = None
    available_fields = get_available_fields(None)
    create_gui(available_fields)
