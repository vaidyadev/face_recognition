import re
import time
import os
import threading
import tkinter as tk
from tkinter import ttk, Label, Frame, Canvas, Button, Text, Scrollbar, messagebox
from tkinter import LEFT, RIGHT, BOTTOM, TOP, BOTH, X, Y, END, SOLID, FLAT, NONE, NE, NW, WORD, DISABLED, NORMAL, SEL_FIRST, SEL_LAST, HORIZONTAL, VERTICAL
from PIL import Image, ImageTk
import tempfile
import matplotlib.pyplot as plt
import matplotlib
from .audio import speak_text_gtts

# Ensure Agg backend
matplotlib.use("Agg")

def remove_explanation_lines(code):
    """Removes all explanation lines and keeps only the actual code."""
    patterns = [
        r'#.*(you can|save this|run this|extension|\.py|when you run|output will be).*',
        r'"""[\s\S]*?"""',
        r"'''[\s\S]*?'''",
        r'#.*(example|note:|tip:|warning:).*'
    ]
    
    for pattern in patterns:
        code = re.sub(pattern, '', code, flags=re.IGNORECASE)
    
    # Only remove completely empty lines, not just whitespace ones
    lines = [line for line in code.split('\n') if line.strip() or line == '']
    return '\n'.join(lines).strip()

def render_latex_equation(text_widget, latex_expr):
    try:
        # Create the figure and render math
        fig, ax = plt.subplots(figsize=(0.01, 0.01))
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.text(0.5, 0.5, f"${latex_expr}$", horizontalalignment='center',
                verticalalignment='center', fontsize=16)

        # Save to temp file and close plot
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"latex_{int(time.time() * 1000)}.png")
        plt.savefig(temp_path, dpi=150, bbox_inches='tight', pad_inches=0.2)
        plt.close(fig)

        # Load image in main thread (from file)
        img = Image.open(temp_path)
        img = ImageTk.PhotoImage(img)
        os.remove(temp_path)

        # Embed into tkinter text widget
        image_label = Label(text_widget, image=img, bg='white')
        image_label.image = img  # Keep reference
        text_widget.window_create(END, window=image_label)
        text_widget.insert(END, '\n')

    except Exception as e:
        print(f"LaTeX render error: {e}")

def copy_code_with_feedback(root, code, text_var):
    root.clipboard_clear()
    root.clipboard_append(code)

    original_text = text_var.get()
    text_var.set("✔ Copied")

    def reset():
        time.sleep(2)
        text_var.set(original_text)

    threading.Thread(target=reset, daemon=True).start()

def bind_mousewheel(widget, target_canvas):
    def on_enter(event):
        widget.bind_all("<MouseWheel>", lambda e: target_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        widget.bind_all("<Shift-MouseWheel>", lambda e: target_canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))

    def on_leave(event):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Shift-MouseWheel>")

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def insert_markdown_table(text_widget, table_text, root, language_code="en"):
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    if len(lines) < 2:
        return

    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    rows = []
    for line in lines[2:]:
        values = [v.strip() for v in line.split('|') if v.strip()]
        if len(values) == len(headers):
            rows.append(values)

    col_widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    col_pixel_widths = [min(max(w * 7, 150), 400) for w in col_widths]

    # === OUTER table frame ===
    outer_frame = Frame(text_widget, bg='white', bd=1, relief=SOLID)
    outer_frame.config(width=700, height=240)
    outer_frame.pack_propagate(False)

    # === Canvas for scrollable table ===
    canvas = Canvas(outer_frame, bg='white', highlightthickness=0)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    vsb = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    vsb.pack(side=RIGHT, fill=Y)

    hsb = ttk.Scrollbar(outer_frame, orient="horizontal", command=canvas.xview)
    hsb.pack(side=BOTTOM, fill=X)

    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # === Inner frame ===
    inner_frame = Frame(canvas, bg='white')
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # === Scroll region binding ===
    def configure_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        if inner_frame.winfo_reqwidth() != canvas.winfo_width():
            canvas.itemconfigure("all", width=inner_frame.winfo_reqwidth())

    inner_frame.bind("<Configure>", configure_scroll_region)

    bind_mousewheel(canvas, canvas)
    

    # === Headers ===
    for col_index, header in enumerate(headers):
        label = Label(inner_frame, text=header, bg="#4CAF50", fg="white",
                    font=("Arial", 10, "bold"), borderwidth=1, relief="solid",
                    padx=8, pady=4, wraplength=col_pixel_widths[col_index], justify=LEFT)
        label.grid(row=0, column=col_index, sticky="nsew")

    def read_selected_text_from_widget(widget):
        try:
            widget.focus_set()
            widget.config(state='normal')
            selected_text = widget.get(SEL_FIRST, SEL_LAST).strip()
            widget.config(state='disabled')
        except Exception:
            # messagebox.showinfo("Speak Selected", "No text selected!", parent=root)
            return

        if not selected_text:
            return

        speak_text_gtts(selected_text, language_code, root)

    def copy_selected_text_from_widget(widget):
        try:
            widget.focus_set()
            widget.config(state='normal')
            selected_text = widget.get(SEL_FIRST, SEL_LAST)
            widget.config(state='disabled')
            root.clipboard_clear()
            root.clipboard_append(selected_text)
        except Exception:
            pass # messagebox.showinfo("Copy", "No text selected!", parent=root)


    # === Cells (Chunked Rendering) ===
    def render_chunk(start_row_index):
        chunk_size = 5  # Process 5 rows at a time
        end_row_index = min(start_row_index + chunk_size, len(rows))
        
        for i in range(start_row_index, end_row_index):
            row_values = rows[i]
            # Row index in grid is i+1 because header is at 0
            grid_row = i + 1 
            
            for col_index, value in enumerate(row_values):
                cell_text_widget = Text(inner_frame, height=4, width=int(col_pixel_widths[col_index] / 7),
                                wrap=WORD, padx=6, pady=2, font=("Arial", 10),
                                bd=1, relief="solid", bg="white")
                
                cell_text_widget.tag_configure("bold", font=("Arial", 10, "bold"))
                
                parts = value.split('**')
                for j, part in enumerate(parts):
                    if j % 2 == 1:
                        cell_text_widget.insert(END, part, "bold")
                    else:
                        cell_text_widget.insert(END, part)
                
                cell_text_widget.config(state=DISABLED)
                cell_text_widget.grid(row=grid_row, column=col_index, sticky="nsew")

                # Bindings
                cell_text_widget.bind("<Control-s>", lambda e, w=cell_text_widget: (w.focus_set(), read_selected_text_from_widget(w)))
                cell_text_widget.bind("<Control-c>", lambda e, w=cell_text_widget: (w.focus_set(), copy_selected_text_from_widget(w)))
                
                # Context Menu
                def show_context_menu(event, w=cell_text_widget):
                    menu = tk.Menu(root, tearoff=0)
                    menu.add_command(label="📋 Copy", command=lambda: copy_selected_text_from_widget(w))
                    menu.add_command(label="🗣️ Speak", command=lambda: read_selected_text_from_widget(w))
                    try:
                        menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        menu.grab_release()
                
                cell_text_widget.bind("<Button-3>", show_context_menu)
        
        # Schedule next chunk if there are more rows
        if end_row_index < len(rows):
            root.after(10, lambda: render_chunk(end_row_index))
        else:
            # Final cleanup or configuration after all rows are rendered
            # Ensure column weights are set (can be done earlier, but safe here too)
            for col in range(len(headers)):
                inner_frame.grid_columnconfigure(col, weight=1)

    # Start rendering chunks
    render_chunk(0)

    # === Copy Button (outside canvas) ===
    copy_btn_text = tk.StringVar(value="📋 Copy")
    copy_btn = Button(outer_frame, textvariable=copy_btn_text,
                    font=("Arial", 6), bg="#e0e0e0", activebackground="#d0d0d0",
                    relief=FLAT, cursor="hand2",
                    command=lambda: copy_code_with_feedback(root, table_text, copy_btn_text))
    copy_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=3)

    text_widget.window_create(END, window=outer_frame)
    text_widget.insert(END, "\n\n")

def insert_comparison_table(text_widget, title, rows):
    """Insert a comparison table from text-based format"""
    table_frame = Frame(text_widget, bg='white', bd=1, relief=SOLID)
    table_frame.pack_propagate(False)
    
    # Add title label
    title_label = Label(table_frame,
                    text=title,
                    font=("Arial", 11, "bold"),
                    bg="#4CAF50",
                    fg="white",
                    padx=10,
                    pady=5)
    title_label.pack(fill=X)
    
    # Create the Treeview
    tree = ttk.Treeview(table_frame, columns=["Aspect", "Details"], show="headings")
    tree.heading("Aspect", text="Aspect")
    tree.heading("Details", text="Details")
    tree.column("Aspect", width=150, anchor='w')
    tree.column("Details", width=500, anchor='w')
    
    # Add rows
    for aspect, details in rows:
        tree.insert('', 'end', values=(aspect, details))
    
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    text_widget.window_create(END, window=table_frame)
        
def insert_table(text_widget, title, content):
    """Insert a formatted table into the chat window"""
    # Parse the table content
    rows = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Determine if it's a markdown-style table
    is_markdown_table = len(rows) > 1 and '|' in rows[0] and '|' in rows[1] and '---' in rows[1]
    
    if is_markdown_table:
        # Process markdown table
        headers = [h.strip() for h in rows[0].split('|') if h.strip()]
        rows = rows[2:]  # Skip header and separator lines
        
        # Create a frame for the table
        table_frame = Frame(text_widget, bg='white', bd=1, relief=SOLID)
        table_frame.pack_propagate(False)
        
        # Add title label
        title_label = Label(table_frame, 
                        text=title,
                        font=("Arial", 11, "bold"),
                        bg="#4CAF50",
                        fg="white",
                        padx=10,
                        pady=5)
        title_label.pack(fill=X)
        
        # Create the table
        tree = ttk.Treeview(table_frame, columns=headers, show="headings")
        
        # Add headers
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=150, anchor='w')
        
        # Add rows
        for row in rows:
            if '|' in row:
                values = [v.strip() for v in row.split('|') if v.strip()]
                if len(values) == len(headers):
                    tree.insert('', 'end', values=values)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack everything
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        
        # Insert into the text widget
        text_widget.window_create(END, window=table_frame)
        text_widget.insert(END, '\n\n')
    else:
        # Process simple text-based table (one item per line)
        table_frame = Frame(text_widget, bg='white', bd=1, relief=SOLID)
        table_frame.pack_propagate(False)
        
        # Add title label
        title_label = Label(table_frame, 
                        text=title,
                        font=("Arial", 11, "bold"),
                        bg="#4CAF50",
                        fg="white",
                        padx=10,
                        pady=5)
        title_label.pack(fill=X)
        
        # Create a text widget for the table
        table_text = Text(table_frame,
                        wrap=NONE,
                        font=("Arial", 10),
                        padx=5,
                        pady=5,
                        bd=0,
                        highlightthickness=0)
        
        # Add content
        for row in rows:
            # Highlight key-value pairs if they exist
            if ':' in row:
                parts = row.split(':', 1)
                table_text.insert(END, parts[0].strip() + ":\t", "bold")
                table_text.insert(END, parts[1].strip() + "\n")
            else:
                table_text.insert(END, "• " + row + "\n")
        
        table_text.tag_configure("bold", font=("Arial", 10, "bold"))
        table_text.config(state=DISABLED)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table_text.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=table_text.xview)
        table_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack everything
        table_text.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        
        # Insert into the text widget
        text_widget.window_create(END, window=table_frame)
        text_widget.insert(END, '\n\n')
