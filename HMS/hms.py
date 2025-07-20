import tkinter as tk
from tkinter import messagebox
import sqlite3


class Room:
    def __init__(self, room_number, room_type, price, availability=True):
        self.room_number = room_number
        self.room_type = room_type  # e.g., Single, Double
        self.price = price
        self.availability = availability

    def __repr__(self):
        return (f"Room Number: {self.room_number}, Type: {self.room_type}, "
                f"Price: {self.price}, Available: {'Yes' if self.availability else 'No'}")


class Customer:
    def __init__(self, name, contact, room_booked=None):
        self.name = name
        self.contact = contact
        self.room_booked = room_booked

    def __repr__(self):
        return (f"Customer Name: {self.name}, Contact: {self.contact}, "
                f"Room Booked: {self.room_booked.room_number if self.room_booked else 'None'}")


class HotelManagementSystem:
    def __init__(self):
        self.conn = sqlite3.connect("hotel_management.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                                room_number INTEGER PRIMARY KEY,
                                room_type TEXT,
                                price REAL,
                                availability INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                                name TEXT,
                                contact TEXT,
                                room_booked INTEGER,
                                FOREIGN KEY(room_booked) REFERENCES rooms(room_number))''')
        self.conn.commit()

    def add_room(self, room_number, room_type, price):
        
        self.cursor.execute("INSERT INTO rooms (room_number, room_type, price, availability) VALUES (?, ?, ?, ?)",
                            (room_number, room_type, price, 1))
        self.conn.commit()

    def view_rooms(self):
        
        self.cursor.execute("SELECT * FROM rooms")
        rooms = self.cursor.fetchall()
        return [Room(r[0], r[1], r[2], bool(r[3])) for r in rooms]

    def check_availability(self, room_number):
        
        self.cursor.execute("SELECT availability FROM rooms WHERE room_number = ?", (room_number,))
        result = self.cursor.fetchone()
        return bool(result[0]) if result else None

    def book_room(self, name, contact, room_number):
        
        if self.check_availability(room_number):
            self.cursor.execute("UPDATE rooms SET availability = 0 WHERE room_number = ?", (room_number,))
            self.cursor.execute("INSERT INTO customers (name, contact, room_booked) VALUES (?, ?, ?)",
                                (name, contact, room_number))
            self.conn.commit()
            return True, f"Room {room_number} booked successfully for {name}!"
        else:
            return False, f"Room {room_number} is not available."

    def customer_records(self):
        
        self.cursor.execute("SELECT * FROM customers")
        customers = self.cursor.fetchall()
        return [Customer(c[0], c[1], Room(c[2], None, None)) for c in customers]

    def checkout(self, room_number):
        
        self.cursor.execute("SELECT * FROM customers WHERE room_booked = ?", (room_number,))
        customer = self.cursor.fetchone()
        if customer:
            self.cursor.execute("UPDATE rooms SET availability = 1 WHERE room_number = ?", (room_number,))
            self.cursor.execute("DELETE FROM customers WHERE room_booked = ?", (room_number,))
            self.conn.commit()
            return True, f"Room {room_number} checked out successfully!"
        return False, f"No customer found in Room {room_number}."


class HotelManagementGUI:
    def __init__(self, root, hotel):
        self.hotel = hotel
        self.root = root
        self.root.title("Hotel Management System")
        self.root.geometry("600x400")

        tk.Label(self.root, text="Hotel Management System", font=("Arial", 20)).pack(pady=10)

        # Buttons for roles
        tk.Button(self.root, text="Admin Panel", font=("Arial", 16), width=15, command=self.admin_panel).pack(pady=10)
        tk.Button(self.root, text="Customer Panel", font=("Arial", 16), width=15, command=self.customer_panel).pack(pady=10)

    def admin_panel(self):
        
        admin_win = tk.Toplevel(self.root)
        admin_win.title("Admin Panel")
        admin_win.geometry("700x500")

        tk.Label(admin_win, text="Admin Panel", font=("Arial", 20)).pack(pady=10)

        # View Rooms
        tk.Button(admin_win, text="View All Rooms", font=("Arial", 14),
                  command=self.view_rooms).pack(pady=5)

        # Add Room
        tk.Button(admin_win, text="Add Room", font=("Arial", 14),
                  command=self.add_room_window).pack(pady=5)

        # Customer Records
        tk.Button(admin_win, text="View Customer Records", font=("Arial", 14),
                  command=self.view_customer_records).pack(pady=5)

    def view_rooms(self):
        #Display all rooms
        room_win = tk.Toplevel(self.root)
        room_win.title("Room Details")
        room_win.geometry("500x400")
        tk.Label(room_win, text="Room Details", font=("Arial", 18)).pack(pady=10)

        rooms = self.hotel.view_rooms()
        if not rooms:
            tk.Label(room_win, text="No rooms available.", font=("Arial", 14)).pack(pady=5)
        else:
            for room in rooms:
                tk.Label(room_win, text=str(room), font=("Arial", 12)).pack(pady=2)

    def add_room_window(self):
       #Open a window to add a new room
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Room")
        add_win.geometry("400x300")

        tk.Label(add_win, text="Add Room", font=("Arial", 18)).pack(pady=10)

        tk.Label(add_win, text="Room Number").pack()
        room_number = tk.Entry(add_win)
        room_number.pack()

        tk.Label(add_win, text="Room Type").pack()
        room_type = tk.Entry(add_win)
        room_type.pack()

        tk.Label(add_win, text="Price").pack()
        price = tk.Entry(add_win)
        price.pack()

        def add_room_action():
            try:
                self.hotel.add_room(int(room_number.get()), room_type.get(), float(price.get()))
                messagebox.showinfo("Success", f"Room {room_number.get()} added successfully!")
                add_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please try again.")

        tk.Button(add_win, text="Add Room", command=add_room_action).pack(pady=10)

    def view_customer_records(self):
        #Display all customer records
        customer_win = tk.Toplevel(self.root)
        customer_win.title("Customer Records")
        customer_win.geometry("500x400")
        tk.Label(customer_win, text="Customer Records", font=("Arial", 18)).pack(pady=10)

        customers = self.hotel.customer_records()
        if not customers:
            tk.Label(customer_win, text="No customer records.", font=("Arial", 14)).pack(pady=5)
        else:
            for customer in customers:
                tk.Label(customer_win, text=str(customer), font=("Arial", 12)).pack(pady=2)

    def customer_panel(self):
        #Customer panel
        customer_win = tk.Toplevel(self.root)
        customer_win.title("Customer Panel")
        customer_win.geometry("700x500")

        tk.Label(customer_win, text="Customer Panel", font=("Arial", 20)).pack(pady=10)

        # Book Room
        tk.Button(customer_win, text="Book Room", font=("Arial", 14),
                  command=self.book_room_window).pack(pady=5)

        # Checkout
        tk.Button(customer_win, text="Checkout", font=("Arial", 14),
                  command=self.checkout_window).pack(pady=5)

    def book_room_window(self):
        
        book_win = tk.Toplevel(self.root)
        book_win.title("Book Room")
        book_win.geometry("400x300")

        tk.Label(book_win, text="Book Room", font=("Arial", 18)).pack(pady=10)

        tk.Label(book_win, text="Name").pack()
        name = tk.Entry(book_win)
        name.pack()

        tk.Label(book_win, text="Contact").pack()
        contact = tk.Entry(book_win)
        contact.pack()

        tk.Label(book_win, text="Room Number").pack()
        room_number = tk.Entry(book_win)
        room_number.pack()

        def book_room_action():
            try:
                success, message = self.hotel.book_room(name.get(), contact.get(), int(room_number.get()))
                if success:
                    messagebox.showinfo("Success", message)
                    book_win.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please try again.")

        tk.Button(book_win, text="Book Room", command=book_room_action).pack(pady=10)

    def checkout_window(self):
        
        checkout_win = tk.Toplevel(self.root)
        checkout_win.title("Checkout")
        checkout_win.geometry("400x200")

        tk.Label(checkout_win, text="Checkout", font=("Arial", 18)).pack(pady=10)

        tk.Label(checkout_win, text="Room Number").pack()
        room_number = tk.Entry(checkout_win)
        room_number.pack()

        def checkout_action():
            try:
                success, message = self.hotel.checkout(int(room_number.get()))
                if success:
                    messagebox.showinfo("Success", message)
                    checkout_win.destroy()
                else:
                    messagebox.showerror("Error", message)
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please try again.")

        tk.Button(checkout_win, text="Checkout", command=checkout_action).pack(pady=10)


# Run the GUI application
if __name__ == "__main__":
    hotel = HotelManagementSystem()
    root = tk.Tk()
    app = HotelManagementGUI(root, hotel)
    root.mainloop()
