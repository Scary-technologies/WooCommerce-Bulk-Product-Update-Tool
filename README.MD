# WooCommerce Bulk Product Update Tool

This is a Python-based GUI tool that allows you to perform bulk updates on WooCommerce products using the WooCommerce REST API. It features a user-friendly interface built with Tkinter, enabling you to easily modify product details, download product images, and more.

## Features

- **Bulk Update Product Fields**: Update various fields of multiple WooCommerce products at once, such as price, stock quantity, and more.
- **Download Product Images**: Download images of all WooCommerce products and save them locally.
- **Product Filtering**: Select specific fields to update, including custom fields.
- **Progress Tracking**: Displays progress for ongoing operations and logs the results.
- **Save and Load Settings**: Save your WooCommerce API settings locally for quick access.

## Requirements

- Python 3.x
- WooCommerce Python API (`woocommerce-api`)
- Tkinter (included with standard Python distribution)
- Requests library (`requests`)

## Installation

1. Clone this repository or download the code files.
2. Install the required dependencies using pip:
   ```sh
   pip install requests woocommerce
   ```
3. Ensure you have a WooCommerce store with REST API credentials.

## Configuration

1. The script uses a file named `woocommerce_settings.json` to save the WooCommerce store URL, consumer key, and consumer secret.
2. When you first run the application, you will need to enter your WooCommerce API credentials and save them.

## Usage

1. Run the script using Python:
   ```sh
   python woocommerce_bulk_update.py
   ```
2. The GUI will open, allowing you to enter your WooCommerce API credentials or load saved settings.
3. Select the field you wish to update from the dropdown list, provide the new value, and click **Update Products**.
4. You can also download product images or count the total number of products available in your WooCommerce store.

## Notes

- Ensure your WooCommerce store has the REST API enabled and that you have generated API keys with sufficient permissions.
- Large product catalogs may take some time to process. The progress bar and log output will help track the operation's status.

## License

This project is licensed under the MIT License.

