# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 10:29:21 2023

@author: rocha
"""

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pytesseract
from pdf2image import convert_from_path
import pytesseract

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

class OCRSquareSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Square Selector")

        # Create a frame for the image view
        self.image_frame = tk.Frame(root)
        self.image_frame.pack(side="left", fill="both", expand=True)
        
        # Create a button frame for the first row of buttons
        button_frame1 = tk.Frame(self.image_frame)
        button_frame1.pack(side="top")
        
        # Create a second row of buttons for zooming and rotating
        button_frame2 = tk.Frame(self.image_frame)
        button_frame2.pack(side="top")
        
        # Dropdown list options
        psm_options = [
            "--psm 1 (AUTO_OSD)",
            "--psm 3 (AUTO)",
            "--psm 4 (SINGLE_COLUMN)",
            "--psm 6 (SINGLE_BLOCK)",
            "--psm 11 (SPARSE_TEXT)",
            "--psm 12 (SPARSE_TEXT_OSD)"
        ]

        # Function to update the selected option
        def update_selected_option(option):
            self.selected_psm_option.set(option.split('(')[0].strip())
            
        # Create a StringVar to store the selected option
        self.selected_psm_option = tk.StringVar()
        self.selected_psm_option.set(psm_options[3].split('(')[0].strip())  # Set the default option


        # Create a frame for the vertical scrollbar
        y_scroll_frame = tk.Frame(self.image_frame)
        y_scroll_frame.pack(side="right", fill="y")

        # Create a frame for the text view
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(side="left", fill="both", expand=True)

        # Create a main frame to hold all components
        self.main_frame = tk.Frame(self.image_frame)
        self.main_frame.pack(fill="both", expand=True)

        # Initialize variables
        self.image = None
        self.image_zoom = None
        self.start_x = None
        self.start_y = None
        
        self.press_x = None
        self.press_y = None
        
        self.zoom_level = 1.0
        self.coordinates = []
        self.current_image_index = 0
        self.rotate_flag = 0

        # Create a Canvas to display the image
        self.canvas = tk.Canvas(self.main_frame, width=1000, height=850)
        self.canvas.pack(side="top", fill="both", expand=True)

        # Create the horizontal scrollbar
        x_scrollbar = tk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=x_scrollbar.set)

        # Create the vertical scrollbar
        y_scrollbar = tk.Scrollbar(y_scroll_frame, orient="vertical", command=self.canvas.yview)
        y_scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=y_scrollbar.set)
        
        # Create a frame for the text widget
        text_view = tk.Frame(self.text_frame)
        text_view.pack(fill="both", expand=True)

        open_button = tk.Button(button_frame1, text="Open Image", command=self.open_image)
        clear_text_button = tk.Button(button_frame1, text="Clear Text", command=self.clear_text)
        clear_rectangles_button = tk.Button(button_frame1, text="Clear Area", command=self.clear_rectangles)
        ocr_button = tk.Button(button_frame1, text="Perform OCR", command=self.perform_ocr)
        
        # Buttons for image selection
        prev_image_button = tk.Button(button_frame1, text="<", command=self.show_previous_image)
        next_image_button = tk.Button(button_frame1, text=">", command=self.show_next_image)
        
        # Label to display current image number
        self.image_number_label = tk.Label(button_frame1, text="Image 1")

        open_button.grid(row=0, column=0, padx=5)
        clear_text_button.grid(row=0, column=1, padx=5)
        clear_rectangles_button.grid(row=0, column=2, padx=5)
        ocr_button.grid(row=0, column=3, padx=5)
        prev_image_button.grid(row=0, column=4, padx=5)
        self.image_number_label.grid(row=0, column=5, padx=5)
        next_image_button.grid(row=0, column=6, padx=5)
        
        zoom_in_button = tk.Button(button_frame2, text="Zoom In", command=self.zoom_in)
        zoom_out_button = tk.Button(button_frame2, text="Zoom Out", command=self.zoom_out) 
        self.angle_entry = tk.Entry(button_frame2, width=5)
        rotate_button = tk.Button(button_frame2, text="Rotate", command=self.rotate_image)
        # Create the dropdown list button
        psm_dropdown = tk.OptionMenu(button_frame2, self.selected_psm_option, *psm_options, command=update_selected_option)
        psm_dropdown.config(width=25)  # Adjust the width as needed
        
        zoom_in_button.grid(row=0, column=0, padx=5)
        zoom_out_button.grid(row=0, column=1, padx=5)
        self.angle_entry.grid(row=0, column=2, padx=5)
        rotate_button.grid(row=0, column=3, padx=5)
        psm_dropdown.grid(row=0, column=4, padx=5)

        # Create a text widget to display OCR results
        self.text_output = tk.Text(text_view, height=20, width=80)
        self.text_output.pack(fill="both", expand=True)

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        
        if file_path:
            self.coordinates = []
            self.clear_rectangles()
            
            if file_path.endswith(".pdf"):
                # Open and extract images from a PDF
                images = convert_from_path(file_path)
                
                if images:
                    self.images = images  # Store all images
                    self.current_image_index = 0  # Reset to the first image
                    self.show_image()  # Show the first image
                else:
                    self.image = None
            else:
                self.image = Image.open(file_path)
                self.images = None  # Reset images to None when opening a non-PDF image
                
                if self.image:
                    self.image_zoom = self.image
                    self.photo = ImageTk.PhotoImage(self.image)
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                    self.canvas.config(scrollregion=self.canvas.bbox("all"))

                    width, height = self.image.size
                    text = '##################################################################\n'
                    text += f'Image width, height = {width}, {height}\n'
                    text += '##################################################################\n'
                    self.text_output.insert(tk.END, text)
                    self.zoom_level = 1.0
                    self.image_number_label.config(text=f"Image {1}")

    def show_image(self):
        self.zoom_level = 1.0
        self.angle_entry.delete(0, tk.END)  # Clear the angle entry
        
        if self.images and 0 <= self.current_image_index < len(self.images):
            self.image = self.images[self.current_image_index]
            self.image_zoom = self.image
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.update_image_label()
            
            width, height = self.image.size
            text = '##################################################################\n'
            text += f'Image width, height = {width}, {height}\n'
            text += '##################################################################\n'
            self.text_output.insert(tk.END, text)

    def show_previous_image(self):
        if self.images:
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.images) - 1
            self.show_image()

    def show_next_image(self):
        if self.images:
            self.current_image_index += 1
            if self.current_image_index >= len(self.images):
                self.current_image_index = 0
            self.show_image()

    def update_image_label(self):
        if self.images:
            self.image_number_label.config(text=f"Image {self.current_image_index + 1}")


    def on_press(self, event):
        self.start_x = event.x + self.canvas.canvasx(0)
        self.start_y = event.y + self.canvas.canvasy(0)

    def on_drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            self.canvas.delete("rectangle")
            x, y = event.x + self.canvas.canvasx(0), event.y + self.canvas.canvasy(0)
            self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                x,
                y,
                outline="red",
                tags="rectangle"
            )

    def on_release(self, event):
        
        selected_option = self.selected_psm_option.get()

        if self.start_x is not None and self.start_y is not None:
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x + self.canvas.canvasx(0), event.y + self.canvas.canvasy(0)  
            
            #if x1 == x2 and y1 == y2:
            if abs(x1 - x2) < 10 and abs(y1 - y2) < 10:
                if self.press_x is None and self.press_y is None:
                    self.press_x = x1
                    self.press_y = y1
                else:
                    # correct the coordinates if x1 > x2 and y1 > y2
                    if self.press_x > x2:
                        aux = self.press_x
                        self.press_x = x2
                        x2 = aux
                    if self.press_y > y2:
                        aux = self.press_y
                        self.press_y = y2
                        y2 = aux
                    
                    if self.rotate_flag == 0:
                        self.coordinates.append([self.press_x, self.press_y, x2, y2, self.zoom_level, self.current_image_index])
                        self.canvas.create_rectangle(
                            self.press_x,
                            self.press_y,
                            x2,
                            y2,
                            outline="blue",
                            tags="rectangle_type2"
                        )

                        text1 = '------------------------------------------------------------------\n'
                        text1 += f'Area Coord (x1,y1,x2,y2,zoom_level): ([{self.press_x},{self.press_y},{x2},{y2}],{self.zoom_level:.2f})\n'
                        text2 = ''
                        #selected_area = self.image.crop((x1, y1, x2, y2))
                        #selected_area = self.image_zoom.crop((x1, y1, x2, y2))
                        # to use alwais the coordinates of the original image
                        selected_area = self.image.crop((self.press_x/self.zoom_level, self.press_y/self.zoom_level, x2/self.zoom_level, y2/self.zoom_level))
                        #text2 = pytesseract.image_to_string(selected_area)
                        text2 = pytesseract.image_to_string(selected_area, lang = 'eng', config= f'{selected_option}')
                        text = text1 + '------------------------------------------------------------------\n'
                        text += text2
                        #self.text_output.delete(1.0, tk.END)
                        self.text_output.insert(tk.END, text)
                    else:
                        # If to calculate the rotation angle
                        self.canvas.create_line(self.press_x, self.press_y, x2, y2, fill="blue", width=2, tags = 'line')
                        # Calculate the inclination of the line
                        delta_x = x2 - self.press_x
                        delta_y = y2 - self.press_y
                        angle_radians = math.atan2(delta_y, delta_x)
                        angle_degrees = -90 + math.degrees(angle_radians)

                        # Fill the angle_entry with the calculated angle
                        self.angle_entry.delete(0, tk.END)
                        self.angle_entry.insert(0, f"{angle_degrees:.1f}")
                        self.rotate_flag = 0
                    
                    self.press_x = None
                    self.press_y = None
            else:
                # correct the coordinates if x1 > x2 and y1 > y2
                if x1> x2:
                    aux = x1
                    x1= x2
                    x2 = aux
                if y1> y2:
                    aux = y1
                    y1= y2
                    y2 = aux
                self.coordinates.append([x1, y1, x2, y2, self.zoom_level, self.current_image_index])
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline="red",
                    tags="rectangle_type1"
                )
                text1 = '------------------------------------------------------------------\n'
                text1 += f'Area Coord (x1,y1,x2,y2,zoom_level): ([{x1},{y1},{x2},{y2}],{self.zoom_level:.2f})\n'
                text2 = ''
                #selected_area = self.image.crop((x1, y1, x2, y2))
                #selected_area = self.image_zoom.crop((x1, y1, x2, y2))
                # to use always the coordinates of the original image
                selected_area = self.image.crop((x1/self.zoom_level, y1/self.zoom_level, x2/self.zoom_level, y2/self.zoom_level))
                
                #print('selected_option:', selected_option)
                #text2 = pytesseract.image_to_string(selected_area)
                #text2 = pytesseract.image_to_string(selected_area, lang = 'eng', config='--psm 4')
                text2 = pytesseract.image_to_string(selected_area, lang = 'eng', config= f'{selected_option}')
                #text2 = pytesseract.image_to_string(selected_area, lang = 'eng', config= f'-c preserve_interword_spaces=1 {selected_option}')
                
                text = text1 + '------------------------------------------------------------------\n'
                text += text2
                #self.text_output.delete(1.0, tk.END)
                self.text_output.insert(tk.END, text)
                
                print('Text2:', text2.replace('\n\n', '\n'))

    def perform_ocr(self):
        
        selected_option = self.selected_psm_option.get()
        
        text = '##################################################################\n'
        text += 'Len Coordinates List:' + str(len(self.coordinates)) + '\n'
        self.text_output.insert(tk.END, text)
        
        for row in self.coordinates:
            text1 = '------------------------------------------------------------------\n'
            text2 = ''
            #selected_area = self.image_zoom.crop((row[0], row[1], row[2], row[3]))
            if self.images is not None:
                selected_area = self.images[row[5]].crop((row[0]/row[4], row[1]/row[4], row[2]/row[4], row[3]/row[4]))
                width, height = self.images[row[5]].size
                text1 += f'Original Image width, height = {width}, {height}\n\n'
            else:
                # to use alwais the coordinates of the original image
                selected_area = self.image.crop((row[0]/row[4], row[1]/row[4], row[2]/row[4], row[3]/row[4]))
                width, height = self.image.size
                text1 += f'Original Image width, height = {width}, {height}\n\n'
                
            text1 += f'Area Coord (x1,y1,x2,y2, zoom_level): ({row[:4]},{row[4]:.2f})\n'
            text1 += '------------------------------------------------------------------\n' 
            #text2 += pytesseract.image_to_string(selected_area) 
            #text2 += pytesseract.image_to_string(selected_area, lang = 'eng') 
            text2 = pytesseract.image_to_string(selected_area, lang = 'eng', config= f'{selected_option}')
            #text2.replace('\n\n', '\n')
            
            text = text1 + text2
            self.text_output.insert(tk.END, text)
            
        self.coordinates = []
    
    def clear_text(self):
        self.text_output.delete(1.0, tk.END)
        
    def clear_rectangles(self):
        self.canvas.delete("line")
        self.canvas.delete("rectangle")
        self.canvas.delete("rectangle_type1")
        self.canvas.delete("rectangle_type2")

    def zoom_in(self):
        #self.zoom_level += 0.2
        self.zoom_level *= 1.25
        self.update_zoom()

    def zoom_out(self):
        #self.zoom_level -= 0.2
        self.zoom_level *= 0.8
        self.update_zoom()

    def update_zoom(self):
        if self.image is not None:
            
            self.clear_rectangles()
            
            width, height = self.image.size
            new_width = int(width * self.zoom_level)
            new_height = int(height * self.zoom_level)
            
            #print('zoom_level:', self.zoom_level)

            text = '##################################################################\n'
            text += f'Original Image width, height = {width}, {height}\n'
            text += f'Zoomed   Image width, height = {new_width}, {new_height}\n'
            text += '##################################################################\n'
            self.text_output.insert(tk.END, text)
            
            #self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
            #self.photo = ImageTk.PhotoImage(self.image)
            self.image_zoom = self.image.resize((new_width, new_height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image_zoom)
            
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def rotate_image(self):
        self.clear_rectangles()
        
        if self.image is not None:            
            angle_input = self.angle_entry.get()
            if not angle_input:
                #flag to indicate get coordinates to calculate angle
                self.rotate_flag = 1
            else:            
                try:
                    angle = float(self.angle_entry.get())
                    self.image = self.image.rotate(angle, expand=True)
                    if self.images is not None:
                        self.images[self.current_image_index] = self.image
                        #Remove Coordinates of the rotated image
                        for index, row in enumerate(self.coordinates):
                            if row[5] == self.current_image_index:
                                self.coordinates.pop(index)
                        
                    else:
                        self.coordinates =  []
                    self.image_zoom = self.image_zoom.rotate(angle, expand=True)
                    self.update_zoom()
                except ValueError:
                    # Handle invalid input
                    pass           
            
if __name__ == "__main__":
    root = tk.Tk()
    app = OCRSquareSelector(root)
    root.mainloop()