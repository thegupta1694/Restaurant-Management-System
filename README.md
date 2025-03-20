# Casa Delizia Restaurant Management System

A streamlined restaurant management solution built with Streamlit and SQLite, designed to solve the operational challenges at Casa Delizia restaurant.

## Overview

This application provides a comprehensive system for managing all aspects of restaurant operations, including table management, order processing, menu management, billing, inventory tracking, and reservations. It's built as a lightweight yet powerful alternative to the original C++/Qt implementation, using Python's Streamlit framework for rapid deployment and ease of use.

## Features

### Home Dashboard
- Quick overview of restaurant status
- Key metrics including pending orders, available tables, low inventory items, and today's reservations

![image](https://github.com/user-attachments/assets/bfd33eac-1259-4a62-b73c-4925560e1431)

### Table Management
- Visual representation of all tables
- Table status tracking (Available/Occupied)
- Ability to add new tables with custom capacities
- One-click table status changes

![image](https://github.com/user-attachments/assets/9c0fe7e1-89c9-41e5-bc63-6e78db02ec7f)

### Order Processing
- Create new orders for occupied tables
- Add menu items with quantities and special instructions
- Track order status (Pending/Completed)
- Order cancellation functionality
- Automatic bill generation upon order completion

![image](https://github.com/user-attachments/assets/cc812821-8a57-4eaa-be1a-29b471516573)

### Menu Management
- Categorized menu display
- Item availability toggling
- Add new menu items with descriptions and prices
- Remove menu items
- Categorization of menu items

![image](https://github.com/user-attachments/assets/d1b693cb-987a-440c-88fb-ffb5948d4d77)

### Billing
- Process payments (Cash/Card)
- View unpaid bills
- Payment history tracking
- Automatic bill generation from completed orders

![image](https://github.com/user-attachments/assets/37c5b150-88b7-4aab-9e93-cc89a0dad476)

### Inventory Management
- Track stock levels for ingredients
- Set threshold alerts for low inventory
- Update inventory quantities
- Add new inventory items

![image](https://github.com/user-attachments/assets/121bbb3d-e5b6-4b52-a691-2f00068cb9b2)

### Reservations
- Schedule table reservations
- View today's reservations
- Seat guests upon arrival
- Cancel reservations
- Prevent double-booking

![image](https://github.com/user-attachments/assets/b44c3cac-2158-46bd-b33f-5ed785209153)

## Installation and Setup

1. Clone this repository
```bash
git clone https://github.com/thegupta1694/Restaurant-Management-System.git
cd casa-delizia-management
```

2. Install the required dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run app.py
```

## Requirements

- Python 3.7+
- Streamlit
- SQLite3
- Pandas

## System Architecture

The application follows a simplified MVC (Model-View-Controller) architecture:

- **Models**: Implemented as SQLite database tables (tables, menu_items, orders, order_items, bills, inventory, reservations)
- **Views**: Streamlit UI components rendering data from the database
- **Controllers**: Python functions that handle user interactions and update the database

## Database Schema

The application uses SQLite for data persistence with the following tables:

- **menu_items**: Stores all menu items with their categories, prices, and availability
- **tables**: Tracks all restaurant tables with their capacity and current status
- **orders**: Contains all customer orders linked to specific tables
- **order_items**: Stores individual items within each order
- **bills**: Maintains billing information for completed orders
- **inventory**: Tracks stock levels for ingredients and supplies
- **reservations**: Manages table reservations and their status

## Future Enhancements

- User authentication and role-based access
- Detailed sales reporting and analytics
- Kitchen display system
- Customer loyalty program integration
- Online ordering integration
- Mobile app version

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- Streamlit for the amazing framework
- SQLite for providing a simple yet powerful database solution
- Casa Delizia restaurant for the inspiration
