"""
Score GUI Module
"""

__author__ = "Eric Lemmon"
__copyright__ = "Copyright 2021, Eric Lemmon"

import main

__credits = ["Eric Lemmon, Anne Sophie Andersen"]
__version__ = "0.9"
__maintainer__ = "Eric Lemmon"
__email__ = "ec.lemmon@gmail.com"
__status__ = "Testing"


import tkinter as tk
import image_data_loader
import timer
import cell_assigner
from section_manager import SectionManager
from sub_guis import flashable_label
from sub_guis import scrollable_frame
from PIL import ImageTk, Image


class ScoreGUI(tk.Toplevel):
    def __init__(self, root, section_manager: SectionManager, cell_assigner: cell_assigner.CellAssigner,
                 preroll=5, section_start=1, image_trigger=None, color_3="steel blue", color_1="light steel blue",
                 color_2="snow", font_header="Rosewood Std Regular", font_text="Rosewood Std Regular"):
        tk.Toplevel.__init__(self)
        # initialize necessary objects.
        self.root = root
        self.protocol("WM_DELETE_WINDOW", root.destroy)
        self.timer = timer.Timer()
        self.preroll = timer.Timer(preroll)
        self.piece_length = section_manager.get_total_timing()
        self.section_manager = section_manager
        self.start_from(section_start)
        self.cell_assignment_for_score = cell_assigner
        self.first_section = True
        self.image_trigger = image_trigger
        self.geometry('+{}+{}'.format('0', '0'))
        self.grid_rowconfigure(0, minsize=800, weight=1)
        self.grid_columnconfigure(0, minsize=1400, weight=1)

        if self.image_trigger == 1:
            self.bind("<Button-1>", self.on_event)
        elif self.image_trigger == 2:
            self.bind("<space>", self.on_event)
        else:
            pass

        # Title of window
        self.title('Image Viewer App')

        # Set initial display
        self.scrollable_frame = scrollable_frame.ScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, sticky='nsew')
        self.image_path = None

        if section_start == 1 or section_start == 2:
            text = "### TACET ###"
        elif section_start == 3:
            text = '### Imitate Electronics ###'
        else:
            text = ""

        # Set up label for image and starting tacet text
        self.label_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.label_frame.grid(row=1, columnspan=2, sticky="nsew")
        self.label_pad1 = tk.Label(self.label_frame, fg=color_2, bg="white", pady=5)
        self.label_pad1.grid(row=0, columnspan=2, sticky='nsew')
        self.label = flashable_label.FlashableLabel(self.label_frame, text=text, pady=5, font=(font_header, 50),
                                                    fg=color_3, bg="white")
        self.label.grid(row=0, column=1, columnspan=2)
        self.label_frame.grid_columnconfigure(0, weight=1)
        self.label_frame.grid_columnconfigure(2, weight=1)

        # Initialize and run timer
        self.timer_frame = tk.Frame(self.scrollable_frame, bg=color_1)
        self.timer_frame.grid(row=0, columnspan=2, sticky='nsew')
        self.timer_display = flashable_label.FlashableLabel(self.timer_frame, text=self.preroll.get_formatted_time(),
                                                            font=(font_header, 25),
                                                            fg=color_2, bg=color_1)
        self.timer_display.grid(row=0, column=1)
        self.update_timer()

        # Set section text
        self.section = flashable_label.FlashableLabel(self.timer_frame, text="PRE-ROLL",
                                                      font=(font_header, 25),
                                                      fg=color_2, bg=color_1)
        self.section.grid(row=0, column=2, sticky='ew')
        self.section_right_pad = flashable_label.FlashableLabel(self.timer_frame, text="   ",
                                                      font=(font_header, 25),
                                                      fg=color_2, bg=color_1)
        self.section_right_pad.grid(row=0, column=3, sticky='ew')
        self.timer_frame.grid_columnconfigure(0, weight=1)
        self.timer_frame.grid_columnconfigure(3, weight=1)
        self.after((self.preroll.get_time()+1)*1000, self.update_section)

        # Set kill button
        self.buttons_frame = tk.Frame(self.scrollable_frame, bg=color_1)
        self.buttons_frame.grid(row=2, columnspan=3, sticky='nsew')
        self.buttons_pad1 = tk.Label(self.buttons_frame, fg=color_2, bg=color_1, pady=2)
        self.buttons_pad1.grid(row=0, columnspan=3, sticky='ew')
        self.close_program = tk.Button(self.buttons_frame, text="QUIT", font=(font_text, 25),
                                       command=self.close, border=0, activeforeground="black", padx=7,
                                       fg=color_1, bg=color_2)
        self.close_program.grid(row=1, column=0)

        # Set next button
        self.next_button = tk.Button(self.buttons_frame, text="NEXT CELL", font=(font_text, 25),
                                     command=self.on_click, border=0, activeforeground="black", padx=7,
                                     fg=color_1, bg=color_2)
        self.next_button.grid(row=1, column=1)
        self.buttons_pad2 = tk.Label(self.buttons_frame, fg=color_2, bg=color_1, pady=2)
        self.buttons_pad2.grid(row=2, columnspan=3, sticky='nsew')
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(3, weight=1)

        # Set frame to right of everything
        self.instruction_text_frame = tk.Frame(self.scrollable_frame, bg=color_1)
        self.instruction_text_frame.grid(row=0, column=4, rowspan=3, sticky='ns')

        # Label with instructions
        self.instruction_header = flashable_label.FlashableLabel(self.instruction_text_frame,
                                                            text="Instructions\n------------",
                                                            font=(font_header, 25),
                                                            fg=color_2, bg=color_1)
        self.instruction_header.grid(row=0, column=0, sticky='n')

        self.instruction_text = flashable_label.FlashableLabel(self.instruction_text_frame,
                                                               text=self.set_instructions(),
                                                               font=(font_text, 16),
                                                               fg=color_2, bg=color_1,
                                                               wraplength=175, justify='center')
        self.instruction_text.grid(row=1, column=0)

        self.instruction_next_section_header = flashable_label.FlashableLabel(self.instruction_text_frame,
                                                            text="Next Section\n------------",
                                                            font=(font_header, 25),
                                                            fg=color_2, bg=color_1)
        self.instruction_next_section_header.grid(row=2, column=0)

        self.next_section_text = flashable_label.FlashableLabel(self.instruction_text_frame,
                                                               text=self.set_next_section_text(),
                                                               font=(font_text, 16),
                                                               fg=color_2, bg=color_1,
                                                               wraplength=175, justify='center')
        self.next_section_text.grid(row=3, column=0, sticky='s')

        self.resize()

    @staticmethod
    def resize_image(image):
        """
        Resizes the score cell image to be approximately the correct size.
        :param image: ImageTk object
        :return: resized ImageTk
        """
        ratio = min(1300/image.width, 680/image.height)
        return image.resize((int(image.width*ratio), int(image.height*ratio)), Image.ANTIALIAS)

    def get_new_image(self):
        """
        Gets a new image based on the path. Excludes images that come from the same path.
        :return: Returns an ImageTk object.
        """
        image_path = image_data_loader.select_random_image(self.cell_assignment_for_score.cells)
        print(self.image_path, image_path)
        if image_path == self.image_path:
            print("SAME PATH!")
            self.after(ms=0, func=self.set_new_image)
        else:
            self.image_path = image_path
            new_image = Image.open(image_path)
            print(new_image)
            return ImageTk.PhotoImage(ScoreGUI.resize_image(new_image))

    def set_new_image(self):
        """
        Calls self.get_new_image() and configures the center label of the GUI to be the image.
        :return:
        """
        new_image = self.get_new_image()
        self.label.image = new_image
        self.label.config(image=new_image)

    def update_timer(self):
        """
        Logic for updating the timer. Takes into account the ending of the piece, and whether there has been
        a pre-roll set.
        :return: None
        """
        if self.timer.get_time() == self.piece_length:
            self.timer_display.config(text="THE PIECE IS ENDING")
            self.after(0, self.end_of_piece_protocol)
        else:
            if self.preroll.get_time() > 0:
                self.timer_display.config(text=self.preroll.get_formatted_time())
                self.preroll.decrement()
            else:
                self.timer_display.config(text=self.timer.get_formatted_time())
                self.timer.increment()
            self.after(1000, self.update_timer)

    def on_click(self):
        """
        When next button is clicked will remove any text from the central label and set a new image. If in section
        one, will pass silently.
        :return: None
        """
        if self.section_manager.current_section <= 3 or self.section_manager.current_section == 8:
            pass
        else:
            self.label.config(text="")
            self.set_new_image()
        self.resize()

    def on_event(self, event):
        # TODO: Check on event buttons for windows environment
        self.on_click()

    def end_of_piece_protocol(self):
        """
        Organizes the ending of the piece and elegantly ends the main loop.
        :return: None
        """
        end_seconds = 10
        self.timer_display.flash(flashes=end_seconds*4)
        self.after(end_seconds*1000, func=self.root.destroy)

    def update_section(self):
        """
        Logic for updating the section. If this is the first section on boot, will get appropriate time elapsed,
        get the appropriate score cells, and call itself until the end of piece protocol. In further sections
        The next section is loaded, the necessary cells are set and calls update_section through the after
        function on the root.
        :return: None
        """
        if self.first_section:
            duration_of_section = self.section_manager.get_current_section_timing()
            self.section_cells_update()
            self.after(duration_of_section * 1000, func=self.update_section)
            self.section.config(text=self.section_manager.get_current_section_name())
            self.flash_GUI()
            self.first_section = False
        else:
            self.section_manager.next()
            self.section_cells_update()
            if self.section_manager.current_section >= 4 and self.section_manager.current_section <= len(self.section_manager.sections):
                self.on_click()
            if self.section_manager.current_section <= len(self.section_manager.sections):
                duration_of_section = self.section_manager.get_current_section_timing()
                self.section.config(text=self.section_manager.get_current_section_name())
                self.instruction_text.configure(text=self.set_instructions())
                self.next_section_text.configure(text=self.set_next_section_text())
            else:
                duration_of_section = 10
                self.section.config(text="Work Ending")
                self.instruction_text.configure(text="Work Ending")
                self.next_section_text.configure(text="Work Ending")
            self.flash_GUI()
            self.after(duration_of_section*1000, func=self.update_section)


    def flash_GUI(self):
        self.label.flash(flashes=10)
        self.section.flash(flashes=10)
        self.instruction_text.flash(flashes=10)
        self.next_section_text.flash(flashes=10)

    def start_from(self, section_value):
        """
        Helper rehearsal function that sets the starting section of the piece when sections other than the start
        of the piece are selected as the starting point.
        :param section_value: Integer, section of the piece from IntVar in instrument_and_network_settings.py
        :return: None
        """
        timing = self.section_manager.start_from_section(section_value)
        self.timer.set_time(timing)

    def close(self):
        """
        Shorthand to close the whole program.
        :return: None
        """
        self.after(0, func=self.root.destroy)

    def section_two(self):
        pass

    def section_three(self):
        self.label.config(text='### Imitate Electronics ###')

    def section_four(self):
        """
        Updates the cells that are available to the players by removing cells that belong in later sections.
        :return: None
        """
        img_list = ["cell_aggregate_as.png", "cell_aggregate_ecl.png",
                    "cell_first_five_combo_as.png", "cell_first_five_combo_ecl.png",
                    "cell_aggregate_1.png", "cell_aggregate_2.png", "cell_first_five_1.png", "cell_first_five_2.png"]
        directory = image_data_loader.get_path_by_instrument_name(self.root.instrument)
        subtract_this_ca = cell_assigner.CellAssigner(
            image_data_loader.get_these_images(dir=directory, image_list=img_list))
        self.cell_assignment_for_score = self.cell_assignment_for_score - subtract_this_ca

    def section_six(self):
        """
        Updates the cells that are available to the players by removing cells that belong in later sections.
        :return: None
        """
        self.section_four()
        img_list = ["cell_first_five_combo_as.png", "cell_first_five_combo_ecl.png", "cell_first_five_1.png",
                    "cell_first_five_2.png"]
        directory = image_data_loader.get_path_by_instrument_name(self.root.instrument)
        add_this_ca = cell_assigner.CellAssigner(image_data_loader.get_these_images(dir=directory, image_list=img_list))
        self.cell_assignment_for_score = self.cell_assignment_for_score + add_this_ca

    def section_eight(self):
        self.label.config(image='')
        self.label.config(text="### PANIC OR CALMNESS! ###")

    def section_nine(self):
        """
        Adds back in the remaining score cells.
        :return: None
        """
        # self.section_five()
        img_list = ["cell_aggregate_as.png", "cell_aggregate_ecl.png", "cell_aggregate_1.png", "cell_aggregate_2.png"]
        directory = image_data_loader.get_path_by_instrument_name(self.root.instrument)
        add_this_ca = cell_assigner.CellAssigner(
            image_data_loader.get_these_images(dir=directory, image_list=img_list))
        self.cell_assignment_for_score = add_this_ca

    def section_cells_update(self):
        """
        A helper function that executes logical operations based on which section of the piece we are in.
        :return: None
        """
        if self.section_manager.current_section == 3:
            self.section_three()
        elif self.section_manager.current_section == 4:
            self.section_four()
        elif self.section_manager.current_section == 6:
            self.section_six()
        elif self.section_manager.current_section == 8:
            self.section_eight()
        elif self.section_manager.current_section == 9:
            self.section_nine()
        else:
            pass

    def resize(self):
        self.scrollable_frame.resize(fit="fit_all")

    def set_instructions(self):
        string = ""
        string += self.section_manager.get_current_section_instructions()
        return string

    def set_next_section_text(self):
        if self.section_manager.current_section + 1 > len(self.section_manager.sections):
            return "Work Ending"
        else:
            return self.section_manager.sections[self.section_manager.current_section+1][0]

if __name__ == '__main__':

    sections = [("Cosmic", 10),
                ("Element Introduction", 90),
                ("Life Forms", 90),
                ("Emergence of Individuals", 40),
                ("Emergence of collective", 40),
                ("Conflict between collective and individual", 50),
                ("INCISION", 10),
                ("Trancendence: COSMIC RE-FRAMED", 60)]
    sm = SectionManager(sections)
    root = main.Main(sm)
    cells = cell_assigner.CellAssigner(image_data_loader.get_image_paths(dir="cello_cells"))
    gui = ScoreGUI(root, sm, cells)
    gui.state('zoomed')
    root.mainloop()
