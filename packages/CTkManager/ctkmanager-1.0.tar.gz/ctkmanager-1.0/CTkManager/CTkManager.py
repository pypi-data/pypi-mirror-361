from enum import Enum

import customtkinter as ctk
from PIL import Image


class InvalidTheme(Exception):
    """
    Exception raised when an invalid theme is provided.
    """
    pass


class InvalidSheme(Exception):
    """
    Exception raised when an invalid color scheme is provided.
    """
    pass


class Themes(Enum):
    """
    Enumeration of available color themes for the application.

    Attributes
    ----------
    BLUE : str
        The "blue" theme.
    GREEN : str
        The "green" theme.
    DARK_BLUE : str
        The "dark-blue" theme.
    """
    BLUE = "blue"
    GREEN = "green"
    DARK_BLUE = "dark-blue"


class Schemes(Enum):
    """
    Enumeration of available appearance schemes (light/dark) for the application.

    Attributes
    ----------
    DARK : str
        The dark scheme.
    LIGHT : str
        The light scheme.
    SYSTEM : str
        The system scheme (adapts to operating system settings).
    """
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"


class CTkManager:
    """
    Manages the main CustomTkinter application window.

    Allows configuration of window size, title, resizable property,
    color theme, appearance scheme, and icon.
    Also provides static methods for creating and adding various
    CustomTkinter widgets.

    Attributes
    ----------
    _WIDTH : int
        Default window width in pixels.
    _HEIGHT : int
        Default window height in pixels.
    _TITLE : str
        Default window title.
    _RESIZABLE : bool
        Default setting for window resizability.
    _THEME : str
        Default color theme of the window.
    THEMES : Themes
        Enumeration of available themes.
    SCHEMES : Schemes
        Enumeration of available schemes.
    _COLOR_SCHEME : str
        Default appearance scheme of the window.
    _ICON : str or None
        Path to the window icon file, or None if not set.
    root : ctk.CTk or None
        The main CustomTkinter window object after it is run.
    """

    def __init__(self):
        """
        Initializes the Window object with default settings.
        """
        self._WIDTH = 800
        self._HEIGHT = 600
        self._TITLE = "E-School"
        self._RESIZABLE = False
        self._THEME = "blue"
        self.THEMES = Themes
        self.SCHEMES = Schemes
        self._COLOR_SCHEME = "dark"
        self._ICON = None
        self.root = None

    def run(self):
        """
        Creates and configures the main CustomTkinter window.

        Sets the title, resizable property, size, appearance mode,
        and default color theme. If an icon is set, it is applied to the window.

        Returns
        -------
        ctk.CTk
            The main CustomTkinter window object.
        """
        self.root = ctk.CTk()
        self.root.title(self._TITLE)
        self.root.resizable(self._RESIZABLE, self._RESIZABLE)
        self.root.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        ctk.set_appearance_mode(self._COLOR_SCHEME)
        ctk.set_default_color_theme(self._THEME)

        if self._ICON:
            self.root.iconbitmap(self._ICON)

        return self.root

    def change_title(self, new_title):
        """
        Changes the title of the window.

        Parameters
        ----------
        new_title : str
            The new title for the window.
        """
        self.root.title(new_title)
        self._TITLE = new_title

    @property
    def title(self):
        """
        Gets the current title of the window.

        Returns
        -------
        str
            The current window title.
        """
        return self._TITLE

    def set_width(self, width):
        """
        Sets the width of the window.

        Parameters
        ----------
        width : int
            The new width of the window in pixels.
        """
        self._WIDTH = width

    @property
    def width(self):
        """
        Gets the current width of the window.

        Returns
        -------
        int
            The current window width in pixels.
        """
        return self._WIDTH

    def set_height(self, height):
        """
        Sets the height of the window.

        Parameters
        ----------
        height : int
            The new height of the window in pixels.
        """
        self._HEIGHT = height

    @property
    def height(self):
        """
        Gets the current height of the window.

        Returns
        -------
        int
            The current window height in pixels.
        """
        return self._HEIGHT

    def change_resizable(self, resizable):
        """
        Changes the resizable property of the window.

        Parameters
        ----------
        resizable : bool
            True to allow resizing, False to disallow.
        """
        self._RESIZABLE = resizable
        self.root.resizable(resizable, resizable)

    @property
    def resizable(self):
        """
        Gets the current resizable setting of the window.

        Returns
        -------
        bool
            True if the window is resizable, False otherwise.
        """
        return self._RESIZABLE

    def change_theme(self, theme):
        """
        Changes the color theme of the application.

        Parameters
        ----------
        theme : str
            The theme name ("blue", "green", "dark-blue").

        Raises
        ------
        InvalidTheme
            If the provided theme name is invalid.
        """
        themes = ["blue", "green", "dark-blue"]
        if theme in themes:
            self._THEME = theme
            ctk.set_default_color_theme(theme)
        else:
            raise InvalidTheme("Invalid theme! There is only ('blue', 'green', 'dark-blue')")

    @property
    def theme(self):
        """
        Gets the current color theme.

        Returns
        -------
        str
            The current theme name.
        """
        return self._THEME

    def set_color_scheme(self, scheme):
        """
        Sets the appearance scheme (dark/light/system) of the application.

        Parameters
        ----------
        scheme : str
            The scheme name ("dark", "light", "system").

        Raises
        ------
        InvalidSheme
            If the provided scheme name is invalid.
        """
        color_schemes = ["dark", "light", "system"]
        if scheme in color_schemes:
            self._COLOR_SCHEME = scheme
            ctk.set_appearance_mode(scheme)
        else:
            raise InvalidSheme("Invalid Sheme! There is only ('dark', 'light', 'system')")

    @property
    def color_scheme(self):
        """
        Gets the current appearance scheme.

        Returns
        -------
        str
            The current appearance scheme name.
        """
        return self._COLOR_SCHEME

    def change_icon(self, icon_filename):
        """
        Changes the icon of the window.

        Parameters
        ----------
        icon_filename : str
            The path to the icon file (e.g., .ico).
        """
        self._ICON = icon_filename
        self.root.iconbitmap(self._ICON)

    @property
    def icon(self):
        """
        Gets the path to the currently set window icon.

        Returns
        -------
        str or None
            The path to the icon file, or None if no icon is set.
        """
        return self._ICON

    @staticmethod
    def create_textvariable(text):
        """
        Creates a CustomTkinter StringVar object with an initial text.

        Parameters
        ----------
        text : str
            The initial text for the StringVar.

        Returns
        -------
        ctk.StringVar
            The StringVar object.
        """
        txt_var = ctk.StringVar()
        txt_var.set(text)
        return txt_var

    @staticmethod
    def add_image(image_filename, size=(20, 20)):
        """
        Creates a CTkImage object from the given image file.

        Parameters
        ----------
        image_filename : str
            The path to the image file.
        size : tuple of int, optional
            The size of the image in pixels (width, height). Defaults to (20, 20).

        Returns
        -------
        ctk.CTkImage
            The CTkImage object.
        """
        image = ctk.CTkImage(light_image=Image.open(image_filename), size=size)
        return image

    @staticmethod
    def create_font(family="Arial", size=14, weight="normal", slant="roman"):
        """
        Creates a CTkFont object with the specified attributes.

        Parameters
        ----------
        family : str, optional
            The font family name. Defaults to "Arial".
        size : int, optional
            The font size. Defaults to 14.
        weight : str, optional
            The font weight ("normal", "bold"). Defaults to "normal".
        slant : str, optional
            The font slant ("roman", "italic"). Defaults to "roman".

        Returns
        -------
        ctk.CTkFont
            The CTkFont object.
        """
        return ctk.CTkFont(family=family, size=size, weight=weight, slant=slant)

    @staticmethod
    def add_button(master, width, height, bg, fg, text, corner, command, font=None, **kwargs):
        """
        Creates and packs a CustomTkinter button.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the button will be added.
        width : int
            The width of the button.
        height : int
            The height of the button.
        bg : str
            The background color of the button.
        fg : str
            The foreground (text) color of the button.
        text : str
            The text displayed on the button.
        corner : int
            The corner radius of the button.
        command : callable
            The function to be called when the button is clicked.
        font : ctk.CTkFont, optional
            The font object for the button's text. Defaults to None.
        **kwargs
            Additional keyword arguments passed to the CTkButton constructor.

        Returns
        -------
        ctk.CTkButton
            The created button object.
        """
        button = ctk.CTkButton(master, width=width, height=height, corner_radius=corner, text=text, background=bg,
                               fg_color=fg, command=command, font=font, **kwargs)
        button.pack()
        return button

    @staticmethod
    def add_button_variable(master, width, height, bg, fg, textvariable, corner, command, font=None, **kwargs):
        """
        Creates and packs a CustomTkinter button with a variable text.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the button will be added.
        width : int
            The width of the button.
        height : int
            The height of the button.
        bg : str
            The background color of the button.
        fg : str
            The foreground (text) color of the button.
        textvariable : ctk.StringVar
            The StringVar object containing the text to be displayed.
        corner : int
            The corner radius of the button.
        command : callable
            The function to be called when the button is clicked.
        font : ctk.CTkFont, optional
            The font object for the button's text. Defaults to None.
        **kwargs
            Additional keyword arguments passed to the CTkButton constructor.

        Returns
        -------
        ctk.CTkButton
            The created button object.
        """
        button = ctk.CTkButton(master, width=width, height=height, corner_radius=corner, textvariable=textvariable,
                               background=bg,
                               fg_color=fg, command=command, font=font, **kwargs)
        button.pack()
        return button

    @staticmethod
    def add_panel(master, width, height, corner, bg, fg, side):
        """
        Creates and packs a CustomTkinter panel (frame).

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the panel will be added.
        width : int
            The width of the panel.
        height : int
            The height of the panel.
        corner : int
            The corner radius of the panel.
        bg : str
            The background color of the panel.
        fg : str
            The foreground (frame) color of the panel.
        side : str
            The side to which the panel will be packed (e.g., "top", "left").

        Returns
        -------
        ctk.CTkFrame
            The created panel object.
        """
        panel = ctk.CTkFrame(master, width=width, height=height, corner_radius=corner, bg_color=bg, fg_color=fg)
        panel.pack(side=side)
        return panel

    @staticmethod
    def add_text(master, width, height, textvariable, bg, fg, font=None, **kwargs):
        """
        Creates and packs a CustomTkinter label with variable text.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the label will be added.
        width : int
            The width of the label.
        height : int
            The height of the label.
        textvariable : ctk.StringVar
            The StringVar object containing the text to be displayed.
        bg : str
            The background color of the label.
        fg : str
            The foreground (text) color of the label.
        font : ctk.CTkFont, optional
            The font object for the label's text. Defaults to None.
        **kwargs
            Additional keyword arguments passed to the CTkLabel constructor.

        Returns
        -------
        ctk.CTkLabel
            The created label object.
        """
        label = ctk.CTkLabel(master, width=width, height=height, bg_color=bg, fg_color=fg, textvariable=textvariable,
                             font=font, **kwargs)
        label.pack()
        return label

    @staticmethod
    def add_scrollableFrame(master, width, height, corner, bg, fg, side):
        """
        Creates and packs a CustomTkinter scrollable frame.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the frame will be added.
        width : int
            The width of the frame.
        height : int
            The height of the frame.
        corner : int
            The corner radius of the frame.
        bg : str
            The background color of the frame.
        fg : str
            The foreground (frame) color of the frame.
        side : str
            The side to which the frame will be packed (e.g., "top", "left").

        Returns
        -------
        ctk.CTkScrollableFrame
            The created scrollable frame object.
        """
        scrollable = ctk.CTkScrollableFrame(master, width=width, height=height, corner_radius=corner, bg_color=bg,
                                            fg_color=fg)
        scrollable.pack(side=side)
        return scrollable

    @staticmethod
    def add_entry(master, width, height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter entry field.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the entry field will be added.
        width : int
            The width of the entry field.
        height : int
            The height of the entry field.
        corner : int
            The corner radius of the entry field.
        bg : str
            The background color of the entry field.
        fg : str
            The foreground (border) color of the entry field.
        font : ctk.CTkFont, optional
            The font object for the text in the entry field. Defaults to None.

        Returns
        -------
        ctk.CTkEntry
            The created entry field object.
        """
        entry = ctk.CTkEntry(master, width=width, height=height, corner_radius=corner, bg_color=bg, fg_color=fg,
                             font=font)
        entry.pack()
        return entry

    @staticmethod
    def add_textbox(master, width, height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter multi-line textbox.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the textbox will be added.
        width : int
            The width of the textbox.
        height : int
            The height of the textbox.
        corner : int
            The corner radius of the textbox.
        bg : str
            The background color of the textbox.
        fg : str
            The foreground (border) color of the textbox.
        font : ctk.CTkFont, optional
            The font object for the text in the textbox. Defaults to None.

        Returns
        -------
        ctk.CTkTextbox
            The created textbox object.
        """
        textbox = ctk.CTkTextbox(master, width=width, height=height, corner_radius=corner, bg_color=bg, fg_color=fg,
                                 font=font)
        textbox.pack()
        return textbox

    @staticmethod
    def add_checkbox(master, width, height, checkbox_width, checkbox_height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter checkbox.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the checkbox will be added.
        width : int
            The width of the entire checkbox widget.
        height : int
            The height of the entire checkbox widget.
        checkbox_width : int
            The width of the checkbox square itself.
        checkbox_height : int
            The height of the checkbox square itself.
        corner : int
            The corner radius of the checkbox.
        bg : str
            The background color of the checkbox.
        fg : str
            The foreground (border) color of the checkbox.
        font : ctk.CTkFont, optional
            The font object for the checkbox text. Defaults to None.

        Returns
        -------
        ctk.CTkCheckBox
            The created checkbox object.
        """
        checkbox = ctk.CTkCheckBox(master, width=width, height=height, checkbox_width=checkbox_width,
                                   checkbox_height=checkbox_height, corner_radius=corner, bg_color=bg,
                                   fg_color=fg, font=font)
        checkbox.pack()
        return checkbox

    @staticmethod
    def add_radiobutton(master, width, height, radiobutton_width, radiobutton_height, corner, bg, fg):
        """
        Creates and packs a CustomTkinter radio button.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the radio button will be added.
        width : int
            The width of the entire radio button widget.
        height : int
            The height of the entire radio button widget.
        radiobutton_width : int
            The width of the radio button circle itself.
        radiobutton_height : int
            The height of the radio button circle itself.
        corner : int
            The corner radius of the radio button.
        bg : str
            The background color of the radio button.
        fg : str
            The foreground (border) color of the radio button.

        Returns
        -------
        ctk.CTkRadioButton
            The created radio button object.
        """
        radiobutton = ctk.CTkRadioButton(master, width=width, height=height, radiobutton_width=radiobutton_width,
                                         radiobutton_height=radiobutton_height, corner_radius=corner, bg_color=bg,
                                         fg_color=fg)
        radiobutton.pack()
        return radiobutton

    @staticmethod
    def add_switch(master, width, height, switch_width, switch_height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter switch.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the switch will be added.
        width : int
            The width of the entire switch widget.
        height : int
            The height of the entire switch widget.
        switch_width : int
            The width of the switch slider itself.
        switch_height : int
            The height of the switch slider itself.
        corner : int
            The corner radius of the switch.
        bg : str
            The background color of the switch.
        fg : str
            The foreground (border) color of the switch.
        font : ctk.CTkFont, optional
            The font object for the switch text. Defaults to None.

        Returns
        -------
        ctk.CTkSwitch
            The created switch object.
        """
        switch = ctk.CTkSwitch(master, width=width, height=height, switch_width=switch_width,
                               switch_height=switch_height, corner_radius=corner, bg_color=bg, fg_color=fg, font=font)
        switch.pack()
        return switch

    @staticmethod
    def add_optionmenu(master, width, height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter option menu (dropdown).

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the option menu will be added.
        width : int
            The width of the option menu.
        height : int
            The height of the option menu.
        corner : int
            The corner radius of the option menu.
        bg : str
            The background color of the option menu.
        fg : str
            The foreground (border) color of the option menu.
        font : ctk.CTkFont, optional
            The font object for the text in the option menu. Defaults to None.

        Returns
        -------
        ctk.CTkOptionMenu
            The created option menu object.
        """
        optionmenu = ctk.CTkOptionMenu(master, width=width, height=height, corner_radius=corner, bg_color=bg,
                                       fg_color=fg, font=font)
        optionmenu.pack()
        return optionmenu

    @staticmethod
    def add_combobox(master, width, height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter combobox.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the combobox will be added.
        width : int
            The width of the combobox.
        height : int
            The height of the combobox.
        corner : int
            The corner radius of the combobox.
        bg : str
            The background color of the combobox.
        fg : str
            The foreground (border) color of the combobox.
        font : ctk.CTkFont, optional
            The font object for the text in the combobox. Defaults to None.

        Returns
        -------
        ctk.CTkComboBox
            The created combobox object.
        """
        combobox = ctk.CTkComboBox(master, width=width, height=height, corner_radius=corner, bg_color=bg, fg_color=fg,
                                   font=font)
        combobox.pack()
        return combobox

    @staticmethod
    def add_slider(master, width, height, corner, bg, fg, _from, to):
        """
        Creates and packs a CustomTkinter slider.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the slider will be added.
        width : int
            The width of the slider.
        height : int
            The height of the slider.
        corner : int
            The corner radius of the slider.
        bg : str
            The background color of the slider.
        fg : str
            The foreground (slider) color of the slider.
        _from : float or int
            The starting value of the slider's range.
        to : float or int
            The ending value of the slider's range.

        Returns
        -------
        ctk.CTkSlider
            The created slider object.
        """
        slider = ctk.CTkSlider(master, width=width, height=height, corner_radius=corner, bg_color=bg, fg_color=fg,
                               _from=_from, to=to)
        slider.pack()
        return slider

    @staticmethod
    def add_progress_bar(master, width, height, corner, bg, fg):
        """
        Creates and packs a CustomTkinter progress bar.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the progress bar will be added.
        width : int
            The width of the progress bar.
        height : int
            The height of the progress bar.
        corner : int
            The corner radius of the progress bar.
        bg : str
            The background color of the progress bar.
        fg : str
            The foreground (bar) color of the progress bar.

        Returns
        -------
        ctk.CTkProgressBar
            The created progress bar object.
        """
        progressbar = ctk.CTkProgressBar(master, width=width, height=height, corner_radius=corner, bg_color=bg,
                                         fg_color=fg)
        progressbar.pack()
        return progressbar

    @staticmethod
    def add_segmentedbutton(master, width, height, corner, bg, fg, font=None):
        """
        Creates and packs a CustomTkinter segmented button.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the segmented button will be added.
        width : int
            The width of the segmented button.
        height : int
            The height of the segmented button.
        corner : int
            The corner radius of the segmented button.
        bg : str
            The background color of the segmented button.
        fg : str
            The foreground (border) color of the segmented button.
        font : ctk.CTkFont, optional
            The font object for the text in the segmented button. Defaults to None.

        Returns
        -------
        ctk.CTkSegmentedButton
            The created segmented button object.
        """
        segmentedbutton = ctk.CTkSegmentedButton(master, width=width, height=height, corner_radius=corner, bg_color=bg,
                                                 fg_color=fg, font=font)
        segmentedbutton.pack()
        return segmentedbutton

    @staticmethod
    def add_tabview(master, width, height, corner, bg, fg):
        """
        Creates and packs a CustomTkinter tabview.

        Parameters
        ----------
        master : ctk.CTk or ctk.CTkFrame
            The parent widget to which the tabview will be added.
        width : int
            The width of the tabview.
        height : int
            The height of the tabview.
        corner : int
            The corner radius of the tabview.
        bg : str
            The background color of the tabview.
        fg : str
            The foreground (border) color of the tabview.

        Returns
        -------
        ctk.CTkTabview
            The created tabview object.
        """
        tabview = ctk.CTkTabview(master, width=width, height=height, corner_radius=corner, bg_color=bg, fg_color=fg)
        tabview.pack()
        return tabview