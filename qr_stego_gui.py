import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from PIL import Image, ImageTk
from qr_stego import QRStego

class QRStegoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Stego: QR Code Steganography Tool")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.stego = QRStego()
        
        # Variables
        self.method_var = tk.StringVar(value="payload")
        self.output_filename = tk.StringVar(value="qr_stego_output.png")
        self.password_var = tk.StringVar()
        self.qr_image = None
        
        # Create tabs
        self.tab_control = ttk.Notebook(root)
        
        self.encode_tab = ttk.Frame(self.tab_control)
        self.decode_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.encode_tab, text='Encode')
        self.tab_control.add(self.decode_tab, text='Decode')
        self.tab_control.pack(expand=1, fill="both")
        
        # Set up the Encode tab
        self.setup_encode_tab()
        
        # Set up the Decode tab
        self.setup_decode_tab()
    
    def setup_encode_tab(self):
        # Create frames
        input_frame = ttk.LabelFrame(self.encode_tab, text="Input")
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        options_frame = ttk.LabelFrame(self.encode_tab, text="Options")
        options_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        output_frame = ttk.LabelFrame(self.encode_tab, text="Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input frame contents
        ttk.Label(input_frame, text="Visible Message:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.visible_message = tk.Text(input_frame, height=3, width=50)
        self.visible_message.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Secret Message:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.secret_message = tk.Text(input_frame, height=5, width=50)
        self.secret_message.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Options frame contents
        ttk.Label(options_frame, text="Steganography Method:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        method_combo = ttk.Combobox(options_frame, textvariable=self.method_var)
        method_combo['values'] = ('payload', 'pixels')
        method_combo['state'] = 'readonly'
        method_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Password (optional):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        password_entry = ttk.Entry(options_frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Output Filename:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        filename_entry = ttk.Entry(options_frame, textvariable=self.output_filename)
        filename_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        browse_btn = ttk.Button(options_frame, text="Browse", command=self.browse_save_location)
        browse_btn.grid(row=2, column=2, padx=5, pady=5)
        
        generate_btn = ttk.Button(options_frame, text="Generate QR Code", command=self.generate_qr)
        generate_btn.grid(row=3, column=0, columnspan=3, padx=5, pady=10)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Output frame contents
        self.output_image_label = ttk.Label(output_frame)
        self.output_image_label.pack(expand=True, fill="both", padx=10, pady=10)
    
    def setup_decode_tab(self):
        # Create frames
        input_frame = ttk.LabelFrame(self.decode_tab, text="Input")
        input_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        options_frame = ttk.LabelFrame(self.decode_tab, text="Options")
        options_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        results_frame = ttk.LabelFrame(self.decode_tab, text="Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input frame contents
        ttk.Label(input_frame, text="QR Code Image:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_file_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_file_var, width=50)
        input_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        browse_btn = ttk.Button(input_frame, text="Browse", command=self.browse_input_file)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Options frame contents
        ttk.Label(options_frame, text="Try Method:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        decode_method_var = tk.StringVar(value="both")
        method_combo = ttk.Combobox(options_frame, textvariable=decode_method_var)
        method_combo['values'] = ('both', 'payload', 'pixels')
        method_combo['state'] = 'readonly'
        method_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.decode_method_var = decode_method_var
        
        ttk.Label(options_frame, text="Password (if needed):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.decode_password_var = tk.StringVar()
        password_entry = ttk.Entry(options_frame, textvariable=self.decode_password_var, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        decode_btn = ttk.Button(options_frame, text="Decode QR Code", command=self.decode_qr)
        decode_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Results frame contents
        ttk.Label(results_frame, text="Visible Message:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.visible_result = tk.Text(results_frame, height=3, width=50)
        self.visible_result.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        ttk.Label(results_frame, text="Hidden Message:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.hidden_result = tk.Text(results_frame, height=5, width=50)
        self.hidden_result.grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(1, weight=1)
    
    def browse_save_location(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.output_filename.set(filename)
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
    
    # def generate_qr(self):
    #     visible_msg = self.visible_message.get("1.0", tk.END).strip()
    #     secret_msg = self.secret_message.get("1.0", tk.END).strip()
    #     password = self.password_var.get() if self.password_var.get() else None
    #     output_file = self.output_filename.get()
    #     method = self.method_var.get()
        
    #     if not visible_msg:
    #         messagebox.showerror("Error", "Visible message is required")
    #         return
        
    #     if not secret_msg:
    #         messagebox.showerror("Error", "Secret message is required")
    #         return
        
    #     try:
    #         if method == "payload":
    #             img = self.stego.embed_message_in_payload(visible_msg, secret_msg, password)
    #             img.save(output_file)
    #         else:  # pixels method
    #             self.stego.embed_message_in_pixels(visible_msg, secret_msg, output_file, password)
    #             img = Image.open(output_file)
            
    #         # Display the generated QR code
    #         self.display_image(img)
    #         messagebox.showinfo("Success", f"QR code with hidden message saved as {output_file}")
        
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
    
    def generate_qr(self):
        visible_msg = self.visible_message.get("1.0", tk.END).strip()
        secret_msg = self.secret_message.get("1.0", tk.END).strip()
        password = self.password_var.get() if self.password_var.get() else None
        output_file = self.output_filename.get()
        method = self.method_var.get()
        
        if not visible_msg:
            messagebox.showerror("Error", "Visible message is required")
            return
        
        try:
            if secret_msg:  # Only use steganography if there's a secret message
                if method == "payload":
                    img = self.stego.embed_message_in_payload(visible_msg, secret_msg, password)
                    img.save(output_file)
                else:  # pixels method
                    self.stego.embed_message_in_pixels(visible_msg, secret_msg, output_file, password)
                    img = Image.open(output_file)
            else:  # Generate simple QR code without steganography
                img = self.stego.create_qr(visible_msg)
                img.save(output_file)
            
            # Display the generated QR code
            self.display_image(img)
            if secret_msg:
                messagebox.showinfo("Success", f"QR code with hidden message saved as {output_file}")
            else:
                messagebox.showinfo("Success", f"Simple QR code saved as {output_file}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")

    def decode_qr(self):
        input_file = self.input_file_var.get()
        password = self.decode_password_var.get() if self.decode_password_var.get() else None
        method = self.decode_method_var.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid QR code image")
            return
        
        try:
            visible_msg = None
            secret_msg = None
            
            # Try both methods if selected
            if method == "both" or method == "payload":
                visible_msg, secret_from_payload = self.stego.extract_from_payload(input_file, password)
                if secret_from_payload:
                    secret_msg = secret_from_payload
            
            if (method == "both" and not secret_msg) or method == "pixels":
                v_msg, secret_from_pixels = self.stego.extract_from_pixels(input_file, password)
                if secret_from_pixels:
                    secret_msg = secret_from_pixels
                if not visible_msg:
                    visible_msg = v_msg
            
            # Display results
            self.visible_result.delete("1.0", tk.END)
            self.hidden_result.delete("1.0", tk.END)
            
            if visible_msg:
                self.visible_result.insert(tk.END, visible_msg)
            else:
                self.visible_result.insert(tk.END, "No visible message found or could not decode QR code")
            
            if secret_msg:
                self.hidden_result.insert(tk.END, secret_msg)
            else:
                self.hidden_result.insert(tk.END, "No hidden message found")
            
            # Display the QR code
            self.display_image(Image.open(input_file), tab="decode")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode QR code: {str(e)}")
    
    def display_image(self, img, tab="encode"):
        # Resize image for display if needed
        width, height = img.size
        max_size = 300
        
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            width = int(width * ratio)
            height = int(height * ratio)
            img = img.resize((width, height), Image.LANCZOS)
        
        # Convert to PhotoImage and display
        photo = ImageTk.PhotoImage(img)
        
        if tab == "encode":
            self.output_image_label.config(image=photo)
            self.output_image_label.image = photo  # Keep a reference
        else:
            # If we need to display in decode tab, we'd add a label there
            pass


def main():
    root = tk.Tk()
    app = QRStegoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
