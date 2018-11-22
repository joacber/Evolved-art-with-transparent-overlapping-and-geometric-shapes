import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import style, animation
import matplotlib.ticker as mtick
import cv2
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from Classes.evolve import *

import os

"""
Static Variables
"""
#   window size
#   a couple of methods to get screen size:
#   from win32api import GetSystemMetrics
#
#   print("Width =", GetSystemMetrics(0))
#   print("Height =", GetSystemMetrics(1))
#
#   import gtk, pygtk
#
#   window = gtk.Window()
#   screen = window.get_screen()
#   print "width = " + str(screen.get_width()) + ", height = " + str(screen.get_height())
width_of_window = 1080
height_of_window = 540

#   styles
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
style.use("ggplot")

#   matplotlib
list_of_plot_names = []
plot_figure = Figure()
plot_1 = plot_figure.add_subplot(1, 1, 1)
plt.ion()  # Interactive

#   highest possible difference per pixel
max_pixel_difference = 3.0 * 255.0

#   image
default_image = "resources\\default_placeholder.png"
target_image = "resources\\mona_lisa_crop.jpg"
image_width = 0
image_height = 0

#   Global object variables for window frames
#   For referring between variables in the different windows
#   There are probably better ways to do this
start_page: object = object()
main_page: object = object()
stats_page: object = object()
max_generation = 10000


def animate(i):
    """
    Matplotlib's update function
    Will likely use Tkinter's update instead
    """


def initialize_graph():
    """
    Some initial settings that are applied at startup and need to be reapplied after clearing the plot
    """
    global max_generation
    plot_1.xaxis.label.set_color('c')
    plot_1.yaxis.label.set_color('r')
    plot_1.set_xlabel('Generation')
    plot_1.set_ylabel('Fitness')
    plot_1.set_title('Fitness Graph', x=0.2, fontsize=20)
    plot_1.set_xlim([-(max_generation / 20), max_generation])
    plot_1.set_ylim([0, 100])
    plot_1.xaxis.set_major_locator(mtick.MaxNLocator(11))
    plot_1.yaxis.set_major_locator(mtick.MaxNLocator(11))
    plot_1.yaxis.set_major_formatter(mtick.PercentFormatter())
    plot_1.grid(color='k', alpha=0.5, linestyle='-.', linewidth=0.5)
    plot_1.set_facecolor('xkcd:off white')


def resize_image(input_image):
    """
    :param input_image: jpg target image
    :return: resized jpg image
    """
    global image_width, image_height, image
    img = input_image
    img_height, img_width, can = input_image.shape
    if img_width > img_height:
        base_width = 300
        width_percent = (base_width / float(img_width))
        height_size = int((float(img_height) * float(width_percent)))
        image = cv2.resize(img, (int(base_width), int(height_size)))
        return image
    else:
        base_height = 300
        height_percent = (base_height / float(img_height))
        width_size = int((float(img_width * float(height_percent))))
        image = cv2.resize(img, (int(width_size), int(base_height)))
        return image


def relative_fitness(fitness, *args):
    """
    Calculate fitness relative to image size
    :param fitness: Raw integer fitness score
    :param args: width, height
    :return: Realive fitness between 0 and 100 (percent)
    """
    global image_width, image_height
    if not args:
        #   lowest fitness score possible for this image (amount of pixels * max pixel difference)
        lowest_score: float = int(image_width) * int(image_height) * max_pixel_difference
    else:
        lowest_score: float = int(args[0]) * int(args[1]) * max_pixel_difference
    rel_fitness = (100.0 - (fitness / lowest_score * 100.0))
    return round(rel_fitness, 2)


class EvolutionaryArt(tk.Tk):
    """
    Should create window where user inputs parameters and hits run

    A new window should show target image, current best image in the population
    and an image that highlights differences between the two last best images

    In a new or the same window, graphs can be updated every (5th) generation
    with data that we log in a csv file or something similar
    Rename to Evolutionary_Art later?
    """

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #   Window's size and placement on screen (middle)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width_of_window / 2)
        y_coordinate = (screen_height / 2) - (height_of_window / 2)
        self.geometry("%dx%d+%d+%d" % (width_of_window, height_of_window, x_coordinate, y_coordinate))

        #   Loads icon from resources folder (update later)
        tk.Tk.iconbitmap(self, default='resources\\triangle_and_circle.ico')
        tk.Tk.wm_title(self, "Evolutionary Art")

        #   Initialize some graph parameters like title, names and colours of the axis
        initialize_graph()

        #   Initialize Tkinter
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #   Touple of the different pages
        self.frames = {}

        #   Add page classes to touple
        for F in (StartPage, MainPage, StatsPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        #   Show start page first
        self.show_frame(StartPage)

    #   Function for switching between frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    """
    Functionality:
    Set up parameters for initialization
    Choose image
    Use webcam
    """
    def __init__(self, parent, controller):
        #   Must use global object variables to change instance variables between the pages
        global start_page
        #   Initialize Start Page
        tk.Frame.__init__(self, parent)
        start_page = self
        #   must assign controller to self in order to pass it to a function without lambda
        self.target_image = ""
        self.controller = controller
        self.pil_image = None
        self.opencv_image_r_g_b = None
        #   Frames for organizing visual elements
        self.top = tk.Frame(self, borderwidth=1, relief="solid")
        self.bottom = tk.Frame(self, borderwidth=1, relief="solid")
        self.top_box = tk.Frame(self.top, borderwidth=1, relief="solid")
        self.bottom_left_box = tk.Frame(self.bottom, borderwidth=1, relief="solid")
        self.bottom_right_box = tk.Frame(self.bottom, borderwidth=1, relief="solid")
        #   Place frames within main frame
        self.top.pack(side="top", expand=True, fill="both")
        self.bottom.pack(side="bottom", expand=True, fill="both")
        self.top_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.bottom_left_box.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        self.bottom_right_box.pack(side="right", expand=True, fill="both", padx=5, pady=5)

        self.page_label = ttk.Label(self.top_box, text="Start Page", font=LARGE_FONT)
        self.page_label.grid(row=0, column=2, columnspan=2)
        #   Navigation Buttons
        self.main_page_button = ttk.Button(self.top_box, text="To Main Page",
                                           command=self.initialize_evolution)
        self.main_page_button.grid(row=1, column=2)

        self.stats_page_button = ttk.Button(self.top_box, text="To Statistics Page",
                                            command=self.to_stats_page)
        self.stats_page_button.grid(row=1, column=3)
        #   Parameter controllers for variables that will be locked upon running the program.
        self.amount_of_parents_label = ttk.Label(self.top_box, text="Amount of Parents")
        self.amount_of_parents_slider = tk.Scale(self.top_box, from_=1, to=100, resolution=1, orient="horizontal")
        self.amount_of_parents_label.grid(row=2, column=0)
        self.amount_of_parents_slider.grid(row=2, column=1)
        self.children_per_parent_label = ttk.Label(self.top_box, text="Children per Parent")
        self.children_per_parent_slider = tk.Scale(self.top_box, from_=1, to=100, resolution=1, orient="horizontal")
        self.children_per_parent_label.grid(row=3, column=0)
        self.children_per_parent_slider.grid(row=3, column=1)
        self.vertices_label = ttk.Label(self.top_box, text="Number of Vertices")
        self.vertices_slider = tk.Scale(self.top_box, from_=3, to=20, orient="horizontal")
        self.vertices_label.grid(row=4, column=0)
        self.vertices_slider.grid(row=4, column=1)
        self.number_of_genes_label = ttk.Label(self.top_box, text="# of Genes")
        self.polygons_label = ttk.Label(self.top_box, text="Number of Polygons")
        self.circles_label = ttk.Label(self.top_box, text="Number of Circles")
        self.lines_label = ttk.Label(self.top_box, text="Number of Lines")
        self.polygons_slider = tk.Scale(self.top_box, from_=0, to=100, resolution=1, orient="horizontal")
        self.circles_slider = tk.Scale(self.top_box, from_=0, to=100, resolution=1, orient="horizontal")
        self.lines_slider = tk.Scale(self.top_box, from_=0, to=100, resolution=1, orient="horizontal")
        self.polygons_label.grid(row=5, column=0)
        self.circles_label.grid(row=6, column=0)
        self.lines_label.grid(row=7, column=0)
        self.polygons_slider.grid(row=5, column=1)
        self.circles_slider.grid(row=6, column=1)
        self.lines_slider.grid(row=7, column=1)
        #   TkInter variables for parameter controllers
        self.mutation_var = tk.DoubleVar()
        self.gene_structure_var = tk.DoubleVar()
        self.soft_mutation_var = tk.DoubleVar()
        self.save_image_rate_var = tk.IntVar()
        self.max_generation_var = tk.IntVar()
        self.alpha_limit_var = tk.DoubleVar()

        self.hybrid_soft_mutation_var = tk.IntVar()
        self.hybrid_medium_mutation_var = tk.IntVar()
        self.mutation_type_var = tk.DoubleVar()
        self.mutation_type_var = tk.BooleanVar()
        self.crossover_mutation_var = tk.BooleanVar()
        #   Parameter controllers for variables that will be editable after running the program.
        self.mutation_label = ttk.Label(self.top_box, text="Mutation Probability")
        self.mutation_slider = tk.Scale(self.top_box, from_=0.05, to=1.0, resolution=0.05, orient="horizontal",
                                        variable=self.mutation_var)
        self.mutation_label.grid(row=2, column=2)
        self.mutation_slider.grid(row=2, column=3)
        self.gene_structure_label = ttk.Label(self.top_box, text="Genetic Restructure Rate")
        self.gene_structure_slider = tk.Scale(self.top_box, from_=0, to=1, resolution=0.1, orient="horizontal",
                                              variable=self.gene_structure_var)
        self.gene_structure_label.grid(row=3, column=2)
        self.gene_structure_slider.grid(row=3, column=3)
        self.soft_mutation_label = ttk.Label(self.top_box, text="Soft Mutation Rate")
        self.soft_mutation_slider = tk.Scale(self.top_box, from_=0.1, to=1.0, resolution=0.05, orient="horizontal",
                                             variable=self.soft_mutation_var)
        self.soft_mutation_label.grid(row=4, column=2)
        self.soft_mutation_slider.grid(row=4, column=3)
        self.save_rate_label = ttk.Label(self.top_box, text="Save Rate")
        self.save_rate_slider = tk.Scale(self.top_box, from_=10, to=10000, resolution=10, orient="horizontal",
                                         variable=self.save_image_rate_var)
        self.save_rate_label.grid(row=5, column=2)
        self.save_rate_slider.grid(row=5, column=3)
        self.max_generation_label = ttk.Label(self.top_box, text="Maximum Generations")
        self.max_generation_slider = tk.Scale(self.top_box, from_=0, to=100000, resolution=1000, orient="horizontal",
                                              variable=self.max_generation_var)
        self.max_generation_label.grid(row=6, column=2)
        self.max_generation_slider.grid(row=6, column=3)


        self.hybrid_soft_mutate_label = ttk.Label(self.top_box, text="Hybrid (Soft Mutation)")
        self.hybrid_soft_mutate_slider = tk.Scale(self.top_box, from_=0, to=10, resolution=1, orient="horizontal",
                                                  variable=self.hybrid_soft_mutation_var)
        self.hybrid_medium_mutate_label = ttk.Label(self.top_box, text="Hybrid (Medium Mutation)")
        self.hybrid_medium_mutate_slider = tk.Scale(self.top_box, from_=0, to=10, resolution=1, orient="horizontal",
                                                    variable=self.hybrid_medium_mutation_var)
        self.hybrid_soft_mutate_label.grid(row=2, column=4)
        self.hybrid_soft_mutate_slider.grid(row=2, column=5)
        self.hybrid_medium_mutate_label.grid(row=3, column=4)
        self.hybrid_medium_mutate_slider.grid(row=3, column=5)
        self.mutation_type_button = ttk.Checkbutton(self.top_box, text="Chunk Mutation",
                                                    variable=self.mutation_type_var,
                                                    onvalue=True, offvalue=False)
        self.mutation_type_button.var = self.mutation_type_var
        self.mutation_type_button.grid(row=4, column=5)
        self.crossover_mutation_button = ttk.Checkbutton(self.top_box, text="Crossover Mutation",
                                                         variable=self.crossover_mutation_var,
                                                         onvalue=True, offvalue=False,
                                                         command=self.crossover_mutation_func)
        self.crossover_mutation_button.var = self.crossover_mutation_var
        self.crossover_mutation_button.grid(row=5, column=5)
        #   Set initial controller values at start based on best results
        self.amount_of_parents_slider.set(1)
        self.children_per_parent_slider.set(5)
        self.vertices_slider.set(8)
        self.polygons_slider.set(25)
        self.circles_slider.set(25)
        self.mutation_slider.set(0.10)
        self.soft_mutation_slider.set(0.15)
        self.save_rate_slider.set(1000)
        self.max_generation_slider.set(10000)
        self.hybrid_soft_mutate_slider.set(2)
        self.hybrid_medium_mutate_slider.set(1)
        #   Give equal weight to every column and row
        #   Elements inside will allocate any required space within the frame(s)
        self.top_box.rowconfigure(0, weight=1)
        self.top_box.rowconfigure(1, weight=1)
        self.top_box.rowconfigure(2, weight=1)
        self.top_box.rowconfigure(3, weight=1)
        self.top_box.rowconfigure(4, weight=1)
        self.top_box.rowconfigure(5, weight=1)
        self.top_box.rowconfigure(6, weight=1)
        self.top_box.rowconfigure(7, weight=1)
        self.top_box.columnconfigure(0, weight=1)
        self.top_box.columnconfigure(1, weight=1)
        self.top_box.columnconfigure(2, weight=1)
        self.top_box.columnconfigure(3, weight=1)
        self.top_box.columnconfigure(4, weight=1)
        self.top_box.columnconfigure(5, weight=1)
        # Image selection and webcamera buttons
        self.choose_image = ttk.Button(self.bottom_left_box, text="Choose Image...", command=self.open_image)
        self.choose_image.grid(row=0, column=0)
        self.take_image = ttk.Button(self.bottom_left_box, text="Use Camera", command=self.web_image)
        self.take_image.grid(row=0, column=1)
        #   GIF
        self.gif_query = tk.BooleanVar()
        self.export_gif_button = ttk.Checkbutton(self.bottom_left_box, text="Export GIF",
                                                 variable=self.gif_query,
                                                 onvalue=True, offvalue=False,
                                                 command=self.export_gif)
        self.export_gif_button.var = self.gif_query
        self.export_gif_button.grid(row=1, column=0)
        #   Give equal weight to every column and row
        #   Elements inside will allocate any required space within the frame(s)
        self.bottom_left_box.rowconfigure(0, weight=1)
        self.bottom_left_box.rowconfigure(1, weight=1)
        self.bottom_left_box.columnconfigure(0, weight=1)
        self.bottom_left_box.columnconfigure(1, weight=1)
        #   Image import and display
        self.img = Image.open(default_image)
        self.photo = ImageTk.PhotoImage(self.img)
        self.target_image_label = tk.Label(self.bottom_right_box, image=self.photo)
        #   Storing object through reference (so it doesn't get garbage collected)
        self.target_image_label.image = self.photo
        self.target_image_label.pack(expand=1)

    def crossover_mutation_func(self):
        """Force minimum 2 parents when selecting crossover mutation"""
        if self.crossover_mutation_button.var.get():
            self.amount_of_parents_slider.config(from_=2)
        else:
            self.amount_of_parents_slider.config(from_=1)

    def export_gif(self):
        """
        Check checkbutton variable
        Toggle Save Rate controller on/off
        etc...
        """

    def web_image(self):
        global new_image, start_height, start_width, image
        # cap = cv2.VideoCapture(0)
        cap = cv2.VideoCapture(cv2.CAP_DSHOW)
        print('PRESS SPACE FOR CAPTURE')
        img_scale = 0.5

        while (True):
            ret, frame = cap.read()
            # frame = cv2.resize(frame, (0, 0), fx=cap_scale, fy=cap_scale)
            frame = cv2.resize(frame, (1280, 800))  # Endrer webcam-preview oppløsning
            cv2.imshow('frame', frame)

            key = cv2.waitKey(1)
            if key == ord(' '):
                print("Captured")
                # frame = cv2.resize(frame, (0, 0), fx=img_scale, fy=img_scale) #Skalerer ned bildet ved hjelp av %
                frame = cv2.resize(frame, (320, 200))  # endrer oppløsningen til det endelige bildet
                cv2.imwrite("../resources/webCam.jpg", frame)
                cv2.destroyAllWindows()
                break
        cap.release()

        self.opencv_image = frame
        #   Resize if the image is too large
        start_height, start_width, can = self.opencv_image.shape
        if (start_width, start_height) > (400, 400):
            self.opencv_image = resize_image(self.opencv_image)
        else:
            image = self.opencv_image
        b, g, r = cv2.split(self.opencv_image)
        self.opencv_image_r_g_b = cv2.merge((r, g, b))
        self.pil_image = Image.fromarray(self.opencv_image_r_g_b)
        self.tkinter_photo = ImageTk.PhotoImage(self.pil_image)
        self.target_image_label.configure(image=self.tkinter_photo)
        self.target_image_label.image = self.tkinter_photo
        new_image = True
        main_page.target_image_label.configure(image=self.tkinter_photo)
        main_page.update()


    def open_image(self):
        global new_image, image_width, image_height, start_height, start_width, image
        """
        Overwrite placeholder image
        Later we will pass this to evolution
        """
        self.target_image = str(filedialog.askopenfilename(initialdir="resources\\", title="Select file",
                                                           filetypes=(("jpeg files", "*.jpg"),
                                                                      ("all files", "*.*"))))

        if self.target_image:
            #   Load image with opencv
            self.opencv_image = cv2.imread(self.target_image)
            #   Resize if the image is too large
            start_height, start_width, can = self.opencv_image.shape
            if (start_width, start_height) > (400, 400):
                self.opencv_image = resize_image(self.opencv_image)
            else:
                image = self.opencv_image
            #   Blue, green and red channels from splitting
            b, g, r = cv2.split(self.opencv_image)
            #   Merge red, green and blue channels
            self.opencv_image_r_g_b = cv2.merge((r, g, b))
            #   Load the same image with PIL
            self.pil_image = Image.fromarray(self.opencv_image_r_g_b)
            image_width, image_height = self.pil_image.size

            #   Load PIL image as a TKInter photo image.
            self.tkinter_photo = ImageTk.PhotoImage(self.pil_image)
            #   storing object through reference (so it doesn't get garbage collected)
            self.target_image_label.configure(image=self.tkinter_photo)
            self.target_image_label.image = self.tkinter_photo
            #   Upadate image on Main Page
            new_image = True
            main_page.target_image_label.configure(image=self.tkinter_photo)
            main_page.update()


    def initialize_evolution(self):
        global new_image, amount_of_parents, children_per_parent, save_image_rate, vertices, number_of_genes, shapes_ratio, \
            mutation_probability, soft_mutate_rate, hybrid_soft_mutate, hybrid_medium_mutate, mutation_type, \
            alpha_limit, \
            number_of_types, crossover_mutation, gene_structure_rate, target_image_name, image, max_generation, radius_limit, \
            thickness_limit, wanted_width, wanted_height, export_gif_button, image_width, image_height, start_height, start_width
        """
        Initialize algorithm parameters
        Go to Main Page
        """

        if self.pil_image is None:
            self.target_image = "resources\\mona_lisa_crop.jpg"
            self.opencv_image = cv2.imread(self.target_image)
            start_height, start_width, can = self.opencv_image.shape
            image = self.opencv_image
            b, g, r = cv2.split(self.opencv_image)
            self.opencv_image_r_g_b = cv2.merge((r, g, b))
            self.pil_image = Image.fromarray(self.opencv_image_r_g_b)
            image_width, image_height = self.pil_image.size
            self.tkinter_photo = ImageTk.PhotoImage(self.pil_image)
            #   storing object through reference (so it doesn't get garbage collected)
            self.target_image_label.configure(image=self.tkinter_photo)
            self.target_image_label.image = self.tkinter_photo
            new_image = True
            main_page.target_image_label.configure(image=self.tkinter_photo)
            main_page.update()

        # Population values
        # image = self.opencv_image
        amount_of_parents = self.amount_of_parents_slider.get()
        children_per_parent = self.children_per_parent_slider.get()
        vertices = self.vertices_slider.get()  # number of vertices in hte polygon
        #   Genetic values
        number_of_polygons = self.polygons_slider.get()
        number_of_circles = self.circles_slider.get()
        number_of_lines = self.lines_slider.get()
        number_of_genes = number_of_polygons + number_of_circles + number_of_lines
        shapes_ratio = [number_of_polygons, number_of_circles, number_of_lines]
        #   Parameters
        mutation_probability = self.mutation_slider.get()  # 10% for evolving
        soft_mutate_rate = self.soft_mutation_slider.get()  # 10% now. Change for more drastic change
        hybrid_soft_mutate = self.hybrid_soft_mutate_slider.get()
        hybrid_medium_mutate = self.hybrid_medium_mutate_slider.get()
        max_generation = self.max_generation_slider.get()
        mutation_type = self.mutation_type_button.var.get()
        save_image_rate = self.save_rate_slider.get()
        crossover_mutation = self.crossover_mutation_button.var.get()
        gene_structure_rate = self.gene_structure_slider.get()
        export_gif_button = self.export_gif_button.var.get()
        #   Path to standard image
        path, target_image_name = os.path.split(self.target_image)

        #   Switch Frame
        self.controller.show_frame(MainPage)

    def to_stats_page(self):
        """
        To Statistics Page
        """
        #   Switch Frame
        self.controller.show_frame(StatsPage)


class MainPage(tk.Frame):
    """
    Functionality:
    Display images, graphs and text
    Update every generation or a set time
    """

    def __init__(self, parent, controller):
        #   Must use global object variables to change instance variables between the pages
        global main_page
        tk.Frame.__init__(self, parent)
        main_page = self
        self.generation = 0
        self.controller = controller
        global running, stop_evolve
        running = False
        stop_evolve = False
        self.evolve = None
        #   Frames for organizing visual elements
        self.left = tk.Frame(self, borderwidth=1, relief="solid")
        self.right = tk.Frame(self, borderwidth=1, relief="solid")
        self.middle = tk.Frame(self, borderwidth=1, relief="solid")
        self.top_left_box = tk.Frame(self.left, borderwidth=1, relief="solid")
        self.bottom_left_box = tk.Frame(self.left, borderwidth=1, relief="solid")
        self.middle_box = tk.Frame(self.middle, borderwidth=1, relief="solid")
        self.top_right_box = tk.Frame(self.right, borderwidth=1, relief="solid")
        self.bottom_right_box = tk.Frame(self.right, borderwidth=1, relief="solid")
        #   Place frames within main frame
        self.left.pack(side="left", expand=True, fill="both")
        self.right.pack(side="right", expand=True, fill="both")
        self.middle.pack(expand=True, fill="both")
        self.top_left_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.bottom_left_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.middle_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.top_right_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.bottom_right_box.pack(expand=True, fill="both", padx=5, pady=5)
        #   Navigation Buttons
        self.page_label = tk.Label(self.middle_box, text="Main Page", font=LARGE_FONT)
        self.page_label.grid(row=0, column=2, columnspan=2)
        self.start_page_button = ttk.Button(self.middle_box, text="To Start Page",
                                            command=self.interrupt_evolution)
        self.start_page_button.grid(row=1, column=0, columnspan=3)
        self.stats_page_button = ttk.Button(self.middle_box, text="To Statistics Page",
                                            command=self.to_stats_page)
        self.stats_page_button.grid(row=1, column=3, columnspan=3)
        self.run_button = ttk.Button(self.middle_box, text="Run",
                                     command=self.setup_evolve)
        self.run_button.grid(row=2, column=0, columnspan=2)
        self.pause_button = ttk.Button(self.middle_box, text="Pause",
                                       command=self.pause_evolve)
        self.pause_button.grid(row=2, column=2, columnspan=2)
        self.stop_button = ttk.Button(self.middle_box, text="Stop",
                                      command=self.stop_evolve)
        self.stop_button.grid(row=2, column=4, columnspan=2)
        #   Parameter controllers for variables that will be editable after running the program.
        self.mutation_label = ttk.Label(self.middle_box, text="Mutation Probability", font=SMALL_FONT)
        self.mutation_slider = tk.Scale(self.middle_box, from_=0.01, to=1.0, resolution=0.05, orient="horizontal",
                                        variable=start_page.mutation_var)
        self.mutation_label.grid(row=3, column=0, sticky="w", columnspan=3)
        self.mutation_slider.grid(row=3, column=3, sticky="e", columnspan=3)
        self.gene_structure_label = ttk.Label(self.middle_box, text="Genetic Restructure Rate", font=SMALL_FONT)
        self.gene_structure_slider = tk.Scale(self.middle_box, from_=0, to=1, resolution=0.1, orient="horizontal",
                                              variable=start_page.gene_structure_var)
        self.gene_structure_label.grid(row=4, column=0, sticky="w", columnspan=3)
        self.gene_structure_slider.grid(row=4, column=3, sticky="e", columnspan=3)
        self.soft_mutation_label = ttk.Label(self.middle_box, text="Soft Mutation Rate", font=SMALL_FONT)
        self.soft_mutation_slider = tk.Scale(self.middle_box, from_=0.1, to=1.0, resolution=0.05, orient="horizontal",
                                             variable=start_page.soft_mutation_var)
        self.soft_mutation_label.grid(row=5, column=0, sticky="w", columnspan=3)
        self.soft_mutation_slider.grid(row=5, column=3, sticky="e", columnspan=3)
        self.save_rate_label = ttk.Label(self.middle_box, text="Save Rate", font=SMALL_FONT)
        self.save_rate_slider = tk.Scale(self.middle_box, from_=10, to=10000, resolution=10, orient="horizontal",
                                         variable=start_page.save_image_rate_var)
        self.save_rate_label.grid(row=6, column=0, sticky="w", columnspan=3)
        self.save_rate_slider.grid(row=6, column=3, sticky="e", columnspan=3)


        self.hybrid_soft_mutate_label = ttk.Label(self.middle_box, text="Hybrid (Soft Mutation)", font=SMALL_FONT)
        self.hybrid_soft_mutate_slider = tk.Scale(self.middle_box, from_=0, to=10, resolution=1, orient="horizontal",
                                                  variable=start_page.hybrid_soft_mutation_var)
        self.hybrid_soft_mutate_label.grid(row=7, column=0, sticky="w", columnspan=3)
        self.hybrid_soft_mutate_slider.grid(row=7, column=3, sticky="e", columnspan=3)
        self.hybrid_medium_mutate_label = ttk.Label(self.middle_box, text="Hybrid (Medium Mutation)", font=SMALL_FONT)
        self.hybrid_medium_mutate_slider = tk.Scale(self.middle_box, from_=0, to=10, resolution=1, orient="horizontal",
                                                    variable=start_page.hybrid_medium_mutation_var)
        self.hybrid_medium_mutate_label.grid(row=8, column=0, sticky="w", columnspan=3)
        self.hybrid_medium_mutate_slider.grid(row=8, column=3, sticky="e", columnspan=3)

        self.max_generation_label = ttk.Label(self.middle_box, text="Maximum Generations")

        self.max_generation_slider = tk.Scale(self.middle_box, from_=1000, to=100000, resolution=1000,
                                              orient="horizontal",
                                              variable=start_page.max_generation_var)
        self.max_generation_label.grid(row=9, column=0, sticky="w", columnspan=3)
        self.max_generation_slider.grid(row=9, column=3, sticky="e", columnspan=3)
        self.mutation_type_button = ttk.Checkbutton(self.middle_box, text="Chunk Mutation",
                                                    variable=start_page.mutation_type_var)
        self.mutation_type_button.var = start_page.mutation_type_var.get()
        self.mutation_type_button.grid(row=10, column=3, sticky="e")
        #   Give equal weight to every column and row
        #   Elements inside will allocate any required space within the frame(s)
        self.middle_box.rowconfigure(0, weight=1)
        self.middle_box.rowconfigure(1, weight=1)
        self.middle_box.rowconfigure(2, weight=1)
        self.middle_box.rowconfigure(3, weight=1)
        self.middle_box.rowconfigure(4, weight=1)
        self.middle_box.rowconfigure(5, weight=1)
        self.middle_box.rowconfigure(6, weight=1)
        self.middle_box.rowconfigure(7, weight=1)
        self.middle_box.rowconfigure(8, weight=1)
        self.middle_box.rowconfigure(9, weight=1)
        self.middle_box.rowconfigure(10, weight=1)
        self.middle_box.rowconfigure(11, weight=1)
        self.middle_box.rowconfigure(12, weight=1)
        self.middle_box.columnconfigure(0, weight=1)
        self.middle_box.columnconfigure(1, weight=1)
        self.middle_box.columnconfigure(2, weight=1)
        self.middle_box.columnconfigure(3, weight=1)
        self.middle_box.columnconfigure(4, weight=1)
        self.middle_box.columnconfigure(5, weight=1)
        #   TkInter variables for visual numbers from the executed program
        self.tk_generation = tk.IntVar()
        self.tk_generation.set(0)
        self.tk_abs_fitness = tk.IntVar()
        self.tk_abs_fitness.set(0)
        self.tk_rel_fitness = tk.DoubleVar()
        self.tk_rel_fitness.set(0.0)
        self.tk_time = tk.DoubleVar()
        #   Visual numbers from the executed program
        self.generation_label = ttk.Label(self.top_right_box, text="Generation: ", font=MEDIUM_FONT)
        self.generation_label.grid(row=0, column=0, sticky="w")
        self.generation_variable = ttk.Label(self.top_right_box, textvariable=self.tk_generation)
        self.generation_variable.grid(row=0, column=1, sticky="e")
        self.abs_fitness_label = ttk.Label(self.top_right_box, text="Absolute Fitness: ", font=MEDIUM_FONT)
        self.abs_fitness_label.grid(row=1, column=0, sticky="w")
        self.generation_variable = ttk.Label(self.top_right_box, textvariable=self.tk_abs_fitness)
        self.generation_variable.grid(row=1, column=1, sticky="e")
        self.rel_fitness_label = ttk.Label(self.top_right_box, text="Relative Fitness: ", font=MEDIUM_FONT)
        self.rel_fitness_label.grid(row=2, column=0, sticky="w")
        self.generation_variable = ttk.Label(self.top_right_box, textvariable=self.tk_rel_fitness)
        self.generation_variable.grid(row=2, column=1, sticky="e")
        self.time_label = ttk.Label(self.top_right_box, text="Time elapsed: ", font=MEDIUM_FONT)
        self.time_label.grid(row=3, column=0, sticky="w")
        self.generation_variable = ttk.Label(self.top_right_box, textvariable=self.tk_time)
        self.generation_variable.grid(row=3, column=1, sticky="e")
        #   Give equal weight to every column and row
        #   Elements inside will allocate any required space within the frame(s)
        self.top_right_box.rowconfigure(0, weight=1)
        self.top_right_box.rowconfigure(1, weight=1)
        self.top_right_box.rowconfigure(2, weight=1)
        self.top_right_box.rowconfigure(3, weight=1)
        self.top_right_box.columnconfigure(0, weight=1)
        self.top_right_box.columnconfigure(1, weight=1)
        #   Target Image
        self.img1 = Image.open(default_image)
        self.photo1 = ImageTk.PhotoImage(self.img1)
        self.target_image_label = ttk.Label(self.bottom_left_box, image=self.photo1)
        #   storing object through reference (so it doesn't get garbage collected)
        self.target_image_label.image = self.photo1
        self.target_image_label.pack(expand=1)
        #   Current best image (phenotype)
        self.img2 = Image.open(default_image)
        self.photo2 = ImageTk.PhotoImage(self.img2)
        self.current_image_label = ttk.Label(self.bottom_right_box, image=self.photo2)
        #   storing object through reference (so it doesn't get garbage collected)
        self.current_image_label.image = self.photo2
        self.current_image_label.pack(expand=1)
        #   Toggle controls
        self.stop_button.configure(state='disabled')
        self.pause_button.configure(state='disabled')
        self.run_button.configure(state='normal')

    def interrupt_evolution(self):
        """
        Pause Loop
        Open Start Page
        """
        global running, stop_evolve
        running = False
        self.toggle_controls(running)

        stop_evolve = True
        self.stop_button.configure(state='disabled')
        self.pause_button.configure(state='disabled')
        self.run_button.configure(state='normal')
        #   Switch Frame
        self.controller.show_frame(StartPage)

    def to_stats_page(self):
        """
        Pause Loop
        Open Statistics Page
        """
        global running, stop_evolve
        running = False
        self.toggle_controls(running)
        stop_evolve = True
        self.stop_button.configure(state='disabled')
        self.pause_button.configure(state='disabled')
        self.run_button.configure(state='normal')
        #   Switch Frame
        self.controller.show_frame(StatsPage)

    def stop_evolve(self):
        """
        Break Loop
        """
        global stop_evolve
        stop_evolve = True
        running = False
        self.toggle_controls(running)
        self.stop_button.configure(state='disabled')
        self.pause_button.configure(state='disabled')
        self.run_button.configure(state='normal')

    def pause_evolve(self):
        """
        Pause Loop
        """
        global running
        running = False
        self.toggle_controls(running)
        self.stop_button.configure(state='normal')
        self.pause_button.configure(state='disabled')
        self.run_button.configure(state='normal')

    def setup_evolve(self):
        """
        Initialize algorithm parameters
        """
        global amount_of_parents, children_per_parent, save_image_rate, vertices, number_of_genes, shapes_ratio, \
            mutation_probability, soft_mutate_rate, hybrid_mutate_ratio, mutation_type, alpha_limit,  \
            number_of_types, crossmutate, target_image_name, image, running, new_image, stop_evolve, gene_structure_rate, \
            hybrid_medium_mutate, hybrid_soft_mutate, crossover_mutation, export_gif_button

        if not running and new_image or self.evolve is None:
            self.output = "output_%s" % (time.strftime("%d-%m-%Y_%H-%M-%S"))
            self.evolve = Evolve(image=image, image_name=target_image_name, output_folder=self.output,
                                 save_image_rate=save_image_rate, max_generation=max_generation,
                                 amount_of_parents=amount_of_parents, children_per_parent=children_per_parent,
                                 vertices=vertices, number_of_genes=number_of_genes,
                                 shapes_ratio=shapes_ratio, mutation_probability=mutation_probability,
                                 soft_mutate_rate=soft_mutate_rate, hybrid_soft_mutate=hybrid_soft_mutate,
                                 hybrid_medium_mutate=hybrid_medium_mutate,
                                 mutation_type=mutation_type, gene_structure_rate=gene_structure_rate,
                                 crossover_mutation=crossover_mutation,
                                 export_gif_button=export_gif_button, start_width=start_width, start_height=start_height)
            self.evolve.create_parents()
            self.evolve.logging()
            self.generation = 0
            window.after(1, self.run_evolve)
            new_image = False
            stop_evolve = False
        running = True
        self.toggle_controls(running)
        self.stop_button.configure(state='normal')
        self.pause_button.configure(state='normal')
        self.run_button.configure(state='disabled')

    def run_evolve(self):
        """
        Start loop / algorithm
        """
        global running, stop_evolve, save_image_rate, mutation_probability, mutation_type, gene_structure_rate, export_gif_button, \
            max_generation
        if running:

            self.update_evolve()
            if self.generation < self.evolve.max_generation:
                self.evolve.create_children()
                self.evolve.next_generation()
                self.generation += 1
                self.update_gui()

        if stop_evolve or self.generation >= self.evolve.max_generation:
            self.evolve.end_log()
            self.evolve.make_gif()
            self.evolve.make_fin_image()
            running = False
            self.toggle_controls(running)
            self.stop_button.configure(state='disabled')
            self.pause_button.configure(state='disabled')
            self.run_button.configure(state='normal')
            self.evolve = None
            return
        #   Looping algorithm so GUI doesn't freeze
        window.after(1, self.run_evolve)

    def update_gui(self):
        """
        Update GUI elements while running loop
        """
        if self.generation % self.evolve.save_image_rate == 0:
            b, g, r = cv2.split(self.evolve.parent_genome[0].image)
            self.opencv_image = cv2.merge((r, g, b))
            self.pil_image = Image.fromarray(self.opencv_image)
            self.tkinter_photo = ImageTk.PhotoImage(self.pil_image)
            self.current_image_label.configure(image=self.tkinter_photo)
            self.update()
        #   Update visual numbers: Generation #, Fitness Score and Relative Fitness
        self.tk_generation.set(self.generation)
        self.tk_abs_fitness.set(self.evolve.parent_genome[0].fitness)
        self.tk_rel_fitness.set(relative_fitness(self.evolve.parent_genome[0].fitness))
        self.tk_time.set(0.0)

    def update_evolve(self):
        """
        Get updated variables
        """
        self.evolve.mutation_probability = self.mutation_slider.get()
        self.evolve.gene_structure_rate = self.gene_structure_slider.get()
        self.evolve.soft_mutate_rate = self.soft_mutation_slider.get()
        self.evolve.save_image_rate = self.save_rate_slider.get()
        self.evolve.hybrid_soft_mutate_rate = self.hybrid_soft_mutate_slider.get()
        self.evolve.hybrid_medium_mutate_rate = self.hybrid_medium_mutate_slider.get()
        self.evolve.max_generation = self.max_generation_slider.get()
        self.evolve.mutation_type = start_page.mutation_type_var.get()

    def toggle_controls(self, is_running):
        """
        Toggle parameter controls
        :param is_running:
        :return:
        """
        if is_running:
            #   Disable Controls
            self.mutation_slider.configure(state='disabled')
            self.gene_structure_slider.configure(state='disabled')
            self.soft_mutation_slider.configure(state='disabled')
            self.save_rate_slider.configure(state='disabled')
            self.hybrid_medium_mutate_slider.configure(state='disabled')
            self.hybrid_soft_mutate_slider.configure(state='disabled')
            self.mutation_type_button.configure(state='disabled')
            self.max_generation_slider.configure(state='disabled')

        else:
            #   Enable Controls
            self.mutation_slider.configure(state='normal')
            self.gene_structure_slider.configure(state='normal')
            self.soft_mutation_slider.configure(state='normal')
            self.save_rate_slider.configure(state='normal')
            self.hybrid_medium_mutate_slider.configure(state='normal')
            self.hybrid_soft_mutate_slider.configure(state='normal')
            self.mutation_type_button.configure(state='normal')
            self.max_generation_slider.configure(state='normal')


class StatsPage(tk.Frame):
    """
    Functionality:
    Display images, graphs and text
    Update every generation or a set time
    """

    def __init__(self, parent, controller):
        #   Must use global object variables to change instance variables between the pages
        global stats_page
        tk.Frame.__init__(self, parent)
        stats_page = self
        self.controller = controller
        self.label1 = tk.Label(self, text="Statistics Page", font=LARGE_FONT)
        self.label1.pack(pady=10, padx=10)

        self.start_page_button = ttk.Button(self, text="To Start Page",
                                            command=self.to_start_page)
        self.start_page_button.pack()

        self.main_page_button = ttk.Button(self, text="To Main Page",
                                           command=self.to_main_page)
        self.main_page_button.pack()

        self.graph_button = ttk.Button(self, text="Plot Graph",
                                       command=self.plot_fitness)
        self.graph_button.pack()

        self.clear_button = ttk.Button(self, text="Clear Graph",
                                       command=self.clear_graph)

        self.clear_button.pack()

        self.canvas = FigureCanvasTkAgg(plot_figure, self)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)



    def to_start_page(self):
        """
        To Start Page
        """
        #   Switch Frame
        self.controller.show_frame(StartPage)

    def to_main_page(self):
        """
        To Main Page
        """
        #   Switch Frame
        self.controller.show_frame(MainPage)

    def plot_fitness(self):
        """
        Plots Fitness per Generation
        """
        global list_of_plot_names
        #   Browse for csv file
        try:
            graphData = open(filedialog.askopenfilename(initialdir="..\\", title="Select file",
                                                        filetypes=(("csv files", "*.csv"),
                                                                   ("all files", "*.*"))))
        except:

            print("No file chosen")
            return
        #   Add filename to list for use in legend

        list_of_plot_names.append(graphData.name[(graphData.name.rfind('/')) + 1:-4])
        #   Extract image dimensions
        xx, yy = graphData.readline().split(',')
        #   Extract all lines below the first line to a list
        data_list = graphData.readlines()[1:]
        x_list = []
        y_list = []
        #   Divide every line (element in the list) by commas (csv standard)
        for each_line in data_list:
            if len(each_line) > 0 and each_line != "" or " ":
                x, y = each_line.split(',')
                x_list.append(int(x.strip()))
                y_list.append(relative_fitness(float(y.strip()), xx, yy))
        #   Set new x limit
        last_generation = x_list[-1]
        plot_1.set_xlim([-(last_generation / 20), last_generation])
        #   Plot data
        plot_1.plot(x_list, y_list)
        #   for i, j in enumerate(plot_1.lines):
        #    j.set_color(colors[i]
        #   Make legend from global list of filenames
        plot_1.legend(list_of_plot_names, bbox_to_anchor=(0.35, 1.0, 1, .10), loc=3,
                      ncol=4, borderaxespad=0)
        #   MatPlotLib shows updated graph
        plt.show()
        #   Tkinter re-draws the page which has been updated
        self.canvas.draw()

    def clear_graph(self):
        """
        Clears current plot
        """
        plot_1.clear()
        initialize_graph()
        plt.show()
        self.canvas.draw()


window = EvolutionaryArt()

window.mainloop()
exit(0)
