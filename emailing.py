import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import csv
import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
import threading
import sys
from PIL import Image, ImageTk, ImageDraw
import json
import re

# --- Global Variables ---
df = None

# --- MODERN UI CONFIG ---
PRIMARY_COLOR = "#1e3a8a"
PRIMARY_HOVER = "#1e40af"
SUCCESS_COLOR = "#059669"
SUCCESS_HOVER = "#047857"
ERROR_COLOR = "#dc2626"
WARNING_COLOR = "#d97706"
INFO_COLOR = "#0891b2"
BG_GRADIENT_START = "#0f172a"
BG_GRADIENT_MID = "#1e293b"
BG_GRADIENT_END = "#334155"
CARD_BG = "#ffffff"
CARD_BORDER = "#e2e8f0"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#64748b"
TEXT_LIGHT = "#f1f5f9"
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_HEADING = (FONT_FAMILY, 16, "bold")
FONT_SUBHEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_MONO = ("Consolas", 10)
FONT_FOOTER = (FONT_FAMILY, 10)


# --- Helper function for PyInstaller paths ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ---------- Signatures persistence & helpers ----------
SIGNATURES_FILE = resource_path("signatures.json")


def default_signatures():
    return {
        "Shivam Jha": "<p><strong>Thanks & Regards,</strong><br><br><strong>Shivam Jha</strong><br>Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 8757449770 | <a href=\"https://www.linkedin.com/in/shivam-jha-1649a2188/\" style=\"color:#075985; text-decoration:none;\"><strong>LinkedIn</strong></a></p>",
        "Abdul Kalam": "<p><strong>Thanks & Regards,</strong><br><br><strong>Abdul Kalam</strong><br>Placement Core<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 7075648725 | <a href=\"https://www.linkedin.com/in/abdul-kalam-shaik-b250b4203/\" style=\"color:#075985; text-decoration:none;\"><strong>LinkedIn</strong></a></p>",
        "Patanjali Shandilya": "<p><strong>Thanks & Regards,</strong><br><br><strong>Patanjali Shandilya</strong><br>Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 8871177566 | <a href=\"https://www.linkedin.com/in/patanjali-shandilya-aa6240242/\" style=\"color:#075985; text-decoration:none;\"><strong>LinkedIn</strong></a></p>",
        "Somanath Mahapatra": "<p><strong>Thanks & Regards,</strong><br><br><strong>Somanath Mahapatra</strong><br>Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 7008362910 | <a href=\"https://www.linkedin.com/in/somanath-mahapatra-28066028a/\" style=\"color:#075985; text-decoration:none;\"><strong>LinkedIn</strong></a></p>",
        "Amireddy Vinay Kumar": "<p><strong>Thanks & Regards,</strong><br><br><strong>Amireddy Vinay Kumar</strong><br>Deputy Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 6281675530</p>",
        "Sampurna Saha": "<p><strong>Thanks & Regards,</strong><br><br><strong>Sampurna Saha</strong><br>Deputy Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 9051030103</p>",
        "Harshitha Obula": "<p><strong>Thanks & Regards,</strong><br><br><strong>Harshitha Obula</strong><br>Deputy Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 6301412814</p>",
        "Nikhil R": "<p><strong>Thanks & Regards,</strong><br><br><strong>Nikhil R</strong><br>Deputy Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 7306142561 | <a href=\"https://www.linkedin.com/in/nikhilr2503/\" style=\"color:#075985; text-decoration:none;\"><strong>LinkedIn</strong></a></p>",
        "Mayank": "<p><strong>Thanks & Regards,</strong><br><br><strong>Mayank</strong><br>Deputy Placement Coordinator<br>Department of Chemical Engineering<br>Indian Institute of Technology Madras<br>Chennai | 600036 | India<br>Phone: +91 8160493208</p>"
    }

# Enhanced signature validation function
def validate_signature_styling(signature_html):
    """Ensure consistent styling in signatures"""
    # Check for LinkedIn links and ensure they have the correct color
    if 'linkedin.com' in signature_html.lower():
        # Replace any existing LinkedIn link colors with the standard blue
        import re
        signature_html = re.sub(
            r'(<a[^>]*href=["\'][^"\']*linkedin[^"\']*["\'][^>]*style=["\'][^"\']*color:)[^;"\')]+',
            r'\1#075985',
            signature_html,
            flags=re.IGNORECASE
        )
    return signature_html

def load_signatures():
    """Load signatures with enhanced debugging and JSON file preference"""
    print(f"DEBUG: Looking for signatures file at: {SIGNATURES_FILE}")
    print(f"DEBUG: File exists: {Path(SIGNATURES_FILE).exists()}")

    try:
        p = Path(SIGNATURES_FILE)
        if p.exists():
            print("DEBUG: JSON file found, attempting to load...")
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"DEBUG: Successfully loaded {len(data)} signatures from JSON")

            if isinstance(data, dict) and data:
                # Debug: Show what colors are being loaded
                print("DEBUG: Loaded signatures with colors:")
                for name, sig in data.items():
                    if "color:#" in sig:
                        # Extract color value for debugging
                        start = sig.find("color:#")
                        end = sig.find(";", start) if sig.find(";", start) > start else sig.find("\"", start)
                        if end > start:
                            color = sig[start:end]
                            print(f"  {name}: {color}")
                        else:
                            print(f"  {name}: color found but couldn't extract")
                    else:
                        print(f"  {name}: no color styling found")
                return data
        else:
            print("DEBUG: JSON file doesn't exist, will create with defaults")
    except Exception as e:
        print(f"DEBUG: Error loading JSON file: {e}")

    # If we get here, either file doesn't exist or there was an error
    print("DEBUG: Using default signatures and creating JSON file")
    sigs = default_signatures()
    try:
        Path(SIGNATURES_FILE).write_text(json.dumps(sigs, ensure_ascii=False, indent=2), encoding="utf-8")
        print("DEBUG: Successfully created new signatures.json file")
    except Exception as e:
        print(f"DEBUG: Could not create JSON file: {e}")
    return sigs


# Modified save_signatures function with validation
def save_signatures(signatures: dict) -> bool:
    try:
        # Validate and normalize signatures before saving
        normalized_signatures = {}
        for name, sig in signatures.items():
            normalized_signatures[name] = validate_signature_styling(sig)

        with open(SIGNATURES_FILE, 'w', encoding='utf-8') as f:
            json.dump(normalized_signatures, f, ensure_ascii=False, indent=2)
        print(f"DEBUG: Successfully saved {len(normalized_signatures)} signatures to JSON with validation")
        return True
    except Exception as e:
        print(f"DEBUG: Could not save signatures: {e}")
        return False

def force_reload_signatures():
    """Force reload signatures from JSON file"""
    global signature_map
    print("DEBUG: Force reloading signatures...")
    signature_map = load_signatures()

    # Update the dropdown
    signature_dropdown['values'] = list(signature_map.keys())
    if signature_map:
        selected_signature.set(list(signature_map.keys())[0])

    print("DEBUG: Signatures reloaded and dropdown updated")
    return signature_map


def strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# -----------------------------------------------------

# --- UI and Backend Functions ---
def create_gradient_image(width, height):
    if width <= 0 or height <= 0: return None
    gradient_image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient_image)
    colors = [BG_GRADIENT_START, BG_GRADIENT_MID, BG_GRADIENT_END]
    sections = len(colors) - 1
    section_height = height // sections
    for section in range(sections):
        color1, color2 = colors[section], colors[section + 1]
        y_start = section * section_height
        y_end = (section + 1) * section_height if section < sections - 1 else height
        r1, g1, b1 = root.winfo_rgb(color1)
        r1 //= 256;
        g1 //= 256;
        b1 //= 256
        r2, g2, b2 = root.winfo_rgb(color2)
        r2 //= 256;
        g2 //= 256;
        b2 //= 256
        steps = y_end - y_start
        if steps <= 0: continue
        for i in range(steps):
            y = y_start + i
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    return gradient_image


def update_background(event):
    bg_image = create_gradient_image(event.width, event.height)
    if bg_image:
        bg_photo = ImageTk.PhotoImage(bg_image)
        background_label.config(image=bg_photo)
        background_label.image = bg_photo


def process_logo(path, size):
    img = Image.open(resource_path(path)).convert("RGBA")
    img.thumbnail((size, size), Image.LANCZOS)
    square_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    square_img.paste(img, offset)
    return ImageTk.PhotoImage(square_img)


def upload_csv():
    global df
    filepath = filedialog.askopenfilename(title="Select Contacts CSV", filetypes=[('CSV Files', '*.csv')])
    if not filepath: return
    try:
        with open(filepath, newline='', encoding='utf-8-sig') as f:
            df = list(csv.DictReader(f))
        update_status(f"✅ Successfully loaded {len(df)} contacts", "success")
        log_message(f"📊 Loaded {len(df)} contacts from CSV")
        animate_counter(contact_counter, len(df))
    except Exception as e:
        update_status(f"❌ Error loading file: {e}", "error")


def animate_counter(label, target, current=0):
    if current <= target:
        label.config(text=str(current))
        label.after(20, lambda: animate_counter(label, target, current + max(1, target // 20)))
    else:
        label.config(text=str(target))


def start_sending_emails():
    if df is None:
        update_status("⚠️ Please upload a CSV file first", "warning")
        return
    threading.Thread(target=send_emails_thread, daemon=True).start()


def send_emails_thread():
    send_button.config(state="disabled")
    smtp_user = smtp_user_entry.get()
    smtp_pass = password_entry.get()
    if not smtp_user or not smtp_pass:
        update_status("🔐 Credentials required", "error")
        send_button.config(state="normal")
        return

    selected_template_name = selected_template.get()
    html_filename = template_map.get(selected_template_name)
    research_image_filename = research_image_map.get(selected_template_name,
                                                     "research_hexagon.png")  # Fallback to default

    filepath = resource_path(os.path.join("templates", html_filename))
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            template_html = f.read()
    except FileNotFoundError:
        update_status(f"📄 Template '{html_filename}' not found", "error")
        send_button.config(state="normal")
        return
    try:
        update_status("🔄 Connecting to email server...", "info")
        progress_bar['maximum'] = len(df)
        progress_bar['value'] = 0
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            update_status("📤 Sending emails...", "info")
            for i, row in enumerate(df, start=1):
                company_name = row.get('Company Name') or 'your organization'
                row['Company'] = company_name
                to_addr = row.get('Email')
                if not to_addr: continue
                msg = build_email_message(smtp_user, to_addr, row, template_html, research_image_filename)
                smtp.send_message(msg)
                log_message(f"✉️ [{i}/{len(df)}] Sent to {to_addr}")
                update_status(f"📨 Sending... {i}/{len(df)} ({int(i / len(df) * 100)}%)", "info")
                progress_bar['value'] = i
                email_sent_counter.config(text=str(i))
                root.update_idletasks()
                time.sleep(1.0)
        update_status("🎉 All emails sent successfully!", "success")
    except smtplib.SMTPAuthenticationError:
        update_status("❌ Authentication failed", "error")
    except Exception as e:
        update_status(f"❌ Error: {e}", "error")
    finally:
        send_button.config(state="normal")
        progress_bar['value'] = 0


def build_email_message(from_addr, to_addr, row, template_html, research_image_filename):
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = "IIT Madras Placement Invitation for the 2025-2026 Academic Year"
    msg_root['From'] = from_addr
    msg_root['To'] = to_addr
    msg_alt = MIMEMultipart('alternative')
    msg_root.attach(msg_alt)

    sig_name = selected_signature.get() if selected_signature.get() else (
        list(signature_map.keys())[0] if signature_map else "")
    sig_html = signature_map.get(sig_name, "")
    sig_plain = strip_html(sig_html)

    plain_text = f"Dear {row.get('HR Name', 'Hiring Manager')},\n\nGreetings from the Placement Team, IIT Madras.\n\n{sig_plain}"
    msg_alt.attach(MIMEText(plain_text, 'plain'))

    try:
        # Use a dictionary to handle the new signature placeholder gracefully
        template_vars = {
            "HR Name": row.get('HR Name', 'Hiring Manager'),
            "Company": row['Company'],
            "Signature": sig_html
        }
        html_body = template_html.format(**template_vars)
    except KeyError:
        # Fallback for older templates that might not have all placeholders
        html_body = template_html.replace("{HR Name}", row.get('HR Name', 'Hiring Manager'))
        html_body = html_body.replace("{Company}", row['Company'])
        html_body = html_body.replace("{Signature}", sig_html)  # Ensure signature is replaced

    msg_alt.attach(MIMEText(html_body, 'html'))

    image_files = [
        ('header', os.path.join('images', 'header_banner.jpg')),
        ('research', os.path.join('images', research_image_filename)),
        ('campus', os.path.join('images', 'campus.jpg')),
        ('logo', os.path.join('images', 'iit_logo.png'))
    ]

    for cid, filename in image_files:
        filepath = resource_path(filename)
        if Path(filepath).exists():
            with open(filepath, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<{cid}>')
                msg_root.attach(img)
        else:
            log_message(f"⚠️ Image not found: {filepath}")
    return msg_root


def log_message(message):
    timestamp = time.strftime("%H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] {message}\n", "log")
    log_text.see(tk.END)


def update_status(message, status_type="info"):
    colors = {"success": SUCCESS_COLOR, "error": ERROR_COLOR, "warning": WARNING_COLOR, "info": INFO_COLOR}
    status_label.config(text=message, fg=colors.get(status_type, TEXT_PRIMARY))
    icons = {"success": "✅", "error": "❌", "warning": "⚠", "info": "ℹ"}
    status_icon.config(text=icons.get(status_type, "•"), fg=colors.get(status_type, TEXT_PRIMARY))


class ModernCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=CARD_BG, relief='flat', highlightthickness=1, highlightbackground=CARD_BORDER,
                         **kwargs)


class ModernButton(tk.Button):
    def __init__(self, parent, bg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, **kwargs):
        super().__init__(parent, relief='flat', bd=0, cursor='hand2', activebackground=hover_color,
                         font=FONT_SUBHEADING, bg=bg_color, fg='white', padx=20, pady=12, **kwargs)
        self.bg_color, self.hover_color = bg_color, hover_color
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_color))
        self.bind("<Leave>", lambda e: self.configure(bg=self.bg_color))


# --- Configure ttk styles for better visibility ---
def configure_ttk_styles():
    style = ttk.Style()

    # Configure Combobox style for better visibility
    style.configure('Modern.TCombobox',
                    fieldbackground='white',
                    background='white',
                    foreground=TEXT_PRIMARY,
                    borderwidth=2,
                    relief='solid',
                    focuscolor=PRIMARY_COLOR,
                    selectbackground=PRIMARY_COLOR,
                    selectforeground='white',
                    arrowcolor=TEXT_PRIMARY)

    style.map('Modern.TCombobox',
              fieldbackground=[('readonly', 'white'),
                               ('focus', 'white')],
              selectbackground=[('readonly', PRIMARY_COLOR)],
              selectforeground=[('readonly', 'white')],
              bordercolor=[('focus', PRIMARY_COLOR),
                           ('!focus', CARD_BORDER)])

    # Configure dropdown list style
    root.option_add('*TCombobox*Listbox.selectBackground', PRIMARY_COLOR)
    root.option_add('*TCombobox*Listbox.selectForeground', 'white')
    root.option_add('*TCombobox*Listbox.background', 'white')
    root.option_add('*TCombobox*Listbox.foreground', TEXT_PRIMARY)
    root.option_add('*TCombobox*Listbox.font', FONT_BODY)


# --- Main UI Setup ---
root = tk.Tk()
root.title("IITM ConnectSuite - Professional Edition")
root.geometry("1200x800")
root.resizable(True, True)
root.minsize(1100, 750)

# Configure ttk styles after root is created
configure_ttk_styles()

background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.bind("<Configure>", update_background)

try:
    placement_logo_tk = process_logo(os.path.join('images', 'placement_logo.png'), 90)
    iit_logo_tk = process_logo(os.path.join('images', 'iit_logo.png'), 60)
except Exception as e:
    print(f"Error loading images from 'images' folder: {e}")
    placement_logo_tk = iit_logo_tk = None

main_frame = tk.Frame(root, bg=BG_GRADIENT_START)
main_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=1.0, relheight=1.0)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

header_frame = tk.Frame(main_frame, bg=BG_GRADIENT_START)
header_frame.grid(row=0, column=0, sticky='ew', padx=30, pady=(20, 0))
header_frame.grid_columnconfigure(1, weight=1)
if placement_logo_tk: tk.Label(header_frame, image=placement_logo_tk, bg=BG_GRADIENT_START).grid(row=0, column=0,
                                                                                                 rowspan=2,
                                                                                                 padx=(0, 20),
                                                                                                 sticky='w')
title_frame = tk.Frame(header_frame, bg=BG_GRADIENT_START)
title_frame.grid(row=0, column=1, rowspan=2, sticky='w')
tk.Label(title_frame, text="IITM ConnectSuite", font=FONT_TITLE, fg=TEXT_LIGHT, bg=BG_GRADIENT_START).pack(anchor='sw')
tk.Label(title_frame, text="Professional Outreach Platform • IIT Madras PG CH Team", font=FONT_SMALL, fg="#94a3b8",
         bg=BG_GRADIENT_START).pack(anchor='nw')
if iit_logo_tk: tk.Label(header_frame, image=iit_logo_tk, bg=BG_GRADIENT_START).grid(row=0, column=2, rowspan=2,
                                                                                     padx=(20, 0), sticky='e')

stats_frame = tk.Frame(main_frame, bg=BG_GRADIENT_START, height=60)
stats_frame.grid(row=1, column=0, sticky='ew', padx=30, pady=(10, 20))
for i in range(2): stats_frame.columnconfigure(i, weight=1)
stat_cards = [("📊", "Contacts Loaded", "contact_counter", "0"), ("📤", "Emails Sent", "email_sent_counter", "0")]
for i, (icon, label, var_name, default) in enumerate(stat_cards):
    stat_card = tk.Frame(stats_frame, bg="#1e293b", relief='flat', highlightthickness=1, highlightbackground="#334155")
    stat_card.grid(row=0, column=i, sticky='nsew', padx=5)
    tk.Label(stat_card, text=icon, font=(FONT_FAMILY, 20), fg=PRIMARY_COLOR, bg="#1e293b").pack(side='left',
                                                                                                padx=(15, 5))
    text_frame = tk.Frame(stat_card, bg="#1e293b")
    text_frame.pack(side='left', fill='both', expand=True, pady=10)
    counter_label = tk.Label(text_frame, text=default, font=FONT_HEADING, fg=TEXT_LIGHT, bg="#1e293b")
    counter_label.pack(anchor='w')
    if var_name == "contact_counter":
        contact_counter = counter_label
    elif var_name == "email_sent_counter":
        email_sent_counter = counter_label
    tk.Label(text_frame, text=label, font=FONT_SMALL, fg="#94a3b8", bg="#1e293b").pack(anchor='w')

content_container = tk.Frame(main_frame, bg=BG_GRADIENT_START)
content_container.grid(row=2, column=0, sticky='nsew', padx=30, pady=(0, 30))
content_container.grid_columnconfigure(1, weight=1)
content_container.grid_rowconfigure(0, weight=1)

# --- REVISED: left_panel now uses grid with row weights and better sizing ---
left_panel = tk.Frame(content_container, bg=BG_GRADIENT_START, width=320)  # Fixed width for consistency
left_panel.grid(row=0, column=0, sticky='ns', padx=(0, 15))
left_panel.grid_propagate(False)  # Maintain fixed width
left_panel.grid_rowconfigure(0, weight=1)  # Configuration card can expand
left_panel.grid_rowconfigure(1, weight=0)  # Action card will take natural height

config_card = ModernCard(left_panel)
config_card.grid(row=0, column=0, sticky='new', pady=(0, 15))
config_card.grid_columnconfigure(0, weight=1)  # Allow content to expand horizontally

config_header = tk.Frame(config_card, bg=CARD_BG)
config_header.grid(row=0, column=0, sticky='ew', padx=25, pady=(20, 15))
tk.Label(config_header, text="⚙️", font=(FONT_FAMILY, 20), bg=CARD_BG).pack(side='left')
tk.Label(config_header, text="Configuration", font=FONT_HEADING, fg=TEXT_PRIMARY, bg=CARD_BG).pack(side='left',
                                                                                                   padx=(10, 0))

# Gmail Address
tk.Label(config_card, text="Gmail Address", font=FONT_SMALL, fg=TEXT_SECONDARY, bg=CARD_BG).grid(row=1, column=0,
                                                                                                 sticky='w', padx=25,
                                                                                                 pady=(0, 5))
smtp_user_entry = tk.Entry(config_card, font=FONT_BODY, relief='solid', bd=2, highlightthickness=1,
                           highlightcolor=PRIMARY_COLOR)
smtp_user_entry.grid(row=2, column=0, sticky='ew', padx=25, pady=(0, 15))

# App Password
tk.Label(config_card, text="App Password", font=FONT_SMALL, fg=TEXT_SECONDARY, bg=CARD_BG).grid(row=3, column=0,
                                                                                                sticky='w', padx=25,
                                                                                                pady=(0, 5))
password_entry = tk.Entry(config_card, font=FONT_BODY, relief='solid', bd=2, show="•", highlightthickness=1,
                          highlightcolor=PRIMARY_COLOR)
password_entry.grid(row=4, column=0, sticky='ew', padx=25, pady=(0, 15))

# Email Template
tk.Label(config_card, text="Email Template", font=FONT_SMALL, fg=TEXT_SECONDARY, bg=CARD_BG).grid(row=5, column=0,
                                                                                                  sticky='w', padx=25,
                                                                                                  pady=(0, 5))

template_map = {
    "🎓 IIT Madras Professional": "iit_madras_template.html",
    "🛢️ Oil & Gas": "oil_and_gas_template.html",
    "🧬 Pharma & Biotech": "pharma_template.html",
    "⚡ Battery & EV": "battery_ev_template.html",
    "💡 Semiconductor & Emerging Tech": "semiconductor_template.html",
    "♻️ Renewable & Environmental": "renewable_energy_template.html"
}
research_image_map = {
    "🎓 IIT Madras Professional": "research_hexagon.png",
    "🛢️ Oil & Gas": "research_hexagon3.png",
    "🧬 Pharma & Biotech": "research_hexagon2.png",
    "⚡ Battery & EV": "research_hexagon4.png",
    "💡 Semiconductor & Emerging Tech": "research_hexagon5.png",
    "♻️ Renewable & Environmental": "research_hexagon6.png"
}

selected_template = tk.StringVar()
template_dropdown = ttk.Combobox(config_card, textvariable=selected_template, values=list(template_map.keys()),
                                 state="readonly", font=FONT_BODY, style='Modern.TCombobox', height=10)
template_dropdown.grid(row=6, column=0, sticky='ew', padx=25, pady=(0, 15))
template_dropdown.set(list(template_map.keys())[0])

# --- SIGNATURES LOADING WITH DEBUG ---
print("=" * 60)
print("DEBUG: Starting signature loading process...")
signature_map = load_signatures()
print("=" * 60)

selected_signature = tk.StringVar()
if signature_map:
    selected_signature.set(list(signature_map.keys())[0])

# Sender Signature
tk.Label(config_card, text="Sender Signature", font=FONT_SMALL, fg=TEXT_SECONDARY, bg=CARD_BG).grid(row=7, column=0,
                                                                                                    sticky='w', padx=25,
                                                                                                    pady=(0, 5))
signature_dropdown = ttk.Combobox(config_card, textvariable=selected_signature, values=list(signature_map.keys()),
                                  state="readonly", font=FONT_BODY, style='Modern.TCombobox', height=10)
signature_dropdown.grid(row=8, column=0, sticky='ew', padx=25, pady=(0, 8))
if signature_map:
    signature_dropdown.set(list(signature_map.keys())[0])


def open_signature_editor():
    editor = tk.Toplevel(root)
    editor.title("Edit Signatures")
    editor.geometry("920x540")
    editor.configure(bg=CARD_BG)

    left = tk.Frame(editor, width=260, bg=CARD_BG)
    left.pack(side="left", fill="y", padx=8, pady=8)
    right = tk.Frame(editor, bg=CARD_BG)
    right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

    listbox = tk.Listbox(left, font=FONT_BODY, selectbackground=PRIMARY_COLOR, selectforeground='white')
    listbox.pack(fill="both", expand=True, padx=6, pady=6)
    for name in signature_map.keys():
        listbox.insert(tk.END, name)

    text_area = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=FONT_BODY)
    text_area.pack(fill="both", expand=True, padx=6, pady=6)

    def on_select(evt=None):
        sel = listbox.curselection()
        if not sel: return
        name = listbox.get(sel[0])
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, signature_map.get(name, ""))

    def save_current():
        sel = listbox.curselection()
        if not sel:
            update_status("⚠️ Select a signature to save", "warning")
            return
        name = listbox.get(sel[0])
        signature_map[name] = text_area.get("1.0", tk.END).rstrip()
        if save_signatures(signature_map):
            signature_dropdown['values'] = list(signature_map.keys())
            update_status(f"✅ Saved signature for {name}", "success")
            log_message(f"💾 Saved signature: {name}")
        else:
            update_status("❌ Could not save signatures", "error")

    def add_signature():
        new_index = len(signature_map) + 1
        new_name = f"New Person {new_index}"
        signature_map[new_name] = "<p><strong>{Name}</strong><br>Title</p>"
        listbox.insert(tk.END, new_name)
        save_signatures(signature_map)
        signature_dropdown['values'] = list(signature_map.keys())
        update_status(f"✅ Added signature slot: {new_name}", "success")
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(tk.END)
        on_select()

    def delete_signature():
        sel = listbox.curselection()
        if not sel:
            update_status("⚠️ Select a signature to delete", "warning")
            return
        idx = sel[0]
        name = listbox.get(idx)
        if name in signature_map:
            del signature_map[name]
            listbox.delete(idx)
            save_signatures(signature_map)
            signature_dropdown['values'] = list(signature_map.keys())
            update_status(f"✅ Deleted signature {name}", "info")
            log_message(f"🗑️ Deleted signature: {name}")
            if listbox.size() > 0:
                listbox.selection_set(0)
                on_select()
            else:
                text_area.delete("1.0", tk.END)

    btn_frame = tk.Frame(right, bg=CARD_BG)
    btn_frame.pack(fill="x", pady=(6, 0))
    tk.Button(btn_frame, text="Save", command=save_current, bg=SUCCESS_COLOR, fg='white', relief='flat',
              font=FONT_SUBHEADING, cursor='hand2').pack(side="left", padx=6)
    tk.Button(btn_frame, text="Add", command=add_signature, bg=PRIMARY_COLOR, fg='white', relief='flat',
              font=FONT_SUBHEADING, cursor='hand2').pack(side="left", padx=6)
    tk.Button(btn_frame, text="Delete", command=delete_signature, bg=ERROR_COLOR, fg='white', relief='flat',
              font=FONT_SUBHEADING, cursor='hand2').pack(side="left", padx=6)

    listbox.bind("<<ListboxSelect>>", lambda e: on_select(e))
    if listbox.size() > 0:
        listbox.selection_set(0);
        on_select()


# Edit Signatures Button
edit_sig_button = tk.Button(config_card, text="✏️ Edit", command=open_signature_editor,
                            bg='#f8fafc', fg=TEXT_PRIMARY, relief='solid', bd=1, font=(FONT_FAMILY, 8),
                            cursor='hand2', pady=4)
edit_sig_button.grid(row=9, column=0, sticky='ew', padx=25, pady=(0, 8))


# Reload Signatures Button
def reload_signatures_command():
    force_reload_signatures()
    update_status("🔄 Signatures reloaded from JSON file", "success")
    log_message("🔄 Force reloaded signatures from JSON")


reload_sig_button = tk.Button(config_card, text="🔄 Reload", command=reload_signatures_command,
                              bg='#e5f3ff', fg=TEXT_PRIMARY, relief='solid', bd=1, font=(FONT_FAMILY, 8),
                              cursor='hand2', pady=4)
reload_sig_button.grid(row=10, column=0, sticky='ew', padx=25, pady=(0, 15))

action_card = ModernCard(left_panel)
action_card.grid(row=1, column=0, sticky='ew')
action_card.grid_columnconfigure(0, weight=1)

action_header = tk.Frame(action_card, bg=CARD_BG)
action_header.grid(row=0, column=0, sticky='ew', padx=20, pady=(15, 10))
tk.Label(action_header, text="🚀", font=(FONT_FAMILY, 16), bg=CARD_BG).pack(side='left')
tk.Label(action_header, text="Quick Actions", font=(FONT_FAMILY, 14, "bold"), fg=TEXT_PRIMARY, bg=CARD_BG).pack(
    side='left', padx=(8, 0))

buttons_frame = tk.Frame(action_card, bg=CARD_BG)
buttons_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 15))
buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=1)

# Smaller, more compact buttons
upload_button = tk.Button(buttons_frame, text="📁 Upload CSV", bg=PRIMARY_COLOR, fg='white',
                          relief='flat', bd=0, cursor='hand2', font=(FONT_FAMILY, 10, "bold"),
                          padx=8, pady=8, command=upload_csv)
upload_button.grid(row=0, column=0, sticky='ew', padx=(0, 3))

send_button = tk.Button(buttons_frame, text="📤 Send Emails", bg=SUCCESS_COLOR, fg='white',
                        relief='flat', bd=0, cursor='hand2', font=(FONT_FAMILY, 10, "bold"),
                        padx=8, pady=8, command=start_sending_emails)
send_button.grid(row=0, column=1, sticky='ew', padx=(3, 0))

right_panel = tk.Frame(content_container, bg=BG_GRADIENT_START)
right_panel.grid(row=0, column=1, sticky='nsew')
right_panel.grid_rowconfigure(1, weight=1)
right_panel.grid_columnconfigure(0, weight=1)

status_card = ModernCard(right_panel)
status_card.grid(row=0, column=0, sticky='ew', pady=(0, 15))

status_header = tk.Frame(status_card, bg=CARD_BG)
status_header.pack(fill="x", padx=25, pady=(20, 15))
status_icon = tk.Label(status_header, text="ℹ", font=(FONT_FAMILY, 20), fg=INFO_COLOR, bg=CARD_BG)
status_icon.pack(side='left')
tk.Label(status_header, text="Current Status", font=FONT_HEADING, fg=TEXT_PRIMARY, bg=CARD_BG).pack(side='left',
                                                                                                    padx=(10, 0))

status_label = tk.Label(status_card, text="🎯 Ready to begin. Upload your CSV file to start.", font=FONT_BODY,
                        fg=TEXT_SECONDARY, bg=CARD_BG, anchor="w", wraplength=500)
status_label.pack(fill="x", padx=25, pady=(0, 10))

progress_bar = ttk.Progressbar(status_card, mode='determinate', length=300)
progress_bar.pack(fill="x", padx=25, pady=(0, 20))

log_card = ModernCard(right_panel)
log_card.grid(row=1, column=0, sticky='nsew')
log_card.grid_rowconfigure(1, weight=1)
log_card.columnconfigure(0, weight=1)

log_header = tk.Frame(log_card, bg=CARD_BG)
log_header.pack(fill="x", padx=25, pady=(20, 15))
tk.Label(log_header, text="📊", font=(FONT_FAMILY, 20), bg=CARD_BG).pack(side='left')
tk.Label(log_header, text="Activity Monitor", font=FONT_HEADING, fg=TEXT_PRIMARY, bg=CARD_BG).pack(side='left',
                                                                                                   padx=(10, 0))

log_frame = tk.Frame(log_card, bg="#0f172a", highlightthickness=2, highlightbackground="#334155")
log_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=FONT_MONO, bg="#0f172a", fg="#94a3b8", relief='flat',
                                     bd=0, insertbackground="#94a3b8")
log_text.pack(fill="both", expand=True, padx=2, pady=2)
log_text.tag_config("log", foreground="#10b981")

log_message("🚀 System initialized successfully")
log_message("💡 Ready for operations")

footer_frame = tk.Frame(main_frame, bg="#0f172a", height=50)
footer_frame.grid(row=3, column=0, sticky='ew')
footer_frame.pack_propagate(False)

footer_text = tk.Text(footer_frame, height=1, bg="#0f172a", relief='flat', bd=0, font=FONT_FOOTER, highlightthickness=0)
footer_text.pack(expand=True, fill='both', pady=15)
footer_text.tag_configure("gray", foreground="#64748b", justify='center')
footer_text.tag_configure("red", foreground="#dc2626", justify='center')
footer_text.insert(tk.END, "Made with ", "gray")
footer_text.insert(tk.END, "♥", "red")
footer_text.insert(tk.END, " in IIT Madras", "gray")
footer_text.configure(state='disabled')

for child in main_frame.winfo_children():
    if isinstance(child, tk.Frame):
        child.configure(bg=BG_GRADIENT_START)

root.mainloop()