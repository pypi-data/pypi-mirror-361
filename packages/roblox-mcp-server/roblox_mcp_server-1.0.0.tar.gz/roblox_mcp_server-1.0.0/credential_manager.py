import tkinter as tk
import webbrowser
from tkinter import messagebox
import keyring

SERVICE_ID = "ROBLOX_MCP_SERVER"
USERNAME = ".ROBLOXSECURITY"


def save_roblox_auth_key(key: str):
    try:
        keyring.set_password(SERVICE_ID, USERNAME, key)
        return True, "Roblox key saved securely!"
    except Exception as e:
        return False, f"Error saving key: {e}"


def get_roblox_auth_key():
    try:
        key = keyring.get_password(SERVICE_ID, USERNAME)
        if key:
            return True, key
        else:
            return False, "No Roblox key found."
    except Exception as e:
        return False, f"Error retrieving key: {e}"


def clear_roblox_auth_key():
    try:
        if keyring.get_password(SERVICE_ID, USERNAME):
            keyring.delete_password(SERVICE_ID, USERNAME)
            return True, "Roblox key cleared successfully!"
        else:
            return False, "No Roblox key to clear."
    except Exception as e:
        return False, f"Error clearing key: {e}"


class RobloxKeyManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Roblox Key Manager (Roblox MCP Server)")
        master.geometry("400x300")

        self.key_label = tk.Label(master, text="Enter Roblox Auth Key:")
        self.key_label.pack(pady=5)

        self.key_entry = tk.Entry(master, width=50, show="*")
        self.key_entry.pack(pady=5)

        self.save_button = tk.Button(
            master, text="Save Key", command=self.handle_save_key
        )
        self.save_button.pack(pady=5)

        self.get_button = tk.Button(master, text="Get Key", command=self.handle_get_key)
        self.get_button.pack(pady=5)

        self.clear_button = tk.Button(
            master, text="Clear Key", command=self.handle_clear_key
        )
        self.clear_button.pack(pady=5)

        self.status_label = tk.Label(master, text="", fg="blue")
        self.status_label.pack(pady=10)

        self.display_label = tk.Label(
            master,
            text="Stored Key: (Not shown for security)",
            wraplength=350,
            justify="left",
        )
        self.display_label.pack(pady=5)

        self.link_label = tk.Label(
            master, text="How to get ROBLOX Auth Key? [Click here]", cursor="hand2"
        )
        self.link_label.pack(pady=5)
        self.link_label.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new(
                "https://github.com/ro-py/ro.py/blob/main/docs/tutorials/roblosecurity.md"
            ),
        )

    def handle_save_key(self):
        key = self.key_entry.get()
        if not key:
            messagebox.showwarning("Input Error", "Please enter a key to save.")
            return

        success, message = save_roblox_auth_key(key)
        if success:
            messagebox.showinfo("Success", message)
            self.status_label.config(text=message, fg="green")
            self.key_entry.delete(0, tk.END)
            self.display_label.config(text="Stored Key: ***** (Key updated)")
        else:
            messagebox.showerror("Error", message)
            self.status_label.config(text=message, fg="red")

    def handle_get_key(self):
        success, result = get_roblox_auth_key()
        if success:
            self.display_label.config(text=f"Stored Key: {result}")
            self.status_label.config(text="Key retrieved successfully!", fg="green")
            messagebox.showinfo(
                "Key Retrieved",
                "Key was retrieved. Check the 'Stored Key' label. "
                "In a real app, you'd use it directly, not display it!",
            )
        else:
            self.display_label.config(text="Stored Key: (None found)")
            self.status_label.config(text=result, fg="red")
            messagebox.showerror("Error", result)

    def handle_clear_key(self):
        success, message = clear_roblox_auth_key()
        if success:
            messagebox.showinfo("Success", message)
            self.status_label.config(text=message, fg="green")
            self.display_label.config(text="Stored Key: (None found)")
        else:
            messagebox.showerror("Error", message)
            self.status_label.config(text=message, fg="red")


def open_app():
    root = tk.Tk()
    app = RobloxKeyManagerApp(root)
    root.mainloop()
