import time
import matplotlib
try:
    matplotlib.use("Qt5Agg")
except ImportError:
    pass

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from matplotlib.widgets import Button
from astropy.visualization import (
    ImageNormalize, LinearStretch, LogStretch, SqrtStretch
)

class ApertureSelectorNoMargins:
    """
    Example of an interactive line selector that forces all calculations
    to be in raw image data coordinates with no extra margins. The figure
    is set up so that (0,0) in data coords is at the bottom-left corner
    of the axes, and (nx, ny) is at the top-right, with a 1:1 aspect ratio.
    """

    def __init__(self, image, title="Select Satellite Trail (No Margins)",
                 img_norm='lin', cmap='gray_r'):
        self.image = image
        self.title = title
        self.img_norm = img_norm
        self.cmap = cmap

        # Image shape
        self.ny, self.nx = image.shape

        # Initial geometry: center at image center; default length
        self.cx, self.cy = self.nx / 2, self.ny / 2
        self.length = self.nx / 5.0
        self.theta = 0.0  # angle in degrees from positive x-axis

        # Interaction state
        self.dragging_center = False
        self.dragging_endpoint = False
        self.rotating = False
        self.shift_pressed = False
        self.active_endpoint = None
        self.independent_drag = False
        self.last_x = 0.0
        self.last_y = 0.0
        self.last_motion_event = None
        self.start_theta = 0.0
        self.start_angle = 0.0

        # Endpoint positions (for ctrl-drag)
        self.endpoint1 = None
        self.endpoint2 = None

        # Rate-limit for blitting
        self.last_draw_time = 0.0
        self.redraw_interval = 0.02

        # Background for dynamic axis
        self.dyn_background = None
        self.first_draw_complete = False

        # Visual items
        self.line_artist = None
        self.endpoint_circles = []
        self.center_crosshair_h = None
        self.center_crosshair_v = None
        self.help_annotation = None

        self._setup_figure()

    def _setup_figure(self):
        self.fig = plt.figure(figsize=(8, 8))
        self.fig.suptitle(self.title, fontsize=11)

        # Bottom axis for the image only
        self.ax_img = self.fig.add_axes([0.05, 0.05, 0.65, 0.9])

        # Force the display to match data coordinates exactly
        # extent=(0, nx, 0, ny) => the image goes from x=0..nx, y=0..ny
        vmin = np.nanpercentile(self.image, 1.)
        vmax = np.nanpercentile(self.image, 99.5)
        if self.img_norm == 'lin':
            norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LinearStretch())
        elif self.img_norm == 'log':
            norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch())
        else:
            norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=SqrtStretch())

        self.ax_img.imshow(
            self.image,
            norm=norm,
            cmap=self.cmap,
            origin='lower',
            extent=(0, self.nx, 0, self.ny)
        )
        self.ax_img.set_xlim(0, self.nx)
        self.ax_img.set_ylim(0, self.ny)
        self.ax_img.set_aspect('equal', 'box')  # 1:1 aspect ratio

        # Top axis for dynamic drawing
        self.ax_dyn = self.fig.add_axes([0.05, 0.05, 0.65, 0.9],
                                        sharex=self.ax_img, sharey=self.ax_img)
        self.ax_dyn.set_facecolor("none")
        self.ax_dyn.set_zorder(2)
        self.ax_dyn.set_xticks([])
        self.ax_dyn.set_yticks([])
        for spine in self.ax_dyn.spines.values():
            spine.set_visible(False)

        # Also force no margins and 1:1 aspect here
        self.ax_dyn.set_xlim(0, self.nx)
        self.ax_dyn.set_ylim(0, self.ny)
        self.ax_dyn.set_aspect('equal', 'box')

        # Right axis for help annotation
        self.info_ax = self.fig.add_axes([0.72, 0.05, 0.25, 0.9])
        self.info_ax.axis('off')

        # Help annotation
        self.help_annotation = self.info_ax.annotate(
            "",
            xy=(0, 1),
            xycoords='axes fraction',
            ha='left', va='top',
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.7)
        )

        # Main line
        self.line_artist = Line2D([], [], color='lime', linewidth=2, alpha=0.8, visible=False)
        self.ax_dyn.add_line(self.line_artist)

        # Endpoint circles
        for i in range(2):
            circle = Circle((0, 0), radius=8, facecolor='yellow', edgecolor='black', lw=2, visible=True)
            self.ax_dyn.add_patch(circle)
            self.endpoint_circles.append(circle)

        # Center crosshair
        self.center_crosshair_h = Line2D([], [], color='white', linewidth=2, linestyle='--', visible=True)
        self.center_crosshair_v = Line2D([], [], color='white', linewidth=2, linestyle='--', visible=True)
        self.ax_dyn.add_line(self.center_crosshair_h)
        self.ax_dyn.add_line(self.center_crosshair_v)

        # Connect events
        self.fig.canvas.mpl_connect('draw_event', self.on_draw)
        self.fig.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('key_release_event', self.on_key_release)

    def on_draw(self, event):
        if event.canvas != self.fig.canvas:
            return
        self.ax_dyn.cla()
        self.ax_dyn.set_facecolor("none")
        self.ax_dyn.set_xticks([])
        self.ax_dyn.set_yticks([])
        for spine in self.ax_dyn.spines.values():
            spine.set_visible(False)

        # Keep the forced limits and aspect
        self.ax_dyn.set_xlim(0, self.nx)
        self.ax_dyn.set_ylim(0, self.ny)
        self.ax_dyn.set_aspect('equal', 'box')

        self.dyn_background = self.fig.canvas.copy_from_bbox(self.ax_dyn.bbox)
        self.line_artist.set_visible(True)
        self.first_draw_complete = True

    def on_key_press(self, event):
        if event.key == 'enter':
            plt.close(self.fig)
        elif event.key == 'shift':
            self.shift_pressed = True

    def on_key_release(self, event):
        if event.key == 'shift':
            self.shift_pressed = False
            self.rotating = False

    def on_button_press(self, event):
        if event.inaxes != self.ax_dyn:
            return
        if event.xdata is None or event.ydata is None:
            return

        self.last_x, self.last_y = event.xdata, event.ydata

        if self.shift_pressed:
            self.rotating = True
            self.start_theta = self.theta
            self.start_angle = np.degrees(np.arctan2(event.ydata - self.cy, event.xdata - self.cx))
            return

        ep_idx = self.get_endpoint_index(event.xdata, event.ydata)
        if ep_idx is not None:
            self.dragging_endpoint = True
            self.active_endpoint = ep_idx
            if event.key and ('control' in event.key or 'ctrl' in event.key):
                self.independent_drag = True
                self.endpoint1, self.endpoint2 = self._compute_endpoints()
            else:
                self.independent_drag = False
            return

        if self._inside_center(event.xdata, event.ydata):
            self.dragging_center = True

    def on_button_release(self, event):
        if self.dragging_endpoint and self.independent_drag:
            x1, y1 = self.endpoint1
            x2, y2 = self.endpoint2
            self.cx = (x1 + x2) / 2.0
            self.cy = (y1 + y2) / 2.0
            self.length = np.hypot(x2 - x1, y2 - y1)
            self.theta = np.degrees(np.arctan2(y1 - y2, x1 - x2))
            self.independent_drag = False

        self.dragging_center = False
        self.dragging_endpoint = False
        self.rotating = False
        self.active_endpoint = None

    def on_motion(self, event):
        if event.inaxes != self.ax_dyn:
            return
        if event.xdata is None or event.ydata is None:
            self._blit_draw()
            return

        dx = event.xdata - self.last_x
        dy = event.ydata - self.last_y

        if self.rotating and self.shift_pressed:
            cur_angle = np.degrees(np.arctan2(event.ydata - self.cy, event.xdata - self.cx))
            angle_diff = cur_angle - self.start_angle
            self.theta = (self.start_theta + angle_diff) % 360
        elif self.dragging_endpoint and (self.active_endpoint is not None):
            if not self.independent_drag:
                vx = event.xdata - self.cx
                vy = event.ydata - self.cy
                new_half_length = np.hypot(vx, vy)
                self.length = 2 * new_half_length
                self.theta = np.degrees(np.arctan2(vy, vx))
            else:
                if self.active_endpoint == 0:
                    self.endpoint1 = (event.xdata, event.ydata)
                else:
                    self.endpoint2 = (event.xdata, event.ydata)
        elif self.dragging_center:
            self.cx += dx
            self.cy += dy

        self.last_x = event.xdata
        self.last_y = event.ydata

        now = time.time()
        if (now - self.last_draw_time) < self.redraw_interval:
            return
        self.last_draw_time = now
        self._blit_draw()

    def _blit_draw(self):
        if self.dyn_background is None:
            self.fig.canvas.draw()
            return
        if not plt.fignum_exists(self.fig.number):
            return

        self._update_artists()
        self.fig.canvas.restore_region(self.dyn_background)
        self.ax_dyn.draw_artist(self.line_artist)
        for circle in self.endpoint_circles:
            self.ax_dyn.draw_artist(circle)
        self.ax_dyn.draw_artist(self.center_crosshair_h)
        self.ax_dyn.draw_artist(self.center_crosshair_v)
        self.info_ax.draw_artist(self.help_annotation)
        if plt.fignum_exists(self.fig.number):
            self.fig.canvas.blit(self.ax_dyn.bbox)
            self.fig.canvas.blit(self.info_ax.bbox)

    def _update_artists(self):
        if not self.independent_drag:
            pt1, pt2 = self._compute_endpoints()
        else:
            pt1, pt2 = self.endpoint1, self.endpoint2

        self.line_artist.set_data([pt1[0], pt2[0]], [pt1[1], pt2[1]])
        self.endpoint_circles[0].center = pt1
        self.endpoint_circles[1].center = pt2

        crosshair_size = 10
        self.center_crosshair_h.set_data([self.cx - crosshair_size, self.cx + crosshair_size],
                                         [self.cy, self.cy])
        self.center_crosshair_v.set_data([self.cx, self.cx],
                                         [self.cy - crosshair_size, self.cy + crosshair_size])

        ds9_angle = (90 - self.theta) % 360
        help_text = (
            "Controls:\n"
            " • Drag endpoint: resize symmetrically\n"
            " • Ctrl+Drag endpoint: adjust independently\n"
            " • Drag center: move the line\n"
            " • Shift+Drag: rotate (only while shift is held)\n"
            " • Press Enter: confirm"
        )
        separator = "\n" + "-" * 30 + "\n"
        stats_text = (
            f"Line Status:\n"
            f"  Center = ({self.cx:.1f}, {self.cy:.1f})\n"
            f"  Length = {self.length:.1f}\n"
            f"  Angle  = {self.theta:.1f}° (ds9)\n"
            f"  Angle  = {ds9_angle:.1f}° (ds9)\n"
            f"  Mode   = {self._active_mode_str()}"
        )
        combined = help_text + separator + stats_text
        self.help_annotation.set_text(combined)

    def _active_mode_str(self):
        if self.rotating:
            return "Rotating"
        elif self.dragging_endpoint:
            if self.independent_drag:
                return f"Independent endpoint {self.active_endpoint} drag"
            return f"Symmetric endpoint {self.active_endpoint} drag"
        elif self.dragging_center:
            return "Moving center"
        return "Idle"

    def _compute_endpoints(self):
        theta_rad = np.radians(self.theta)
        dx = (self.length / 2) * np.cos(theta_rad)
        dy = (self.length / 2) * np.sin(theta_rad)
        pt1 = (self.cx + dx, self.cy + dy)
        pt2 = (self.cx - dx, self.cy - dy)
        return pt1, pt2

    def get_endpoint_index(self, gx, gy, threshold=10):
        pt1, pt2 = (self._compute_endpoints() if not self.independent_drag
                    else (self.endpoint1, self.endpoint2))
        d1 = np.hypot(gx - pt1[0], gy - pt1[1])
        d2 = np.hypot(gx - pt2[0], gy - pt2[1])
        if d1 < threshold or d2 < threshold:
            return 0 if d1 < d2 else 1
        return None

    def _inside_center(self, gx, gy, threshold=10):
        return np.hypot(gx - self.cx, gy - self.cy) < threshold

    def show(self):
        self.fig.canvas.draw()
        plt.show()

        ds9_angle = (90 - self.theta) % 360
        return {
            'position': (self.cx, self.cy),
            'width': self.length,
            'height': 100.0,
            'theta': self.theta,
        }


def select_aperture_no_margins(image):
    selector = ApertureSelectorNoMargins(image)
    return selector.show()
# def select_aperture_interactive(image):
#     selector = ApertureSelectorTwoLayer(image, title="Interactive Line Selector")
#     return selector.show()


# --------------------------------------------------------------
def confirm_trail_gui(image, norm_type='sqrt', cmap='gray_r'):
    fig = plt.figure(figsize=(3.5, 3.5))
    manager = plt.get_current_fig_manager()
    if hasattr(manager, 'toolbar'):
        manager.toolbar.hide()

    fig.subplots_adjust(top=0.8, bottom=0.125, left=0.1, right=0.9)
    fig.suptitle("Mark satellite trail in this image?", fontsize=10)

    ax_img = fig.add_axes([0, 0.3, 1, 0.6])
    ax_img.set_xticks([])
    ax_img.set_yticks([])

    vmin = float(np.nanpercentile(image, 1.0))
    vmax = float(np.nanpercentile(image, 99.5))
    if norm_type == 'lin':
        norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LinearStretch())
    elif norm_type == 'log':
        norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch())
    else:
        norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=SqrtStretch())

    ax_img.imshow(image, cmap=cmap, norm=norm, origin='lower')

    yes_ax = fig.add_axes([0.15, 0.1, 0.3, 0.1])
    no_ax = fig.add_axes([0.55, 0.1, 0.3, 0.1])
    btn_yes = Button(yes_ax, "Yes")
    btn_no = Button(no_ax, "No")
    btn_yes.label.set_fontsize(9)
    btn_no.label.set_fontsize(9)

    result = {'answer': None}

    def on_yes(ev):
        result['answer'] = True
        plt.close(fig)

    def on_no(ev):
        result['answer'] = False
        plt.close(fig)

    btn_yes.on_clicked(on_yes)
    btn_no.on_clicked(on_no)
    plt.tight_layout()
    plt.show()
    return result['answer'] if result['answer'] is not None else False


def confirm_trail_and_select_aperture_gui(image):
    has_trail = confirm_trail_gui(image)
    if has_trail:
        return select_aperture_no_margins(image)
        # return select_aperture_interactive(image)
    else:
        return None
