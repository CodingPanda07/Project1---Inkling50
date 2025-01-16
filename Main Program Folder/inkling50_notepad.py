# import all the libraries that I need, including system, os, bootstrap (to make things look better), and tkinter (important for basic functionalities)
import sys
import os
import ttkbootstrap
import platform
import flet as ft
import tkinter as tk
import tkinter.font as tkFont
import ctypes
import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tkinter import *
from ttkbootstrap import Window, Style
from ttkbootstrap.constants import *
from tkinter.messagebox import showinfo, showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename
# import timer since this will be important later on to integrate timer with the document function itself
from threading import Timer # For calling the timer function
# import fpdf so user can save file as a pdf, though this will be done automatically later on
from fpdf import FPDF  # For saving files as PDF

if sys.platform == "darwin":
    from tkinter import _tkinter
    _tkinter.TkVersion = 8.6
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class Notepad:
    def __init__(self):
        # Initialize the root window with ttkbootstrap
        self.__root = Window(themename="classic") # start with window, style it journal
        self.__root.title("Notepad") # title the window notepad
        self.__root.geometry("800x600")  # Default size

        # Set up text area with default font
        self.__thisTextArea = Text(self.__root, wrap=WORD, undo=True, font=("Calibri", 12))
        self.__file = None 

        # Create menu bar and status bar
        self.__thisMenuBar = Menu(self.__root) # Create new root to menu function from tkinter library
        self.__createMenuBar() # Create new function later on 
        self.__createStatusBar()

        # Toolbar setup
        self.__createToolbar()

        # Add scrollbars
        self.__thisScrollBar = Scrollbar(self.__root, command=self.__thisTextArea.yview)
        self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)
        self.__thisScrollBar.grid(row=1, column=2, sticky=NS)
        self.__thisTextArea.grid(row=1, column=1, sticky=NSEW)

        # Configure resizing weights
        self.__root.grid_rowconfigure(1, weight=1)
        self.__root.grid_columnconfigure(1, weight=1)

        # Idle timer setup
        self.idle_time_limit = 2000000  # milliseconds
        self.idle_timer = None

        # Bind events
        self.__bindEvents()

    def run(self):
        """Run the main application loop."""
        self.__root.mainloop()

    def __bindEvents(self):
        self.__root.bind("<Key>", self.__onKeyPress)
        self.__root.bind("<Configure>", self.__adjustSize)
        self.__root.bind("<Control-b>", lambda event: self.__makeBold())
        self.__root.bind("<Control-i>", lambda event: self.__makeItalic())
        self.__root.bind("<Control-u>", lambda event: self.__makeUnderline())
        self.__thisTextArea.bind("<KeyRelease>", self.__updateWordCount)

        # Disable copy-paste key bindings
        self.__thisTextArea.bind("<Control-c>", self.__disableAction)
        self.__thisTextArea.bind("<Control-v>", self.__disableAction)
        self.__thisTextArea.bind("<Command-c>", self.__disableAction)  # macOS Copy
        self.__thisTextArea.bind("<Command-v>", self.__disableAction)  # macOS Paste

    def __onKeyPress(self, event):
        self.__resetIdleTimer()

    def __resetIdleTimer(self):
        if self.idle_timer is not None:
            self.__root.after_cancel(self.idle_timer)
        self.idle_timer = self.__root.after(self.idle_time_limit, self.__deleteDocument)

    def __deleteDocument(self):

        # Add some comments or message here before it's deleted in Fletch

        self.__thisTextArea.delete(1.0, "end")
        self.__disableTyping()

    def __disableTyping(self):
        self.__thisTextArea.config(state="disabled")

    def __createMenuBar(self):
        file_menu = Menu(self.__thisMenuBar, tearoff=0)
        file_menu.add_command(label="New", command=self.__newFile)
        file_menu.add_command(label="Open", command=self.__openFile)
        file_menu.add_command(label="Save", command=self.__saveFile)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.__quitApplication)
        self.__thisMenuBar.add_cascade(label="File", menu=file_menu)

        format_menu = Menu(self.__thisMenuBar, tearoff=0)
        format_menu.add_command(label="Bold", command=self.__makeBold)
        format_menu.add_command(label="Italic", command=self.__makeItalic)
        format_menu.add_command(label="Underline", command=self.__makeUnderline)
        format_menu.add_command(label="Bold + Underline", command=self.__makeBoldUnderline)
        format_menu.add_command(label="Italic + Underline", command=self.__makeItalicUnderline)
        format_menu.add_command(label="Bold + Italic", command=self.__makeBoldItalic)
        format_menu.add_command(label="Bold + Italic + Underline", command=self.__makeBoldItalicUnderline)
        self.__thisMenuBar.add_cascade(label="Format", menu=format_menu)

        help_menu = Menu(self.__thisMenuBar, tearoff=0)
        help_menu.add_command(label="About Notepad", command=self.__showAbout)
        self.__thisMenuBar.add_cascade(label="Help", menu=help_menu)

        self.__root.config(menu=self.__thisMenuBar)

    def __createToolbar(self):
        # Create a toolbar frame
        toolbar = Frame(self.__root, height=30, bg="lightgray")
        toolbar.grid(row=0, column=0, columnspan=3, sticky=W + E)

        # Buttons for text formatting
        bold_btn = Button(toolbar, text="B", command=self.__makeBold, font=("Calibri", 12, "bold"), width=3)
        bold_btn.grid(row=0, column=0, padx=5, pady=5)

        italic_btn = Button(toolbar, text="I", command=self.__makeItalic, font=("Calibri", 12, "italic"), width=3)
        italic_btn.grid(row=0, column=1, padx=5, pady=5)

        underline_btn = Button(toolbar, text="U", command=self.__makeUnderline, font=("Calibri", 12, "underline"), width=3)
        underline_btn.grid(row=0, column=2, padx=5, pady=5)

        # Buttons for advanced text formatting

        bold_underline_btn = Button(toolbar, text="B+U", command=self.__makeBoldUnderline, font=("Calibri", 12, "bold", "underline"), width=4)
        bold_underline_btn.grid(row=0, column=3, padx=5, pady=5)

        italic_underline_btn = Button(toolbar, text="I+U", command=self.__makeItalicUnderline, font=("Calibri", 12, "italic", "underline"), width=4)
        italic_underline_btn.grid(row=0, column=4, padx=5, pady=5)

        bold_italic_btn = Button(toolbar, text="B+I", command=self.__makeBoldItalic, font=("Calibri", 12, "bold", "italic"), width=4)
        bold_italic_btn.grid(row=0, column=5, padx=5, pady=5)

        bold_italic_underline_btn = Button(toolbar, text="B+I+U", command=self.__makeBoldItalicUnderline, font=("Calibri", 12, "bold", "italic", "underline"), width=5)
        bold_italic_underline_btn.grid(row=0, column=6, padx=5, pady=5)

        # Buttons for center text, highlight, and text color

        centerTextButton = Button(toolbar, text="Center Text", command=self.__centerText)
        centerTextButton.grid(row=0, column=7, padx=5, pady=5)

        highlightBlackButton = Button(toolbar, text="Highlight Black", command=lambda: self.__highlightText("black"))
        highlightBlackButton.grid(row=0, column=8, padx=5, pady=5)

        highlightBlueButton = Button(toolbar, text="Highlight Blue", command=lambda: self.__highlightText("blue"))
        highlightBlueButton.grid(row=0, column=9, padx=5, pady=5)

        highlightRedButton = Button(toolbar, text="Highlight Red", command=lambda: self.__highlightText("red"))
        highlightRedButton.grid(row=0, column=10, padx=5, pady=5)

        highlightGreenButton = Button(toolbar, text="Highlight Green", command=lambda: self.__highlightText("green"))
        highlightGreenButton.grid(row=0, column=11, padx=5, pady=5)

        textColorBlackButton = Button(toolbar, text="Text Black", command=lambda: self.__changeTextColor("black"))
        textColorBlackButton.grid(row=0, column=12, padx=5, pady=5)

        textColorBlueButton = Button(toolbar, text="Text Blue", command=lambda: self.__changeTextColor("blue"))
        textColorBlueButton.grid(row=0, column=13, padx=5, pady=5)

        textColorRedButton = Button(toolbar, text="Text Red", command=lambda: self.__changeTextColor("red"))
        textColorRedButton.grid(row=0, column=14, padx=5, pady=5)

        textColorGreenButton = Button(toolbar, text="Text Green", command=lambda: self.__changeTextColor("green"))
        textColorGreenButton.grid(row=0, column=15, padx=5, pady=5)


    def __createStatusBar(self):
        self.__statusBar = Label(self.__root, text="Words: 0", anchor=E, bg="white", relief=SUNKEN)
        self.__statusBar.grid(row=3, column=0, columnspan=3, sticky=W + E)

    def __updateWordCount(self, event=None):
        text = self.__thisTextArea.get(1.0, END)
        words = len(text.split())
        self.__statusBar.config(text=f"Words: {words}")

    def __disableAction(self, event=None):
        showinfo("Action Blocked", "Copy and Paste are disabled.")
        return "break"

    def __adjustSize(self, event=None):
        pass  # Adjust layout as needed here

    def __quitApplication(self):
        if self.timer:
            self.timer.cancel()  # Cancel the idle timer thread
        self.__root.destroy()

    def __showAbout(self):
        showinfo("About Notepad", "Enhanced Notepad with advanced features.")

    def __newFile(self):
        self.__thisTextArea.delete(1.0, END)

    def __openFile(self):
        try:
            file = askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file:
                with open(file, "r") as f:
                    self.__thisTextArea.delete(1.0, END)
                    self.__thisTextArea.insert(1.0, f.read())
        except Exception as e:
            showerror("Error", f"Failed to open file: {e}")

    def __saveFile(self):
        try:
            file = asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if file:
                self.__saveAsPDF(file)
        except Exception as e:
            showerror("Error", f"Failed to save file: {e}")

    def __saveAsPDF(self, file):

        # Set up the document
        pdf = SimpleDocTemplate(file, pagesize=letter)
        base_style = ParagraphStyle(
            name="Base",
            fontName="Helvetica",
            fontSize=12,
        )

        # Extract and style content
        styled_texts = self.__getStyledTextSegments()

        # Combine all text with inline styles
        combined_paragraph = self.__buildStyledParagraph(styled_texts)

        # Create the flowable content
        flowables = [Paragraph(combined_paragraph, base_style)]

        # Build the PDF
        pdf.build(flowables)


    def __getStyledTextSegments(self):
        """
        Processes text and tags into styled segments.
        Returns a list of tuples: (text_segment, style_dict).
        """
        start_index = "1.0"
        end_index = self.__thisTextArea.index("end-1c")
        text = self.__thisTextArea.get(start_index, end_index)
        tags = self.__getTagsInRange(start_index, end_index)

        segments = []
        current_pos = 0

        # Sort and iterate over tag ranges
        tag_ranges = []
        for tag, (start, end) in tags.items():
            start_idx = self.__textIndexToInt(start)
            end_idx = self.__textIndexToInt(end)
            tag_ranges.append((start_idx, end_idx, tag))

        tag_ranges.sort(key=lambda x: x[0])

        active_tags = set()
        for start_idx, end_idx, tag in tag_ranges:
            # Add plain text before a styled range
            if current_pos < start_idx:
                segments.append((text[current_pos:start_idx], self.__styleDictFromTags(active_tags)))

            # Add the new tag and styled text
            active_tags.add(tag)
            segments.append((text[start_idx:end_idx], self.__styleDictFromTags(active_tags)))

            # Move current position forward
            current_pos = end_idx

            # Remove tag after processing
            active_tags.remove(tag)

        # Add remaining plain text
        if current_pos < len(text):
            segments.append((text[current_pos:], self.__styleDictFromTags(active_tags)))

        return segments


    def __buildStyledParagraph(self, segments):
        """
        Combines styled segments into a single HTML-compatible paragraph string.
        """
        paragraph = ""
        for text, style_dict in segments:
            style_span = self.__getStyleSpan(style_dict)
            paragraph += f"<span {style_span}>{text}</span>"
        return paragraph


    def __getStyleSpan(self, style_dict):
        """
        Converts a style dictionary into an inline CSS-like span.
        """
        styles = []
        if style_dict.get("bold"):
            styles.append("font-weight: bold;")
        if style_dict.get("italic"):
            styles.append("font-style: italic;")
        if style_dict.get("underline"):
            styles.append("text-decoration: underline;")
        if "color" in style_dict:
            styles.append(f"color: {style_dict['color']};")
        if "background" in style_dict:
            styles.append(f"background-color: {style_dict['background']};")
        return f'style="{" ".join(styles)}"'


    def __styleDictFromTags(self, tags):
        """
        Converts active tags into a style dictionary.
        """
        style = {}
        for tag in tags:
            if "bold" in tag:
                style["bold"] = True
            if "italic" in tag:
                style["italic"] = True
            if "underline" in tag:
                style["underline"] = True
            if "text_color_" in tag:
                color = tag.replace("text_color_", "")
                style["color"] = self.__getColorHex(color)
            if "highlight_" in tag:
                highlight = tag.replace("highlight_", "")
                style["background"] = self.__getColorHex(highlight)
        return style


    def __textIndexToInt(self, index):
        """
        Converts a Tkinter text index (line.column) into an integer for sorting.
        """
        line, col = map(int, index.split('.'))
        return (line - 1) * 1000 + col


    def __getColorHex(self, color_name):
        """
        Maps color names to hex codes.
        """
        color_map = {
            "black": "#000000",
            "red": "#FF0000",
            "blue": "#0000FF",
            "green": "#00FF00",
            "yellow": "#FFFF00",
        }
        return color_map.get(color_name, "#000000")


    def __getTagsInRange(self, start_index, end_index):
        """
        Retrieve all tags and their ranges within the specified range.
        """
        tags = {}
        for tag in self.__thisTextArea.tag_names():
            tag_ranges = self.__thisTextArea.tag_ranges(tag)
            for i in range(0, len(tag_ranges), 2):
                tag_start = self.__thisTextArea.index(tag_ranges[i])
                tag_end = self.__thisTextArea.index(tag_ranges[i + 1])
                if self.__thisTextArea.compare(tag_start, "<=", end_index) and self.__thisTextArea.compare(tag_end, ">", start_index):
                    tags[tag] = (max(tag_start, start_index), min(tag_end, end_index))
        return tags


    def __makeBold(self):
        self.__applyTag("bold", {"font": ("Calibri", 12, "bold")})

    def __makeItalic(self):
        self.__applyTag("italic", {"font": ("Calibri", 12, "italic")})

    def __makeUnderline(self):
        self.__applyTag("underline", {"font": ("Calibri", 12, "underline")})
    
    def __makeBoldUnderline(self):
        self.__applyTag("bold_underline", {"font": ("Calibri", 12, "bold", "underline")})

    def __makeItalicUnderline(self):
        self.__applyTag("italic_underline", {"font": ("Calibri", 12, "italic", "underline")})

    def __makeBoldItalic(self):
        self.__applyTag("bold_italic", {"font": ("Calibri", 12, "bold", "italic")})

    def __makeBoldItalicUnderline(self):
        self.__applyTag("bold_italic_underline", {"font": ("Calibri", 12, "bold", "italic", "underline")})

    def __applyTag(self, tag, config):
        # Configure the tag properties
        self.__thisTextArea.tag_config(tag, **config)
        try:
            # Ensure some text is selected
            if not self.__thisTextArea.tag_ranges("sel"):
                raise ValueError("No text selected to apply the tag.")

            # Check if the tag is already applied and toggle it
            current_tags = self.__thisTextArea.tag_names("sel.first")
            if tag in current_tags:
                # Remove the tag if it's already applied
                self.__thisTextArea.tag_remove(tag, "sel.first", "sel.last")
            else:
                # Add the tag if it's not applied
                self.__thisTextArea.tag_add(tag, "sel.first", "sel.last")
        except ValueError as e:
            print(e)  # Optionally, notify the user of the error
        except Exception as e:
            print(f"Error applying tag {tag}: {e}")


    def __centerText(self):
    # Apply a tag to center-align text
        self.__thisTextArea.tag_configure("center", justify='center')
        self.__thisTextArea.tag_add("center", "sel.first", "sel.last")

    def __highlightText(self, color):
        try:
            # Ensure text is selected
            if not self.__thisTextArea.tag_ranges("sel"):
                raise ValueError("No text selected for highlighting.")
            
            # Add the highlight tag
            self.__thisTextArea.tag_add(f"highlight_{color}", "sel.first", "sel.last")
            self.__thisTextArea.tag_configure(f"highlight_{color}", background=color)
        except ValueError as e:
            print(e)  # Optionally show this message to the user

    def __changeTextColor(self, color):
        try:
            # Ensure text is selected
            if not self.__thisTextArea.tag_ranges("sel"):
                raise ValueError("No text selected for color change.")
            
            # Add the text color tag
            self.__thisTextArea.tag_add(f"text_color_{color}", "sel.first", "sel.last")
            self.__thisTextArea.tag_configure(f"text_color_{color}", foreground=color)
        except ValueError as e:
            print(e)  # Optionally show this message to the user


    def __textIndexToInt(self, index):
        """Converts text indices (line.column) into a single integer for sorting."""
        line, col = map(int, index.split('.'))
        return (line - 1) * 1000 + col


    def __getColorHex(self, color_name):
        """Maps color names to hex codes."""
        color_map = {
            "black": "#000000",
            "red": "#FF0000",
            "blue": "#0000FF",
            "green": "#00FF00",
        }
        return color_map.get(color_name, "#000000")


    def __getTagsInRange(self, start_index, end_index):
        """Retrieve all tags and their ranges within the specified range."""
        tags = {}
        for tag in self.__thisTextArea.tag_names():
            tag_ranges = self.__thisTextArea.tag_ranges(tag)
            for i in range(0, len(tag_ranges), 2):
                tag_start = self.__thisTextArea.index(tag_ranges[i])
                tag_end = self.__thisTextArea.index(tag_ranges[i + 1])
                if self.__thisTextArea.compare(tag_start, "<=", end_index) and self.__thisTextArea.compare(tag_end, ">", start_index):
                    tags[tag] = (max(tag_start, start_index), min(tag_end, end_index))
        return tags

    def __makeBold(self):
        self.__applyTag("bold", {"font": ("Calibri", 12, "bold")})

    def __makeItalic(self):
        self.__applyTag("italic", {"font": ("Calibri", 12, "italic")})

    def __makeUnderline(self):
        self.__applyTag("underline", {"font": ("Calibri", 12, "underline")})
    
    def __makeBoldUnderline(self):
        self.__applyTag("bold_underline", {"font": ("Calibri", 12, "bold", "underline")})

    def __makeItalicUnderline(self):
        self.__applyTag("italic_underline", {"font": ("Calibri", 12, "italic", "underline")})

    def __makeBoldItalic(self):
        self.__applyTag("bold_italic", {"font": ("Calibri", 12, "bold", "italic")})

    def __makeBoldItalicUnderline(self):
        self.__applyTag("bold_italic_underline", {"font": ("Calibri", 12, "bold", "italic", "underline")})

    def __applyTag(self, tag, config):
        # Configure the tag properties
        self.__thisTextArea.tag_config(tag, **config)
        try:
            # Ensure some text is selected
            if not self.__thisTextArea.tag_ranges("sel"):
                raise ValueError("No text selected to apply the tag.")

            # Check if the tag is already applied and toggle it
            current_tags = self.__thisTextArea.tag_names("sel.first")
            if tag in current_tags:
                # Remove the tag if it's already applied
                self.__thisTextArea.tag_remove(tag, "sel.first", "sel.last")
            else:
                # Add the tag if it's not applied
                self.__thisTextArea.tag_add(tag, "sel.first", "sel.last")
        except ValueError as e:
            print(e)  # Optionally, notify the user of the error
        except Exception as e:
            print(f"Error applying tag {tag}: {e}")


    def __centerText(self):
    # Apply a tag to center-align text
        self.__thisTextArea.tag_configure("center", justify='center')
        self.__thisTextArea.tag_add("center", "sel.first", "sel.last")

    def __highlightText(self, color):
        try:
            # Ensure text is selected
            if not self.__thisTextArea.tag_ranges("sel"):
                raise ValueError("No text selected for highlighting.")
            
            # Add the highlight tag
            self.__thisTextArea.tag_add(f"highlight_{color}", "sel.first", "sel.last")
            self.__thisTextArea.tag_configure(f"highlight_{color}", background=color)
        except ValueError as e:
            print(e)  # Optionally show this message to the user

    def __changeTextColor(self, color):
        try:
            # Ensure text is selected
            if not self.__thisTextArea.tag_ranges("sel"):
                raise ValueError("No text selected for color change.")
            
            # Add the text color tag
            self.__thisTextArea.tag_add(f"text_color_{color}", "sel.first", "sel.last")
            self.__thisTextArea.tag_configure(f"text_color_{color}", foreground=color)
        except ValueError as e:
            print(e)  # Optionally show this message to the user

# Run the application
if __name__ == "__main__":
    Notepad().run()
