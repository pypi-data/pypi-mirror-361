"""
A module for navigating frames, making it easier to place points.
By default, you can zoom with the mouse wheel and pan with Ctrl + left click.
"""

from PyQt5.QtCore import Qt


class MouseNavigationHandler:
    def __init__(self, canvas, ax):
        self.canvas = canvas
        self.ax = ax

        self.scale = 1.0
        self.panning = False
        self.press_event = None

        # Event connections
        self.canvas.mpl_connect('scroll_event', self.zoom)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def zoom(self, event):
        base_scale = 2  # +30% or -30% per scroll
        scale_factor = base_scale if event.button == 'down' else 1 / base_scale
        self.scale *= scale_factor

        if event.xdata is None or event.ydata is None:
            return

        xdata, ydata = event.xdata, event.ydata
        cur_xlim, cur_ylim = self.ax.get_xlim(), self.ax.get_ylim()

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.canvas.draw_idle()

    def on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return
        ctrl = hasattr(event, 'guiEvent') and event.guiEvent.modifiers() & Qt.ControlModifier
        if event.button == 1 and ctrl:
            self.press_event = event
            self.panning = True

    def on_mouse_release(self, event):
        if event.button == 1:
            self.panning = False
            self.press_event = None

    def on_mouse_move(self, event):
        if not self.panning or self.press_event is None or event.inaxes != self.ax:
            return

        dx = event.xdata - self.press_event.xdata
        dy = event.ydata - self.press_event.ydata

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        self.ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
        self.ax.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)

        self.canvas.draw_idle()
        self.press_event = event