import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Database Connection
conn = sqlite3.connect("library.db")
cur = conn.cursor()

# Create Tables
cur.execute("""
CREATE TABLE IF NOT EXISTS Books(
    BookID INTEGER PRIMARY KEY,
    Title TEXT,
    Author TEXT,
    Genre TEXT,
    AvailableCopies INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Members(
    MemberID INTEGER PRIMARY KEY,
    Name TEXT,
    Phone TEXT,
    JoinDate TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Borrow(
    BorrowID INTEGER PRIMARY KEY AUTOINCREMENT,
    BookID INTEGER,
    MemberID INTEGER,
    IssueDate TEXT,
    ReturnDate TEXT
)
""")
conn.commit()

# ---------------- Functions ----------------

def add_book():
    bid = entry_bid.get()
    title = entry_title.get()
    auth = entry_author.get()
    gen = entry_genre.get()
    copies = entry_copies.get()

    if "" in (bid, title, auth, gen, copies):
        messagebox.showwarning("Warning", "All fields are required")
        return
    
    try:
        cur.execute("INSERT INTO Books VALUES (?, ?, ?, ?, ?)", 
                    (bid, title, auth, gen, copies))
        conn.commit()
        messagebox.showinfo("Success", "Book Added Successfully!")
    except:
        messagebox.showerror("Error", "Book ID Already Exists")

def add_member():
    mid = entry_mid.get()
    name = entry_mname.get()
    phone = entry_phone.get()
    join = entry_join.get()

    if "" in (mid, name, phone, join):
        messagebox.showwarning("Warning", "All fields are required")
        return
    
    try:
        cur.execute("INSERT INTO Members VALUES (?, ?, ?, ?)",
                    (mid, name, phone, join))
        conn.commit()
        messagebox.showinfo("Success", "Member Added Successfully!")
    except:
        messagebox.showerror("Error", "Member ID Already Exists")

def issue_book():
    bid = entry_ibook.get()
    mid = entry_imember.get()
    date = entry_idate.get()

    cur.execute("SELECT AvailableCopies FROM Books WHERE BookID=?", (bid,))
    data = cur.fetchone()

    if data and int(data[0]) > 0:
        cur.execute("INSERT INTO Borrow(BookID, MemberID, IssueDate, ReturnDate) VALUES (?, ?, ?, NULL)",
                    (bid, mid, date))
        cur.execute("UPDATE Books SET AvailableCopies = AvailableCopies - 1 WHERE BookID=?", (bid,))
        conn.commit()
        messagebox.showinfo("Success", "Book Issued!")
    else:
        messagebox.showerror("Error", "Book Not Available")

def return_book():
    bid = entry_rbook.get()
    mid = entry_rmember.get()
    date = entry_rdate.get()

    cur.execute("UPDATE Borrow SET ReturnDate=? WHERE BookID=? AND MemberID=? AND ReturnDate IS NULL",
                (date, bid, mid))
    cur.execute("UPDATE Books SET AvailableCopies = AvailableCopies + 1 WHERE BookID=?", (bid,))
    conn.commit()
    messagebox.showinfo("Success", "Book Returned!")

def show_reports():
    text.delete("1.0", tk.END)

    text.insert(tk.END, "Most Borrowed Book:\n")
    cur.execute("""
    SELECT Books.Title, COUNT(Borrow.BookID)
    FROM Borrow JOIN Books ON Borrow.BookID=Books.BookID
    GROUP BY Borrow.BookID ORDER BY COUNT(Borrow.BookID) DESC LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        text.insert(tk.END, f"{row[0]} (Borrowed {row[1]} times)\n")

    text.insert(tk.END, "\nBooks Borrowed Per Member:\n")
    cur.execute("""
    SELECT Members.Name, COUNT(Borrow.MemberID)
    FROM Borrow JOIN Members ON Borrow.MemberID = Members.MemberID
    GROUP BY Borrow.MemberID
    """)
    for r in cur.fetchall():
        text.insert(tk.END, f"{r[0]} - {r[1]} books\n")

    text.insert(tk.END, "\nOverdue Books (Not Returned 15+ days):\n")
    cur.execute("""
    SELECT Members.Name, Books.Title, Borrow.IssueDate
    FROM Borrow 
    JOIN Books ON Borrow.BookID=Books.BookID
    JOIN Members ON Borrow.MemberID=Members.MemberID
    WHERE ReturnDate IS NULL
    """)
    for r in cur.fetchall():
        issue = datetime.strptime(r[2], "%Y-%m-%d")
        if (datetime.today() - issue).days > 15:
            text.insert(tk.END, f"{r[0]} - {r[1]} (Issued: {r[2]})\n")

# ---------------- GUI ----------------

root = tk.Tk()
root.title("Library Management System")
root.geometry("850x550")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Add Book Tab
tab1 = tk.Frame(notebook)
notebook.add(tab1, text="Add Book")

tk.Label(tab1, text="Book ID:").grid(row=0, column=0)
entry_bid = tk.Entry(tab1); entry_bid.grid(row=0, column=1)

tk.Label(tab1, text="Title:").grid(row=1, column=0)
entry_title = tk.Entry(tab1); entry_title.grid(row=1, column=1)

tk.Label(tab1, text="Author:").grid(row=2, column=0)
entry_author = tk.Entry(tab1); entry_author.grid(row=2, column=1)

tk.Label(tab1, text="Genre:").grid(row=3, column=0)
entry_genre = tk.Entry(tab1); entry_genre.grid(row=3, column=1)

tk.Label(tab1, text="Available Copies:").grid(row=4, column=0)
entry_copies = tk.Entry(tab1); entry_copies.grid(row=4, column=1)

tk.Button(tab1, text="Add Book", command=add_book).grid(row=5, column=1)

# Add Member Tab
tab2 = tk.Frame(notebook)
notebook.add(tab2, text="Add Member")

tk.Label(tab2, text="Member ID:").grid(row=0, column=0)
entry_mid = tk.Entry(tab2); entry_mid.grid(row=0, column=1)

tk.Label(tab2, text="Name:").grid(row=1, column=0)
entry_mname = tk.Entry(tab2); entry_mname.grid(row=1, column=1)

tk.Label(tab2, text="Phone:").grid(row=2, column=0)
entry_phone = tk.Entry(tab2); entry_phone.grid(row=2, column=1)

tk.Label(tab2, text="Join Date (YYYY-MM-DD):").grid(row=3, column=0)
entry_join = tk.Entry(tab2); entry_join.grid(row=3, column=1)

tk.Button(tab2, text="Add Member", command=add_member).grid(row=4, column=1)

# Issue Book Tab
tab3 = tk.Frame(notebook)
notebook.add(tab3, text="Issue Book")

tk.Label(tab3, text="Book ID:").grid(row=0, column=0)
entry_ibook = tk.Entry(tab3); entry_ibook.grid(row=0, column=1)

tk.Label(tab3, text="Member ID:").grid(row=1, column=0)
entry_imember = tk.Entry(tab3); entry_imember.grid(row=1, column=1)

tk.Label(tab3, text="Issue Date (YYYY-MM-DD):").grid(row=2, column=0)
entry_idate = tk.Entry(tab3); entry_idate.grid(row=2, column=1)

tk.Button(tab3, text="Issue Book", command=issue_book).grid(row=3, column=1)

# Return Book Tab
tab4 = tk.Frame(notebook)
notebook.add(tab4, text="Return Book")

tk.Label(tab4, text="Book ID:").grid(row=0, column=0)
entry_rbook = tk.Entry(tab4); entry_rbook.grid(row=0, column=1)

tk.Label(tab4, text="Member ID:").grid(row=1, column=0)
entry_rmember = tk.Entry(tab4); entry_rmember.grid(row=1, column=1)

tk.Label(tab4, text="Return Date (YYYY-MM-DD):").grid(row=2, column=0)
entry_rdate = tk.Entry(tab4); entry_rdate.grid(row=2, column=1)

tk.Button(tab4, text="Return Book", command=return_book).grid(row=3, column=1)

# Reports Tab
tab5 = tk.Frame(notebook)
notebook.add(tab5, text="Reports")

text = tk.Text(tab5, width=90, height=25)
text.pack()
tk.Button(tab5, text="Show Reports", command=show_reports).pack()

root.mainloop()
