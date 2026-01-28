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

def render_latex_equation(text_widget, latex_expr, is_dark=False):
    try:
        # Create the figure and render math
        fig, ax = plt.subplots(figsize=(0.01, 0.01))
        fig.patch.set_visible(False)
        ax.axis('off')
        
        # Render roughly Black text initially
        ax.text(0.5, 0.5, f"${latex_expr}$", horizontalalignment='center',
                verticalalignment='center', fontsize=16, color='black')

        # Save to temp file and close plot
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"latex_{int(time.time() * 1000)}.png")
        plt.savefig(temp_path, dpi=150, bbox_inches='tight', pad_inches=0.2, transparent=True)
        plt.close(fig)

        # Load image in main thread (from file)
        img_light = Image.open(temp_path).convert("RGBA")
        os.remove(temp_path)
        
        # Create Dark Version (Invert colors efficiently)
        # We want White text where it was Black, keeping Alpha.
        # Since source is Black text on Transparent, we can just create a White image and use source Alpha.
        r, g, b, alpha = img_light.split()
        img_dark = Image.merge("RGBA", (
            Image.new("L", img_light.size, 255), # R=255 (White)
            Image.new("L", img_light.size, 255), # G=255
            Image.new("L", img_light.size, 255), # B=255
            alpha # Original Alpha
        ))
        
        # Convert to PhotoImage
        tk_img_light = ImageTk.PhotoImage(img_light)
        tk_img_dark = ImageTk.PhotoImage(img_dark)

        # Initial State
        current_img = tk_img_dark if is_dark else tk_img_light
        current_bg = text_widget.cget("bg") # Match parent text widget

        # Embed into tkinter text widget
        # Note: bg='white' hardcoded previously might show box. Using parent bg is better.
        image_label = Label(text_widget, image=current_img, bg=current_bg)
        
        # Store references to BOTH images to prevent GC
        image_label.img_light_ref = tk_img_light
        image_label.img_dark_ref = tk_img_dark
        
        # === OPTIMIZED THEME UPDATE CALLBACK ===
        def manual_theme_update(is_dark_mode):
            target_img = image_label.img_dark_ref if is_dark_mode else image_label.img_light_ref
            # Need to match the text widget background which might have changed
            # We can assume standard theme colors or query parent? 
            # Querying parent during update might render Old color if parent hasn't updated yet.
            # Safer to use the standard theme colors we know.
            # Dynamic Background Matching:
            try:
                target_bg = text_widget.cget('bg')
            except:
                target_bg = '#1e1e1e' if is_dark_mode else 'white'

            image_label.config(image=target_img, bg=target_bg)
            
        image_label.update_manual_theme = manual_theme_update
        
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

def insert_markdown_table(text_widget, table_text, root, language_code="en", is_dark=False):
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
    
    # Theme Colors
    bg_color = "#1e1e1e" if is_dark else "white"
    fg_color = "#e0e0e0" if is_dark else "black"
    scroll_bg = "#2e2e2e" if is_dark else "white"

    # === OUTER table frame ===
    outer_frame = Frame(text_widget, bg=bg_color, bd=1, relief=SOLID)
    outer_frame.config(width=700, height=240)
    outer_frame.pack_propagate(False)

    # === Canvas for scrollable table ===
    canvas = Canvas(outer_frame, bg=scroll_bg, highlightthickness=0)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    vsb = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    vsb.pack(side=RIGHT, fill=Y)

    hsb = ttk.Scrollbar(outer_frame, orient="horizontal", command=canvas.xview)
    hsb.pack(side=BOTTOM, fill=X)

    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # === Inner frame ===
    inner_frame = Frame(canvas, bg=bg_color)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # === Scroll region binding ===
    def configure_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        if inner_frame.winfo_reqwidth() != canvas.winfo_width():
            canvas.itemconfigure("all", width=inner_frame.winfo_reqwidth())

    inner_frame.bind("<Configure>", configure_scroll_region)

    bind_mousewheel(canvas, canvas)
    
    # Store reference to all created cell widgets for performing bulk updates properly
    all_table_cells = [] 
    
    # === OPTIMIZED THEME UPDATE CALLBACK ===
    def manual_theme_update(is_dark_mode):
        bg_c = "#1e1e1e" if is_dark_mode else "white"
        fg_c = "#e0e0e0" if is_dark_mode else "black"
        scroll_c = "#2e2e2e" if is_dark_mode else "white"
        
        outer_frame.config(bg=bg_c)
        canvas.config(bg=scroll_c)
        inner_frame.config(bg=bg_c)
        
        # Copy Button needs update too (created later, but scope is shared)
        # We can update it if it exists
        if 'copy_btn' in locals():
             copy_btn_bg = "#3d3d3d" if is_dark_mode else "#e0e0e0"
             copy_btn_fg = "white" if is_dark_mode else "black"
             copy_btn_active = "#4d4d4d" if is_dark_mode else "#d0d0d0"
             copy_btn.config(bg=copy_btn_bg, fg=copy_btn_fg, activebackground=copy_btn_active)

        for cell in all_table_cells:
            cell.config(bg=bg_c, fg=fg_c)
            
    outer_frame.update_manual_theme = manual_theme_update

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
                                bd=1, relief="solid", bg=bg_color, fg=fg_color)
                
                cell_text_widget.tag_configure("bold", font=("Arial", 10, "bold"))
                
                parts = value.split('**')
                for j, part in enumerate(parts):
                    if j % 2 == 1:
                        cell_text_widget.insert(END, part, "bold")
                    else:
                        cell_text_widget.insert(END, part)
                
                cell_text_widget.config(state=DISABLED)
                cell_text_widget.grid(row=grid_row, column=col_index, sticky="nsew")
                
                # Track for optimized update
                all_table_cells.append(cell_text_widget)

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
    
    # Theme-aware colors for initial creation
    c_bg = "#3d3d3d" if is_dark else "#e0e0e0"
    c_fg = "white" if is_dark else "black"
    c_active = "#4d4d4d" if is_dark else "#d0d0d0"
    
    copy_btn = Button(outer_frame, textvariable=copy_btn_text,
                    font=("Arial", 6), bg=c_bg, fg=c_fg, activebackground=c_active, activeforeground=c_fg,
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
