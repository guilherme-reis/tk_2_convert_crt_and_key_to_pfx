import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import platform

ERROR_TITLE = "Error"

def is_openssl_installed():
    try:
        process = subprocess.Popen(['openssl', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, _ = process.communicate()
        return process.returncode == 0
    except FileNotFoundError:
        return False

def execute_command(cmd):
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode(), stderr.decode()
    except subprocess.CalledProcessError as e:
        return None, e.stderr

def show_error(message):
    messagebox.showerror(ERROR_TITLE, message)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, message + "\n")
    result_text.config(state=tk.DISABLED)

def clear_result_text():
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)

def convert_crt_and_key_to_pfx():
    if not is_openssl_installed():
        show_error("OpenSSL is not installed. Please install OpenSSL and try again.")
        return
    
    crt_file = entry_crt.get()
    key_file = entry_key.get()
    password = entry_pass.get()
    
    if not crt_file or not key_file or not password:
        show_error("Please fill in all the required fields.")
        return
    
    clear_result_text()
    
    current_directory = os.path.dirname(crt_file)
    output_file = os.path.join(current_directory, f'certificate_password_{password}.pfx')
    
    cmd = [
        'openssl', 'pkcs12', '-export', '-out', output_file,
        '-inkey', key_file, '-in', crt_file, '-passin', f'pass:{password}', '-legacy', '-passout', f'pass:{password}'
    ]
    
    stdout, stderr = execute_command(' '.join(cmd))
    
    if stderr:
        show_error(f'Error executing the command: {stderr}')
    else:
        print(stdout)
        print('Conversion completed successfully!\n')
        messagebox.showinfo("Success", "Conversion completed successfully!")
        

        ler_pfx_cmd = f'openssl pkcs12 -in {output_file} -clcerts -nokeys -passin pass:{password} -legacy | openssl x509 -noout -subject -nameopt sep_multiline'
        result_ler_pfx, _ = execute_command(ler_pfx_cmd)

        if result_ler_pfx is not None:
            print(result_ler_pfx.replace("subject=", "Certificate Data:"))
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f'Crt File: {output_file}\n')
            result_text.insert(tk.END, result_ler_pfx.replace("subject=", "Certificate Data:") + "\n")
        else:
            show_error("Error reading certificate data.")

def browse_file(entry_widget, file_type):
    file_path = filedialog.askopenfilename(title=f"Select the {file_type} file.", filetypes=[(f"{file_type.upper()} Files", f"*.{file_type.lower()}")])
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)

def create_label_and_entry(frame, row, text, width=None):
    label = tk.Label(frame, text=text)
    label.grid(row=row, column=0, padx=(0, 5), pady=10, sticky=tk.W)
    
    entry = tk.Entry(frame, width=width or 65)
    entry.grid(row=row, column=1, padx=(0, 5), pady=10)
    
    return entry

window = tk.Tk()

frame_input = tk.Frame(window)
frame_input.pack(padx=10, pady=10)

entry_crt = create_label_and_entry(frame_input, 0, "Path of the CRT file:")
entry_key = create_label_and_entry(frame_input, 1, "Path of the KEY file:")
entry_pass = create_label_and_entry(frame_input,2, "Password:")


button_browse_crt = tk.Button(frame_input, text="Browse", command=lambda: browse_file(entry_crt, "CRT"))
button_browse_crt.grid(row=0, column=2, pady=10)

button_browse_key = tk.Button(frame_input, text="Browse", command=lambda: browse_file(entry_key, "KEY"))
button_browse_key.grid(row=1, column=2, pady=10)

button_convert = tk.Button(window, text="Convert", command=convert_crt_and_key_to_pfx)
button_convert.pack(pady=10)

button_clear_result = tk.Button(window, text="Clear Result", command=clear_result_text)
button_clear_result.pack(pady=10)

result_text = tk.Text(window, height=10, width=100, state=tk.DISABLED)
result_text.pack(padx=10, pady=10)

window.title("CRT and KEY to PFX Converter")
window_width = 820
window_height = 400
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x_coordinate = (screen_width / 2) - (window_width / 2)
y_coordinate = (screen_height / 2) - (window_height / 2)

window.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

window.update_idletasks()

window.mainloop()
