import mysql.connector
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

connection = None
main_frame = None

def connect_to_mysql():
    try:
        global connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sandhya",
            database="VTMERCH"
        )
        print("Connected to MySQL database successfully!")
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to connect to MySQL database: {error}")

def handle_login():
    username = username_entry.get()
    password = password_entry.get()

    try:
        cursor = connection.cursor()
        query = "SELECT * FROM Employee WHERE Username = %s AND Password = %s"
        cursor.execute(query, (username, password))
        employee = cursor.fetchone()

        if employee:
            login_frame.pack_forget()
            role = employee[2] 
            UserID = employee[0]

            if role == "Manager":
                show_main_menu("Manager", username, UserID)
            else:
                show_main_menu("Employee", username, UserID)
        else:
            query = "SELECT * FROM User WHERE Username = %s AND Password = %s"
            cursor.execute(query, (username, password))
            User = cursor.fetchone()
            if User:
                UserID = User[0]
                login_frame.pack_forget()
                show_main_menu("User", username, UserID)
            else : 
                messagebox.showerror("Login Failed", "Invalid username or password.")

        
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to authenticate user: {error}")

def handle_signup():
    username = signup_username_entry.get()
    password = signup_password_entry.get()
    shipping_address = signup_shipping_address_entry.get()
    default_card_number = signup_default_card_number_entry.get()
    email_id = signup_email_id_entry.get()

    try:
        cursor = connection.cursor()

        # Fetch the maximum UserID from the User table
        cursor.execute("SELECT MAX(UserID) FROM User")
        result = cursor.fetchone()
        max_user_id = result[0] if result[0] else 0  # If no users, start with UserID 1

        # Increment the max_user_id to generate the next UserID
        new_user_id = max_user_id + 1

        # Insert the new user record into the User table
        query = "INSERT INTO User (UserID, Username, Password, ShippingAddress, DefaultCardNumber, EmailID) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (new_user_id, username, password, shipping_address, default_card_number, email_id))
        connection.commit()
        cursor.close()

        messagebox.showinfo("Signup Successful", f"You have successfully signed up as User with UserID: {new_user_id}.")
        signup_frame.pack_forget()
        login_frame.pack(expand=True)
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to sign up: {error}")

    username = signup_username_entry.get()
    password = signup_password_entry.get()
    shipping_address = signup_shipping_address_entry.get()
    default_card_number = signup_default_card_number_entry.get()
    email_id = signup_email_id_entry.get()

    try:
        cursor = connection.cursor()
        query = "INSERT INTO User (Username, Password, ShippingAddress, DefaultCardNumber, EmailID) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (username, password, shipping_address, default_card_number, email_id))
        connection.commit()
        cursor.close()
        messagebox.showinfo("Signup Successful", "You have successfully signed up as a Manager.")
        signup_frame.pack_forget()
        login_frame.pack(expand=True)
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to sign up: {error}")

def show_signup_frame():
    login_frame.pack_forget()
    signup_frame.pack(expand=True)

def show_login_frame():
    signup_frame.pack_forget()
    login_frame.pack(expand=True)
    
def create_employee_role_chart(Role, user_id):
    global main_frame
    try:
        # Clear previous content if any
        main_frame.pack_forget()
        login_frame.pack_forget()

        scroll_frame = ttk.Frame(window)
        scroll_frame.pack(fill="both", expand=True)

        # Create a canvas to hold the charts
        canvas = tk.Canvas(scroll_frame)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas to hold the chart content
        chart_frame = ttk.Frame(canvas, padding="10")
        canvas.create_window((0, 0), window=chart_frame, anchor="nw")

        # Fetch data from database
        cursor = connection.cursor()
        
        stats_frame = ttk.Frame(chart_frame, padding="10")
        stats_frame.pack(side=tk.TOP, fill="both", expand=True)
        
        def Transfers(cursor, chart_frame):
            try:
                # Data for bar chart: Inventory categories
                query = "SELECT Category, COUNT(*) FROM Inventory GROUP BY Category"
                cursor.execute(query)
                category_counts = cursor.fetchall()

                # Data for line graph: Inventory prices
                query = "SELECT Price, COUNT(*) FROM Inventory GROUP BY Price"
                cursor.execute(query)
                price_counts = cursor.fetchall()

                # Data for bar chart: Inventory sizes
                query = "SELECT size, COUNT(*) FROM Inventory GROUP BY size"
                cursor.execute(query)
                size_counts = cursor.fetchall()

                # Data for line graph: Quantity and Request Date from Transfers
                query = "SELECT Quantity, RequestDate FROM Transfers"
                cursor.execute(query)
                quantity_request_data = cursor.fetchall()

                # Data for pie chart: Pending and Approved Transfers
                query = "SELECT Status, COUNT(*) FROM Transfers GROUP BY Status"
                cursor.execute(query)
                status_counts = cursor.fetchall()

                # Data for scatter plot: Request day and Approval date difference per item
                query = "SELECT RequestDate, ApprovalDate FROM Transfers"
                cursor.execute(query)
                request_approval_dates = cursor.fetchall()

                cursor.close()

                # Extract data for Inventory charts
                categories = [category[0] for category in category_counts]
                category_count_values = [count[1] for count in category_counts]

                prices = [price[0] for price in price_counts]
                price_count_values = [count[1] for count in price_counts]

                sizes = [size[0] for size in size_counts]
                size_count_values = [count[1] for count in size_counts]

                # Extract data for Transfers charts
                quantities = [data[0] for data in quantity_request_data]
                request_dates = [data[1] for data in quantity_request_data]

                statuses = [status[0] for status in status_counts]
                status_count_values = [count[1] for count in status_counts]

                request_dates_diff = [data[0] for data in request_approval_dates]
                approval_dates = [data[1] for data in request_approval_dates]

                # Inventory charts
                fig1_inv, ax1_inv = plt.subplots(figsize=(12, 8))
                ax1_inv.bar(categories, category_count_values, color='blue')
                ax1_inv.set_xlabel('Inventory Categories')
                ax1_inv.set_ylabel('Number of Items')
                ax1_inv.set_title('Inventory Distribution by Category')
                ax1_inv.set_xticks(range(len(categories)))
                ax1_inv.set_xticklabels(categories, rotation=45)

                canvas1_inv = FigureCanvasTkAgg(fig1_inv, master=chart_frame)
                canvas1_inv.draw()
                canvas1_inv.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig2_inv, ax2_inv = plt.subplots(figsize=(8, 6))
                ax2_inv.plot(prices, price_count_values, marker='o', linestyle='-', color='green')
                ax2_inv.set_xlabel('Prices')
                ax2_inv.set_ylabel('Number of Items')
                ax2_inv.set_title('Inventory Distribution by Price')
                ax2_inv.set_xticks(range(len(prices)))
                ax2_inv.set_xticklabels(prices, rotation=45)

                canvas2_inv = FigureCanvasTkAgg(fig2_inv, master=chart_frame)
                canvas2_inv.draw()
                canvas2_inv.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig3_inv, ax3_inv = plt.subplots(figsize=(8, 6))
                ax3_inv.bar(sizes, size_count_values, color='red')
                ax3_inv.set_xlabel('Sizes')
                ax3_inv.set_ylabel('Number of Items')
                ax3_inv.set_title('Inventory Distribution by Size')
                ax3_inv.set_xticks(range(len(sizes)))
                ax3_inv.set_xticklabels(sizes, rotation=45)

                canvas3_inv = FigureCanvasTkAgg(fig3_inv, master=chart_frame)
                canvas3_inv.draw()
                canvas3_inv.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                # Transfers charts
                fig1_trans, ax1_trans = plt.subplots(figsize=(10, 6))
                ax1_trans.plot(request_dates, quantities, marker='o', linestyle='-', color='blue')
                ax1_trans.set_xlabel('Request Dates')
                ax1_trans.set_ylabel('Quantity')
                ax1_trans.set_title('Quantity vs Request Date')
                ax1_trans.set_xticklabels(request_dates, rotation=45)

                canvas1_trans = FigureCanvasTkAgg(fig1_trans, master=chart_frame)
                canvas1_trans.draw()
                canvas1_trans.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig2_trans, ax2_trans = plt.subplots(figsize=(8, 6))
                ax2_trans.pie(status_count_values, labels=statuses, autopct='%1.1f%%', startangle=140)
                ax2_trans.axis('equal')
                ax2_trans.set_title('Transfers Status Distribution')

                canvas2_trans = FigureCanvasTkAgg(fig2_trans, master=chart_frame)
                canvas2_trans.draw()
                canvas2_trans.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                # Calculate and display differences between request and approval dates
                date_differences = [(approval_dates[i] - request_dates_diff[i]).days for i in range(len(request_dates_diff))]
                avg_difference = sum(date_differences) / len(date_differences)

                stats_frame = ttk.Frame(chart_frame, padding="10")
                stats_frame.pack(side=tk.TOP, fill="both", expand=True)

                ttk.Label(stats_frame, text=f"Avg Approval Time (days): {avg_difference:.2f}").pack(anchor=tk.W)

            except mysql.connector.Error as error:
                messagebox.showerror("Error", f"Failed to fetch data from MySQL: {error}")

            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        def Transfers_user(cursor, chart_frame, user_id):
            try:
                # Data for bar chart: Inventory categories
                query = "SELECT Category, COUNT(*) FROM Inventory GROUP BY Category"
                cursor.execute(query)
                category_counts = cursor.fetchall()

                # Data for line graph: Inventory prices
                query = "SELECT Price, COUNT(*) FROM Inventory GROUP BY Price"
                cursor.execute(query)
                price_counts = cursor.fetchall()

                # Data for bar chart: Inventory sizes
                query = "SELECT size, COUNT(*) FROM Inventory GROUP BY size"
                cursor.execute(query)
                size_counts = cursor.fetchall()

                # Data for line graph: Quantity and Request Date from Transfers (for a specific user)
                query = "SELECT Quantity, RequestDate FROM Transfers"
                cursor.execute(query)
                quantity_request_data = cursor.fetchall()

                # Data for pie chart: Pending and Approved Transfers (for a specific user)
                query = "SELECT Status, COUNT(*) FROM Transfers"
                cursor.execute(query)
                status_counts = cursor.fetchall()

                # Data for scatter plot: Request day and Approval date difference per item (for a specific user)
                query = "SELECT RequestDate, ApprovalDate FROM Transfers"
                cursor.execute(query)
                request_approval_dates = cursor.fetchall()

                cursor.close()

                # Extract data for Inventory charts
                categories = [category[0] for category in category_counts]
                category_count_values = [count[1] for count in category_counts]

                prices = [price[0] for price in price_counts]
                price_count_values = [count[1] for count in price_counts]

                sizes = [size[0] for size in size_counts]
                size_count_values = [count[1] for count in size_counts]

                # Extract data for Transfers charts
                quantities = [data[0] for data in quantity_request_data]
                request_dates = [data[1] for data in quantity_request_data]

                statuses = [status[0] for status in status_counts]
                status_count_values = [count[1] for count in status_counts]

                request_dates_diff = [data[0] for data in request_approval_dates]
                approval_dates = [data[1] for data in request_approval_dates]

                # Inventory charts
                fig1_inv, ax1_inv = plt.subplots(figsize=(12, 8))
                ax1_inv.bar(categories, category_count_values, color='blue')
                ax1_inv.set_xlabel('Inventory Categories')
                ax1_inv.set_ylabel('Number of Items')
                ax1_inv.set_title('Inventory Distribution by Category')
                ax1_inv.set_xticks(range(len(categories)))
                ax1_inv.set_xticklabels(categories, rotation=45)

                canvas1_inv = FigureCanvasTkAgg(fig1_inv, master=chart_frame)
                canvas1_inv.draw()
                canvas1_inv.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig2_inv, ax2_inv = plt.subplots(figsize=(8, 6))
                ax2_inv.plot(prices, price_count_values, marker='o', linestyle='-', color='green')
                ax2_inv.set_xlabel('Prices')
                ax2_inv.set_ylabel('Number of Items')
                ax2_inv.set_title('Inventory Distribution by Price')
                ax2_inv.set_xticks(range(len(prices)))
                ax2_inv.set_xticklabels(prices, rotation=45)

                canvas2_inv = FigureCanvasTkAgg(fig2_inv, master=chart_frame)
                canvas2_inv.draw()
                canvas2_inv.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig3_inv, ax3_inv = plt.subplots(figsize=(8, 6))
                ax3_inv.bar(sizes, size_count_values, color='red')
                ax3_inv.set_xlabel('Sizes')
                ax3_inv.set_ylabel('Number of Items')
                ax3_inv.set_title('Inventory Distribution by Size')
                ax3_inv.set_xticks(range(len(sizes)))
                ax3_inv.set_xticklabels(sizes, rotation=45)

                canvas3_inv = FigureCanvasTkAgg(fig3_inv, master=chart_frame)
                canvas3_inv.draw()
                canvas3_inv.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                # Transfers charts
                fig1_trans, ax1_trans = plt.subplots(figsize=(10, 6))
                ax1_trans.plot(request_dates, quantities, marker='o', linestyle='-', color='blue')
                ax1_trans.set_xlabel('Request Dates')
                ax1_trans.set_ylabel('Quantity')
                ax1_trans.set_title('Quantity vs Request Date')
                ax1_trans.set_xticklabels(request_dates, rotation=45)

                canvas1_trans = FigureCanvasTkAgg(fig1_trans, master=chart_frame)
                canvas1_trans.draw()
                canvas1_trans.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig2_trans, ax2_trans = plt.subplots(figsize=(8, 6))
                ax2_trans.pie(status_count_values, labels=statuses, autopct='%1.1f%%', startangle=140)
                ax2_trans.axis('equal')
                ax2_trans.set_title('Transfers Status Distribution')

                canvas2_trans = FigureCanvasTkAgg(fig2_trans, master=chart_frame)
                canvas2_trans.draw()
                canvas2_trans.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                # Calculate and display differences between request and approval dates
                date_differences = [(approval_dates[i] - request_dates_diff[i]).days for i in range(len(request_dates_diff))]
                avg_difference = sum(date_differences) / len(date_differences)

                stats_frame = ttk.Frame(chart_frame, padding="10")
                stats_frame.pack(side=tk.TOP, fill="both", expand=True)

                ttk.Label(stats_frame, text=f"Avg Approval Time (days): {avg_difference:.2f}").pack(anchor=tk.W)

            except mysql.connector.Error as error:
                messagebox.showerror("Error", f"Failed to fetch data from MySQL: {error}")

            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        def Transactions(cursor, chart_frame):
            try:
                # Quantity by Item (Transactions)
                query3 = "SELECT ItemID, SUM(Quantity) FROM Transaction GROUP BY ItemID"
                cursor.execute(query3)
                item_quantities = cursor.fetchall()

                # Average Total Amount per Transaction (Transactions)
                query5 = "SELECT Date, AVG(TotalAmount) FROM Transaction GROUP BY Date"
                cursor.execute(query5)
                date_avg_amounts = cursor.fetchall()

                # Extracting overall statistics (Transactions)
                query_stats = "SELECT COUNT(*), SUM(Quantity), SUM(TotalAmount) FROM Transaction"
                cursor.execute(query_stats)
                overall_stats = cursor.fetchone()

                # Quantity vs Request Date (Transfers)
                query6 = "SELECT RequestDate, SUM(Quantity) FROM Transfers GROUP BY RequestDate"
                cursor.execute(query6)
                quantity_request_data = cursor.fetchall()

                # Transfers Status Distribution (Transfers)
                query7 = "SELECT Status, COUNT(*) FROM Transfers GROUP BY Status"
                cursor.execute(query7)
                status_counts = cursor.fetchall()

                cursor.close()

                # Extract data (Transactions)
                items = [item[0] for item in item_quantities]
                item_quantities = [item[1] for item in item_quantities]

                avg_dates = [data[0] for data in date_avg_amounts]
                avg_amounts = [data[1] for data in date_avg_amounts]

                # Extract data (Transfers)
                request_dates = [data[0] for data in quantity_request_data]
                quantities = [data[1] for data in quantity_request_data]

                statuses = [status[0] for status in status_counts]
                status_count_values = [count[1] for count in status_counts]

                # Overall stats (Transactions)
                total_transactions = overall_stats[0]
                total_quantity = overall_stats[1]
                total_amount = overall_stats[2]
                avg_quantity_per_transaction = total_quantity / total_transactions
                avg_amount_per_transaction = total_amount / total_transactions

                # Display overall stats
                stats_frame = ttk.Frame(chart_frame, padding="10")
                stats_frame.pack(side=tk.TOP, fill="both", expand=True)

                ttk.Label(stats_frame, text=f"Total Transactions: {total_transactions}").pack(anchor=tk.W)
                ttk.Label(stats_frame, text=f"Total Quantity: {total_quantity}").pack(anchor=tk.W)
                ttk.Label(stats_frame, text=f"Total Amount: ${total_amount:.2f}").pack(anchor=tk.W)
                ttk.Label(stats_frame, text=f"Average Quantity per Transaction: {avg_quantity_per_transaction:.2f}").pack(anchor=tk.W)
                ttk.Label(stats_frame, text=f"Average Amount per Transaction: ${avg_amount_per_transaction:.2f}").pack(anchor=tk.W)

                # Graphs (Transactions)
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                ax3.bar(items, item_quantities, color='green')
                ax3.set_xlabel('Item IDs')
                ax3.set_ylabel('Total Quantity')
                ax3.set_title('Quantity by Item')

                canvas3 = FigureCanvasTkAgg(fig3, master=chart_frame)
                canvas3.draw()
                canvas3.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig5, ax5 = plt.subplots(figsize=(10, 6))
                ax5.plot(avg_dates, avg_amounts, marker='o', linestyle='-', color='red')
                ax5.set_xlabel('Date')
                ax5.set_ylabel('Average Total Amount ($)')
                ax5.set_title('Average Total Amount per Transaction')
                ax5.set_xticklabels(avg_dates, rotation=45)

                canvas5 = FigureCanvasTkAgg(fig5, master=chart_frame)
                canvas5.draw()
                canvas5.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                # Graphs (Transfers)
                fig6, ax6 = plt.subplots(figsize=(10, 6))
                ax6.plot(request_dates, quantities, marker='o', linestyle='-', color='blue')
                ax6.set_xlabel('Request Date')
                ax6.set_ylabel('Quantity')
                ax6.set_title('Quantity vs Request Date')
                ax6.set_xticklabels(request_dates, rotation=45)

                canvas6 = FigureCanvasTkAgg(fig6, master=chart_frame)
                canvas6.draw()
                canvas6.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

                fig7, ax7 = plt.subplots(figsize=(10, 6))
                ax7.pie(status_count_values, labels=statuses, autopct='%1.1f%%', startangle=140)
                ax7.axis('equal')
                ax7.set_title('Transfers Status Distribution')

                canvas7 = FigureCanvasTkAgg(fig7, master=chart_frame)
                canvas7.draw()
                canvas7.get_tk_widget().pack(side=tk.TOP, fill="both", expand=True)

            except mysql.connector.Error as error:
                messagebox.showerror("Error", f"Failed to fetch data from MySQL: {error}")

            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        
        if (Role == "Manager"):
            Transfers(cursor, chart_frame)
        elif (Role == "Employee"):
            Transactions(cursor, chart_frame)
        else :
            Transfers_user(cursor, chart_frame, user_id)

        def handle_back():
            stats_frame.pack_forget()
            chart_frame.pack_forget()
            scroll_frame.pack_forget()
            canvas.pack_forget()
            
            main_frame.pack(fill="both", expand=True)

        ttk.Button(stats_frame, text="Back", command=handle_back, width=10, style="TButton").pack(side=tk.LEFT, padx=5)

    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to fetch data from MySQL: {error}")

    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        
def change_password(Role, Username):
        new_password = simpledialog.askstring("Change Password", "Enter new password:", show='*')
        if not new_password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return
        try:
            cursor = connection.cursor()
            if Role == "Manager" or Role == "Employee":
                update_query = "UPDATE Employee SET Password = %s WHERE Username = %s"
            else:
                update_query = "UPDATE User SET Password = %s WHERE Username = %s"

            cursor.execute(update_query, (new_password, Username))
            connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Password changed successfully.")
            
        except mysql.connector.Error as error:
            messagebox.showerror("Error", f"Failed to update password: {error}")

def show_main_menu(Role, Username, UserID):
   

    global main_frame

    # Create main frame
    main_frame = ttk.Frame(window, style="Main.TFrame")
    main_frame.pack(fill="both", expand=True)
    


    style = ttk.Style()
    style.configure("Header.TFrame", background="#630031")
    style.configure("Footer.TFrame", background="#630031")
    style.configure("TButton", background="#CF4420", foreground="#630031")

    # Header Section
    header_frame = ttk.Frame(main_frame, style="Header.TFrame")
    header_frame.pack(fill="both")

    header_label = ttk.Label(header_frame, text="Welcome to VT Merch", font=("Helvetica", 20, "bold"), foreground="#CF4420", background="#630031")
    header_label.pack(pady=10)

    # User Info Section
    user_info_frame = ttk.Frame(main_frame, padding="20")
    user_info_frame.pack()

    ttk.Label(user_info_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="E")
    ttk.Label(user_info_frame, text=Username, font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(user_info_frame, text="Role:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="E")
    ttk.Label(user_info_frame, text=Role, font=("Helvetica", 12)).grid(row=1, column=1, padx=10, pady=5, sticky="W")

    # Change Password and Logout Section
    action_frame = ttk.Frame(main_frame, padding="20")
    action_frame.pack()

    # ttk.Button(action_frame, text="Change Password", command=change_password(Role, Username), style="TButton").grid(row=0, column=0, padx=10, pady=5)
    ttk.Button(action_frame, text="Change Password", command=lambda: change_password(Role, Username), style="TButton").grid(row=0, column=0, padx=10, pady=5)
   
    ttk.Button(action_frame, text="Logout", command=handle_logout, style="TButton").grid(row=0, column=1, padx=10, pady=5)

    ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill="x", pady=10)

    # Button Section
    button_names = [
        ("Storage Location", 'storagelocation', ['StoreID', 'LocationType', 'Description'], 'LocationID'),
        ("Employee", 'employee', ['Name', 'Role', 'ContactInformation', 'StoreID', 'Username', 'Password'], 'EmployeeID'),
        ("Store", 'store', ['StoreName', 'Location'], 'StoreID'),
        ("Transfers", 'transfers', ['SourceStoreID', 'DestinationStoreID', 'ItemID', 'Quantity', 'Status', 'RequestDate', 'ApprovalDate'], 'TransferID'),
        ("Shopping Cart", 'shoppingcart', ['ItemID', 'UserID', 'DateAdded'], 'CartID'),
        ("Inventory", 'inventory', ['ProductName', 'UniqueNumber', 'Size', 'TotalCount', 'Name', 'Description', 'Category', 'Price'], 'ItemID'),
        ("Online Order", 'onlineorder', ['ItemID', 'UserID', 'OrderDate', 'ShippingAddress', 'Status'], 'OrderID'),
        ("User", 'user', ['Username', 'Password', 'ShippingAddress', 'DefaultCardNumber', 'EmailID'], 'UserID')
    ]

    if Role == "Manager":
        for name, table, fields, primary_key in button_names:
            button = ttk.Button(main_frame, text=name, command=lambda t=table, f=fields, p=primary_key: show_table_frame(t, f, p, Role, UserID), style="TButton")
            button.pack(pady=5)
        ttk.Button(main_frame, text="Stats", command=lambda: create_employee_role_chart(Role, UserID), width=10, style="TButton").pack(pady=5)

    elif Role == "User":
        button_indices = [4, 5, 6]
        relevant_buttons = [button_names[idx] for idx in button_indices]
        for name, table, fields, primary_key in relevant_buttons:
            button = ttk.Button(main_frame, text=name, command=lambda t=table, f=fields, p=primary_key: show_table_frame(t, f, p, Role,UserID), style="TButton")
            button.pack(pady=5)
        ttk.Button(main_frame, text="Stats", command=lambda: create_employee_role_chart(Role, UserID), width=10, style="TButton").pack(pady=5)

    
    else :
        button_indices = [0, 2, 3, 5]
        relevant_buttons = [button_names[idx] for idx in button_indices]
        for name, table, fields, primary_key in relevant_buttons:
            button = ttk.Button(main_frame, text=name, command=lambda t=table, f=fields, p=primary_key: show_table_frame(t, f, p, Role,UserID), style="TButton")
            button.pack(pady=5)
        ttk.Button(main_frame, text="Stats", command=lambda: create_employee_role_chart(Role, UserID), width=10, style="TButton").pack(pady=5)

        

    # Footer Section
    footer_frame = ttk.Frame(main_frame, style="Footer.TFrame")
    footer_frame.pack(fill="x", side=tk.BOTTOM)

    ttk.Label(footer_frame, text="Virginia Tech", foreground="#CF4420", font=("Helvetica", 10), background="#630031").pack(side=tk.LEFT, padx=10)
    ttk.Label(footer_frame, text="Powered by VT Merch", foreground="#CF4420", font=("Helvetica", 10), background="#630031").pack(side=tk.RIGHT, padx=10)



def handle_logout():
    global main_frame
    if main_frame:
        main_frame.destroy()
    login_frame.pack(expand=True)

def show_table_frame(table_name, fields, primary_key, Role, UserID):
    global entries, table

    def handle_back():
        table_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)

    def handle_insert():
        insert_record(table_name, fields, primary_key)

    def handle_delete():
        delete_record(table_name, primary_key)

    def handle_update():
        update_record(table_name, fields, primary_key)
    
    def handle_show_table():
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        records = cursor.fetchall()
        for row in table.get_children():
            table.delete(row)
        for record in records:
            table.insert('', 'end', values=record)
        cursor.close()

    
    def handle_search():
            search_term = search_entry.get()
            cursor = connection.cursor()
            query = f"SELECT * FROM {table_name} WHERE {primary_key} LIKE %s OR " + " OR ".join([f"{field} LIKE %s" for field in fields])
            cursor.execute(query, tuple([f"%{search_term}%"] * (len(fields) + 1)))
            records = cursor.fetchall()
            
            # Clear the existing table
            for row in table.get_children():
                table.delete(row)
            
            # Insert new records into the table
            for record in records:
                table.insert('', 'end', values=record)
            
            cursor.close()


    main_frame.pack_forget()
    table_frame = ttk.Frame(window, padding="20")
    table_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(table_frame, text=f"{table_name.capitalize()} Table Operations", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)

    inner_frame = ttk.Frame(table_frame)
    inner_frame.pack(fill="both", expand=True, pady=20)
    
    if (Role == "User") :
        # Display Shopping Cart
        if table_name == "shoppingcart":
            def show_shopping_cart(inner_frame, connection, UserID):
                    try:
                        for widget in inner_frame.winfo_children():
                            widget.destroy()

                        # Create canvas widget for scrolling
                        canvas = tk.Canvas(inner_frame)
                        canvas.pack(side=tk.LEFT, fill="both", expand=True)

                        # Add scrollbar to the canvas
                        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview)
                        scrollbar.pack(side=tk.LEFT, fill="y")

                        # Configure canvas to use scrollbar
                        canvas.configure(yscrollcommand=scrollbar.set)

                        # Create a frame inside the canvas to hold the items
                        items_frame = ttk.Frame(canvas)
                        canvas.create_window((0, 0), window=items_frame, anchor="nw")


                        cursor = connection.cursor()
                        cursor.execute("SELECT s.CartID, s.ItemID, s.UserID, s.DateAdded, "
                                    "i.ProductName, i.UniqueNumber, i.Size, i.TotalCount, i.Name, "
                                    "i.Description, i.Category, i.Price "
                                    "FROM shoppingcart s "
                                    "JOIN inventory i ON s.ItemID = i.ItemID "
                                    "WHERE s.UserID = %s", (UserID,))
                        cart_items = cursor.fetchall()
                        cursor.close()

                        for cart_item in cart_items:
                            cart_id, item_id, user_id, date_added, product_name, unique_number, size, total_count, name, description, category, price = cart_item

                            # Create a frame for each cart item
                            cart_item_frame = ttk.Frame(inner_frame, borderwidth=2, relief="groove", padding=10)
                            cart_item_frame.pack(side=tk.LEFT, fill="x", padx=10, pady=10)

                            # Display cart item details
                            ttk.Label(cart_item_frame, text=f"Shopping Cart - Item ID: {item_id}", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(cart_item_frame, text=f"Date Added: {date_added}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(cart_item_frame, text=f"Inventory - Item ID: {unique_number}", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(cart_item_frame, text=f"Product Name: {product_name}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(cart_item_frame, text=f"Size: {size}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(cart_item_frame, text=f"Category: {category}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(cart_item_frame, text=f"Price: {price}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)

                            # Add delete button
                            ttk.Button(cart_item_frame, text="Delete", command=lambda id=item_id: handle_delete_from_cart(id)).pack(side=tk.RIGHT, padx=5)
                            
                            # Add checkout button
                            ttk.Button(cart_item_frame, text="Checkout", command=lambda id=item_id: handle_checkout(id, UserID)).pack(side=tk.RIGHT, padx=5)

                    except Exception as e:
                        print(f"Error displaying shopping cart: {e}")

                    def handle_delete_from_cart(item_id):
                        try:
                            cursor = connection.cursor()
                            cursor.execute("DELETE FROM shoppingcart WHERE ItemID = %s", (item_id,))
                            connection.commit()
                            cursor.close()
                            print(f"Deleted item {item_id} from shopping cart")
                        except Exception as e:
                            print(f"Error deleting item from shopping cart: {e}")

                    def handle_checkout(item_id, UserID):
                        try:
                            # Get the current maximum CartID from shoppingcart table
                            cursor = connection.cursor()
                            cursor.execute("SELECT MAX(CartID) FROM shoppingcart")
                            max_cart_id = cursor.fetchone()[0]  # Fetch the maximum CartID
                            new_cart_id = max_cart_id + 1 if max_cart_id else 1  # Increment CartID
                            
                            # First, delete item from shopping cart
                            cursor.execute("DELETE FROM shoppingcart WHERE ItemID = %s", (item_id,))
                            
                            # Then, insert item into onlineorder with status pending
                            cursor.execute("INSERT INTO onlineorder (OrderID, ItemID, UserID, OrderDate, ShippingAddress, Status) "
                                        "VALUES (%s, %s, %s, NOW(), '', 'pending')", (new_cart_id, item_id, UserID))
                            
                            connection.commit()
                            cursor.close()
                            print(f"Checked out item {item_id} with CartID {new_cart_id}")

                        except Exception as e:
                            print(f"Error checking out item: {e}")
                            
                    items_frame.update_idletasks()
                    canvas.config(scrollregion=canvas.bbox("all"))

                        # Bind mousewheel to scroll
                    def on_mousewheel(event):
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    canvas.bind_all("<MouseWheel>", on_mousewheel)
            show_shopping_cart(inner_frame, connection, UserID)
        # Display Inventory
        elif table_name == "inventory":
            def show_inventory_items(inner_frame, connection, UserID):
                    try:
                        # Clear existing widgets in inner_frame
                        for widget in inner_frame.winfo_children():
                            widget.destroy()

                        # Create canvas widget for scrolling
                        canvas = tk.Canvas(inner_frame)
                        canvas.pack(side=tk.LEFT, fill="both", expand=True)

                        # Add scrollbar to the canvas
                        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview)
                        scrollbar.pack(side=tk.RIGHT, fill="y")

                        # Configure canvas to use scrollbar
                        canvas.configure(yscrollcommand=scrollbar.set)

                        # Create a frame inside the canvas to hold the items
                        items_frame = ttk.Frame(canvas)
                        canvas.create_window((0, 0), window=items_frame, anchor="nw")

                        # Query inventory items from the database
                        cursor = connection.cursor()
                        cursor.execute("SELECT ItemID, ProductName, UniqueNumber, Size, TotalCount, Name, Description, Category, Price FROM inventory")
                        inventory_items = cursor.fetchall()
                        cursor.close()

                        # Function to handle adding the item to the cart
                        def add_to_cart(item_id, UserID):
                            try:
                                # Retrieve the last CartID from the shoppingcart table
                                cursor = connection.cursor()
                                cursor.execute("SELECT MAX(CartID) FROM shoppingcart")
                                last_cart_id = cursor.fetchone()[0]  # Get the last CartID
                                new_cart_id = last_cart_id + 1 if last_cart_id else 1  # Generate a new CartID

                                # Insert the new item into shoppingcart
                                cursor.execute("INSERT INTO shoppingcart (CartID, ItemID, UserID, DateAdded) VALUES (%s, %s, %s, NOW())",
                                            (new_cart_id, item_id, UserID))
                                
                                connection.commit()
                                cursor.close()
                                print(f"Added item {item_id} to cart with CartID {new_cart_id}")
                            except Exception as e:
                                print(f"Error adding item to cart: {e}")

                        # Add inventory items to items_frame
                        for idx, item in enumerate(inventory_items):
                            item_id, product_name, unique_number, size, total_count, name, description, category, price = item

                            # Create a frame for each item
                            item_frame = ttk.Frame(items_frame, borderwidth=2, relief="groove", padding=10, style="Item.TFrame")
                            item_frame.pack(side=tk.TOP, fill="x", padx=10, pady=10)

                            # Display item details
                            ttk.Label(item_frame, text=f"Product Name: {product_name}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Unique Number: {unique_number}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Size: {size}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Total Count: {total_count}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Name: {name}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Description: {description}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Category: {category}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                            ttk.Label(item_frame, text=f"Price: {price}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)

                            # Add plus button
                            plus_button = ttk.Button(item_frame, text="+", command=lambda item_id=item_id: add_to_cart(item_id,UserID), width=2)
                            plus_button.pack(anchor="e", padx=10, pady=2)

                        # Update the scroll region and bindings
                        items_frame.update_idletasks()
                        canvas.config(scrollregion=canvas.bbox("all"))

                        # Bind mousewheel to scroll
                        def on_mousewheel(event):
                            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                        canvas.bind_all("<MouseWheel>", on_mousewheel)

                    except Exception as e:
                        print(f"Error: {e}")

                # Add style for the item frames
            style = ttk.Style()
            style.configure("Item.TFrame", background="#f0f0f0")  # Change background color as needed

# Call the function
            show_inventory_items(inner_frame, connection, UserID)



        elif table_name == "onlineorder":
            cursor = connection.cursor()
            cursor.execute("SELECT o.ItemID, o.UserID, o.OrderDate, o.ShippingAddress, o.Status, " 
                        "i.ProductName, i.UniqueNumber, i.Size, i.TotalCount, i.Name, "
                        "i.Description, i.Category, i.Price "
                        "FROM onlineorder o "
                        "JOIN inventory i ON o.ItemID = i.ItemID "
                        "WHERE o.UserID = %s", (UserID,))
            
            orders = cursor.fetchall()
            cursor.close()

            for order in orders:
                item_id, user_id, order_date, shipping_address, status, product_name, unique_number, size, total_count, name, description, category, price = order
                
                # Create a frame for each order and inventory item
                order_frame = ttk.Frame(inner_frame, borderwidth=2, relief="groove", padding=10)
                order_frame.pack(side=tk.LEFT, padx=10, pady=10)

                # Display order details
                ttk.Label(order_frame, text=f"Order - Item ID: {item_id}", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Order Date: {order_date}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Shipping Address: {shipping_address}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Status: {status}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Inventory - Item ID: {unique_number}", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Product Name: {product_name}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Size: {size}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Category: {category}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)
                ttk.Label(order_frame, text=f"Price: {price}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=2)


        button_frame = ttk.Frame(inner_frame, padding="10 0 0 0")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Back", command=handle_back, width=10, style="TButton").pack(side=tk.LEFT, padx=5)



    if Role in ["Manager", "Employee"]:
            entries = {}
            for i, field in enumerate(fields):
                ttk.Label(inner_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5, sticky="W")
                entry = ttk.Entry(inner_frame, font=("Helvetica", 12))
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="W")
                entries[field] = entry

            ttk.Label(inner_frame, text=f"{primary_key}:").grid(row=len(fields), column=0, padx=5, pady=5, sticky="W")
            primary_entry = ttk.Entry(inner_frame, font=("Helvetica", 12))
            primary_entry.grid(row=len(fields), column=1, padx=5, pady=5, sticky="W")
            entries[primary_key] = primary_entry

            button_frame = ttk.Frame(inner_frame, padding="10 0 0 0")
            button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

            ttk.Button(button_frame, text="Insert", command=handle_insert).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Delete", command=handle_delete).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Update", command=handle_update).pack(side=tk.LEFT, padx=5)
            # ttk.Button(button_frame, text="Show Table", command=handle_show_table).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Back", command=handle_back).pack(side=tk.LEFT, padx=5)
            
            # Create a Treeview widget to display table records
            all_fields = [primary_key]+ fields
            
            search_frame = ttk.Frame(table_frame)
            search_frame.pack(fill="x", padx=10, pady=10)
            
            search_label = ttk.Label(search_frame, text="Search:")
            search_label.pack(side=tk.LEFT, padx=5)
            
            search_entry = ttk.Entry(search_frame, font=("Helvetica", 12))
            search_entry.pack(side=tk.LEFT, padx=5)
            
            search_button = ttk.Button(search_frame, text="Search", command=handle_search)
            search_button.pack(side=tk.LEFT, padx=5)

        # Create the Treeview table
            table = ttk.Treeview(table_frame, columns=all_fields, show="headings")
            table.pack(fill="both", expand=True)

        # Set column headings
            for field in all_fields:
               table.heading(field, text=field)
               
                # Search bar

            
            handle_show_table()



def insert_record(table_name, fields, primary_key):
    try:
        cursor = connection.cursor()
        values = tuple(entries[field].get() for field in fields)
        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['%s']*len(fields))})"
        cursor.execute(query, values)
        connection.commit()
        messagebox.showinfo("Insert Successful", f"Record inserted successfully into {table_name}.")
        handle_show_table()  # Refresh the table after insertion
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to insert record into {table_name}: {error}")
    finally:
        cursor.close()

def delete_record(table_name, primary_key):
    try:
        cursor = connection.cursor()
        value = entries[primary_key].get()
        query = f"DELETE FROM {table_name} WHERE {primary_key} = %s"
        cursor.execute(query, (value,))
        connection.commit()
        messagebox.showinfo("Delete Successful", f"Record deleted successfully from {table_name}.")
        handle_show_table()  # Refresh the table after deletion
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to delete record from {table_name}: {error}")
    finally:
        cursor.close()

def update_record(table_name, fields, primary_key):
    try:
        cursor = connection.cursor()
        set_values = ', '.join([f"{field} = %s" for field in fields])
        primary_value = entries[primary_key].get()
        update_query = f"UPDATE {table_name} SET {set_values} WHERE {primary_key} = %s"
        update_data = tuple(entries[field].get() for field in fields) + (primary_value,)
        cursor.execute(update_query, update_data)
        connection.commit()
        messagebox.showinfo("Update Successful", f"Record updated successfully in {table_name}.")
        handle_show_table()  # Refresh the table after update
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to update record in {table_name}: {error}")
    finally:
        cursor.close()


window = tk.Tk()
window.title("VT Merch Application")
window.geometry("1000x600")


# Create a frame for the login section with maroon background
header_frame = ttk.Frame(main_frame, style="Header.TFrame")
header_frame.pack(fill="x")

header_label = ttk.Label(header_frame, text="Welcome to VT Merch", font=("Helvetica", 20, "bold"), foreground="#CF4420", background="#630031")
header_label.pack(pady=10)
    
login_frame = ttk.Frame(window, padding="40 20", style="Maroon.TFrame")
login_frame.pack(expand=True)

background_image = Image.open("D:/Torg.jpg")  # Replace with your image file
background_image = background_image.resize((1400, 800))
bg_image = ImageTk.PhotoImage(background_image)

    # Create a label to hold the background image
background_label = tk.Label(window, image=bg_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Create a frame for the login section with maroon background
login_frame = ttk.Frame(window, padding="40 20", style="Maroon.TFrame")
login_frame.pack(expand=True)

    # Define a custom style for the maroon frame
window.tk_setPalette(background='white', foreground='white')

style = ttk.Style()
style.configure("Maroon.TFrame", background='white', foreground='white')



ttk.Label(login_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="E")
username_entry = ttk.Entry(login_frame, font=("Helvetica", 12))
username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="W")

ttk.Label(login_frame, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="E")
password_entry = ttk.Entry(login_frame, show="*", font=("Helvetica", 12))
password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="W")

login_button = ttk.Button(login_frame, text="Login", command=handle_login)
login_button.grid(row=2, columnspan=2, pady=10)

signup_link = ttk.Label(login_frame, text="Don't have an account? Sign up", font=("Helvetica", 10), foreground="blue", cursor="hand2")
signup_link.grid(row=3, columnspan=2, pady=10)
signup_link.bind("<Button-1>", lambda e: show_signup_frame())


signup_frame = ttk.Frame(window, padding="40 20")

ttk.Label(signup_frame, text="User SignUp", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="E")

ttk.Label(signup_frame, text="Username:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="E")
signup_username_entry = ttk.Entry(signup_frame, font=("Helvetica", 12))
signup_username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="W")

ttk.Label(signup_frame, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="E")
signup_password_entry = ttk.Entry(signup_frame, show="*", font=("Helvetica", 12))
signup_password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="W")

ttk.Label(signup_frame, text="Shipping Address:", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="E")
signup_shipping_address_entry = ttk.Entry(signup_frame, font=("Helvetica", 12))
signup_shipping_address_entry.grid(row=3, column=1, padx=10, pady=5, sticky="W")

ttk.Label(signup_frame, text="Default Card Number:", font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="E")
signup_default_card_number_entry = ttk.Entry(signup_frame, font=("Helvetica", 12))
signup_default_card_number_entry.grid(row=4, column=1, padx=10, pady=5, sticky="W")

ttk.Label(signup_frame, text="Email ID:", font=("Helvetica", 12)).grid(row=5, column=0, padx=10, pady=5, sticky="E")
signup_email_id_entry = ttk.Entry(signup_frame, font=("Helvetica", 12))
signup_email_id_entry.grid(row=5, column=1, padx=10, pady=5, sticky="W")

signup_button = ttk.Button(signup_frame, text="Sign Up", command=handle_signup)
signup_button.grid(row=7, columnspan=2, pady=10)

login_link = ttk.Label(signup_frame, text="Already have an account? Login", font=("Helvetica", 10), foreground="blue", cursor="hand2")
login_link.grid(row=8, columnspan=2, pady=10)
login_link.bind("<Button-1>", lambda e: show_login_frame())

connect_to_mysql()
window.mainloop()
