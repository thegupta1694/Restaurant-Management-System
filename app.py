import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import json
import os

# Ensure database directory exists
if not os.path.exists('database'):
    os.makedirs('database')

# Initialize database
def init_db():
    conn = sqlite3.connect('database/restaurant.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        available BOOLEAN DEFAULT 1
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY,
        capacity INTEGER NOT NULL,
        status TEXT DEFAULT 'Available'
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        table_id INTEGER,
        customer_name TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (table_id) REFERENCES tables (id)
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        menu_item_id INTEGER,
        quantity INTEGER DEFAULT 1,
        notes TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY,
        order_id INTEGER UNIQUE,
        amount REAL NOT NULL,
        payment_method TEXT,
        status TEXT DEFAULT 'Unpaid',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        item_name TEXT NOT NULL UNIQUE,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL,
        threshold INTEGER DEFAULT 10
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY,
        table_id INTEGER,
        customer_name TEXT NOT NULL,
        phone TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        party_size INTEGER NOT NULL,
        status TEXT DEFAULT 'Confirmed',
        FOREIGN KEY (table_id) REFERENCES tables (id)
    )
    ''')
    
    # Add some initial data if tables are empty
    c.execute("SELECT COUNT(*) FROM menu_items")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO menu_items (name, category, price, description) VALUES (?, ?, ?, ?)", [
            ("Margherita Pizza", "Pizza", 12.99, "Classic cheese and tomato pizza"),
            ("Spaghetti Carbonara", "Pasta", 14.99, "Creamy pasta with pancetta"),
            ("Tiramisu", "Dessert", 7.99, "Coffee-flavored Italian dessert"),
            ("House Wine", "Drinks", 6.99, "Red wine by the glass"),
            ("Caesar Salad", "Appetizer", 9.99, "Romaine lettuce with Caesar dressing")
        ])
    
    c.execute("SELECT COUNT(*) FROM tables")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO tables (capacity, status) VALUES (?, ?)", [
            (2, "Available"),
            (4, "Available"),
            (4, "Available"),
            (6, "Available"),
            (8, "Available")
        ])
    
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO inventory (item_name, quantity, unit, threshold) VALUES (?, ?, ?, ?)", [
            ("Flour", 50, "kg", 10),
            ("Tomatoes", 30, "kg", 5),
            ("Mozzarella", 20, "kg", 5),
            ("Olive Oil", 15, "liters", 3),
            ("Basil", 2, "kg", 0.5)
        ])
    
    conn.commit()
    conn.close()

# Initialize session state
def init_session():
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'current_order' not in st.session_state:
        st.session_state.current_order = None
    if 'current_table' not in st.session_state:
        st.session_state.current_table = None

# Navigation
def navigation():
    st.sidebar.title("Casa Delizia")
    st.sidebar.markdown("---")
    if st.sidebar.button("🏠 Home"):
        st.session_state.page = 'home'
    if st.sidebar.button("🍽️ Table Management"):
        st.session_state.page = 'tables'
    if st.sidebar.button("📋 Order Processing"):
        st.session_state.page = 'orders'
    if st.sidebar.button("🍕 Menu Management"):
        st.session_state.page = 'menu'
    if st.sidebar.button("💰 Billing"):
        st.session_state.page = 'billing'
    if st.sidebar.button("📦 Inventory"):
        st.session_state.page = 'inventory'
    if st.sidebar.button("📞 Reservations"):
        st.session_state.page = 'reservations'
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 Casa Delizia")

# Home page
def home_page():
    st.title("Casa Delizia Restaurant Management System")
    st.markdown("""
    Welcome to the Casa Delizia Restaurant Management System. This system helps you manage:
    - Table reservations
    - Order processing
    - Menu management
    - Billing
    - Inventory tracking
    
    Use the sidebar to navigate through different features.
    """)
    
    # Display some quick stats
    conn = sqlite3.connect('database/restaurant.db')
    
    # Pending orders
    pending_orders = pd.read_sql("SELECT COUNT(*) as count FROM orders WHERE status='Pending'", conn)
    
    # Available tables
    available_tables = pd.read_sql("SELECT COUNT(*) as count FROM tables WHERE status='Available'", conn)
    
    # Low inventory items
    low_inventory = pd.read_sql("SELECT COUNT(*) as count FROM inventory WHERE quantity <= threshold", conn)
    
    # Today's reservations
    today = datetime.now().strftime('%Y-%m-%d')
    todays_reservations = pd.read_sql(f"SELECT COUNT(*) as count FROM reservations WHERE date='{today}'", conn)
    
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pending Orders", pending_orders['count'].iloc[0])
    with col2:
        st.metric("Available Tables", available_tables['count'].iloc[0])
    with col3:
        st.metric("Low Inventory Items", low_inventory['count'].iloc[0])
    with col4:
        st.metric("Today's Reservations", todays_reservations['count'].iloc[0])

# Table Management
def tables_page():
    st.title("Table Management")
    
    conn = sqlite3.connect('database/restaurant.db')
    tables = pd.read_sql("SELECT * FROM tables", conn)
    
    # Display tables in a grid
    col1, col2, col3 = st.columns(3)
    for i, row in tables.iterrows():
        with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
            with st.container():
                st.markdown(f"### Table {row['id']}")
                st.markdown(f"**Capacity:** {row['capacity']} people")
                status_color = "green" if row['status'] == "Available" else "red" if row['status'] == "Occupied" else "orange"
                st.markdown(f"**Status:** <span style='color:{status_color}'>{row['status']}</span>", unsafe_allow_html=True)
                
                if row['status'] == "Available":
                    if st.button(f"Occupy Table {row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE tables SET status = 'Occupied' WHERE id = ?", (row['id'],))
                        conn.commit()
                        st.success(f"Table {row['id']} is now occupied")
                        st.experimental_rerun()
                else:
                    if st.button(f"Free Table {row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE tables SET status = 'Available' WHERE id = ?", (row['id'],))
                        conn.commit()
                        st.success(f"Table {row['id']} is now available")
                        st.experimental_rerun()
    
    conn.close()
    
    # Add new table
    st.markdown("---")
    st.subheader("Add New Table")
    with st.form("add_table_form"):
        capacity = st.number_input("Capacity", min_value=1, max_value=20, value=4)
        submit = st.form_submit_button("Add Table")
        
        if submit:
            conn = sqlite3.connect('database/restaurant.db')
            c = conn.cursor()
            c.execute("INSERT INTO tables (capacity, status) VALUES (?, 'Available')", (capacity,))
            conn.commit()
            conn.close()
            st.success("New table added successfully!")
            st.experimental_rerun()

# Order Processing
def orders_page():
    st.title("Order Processing")
    
    conn = sqlite3.connect('database/restaurant.db')
    
    # Select table for new order
    tables = pd.read_sql("SELECT * FROM tables WHERE status = 'Occupied'", conn)
    if len(tables) == 0:
        st.warning("No occupied tables available. Please occupy a table first.")
        conn.close()
        return
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Create New Order")
        with st.form("new_order_form"):
            table_id = st.selectbox("Select Table", tables['id'].tolist())
            customer_name = st.text_input("Customer Name")
            
            submit_order = st.form_submit_button("Create Order")
            if submit_order:
                c = conn.cursor()
                c.execute("INSERT INTO orders (table_id, customer_name, status) VALUES (?, ?, 'Pending')", 
                          (table_id, customer_name))
                conn.commit()
                st.session_state.current_order = c.lastrowid
                st.session_state.current_table = table_id
                st.success(f"Order created for table {table_id}")
                st.experimental_rerun()
    
    # Add items to order
    if st.session_state.current_order:
        order_id = st.session_state.current_order
        table_id = st.session_state.current_table
        
        st.subheader(f"Order #{order_id} for Table {table_id}")
        
        menu_items = pd.read_sql("SELECT * FROM menu_items WHERE available = 1", conn)
        with st.form("add_item_form"):
            item_id = st.selectbox("Select Menu Item", menu_items['id'].tolist(), 
                                  format_func=lambda x: menu_items.loc[menu_items['id'] == x, 'name'].iloc[0])
            quantity = st.number_input("Quantity", min_value=1, value=1)
            notes = st.text_area("Special Instructions")
            
            submit_item = st.form_submit_button("Add to Order")
            if submit_item:
                c = conn.cursor()
                c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, notes) VALUES (?, ?, ?, ?)",
                         (order_id, item_id, quantity, notes))
                conn.commit()
                st.success("Item added to order!")
                st.experimental_rerun()
        
        # Show current order items
        order_items = pd.read_sql(f"""
            SELECT oi.id, mi.name, oi.quantity, mi.price, (oi.quantity * mi.price) as subtotal, oi.notes
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE oi.order_id = {order_id}
        """, conn)
        
        if not order_items.empty:
            st.subheader("Current Order Items")
            st.dataframe(order_items[['name', 'quantity', 'price', 'subtotal', 'notes']])
            
            total = order_items['subtotal'].sum()
            st.markdown(f"**Total: ${total:.2f}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Complete Order"):
                    c = conn.cursor()
                    c.execute("UPDATE orders SET status = 'Completed' WHERE id = ?", (order_id,))
                    conn.commit()
                    
                    # Create bill
                    c.execute("INSERT INTO bills (order_id, amount, status) VALUES (?, ?, 'Unpaid')", 
                              (order_id, total))
                    conn.commit()
                    
                    st.session_state.current_order = None
                    st.session_state.current_table = None
                    st.success("Order completed and bill created!")
                    st.experimental_rerun()
            with col2:
                if st.button("Cancel Order"):
                    c = conn.cursor()
                    c.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
                    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
                    conn.commit()
                    st.session_state.current_order = None
                    st.session_state.current_table = None
                    st.success("Order cancelled!")
                    st.experimental_rerun()
    
    # Display pending orders
    st.markdown("---")
    st.subheader("Pending Orders")
    pending_orders = pd.read_sql("""
        SELECT o.id, o.table_id, o.customer_name, o.created_at, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.status = 'Pending'
        GROUP BY o.id
    """, conn)
    
    if not pending_orders.empty:
        st.dataframe(pending_orders)
    else:
        st.info("No pending orders")
    
    conn.close()

# Menu Management
def menu_page():
    st.title("Menu Management")
    
    conn = sqlite3.connect('database/restaurant.db')
    
    # Display current menu
    menu_items = pd.read_sql("SELECT * FROM menu_items", conn)
    
    st.subheader("Current Menu")
    categories = menu_items['category'].unique()
    for category in categories:
        st.markdown(f"### {category}")
        category_items = menu_items[menu_items['category'] == category]
        
        cols = st.columns(3)
        for i, (_, item) in enumerate(category_items.iterrows()):
            with cols[i % 3]:
                st.markdown(f"**{item['name']}** - ${item['price']:.2f}")
                st.markdown(f"*{item['description']}*")
                status = "Available" if item['available'] else "Unavailable"
                status_color = "green" if item['available'] else "red"
                st.markdown(f"Status: <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if item['available']:
                        if st.button(f"Mark Unavailable {item['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE menu_items SET available = 0 WHERE id = ?", (item['id'],))
                            conn.commit()
                            st.experimental_rerun()
                    else:
                        if st.button(f"Mark Available {item['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE menu_items SET available = 1 WHERE id = ?", (item['id'],))
                            conn.commit()
                            st.experimental_rerun()
                with col2:
                    if st.button(f"Delete {item['id']}"):
                        c = conn.cursor()
                        c.execute("DELETE FROM menu_items WHERE id = ?", (item['id'],))
                        conn.commit()
                        st.experimental_rerun()
    
    # Add new menu item
    st.markdown("---")
    st.subheader("Add New Menu Item")
    with st.form("add_menu_item_form"):
        name = st.text_input("Name")
        category = st.selectbox("Category", list(categories) + ["New Category"])
        if category == "New Category":
            category = st.text_input("New Category Name")
        price = st.number_input("Price", min_value=0.01, step=0.01, format="%.2f")
        description = st.text_area("Description")
        available = st.checkbox("Available", value=True)
        
        submit = st.form_submit_button("Add Menu Item")
        if submit:
            c = conn.cursor()
            c.execute("INSERT INTO menu_items (name, category, price, description, available) VALUES (?, ?, ?, ?, ?)",
                     (name, category, price, description, available))
            conn.commit()
            st.success("New menu item added successfully!")
            st.experimental_rerun()
    
    conn.close()

# Billing
def billing_page():
    st.title("Billing")
    
    conn = sqlite3.connect('database/restaurant.db')
    
    # Display unpaid bills
    unpaid_bills = pd.read_sql("""
        SELECT b.id, o.table_id, o.customer_name, b.amount, b.created_at
        FROM bills b
        JOIN orders o ON b.order_id = o.id
        WHERE b.status = 'Unpaid'
    """, conn)
    
    st.subheader("Unpaid Bills")
    if not unpaid_bills.empty:
        for _, bill in unpaid_bills.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**Bill #{bill['id']}** - Table {bill['table_id']} - {bill['customer_name']}")
                    st.markdown(f"Amount: ${bill['amount']:.2f}")
                    st.markdown(f"Created: {bill['created_at']}")
                with col2:
                    if st.button(f"Pay Cash #{bill['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE bills SET status = 'Paid', payment_method = 'Cash' WHERE id = ?", (bill['id'],))
                        conn.commit()
                        st.success(f"Bill #{bill['id']} paid with cash")
                        st.experimental_rerun()
                with col3:
                    if st.button(f"Pay Card #{bill['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE bills SET status = 'Paid', payment_method = 'Card' WHERE id = ?", (bill['id'],))
                        conn.commit()
                        st.success(f"Bill #{bill['id']} paid with card")
                        st.experimental_rerun()
    else:
        st.info("No unpaid bills")
    
    # Display recent payments
    st.markdown("---")
    st.subheader("Recent Payments")
    recent_payments = pd.read_sql("""
        SELECT b.id, o.table_id, o.customer_name, b.amount, b.payment_method, b.created_at
        FROM bills b
        JOIN orders o ON b.order_id = o.id
        WHERE b.status = 'Paid'
        ORDER BY b.created_at DESC
        LIMIT 10
    """, conn)
    
    if not recent_payments.empty:
        st.dataframe(recent_payments)
    else:
        st.info("No recent payments")
    
    conn.close()

# Inventory Management
def inventory_page():
    st.title("Inventory Management")
    
    conn = sqlite3.connect('database/restaurant.db')
    
    # Display current inventory
    inventory = pd.read_sql("SELECT * FROM inventory", conn)
    
    st.subheader("Current Inventory")
    for _, item in inventory.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            status_color = "red" if item['quantity'] <= item['threshold'] else "green"
            st.markdown(f"**{item['item_name']}**: <span style='color:{status_color}'>{item['quantity']} {item['unit']}</span>", unsafe_allow_html=True)
            if item['quantity'] <= item['threshold']:
                st.warning(f"Low stock! Below threshold of {item['threshold']} {item['unit']}")
        with col2:
            if st.button(f"Update {item['id']}"):
                st.session_state.update_item = item['id']
        with col3:
            if st.button(f"Delete {item['id']}"):
                c = conn.cursor()
                c.execute("DELETE FROM inventory WHERE id = ?", (item['id'],))
                conn.commit()
                st.success(f"Item {item['item_name']} deleted")
                st.experimental_rerun()
    
    # Update inventory item
    if 'update_item' in st.session_state and st.session_state.update_item:
        item_id = st.session_state.update_item
        item = inventory[inventory['id'] == item_id].iloc[0]
        
        st.markdown("---")
        st.subheader(f"Update {item['item_name']}")
        
        with st.form("update_inventory_form"):
            new_quantity = st.number_input("New Quantity", min_value=0, value=int(item['quantity']))
            new_threshold = st.number_input("New Threshold", min_value=0, value=int(item['threshold']))
            
            submit = st.form_submit_button("Update")
            if submit:
                c = conn.cursor()
                c.execute("UPDATE inventory SET quantity = ?, threshold = ? WHERE id = ?",
                         (new_quantity, new_threshold, item_id))
                conn.commit()
                st.success(f"{item['item_name']} updated successfully!")
                st.session_state.update_item = None
                st.experimental_rerun()
    
    # Add new inventory item
    st.markdown("---")
    st.subheader("Add New Inventory Item")
    with st.form("add_inventory_form"):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=0)
        unit = st.selectbox("Unit", ["kg", "liters", "pieces", "bottles", "bags"])
        threshold = st.number_input("Alert Threshold", min_value=0)
        
        submit = st.form_submit_button("Add Item")
        if submit:
            c = conn.cursor()
            c.execute("INSERT INTO inventory (item_name, quantity, unit, threshold) VALUES (?, ?, ?, ?)",
                     (item_name, quantity, unit, threshold))
            conn.commit()
            st.success("New inventory item added successfully!")
            st.experimental_rerun()
    
    conn.close()

# Reservations
def reservations_page():
    st.title("Table Reservations")
    
    conn = sqlite3.connect('database/restaurant.db')
    
    # Display today's reservations
    today = datetime.now().strftime('%Y-%m-%d')
    todays_reservations = pd.read_sql(f"""
        SELECT r.id, r.table_id, r.customer_name, r.phone, r.time, r.party_size, r.status
        FROM reservations r
        WHERE r.date = '{today}'
        ORDER BY r.time
    """, conn)
    
    st.subheader(f"Today's Reservations ({today})")
    if not todays_reservations.empty:
        for _, reservation in todays_reservations.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{reservation['customer_name']}** - Table {reservation['table_id']} - {reservation['time']}")
                    st.markdown(f"Party Size: {reservation['party_size']} - Phone: {reservation['phone']}")
                    status_color = "green" if reservation['status'] == "Confirmed" else "orange" if reservation['status'] == "Pending" else "red"
                    st.markdown(f"Status: <span style='color:{status_color}'>{reservation['status']}</span>", unsafe_allow_html=True)
                with col2:
                    if reservation['status'] == "Confirmed":
                        if st.button(f"Seat {reservation['id']}"):
                            # Update reservation status and table status
                            c = conn.cursor()
                            c.execute("UPDATE reservations SET status = 'Seated' WHERE id = ?", (reservation['id'],))
                            c.execute("UPDATE tables SET status = 'Occupied' WHERE id = ?", (reservation['table_id'],))
                            conn.commit()
                            st.success(f"Reservation {reservation['id']} seated")
                            st.experimental_rerun()
                with col3:
                    if st.button(f"Cancel {reservation['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE reservations SET status = 'Cancelled' WHERE id = ?", (reservation['id'],))
                        conn.commit()
                        st.success(f"Reservation {reservation['id']} cancelled")
                        st.experimental_rerun()
    else:
        st.info("No reservations for today")
    
    # Create new reservation
    st.markdown("---")
    st.subheader("Create New Reservation")
    
    # Get available tables
    tables = pd.read_sql("SELECT * FROM tables", conn)
    
    with st.form("new_reservation_form"):
        customer_name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        date = st.date_input("Date")
        time = st.time_input("Time")
        party_size = st.number_input("Party Size", min_value=1, value=2)
        
        # Filter tables by capacity
        suitable_tables = tables[tables['capacity'] >= party_size]
        if suitable_tables.empty:
            st.warning("No tables available for this party size")
            table_id = None
        else:
            table_id = st.selectbox("Select Table", suitable_tables['id'].tolist(), 
                                  format_func=lambda x: f"Table {x} (Capacity: {tables.loc[tables['id'] == x, 'capacity'].iloc[0]})")
        
        submit = st.form_submit_button("Create Reservation")
        if submit and table_id:
            # Check for existing reservations at the same time
            reservation_date = date.strftime('%Y-%m-%d')
            reservation_time = time.strftime('%H:%M:%S')
            
            c = conn.cursor()
            c.execute("""
                SELECT COUNT(*) FROM reservations
                WHERE table_id = ? AND date = ? AND time = ? AND status != 'Cancelled'
            """, (table_id, reservation_date, reservation_time))
            
            if c.fetchone()[0] > 0:
                st.error("This table is already reserved at this time")
            else:
                c.execute("""
                    INSERT INTO reservations 
                    (table_id, customer_name, phone, date, time, party_size, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Confirmed')
                """, (table_id, customer_name, phone, reservation_date, reservation_time, party_size))
                conn.commit()
                st.success("Reservation created successfully!")
                st.experimental_rerun()
    
    conn.close()

# Main application
def main():
    st.set_page_config(page_title="Casa Delizia", page_icon="🍕", layout="wide")
    
    # Initialize database
    init_db()
    
    # Initialize session state
    init_session()
    
    # Navigation sidebar
    navigation()
    
    # Main content
    if st.session_state.page == 'home':
        home_page()
    elif st.session_state.page == 'tables':
        tables_page()
    elif st.session_state.page == 'orders':
        orders_page()
    elif st.session_state.page == 'menu':
        menu_page()
    elif st.session_state.page == 'billing':
        billing_page()
    elif st.session_state.page == 'inventory':
        inventory_page()
    elif st.session_state.page == 'reservations':
        reservations_page()

if __name__ == "__main__":
    main()
