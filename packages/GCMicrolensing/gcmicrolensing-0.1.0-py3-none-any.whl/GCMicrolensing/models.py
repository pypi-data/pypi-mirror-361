"""High level models for simulating microlensing events.

This module provides simple classes for single-, double-, and triple-lens
microlensing scenarios.  The focus is on producing light curves, centroid
shifts and animated visualisations for teaching or exploratory analyses.

The implementations rely heavily on the `VBMicrolensing` and
`TripleLensing` packages for the low level calculations of image positions
and magnifications.
"""

import math

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import VBMicrolensing
from IPython.display import HTML
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from .TestML import get_allimgs_with_mu, get_crit_caus, getphis_v3, testing
from .triplelens import TripleLensing


class OneL1S:
    """Simple single-lens single-source (1L1S) model.

    Parameters
    ----------
    t0 : float
        Time of closest approach.
    tE : float
        Einstein crossing time.
    rho : float
        Source size in units of the Einstein radius.
    u0_list : list of float
        Impact parameters to evaluate.

    Examples
    --------
    >>> model = OneL1S(t0=0.0, tE=20.0, rho=0.01, u0_list=[0.1])
    >>> model.plot_light_curve()
    """

    def __init__(self, t0, tE, rho, u0_list):

        self.t0 = t0
        self.tE = tE
        self.t = np.linspace(t0 - tE, t0 + tE, 50)
        self.rho = rho
        self.u0_list = u0_list
        self.tau = (self.t - t0) / tE

        self.VBM = VBMicrolensing.VBMicrolensing()
        self.VBM.RelTol = 1e-3
        self.VBM.Tol = 1e-3
        self.VBM.astrometry = True

    def plot_light_curve_on_ax(self, ax):
        """Plot magnification curve on an existing axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis instance to plot on.
        """
        cmap_es = plt.colormaps["BuPu"]
        colors_es = [cmap_es(i) for i in np.linspace(0.5, 1.0, len(self.u0_list))]
        cmap_ps = plt.colormaps["binary"]
        colors_ps = [cmap_ps(i) for i in np.linspace(0.5, 1.0, len(self.u0_list))]

        for idx, u0 in enumerate(self.u0_list):
            color_es = colors_es[idx]
            color_ps = colors_ps[idx]
            u = np.sqrt(u0**2 + self.tau**2)
            pspl_mag = [self.VBM.PSPLMag(ui) for ui in u]
            espl_mag = [self.VBM.ESPLMag2(ui, self.rho) for ui in u]

            ax.plot(self.tau, espl_mag, "-", color=color_es, label=f"ESPL $u_0$ = {u0}")
            ax.plot(
                self.tau,
                pspl_mag,
                "--",
                color=color_ps,
                label=f"PSPL $u_0$ = {u0}",
                alpha=0.7,
            )

        ax.set_xlabel(r"Time ($\tau$)")
        ax.set_ylabel("Magnification")
        ax.set_title("Single-Lens Magnification")
        ax.grid(True)
        ax.legend()

    def plot_centroid_shift_on_ax(self, ax):
        """Plot centroid shift versus time on ``ax``.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis to draw the centroid shift curve on.
        """
        cmap_cs = plt.colormaps["BuPu"]
        colors_cs = [cmap_cs(i) for i in np.linspace(0.5, 1.0, len(self.u0_list))]

        for idx, u0 in enumerate(self.u0_list):
            color_cs = colors_cs[idx]
            u = np.sqrt(u0**2 + self.tau**2)
            centroid_shift = [self.VBM.astrox1 - ui for ui in u]
            ax.plot(self.tau, centroid_shift, color=color_cs, label=f"$u_0$ = {u0}")

        ax.set_xlabel(r"Time ($\tau$)")
        ax.set_ylabel(r"Centroid Shift ($\Delta \theta$)")
        ax.set_title("Astrometric Centroid Shift")
        ax.grid(True)
        ax.legend()

    def plot_light_curve(self):
        """Display the light curve in a new figure."""
        fig, ax = plt.subplots(figsize=(8, 4))
        self.plot_light_curve_on_ax(ax)
        plt.show()

    def plot_centroid_shift(self):
        """Display the centroid shift curve in a new figure."""
        fig, ax = plt.subplots(figsize=(8, 4))
        self.plot_centroid_shift_on_ax(ax)
        plt.show()

    def animate(self):
        """Return a HTML animation of the event."""
        return self._create_animation(figsize=(6, 6), layout="single")

    def show_all(self):
        """Return an animation with light curve and centroid shift."""
        return self._create_animation(figsize=(14, 6), layout="grid")

    def _create_animation(self, figsize=(6, 6), layout="single"):
        """Construct an animation of the microlensing event.

        Parameters
        ----------
        figsize : tuple of float, optional
            Size of the matplotlib figure in inches. Defaults to ``(6, 6)``.
        layout : {{'single', 'grid'}}, optional
            ``'grid'`` will also display the light curve and centroid shift
            during the animation. Defaults to ``'single'``.

        Returns
        -------
        IPython.display.HTML
            HTML representation of the animation for use in notebooks.
        """
        tau = self.tau
        n = len(self.t)
        colors = [plt.colormaps["BuPu"](i) for i in np.linspace(0.5, 1.0, len(self.u0_list))]

        systems = []
        for u0, color in zip(self.u0_list, colors):
            x_source = tau
            y_source = np.full_like(tau, u0)
            u = np.sqrt(x_source**2 + y_source**2)
            espl_mag = [self.VBM.ESPLMag2(ui, self.rho) for ui in u]
            systems.append(
                {
                    "u0": u0,
                    "x": x_source,
                    "y": y_source,
                    "mag": espl_mag,
                    "color": color,
                }
            )

        if layout == "grid":
            fig = plt.figure(figsize=figsize)
            gs = GridSpec(2, 2, width_ratios=[1, 1])
            ax_anim = fig.add_subplot(gs[:, 0])
            ax_light = fig.add_subplot(gs[0, 1])
            ax_centroid = fig.add_subplot(gs[1, 1])
            self.plot_light_curve_on_ax(ax_light)
            self.plot_centroid_shift_on_ax(ax_centroid)
        else:
            fig, ax_anim = plt.subplots(figsize=figsize)

        ax_anim.set_xlim(-2, 2)
        ax_anim.set_ylim(-2, 2)
        ax_anim.set_xlabel(r"X ($\theta_E$)")
        ax_anim.set_ylabel(r"Y ($\theta_E$)")
        ax_anim.set_title("Single-Lens Microlensing Events")
        ax_anim.grid(True)
        ax_anim.set_aspect("equal")
        ax_anim.plot([0], [0], "ko", label="Lens")
        einstein_ring = plt.Circle(
            (0, 0), 1, color="green", fill=False, linestyle="--", linewidth=1.5
        )
        ax_anim.add_patch(einstein_ring)

        source_dots, img_dots, trails_1, trails_2, trail_data = [], [], [], [], []

        for system in systems:
            (s_dot,) = ax_anim.plot(
                [], [], "*", color=system["color"], label=f"$u_0$ = {system['u0']}"
            )
            i_dot = ax_anim.scatter([], [], color=system["color"], s=20)
            t1 = ax_anim.scatter([], [], color=system["color"], alpha=0.3)
            t2 = ax_anim.scatter([], [], color=system["color"], alpha=0.3)
            source_dots.append(s_dot)
            img_dots.append(i_dot)
            trails_1.append(t1)
            trails_2.append(t2)
            trail_data.append({"x1": [], "y1": [], "s1": [], "x2": [], "y2": [], "s2": []})

        ax_anim.legend(loc="lower left")

        def update(frame):
            for i, system in enumerate(systems):
                x_s = system["x"][frame]
                y_s = system["y"][frame]
                u = np.sqrt(x_s**2 + y_s**2)
                theta = np.arctan2(y_s, x_s)
                r_plus = (u + np.sqrt(u**2 + 4)) / 2
                r_minus = (u - np.sqrt(u**2 + 4)) / 2

                x1 = r_plus * np.cos(theta)
                y1 = r_plus * np.sin(theta)
                x2 = r_minus * np.cos(theta)
                y2 = r_minus * np.sin(theta)

                source_dots[i].set_data([x_s], [y_s])
                img_dots[i].set_offsets([[x1, y1], [x2, y2]])
                mag = system["mag"][frame]
                size = 20 * mag
                img_dots[i].set_sizes([size, size])

                trail_data[i]["x1"].append(x1)
                trail_data[i]["y1"].append(y1)
                trail_data[i]["s1"].append(size)
                trail_data[i]["x2"].append(x2)
                trail_data[i]["y2"].append(y2)
                trail_data[i]["s2"].append(size)

                trails_1[i].set_offsets(np.column_stack([trail_data[i]["x1"], trail_data[i]["y1"]]))
                trails_1[i].set_sizes(trail_data[i]["s1"])
                trails_2[i].set_offsets(np.column_stack([trail_data[i]["x2"], trail_data[i]["y2"]]))
                trails_2[i].set_sizes(trail_data[i]["s2"])

            return source_dots + img_dots + trails_1 + trails_2

        ani = animation.FuncAnimation(fig, update, frames=n, interval=50, blit=True)
        plt.tight_layout()
        return HTML(ani.to_jshtml())


class TwoLens1S:
    """Binary-lens, single-source (2L1S) model.

    Examples
    --------
    >>> model = TwoLens1S(t0=0.0, tE=20.0, rho=0.01,
    ...                  u0_list=[0.1], q=0.1, s=1.5, alpha=45)
    >>> model.plot_light_curve()
    """

    def __init__(self, t0, tE, rho, u0_list, q, s, alpha):
        """Create a binary-lens system.

        Parameters
        ----------
        t0 : float
            Time of closest approach.
        tE : float
            Einstein crossing time.
        rho : float
            Source radius in units of the Einstein radius.
        u0_list : list of float
            Impact parameters of the source trajectory.
        q : float
            Lens mass ratio ``m2/m1``.
        s : float
            Separation between the lenses in Einstein radii.
        alpha : float
            Angle of the source trajectory in degrees.
        """
        self.t0 = t0
        self.tE = tE
        self.rho = rho
        self.u0_list = u0_list
        self.q = q
        self.s = s
        self.alpha = alpha
        self.tau = np.linspace(-4, 4, 100)
        self.t = self.t0 + self.tau * self.tE
        self.theta = np.radians(self.alpha)

        self.tau_hr = np.linspace(-4, 4, 1000)
        self.t_hr = self.t0 + self.tau_hr * self.tE

        self.VBM = VBMicrolensing.VBMicrolensing()
        self.VBM.RelTol = 1e-3
        self.VBM.Tol = 1e-3
        self.VBM.astrometry = True
        self.colors = [plt.colormaps["BuPu"](i) for i in np.linspace(1.0, 0.4, len(u0_list))]
        self.systems = self._prepare_systems()

    def _prepare_systems(self):
        """Precompute source trajectories and magnifications."""
        systems = []

        def polygon_area(x, y):
            return 0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

        for u0, color in zip(self.u0_list, self.colors):
            x_src = self.tau * np.cos(self.theta) - u0 * np.sin(
                self.theta
            )  # for animation (lower resolution)
            y_src = self.tau * np.sin(self.theta) + u0 * np.cos(self.theta)

            cent_x = []
            cent_y = []

            for x_s, y_s in zip(x_src, y_src):
                images = self.VBM.ImageContours(self.s, self.q, x_s, y_s, self.rho)

                image_fluxes = []
                image_cx = []
                image_cy = []

                for img in images:
                    x = np.array(img[0])
                    y = np.array(img[1])
                    flux = polygon_area(x, y)

                    if flux > 0:
                        cx = np.mean(x)
                        cy = np.mean(y)
                        image_fluxes.append(flux)
                        image_cx.append(cx)
                        image_cy.append(cy)

                total_flux = np.sum(image_fluxes)

                if total_flux > 0:
                    cx_weighted = np.sum(np.array(image_cx) * image_fluxes) / total_flux
                    cy_weighted = np.sum(np.array(image_cy) * image_fluxes) / total_flux
                else:
                    cx_weighted = np.nan
                    cy_weighted = np.nan

                cent_x.append(cx_weighted)
                cent_y.append(cy_weighted)

            x_src_hr = self.tau_hr * np.cos(self.theta) - u0 * np.sin(
                self.theta
            )  # for centroid shift, higher resolution
            y_src_hr = self.tau_hr * np.sin(self.theta) + u0 * np.cos(self.theta)

            cent_x_hr = []
            cent_y_hr = []

            for x_s, y_s in zip(x_src_hr, y_src_hr):
                images = self.VBM.ImageContours(self.s, self.q, x_s, y_s, self.rho)

                image_fluxes, image_cx, image_cy = [], [], []

                for img in images:
                    x = np.array(img[0])
                    y = np.array(img[1])
                    flux = polygon_area(x, y)

                    if flux > 0:
                        cx = np.mean(x)
                        cy = np.mean(y)
                        image_fluxes.append(flux)
                        image_cx.append(cx)
                        image_cy.append(cy)

                total_flux = np.sum(image_fluxes)

                if total_flux > 0:
                    cx_weighted = np.sum(np.array(image_cx) * image_fluxes) / total_flux
                    cy_weighted = np.sum(np.array(image_cy) * image_fluxes) / total_flux
                else:
                    cx_weighted = np.nan
                    cy_weighted = np.nan

                cent_x_hr.append(cx_weighted)
                cent_y_hr.append(cy_weighted)

            mag, *_ = self.VBM.BinaryLightCurve(
                [
                    math.log(self.s),
                    math.log(self.q),
                    u0,
                    self.theta,
                    math.log(self.rho),
                    math.log(self.tE),
                    self.t0,
                ],
                self.t,
            )

            systems.append(
                {
                    "u0": u0,
                    "color": color,
                    "mag": mag,
                    "x_src": x_src,
                    "y_src": y_src,
                    "cent_x": np.array(cent_x),
                    "cent_y": np.array(cent_y),
                    "x_src_hr": x_src_hr,
                    "y_src_hr": y_src_hr,
                    "cent_x_hr": np.array(cent_x_hr),
                    "cent_y_hr": np.array(cent_y_hr),
                }
            )

        return systems

    def plot_caustic_critical_curves(self):
        """Plot caustics and critical curves for the binary lens."""
        caustics = self.VBM.Caustics(self.s, self.q)
        criticalcurves = self.VBM.Criticalcurves(self.s, self.q)

        lens_handle = Line2D(
            [0],
            [0],
            marker="o",
            color="k",
            linestyle="None",
            label="Lens",
            markersize=6,
        )
        caustic_handle = Line2D([0], [0], color="r", lw=1.2, label="Caustic")
        crit_curve_handle = Line2D(
            [0], [0], color="k", linestyle="--", lw=0.8, label="Critical Curve"
        )
        q_handle = Line2D([0], [0], color="k", linestyle="None", label=rf"$q$ = {self.q}")
        s_handle = Line2D([0], [0], color="k", linestyle="None", label=rf"$s$ = {self.s}")

        plt.figure(figsize=(6, 6))

        for cau in caustics:
            plt.plot(cau[0], cau[1], "r", lw=1.2)
        for crit in criticalcurves:
            plt.plot(crit[0], crit[1], "k--", lw=0.8)

        x1 = -self.s * self.q / (1 + self.q)
        x2 = self.s / (1 + self.q)
        plt.plot([x1, x2], [0, 0], "ko")

        for system in self.systems:
            plt.plot(system["x_src"], system["y_src"], "--", color=system["color"], alpha=0.6)

        plt.xlim(-2, 2)
        plt.ylim(-2, 2)
        plt.xlabel(r"$\theta_x$ ($\theta_E$)")
        plt.ylabel(r"$\theta_y$ ($\theta_E$)")
        plt.title("2L1S Lensing Event")
        plt.gca().set_aspect("equal")
        plt.grid(True)
        plt.legend(
            handles=[
                lens_handle,
                caustic_handle,
                crit_curve_handle,
                q_handle,
                s_handle,
            ],
            loc="upper right",
            prop={"size": 8},
        )
        plt.tight_layout()
        plt.show()

    def plot_light_curve(self):
        """Plot the binary-lens light curve."""
        plt.figure(figsize=(6, 4))

        for system in self.systems:
            plt.plot(
                self.tau,
                system["mag"],
                color=system["color"],
                label=rf"$u_0$ = {system['u0']}",
            )

        plt.xlabel(r"Time ($\tau$)")
        plt.ylabel("Magnification")
        plt.title("Light Curve")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def animate(self):
        """Return an animation showing the event evolution.

        Returns
        -------
        IPython.display.HTML
            HTML representation of the animation for use in notebooks.
        """
        caustics = self.VBM.Caustics(self.s, self.q)
        criticalcurves = self.VBM.Criticalcurves(self.s, self.q)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        fig.subplots_adjust(wspace=0.4)

        lens_handle = Line2D(
            [0],
            [0],
            marker="o",
            color="k",
            linestyle="None",
            label="Lens",
            markersize=6,
        )
        caustic_handle = Line2D([0], [0], color="r", lw=1.2, label="Caustic")
        crit_curve_handle = Line2D(
            [0], [0], color="k", linestyle="--", lw=0.8, label="Critical Curve"
        )
        q_handle = Line2D([0], [0], color="k", linestyle="None", label=rf"$q$ = {self.q}")
        s_handle = Line2D([0], [0], color="k", linestyle="None", label=rf"$s$ = {self.s}")

        ax1.set_xlim(-2, 2)
        ax1.set_ylim(-2, 2)
        ax1.set_xlabel(r"$\theta_x$ ($\theta_E$)")
        ax1.set_ylabel(r"$\theta_y$ ($\theta_E$)")
        ax1.set_title("2L1S Microlensing Event")
        ax1.set_aspect("equal")
        ax1.grid(True)

        for cau in caustics:
            ax1.plot(cau[0], cau[1], "r", lw=1.2)
        for crit in criticalcurves:
            ax1.plot(crit[0], crit[1], "k--", lw=0.8)

        ax1.plot([-self.s * self.q / (1 + self.q), self.s / (1 + self.q)], [0, 0], "ko")

        ax1.legend(
            handles=[
                lens_handle,
                caustic_handle,
                crit_curve_handle,
                q_handle,
                s_handle,
            ],
            loc="upper right",
            prop={"size": 8},
        )

        source_dots = []
        for system in self.systems:
            ax1.plot(system["x_src"], system["y_src"], "--", color=system["color"], alpha=0.4)
            (src_dot,) = ax1.plot([], [], "*", color=system["color"], markersize=10)
            # cen_dot, = ax1.plot(
            #     [], [], 'x', color=system['color'], markersize=6,
            #     label=f"$u_0$ = {system['u0']}"
            # )
            source_dots.append(src_dot)
            # centroid_dots.append(cen_dot)
        ax1.legend(loc="lower right")

        ax2.set_xlim(self.tau[0], self.tau[-1])
        all_mag = np.concatenate([s["mag"] for s in self.systems])
        ax2.set_ylim(min(all_mag) * 0.95, max(all_mag) * 1.05)
        ax2.set_xlabel(r"Time ($\tau$)")
        ax2.set_ylabel("Magnification")
        ax2.set_title("Light Curve")

        tracer_dots = []
        for system in self.systems:
            ax2.plot(
                self.tau,
                system["mag"],
                color=system["color"],
                label=f"$u_0$ = {system['u0']}",
            )
            (dot,) = ax2.plot([], [], "o", color=system["color"], markersize=6)
            tracer_dots.append(dot)
        ax2.legend()

        image_dots = []
        for system in self.systems:
            system_dots = []
            for _ in range(5):
                (img_dot,) = ax1.plot([], [], ".", color=system["color"], alpha=0.6, markersize=4)
                system_dots.append(img_dot)
            image_dots.append(system_dots)

        def update(i):
            artists = []
            for j, system in enumerate(self.systems):
                x_src = system["x_src"][i]
                y_src = system["y_src"][i]

                source_dots[j].set_data([x_src], [y_src])
                tracer_dots[j].set_data([self.tau[i]], [system["mag"][i]])
                artists.extend([source_dots[j], tracer_dots[j]])

                images = self.VBM.ImageContours(self.s, self.q, x_s, y_s, self.rho)

                for k, img_dot in enumerate(image_dots[j]):
                    if k < len(images):
                        img_dot.set_data(images[k][0], images[k][1])
                        img_dot.set_alpha(0.6)
                    else:
                        img_dot.set_data([], [])
                        img_dot.set_alpha(0)
                    artists.append(img_dot)

            return artists

        ani = animation.FuncAnimation(fig, update, frames=len(self.t), interval=50, blit=True)
        plt.close(fig)
        return HTML(ani.to_jshtml())

    def plot_centroid_trajectory(self):
        """Plot the centroid trajectory for each ``u0`` value."""
        plt.figure(figsize=(6, 6))
        for system in self.systems:
            delta_x = system["cent_x_hr"] - system["x_src_hr"]
            delta_y = system["cent_y_hr"] - system["y_src_hr"]
            plt.plot(
                delta_x,
                delta_y,
                color=system["color"],
                label=rf"$u_0$ = {system['u0']}",
            )
        plt.xlim(-0.4, 0.8)
        plt.ylim(-0.4, 0.5)
        plt.xlabel(r"$\delta \Theta_1$")
        plt.ylabel(r"$\delta \Theta_2$")
        plt.gca().set_aspect("equal")
        plt.title("Centroid Trajectory")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_centroid_shift(self):
        """Plot the centroid shift amplitude over time."""
        plt.figure(figsize=(6, 4))
        for system in self.systems:
            delta_x = system["cent_x_hr"] - system["x_src_hr"]
            delta_y = system["cent_y_hr"] - system["y_src_hr"]
            delta_theta = np.sqrt(delta_x**2 + delta_y**2)
            plt.plot(
                self.tau_hr,
                delta_theta,
                color=system["color"],
                label=rf"$u_0$ = {system['u0']}",
            )

        plt.xlabel(r"Time ($\tau$)")
        plt.ylabel(r"$|\delta \vec{\Theta}|$")
        plt.title(r"Centroid Shift over Time ($\tau$)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_all(self):
        """Display a grid of animations and plots."""
        fig = plt.figure(figsize=(9, 9), constrained_layout=True)
        gs = GridSpec(2, 2, figure=fig)

        # --- Top Left: Lensing Animation ---
        ax1 = fig.add_subplot(gs[0, 0])
        caustics = self.VBM.Caustics(self.s, self.q)
        criticalcurves = self.VBM.Criticalcurves(self.s, self.q)

        lens_handle = Line2D(
            [0],
            [0],
            marker="o",
            color="k",
            linestyle="None",
            label="Lens",
            markersize=6,
        )
        caustic_handle = Line2D([0], [0], color="r", lw=1.2, label="Caustic")
        crit_curve_handle = Line2D(
            [0], [0], color="k", linestyle="--", lw=0.8, label="Critical Curve"
        )
        q_handle = Line2D([0], [0], color="k", linestyle="None", label=rf"$q$ = {self.q}")
        s_handle = Line2D([0], [0], color="k", linestyle="None", label=rf"$s$ = {self.s}")

        ax1.set_xlim(-2, 2)
        ax1.set_ylim(-2, 2)
        ax1.set_aspect("equal")
        ax1.grid(True)
        ax1.set_title("2L1S Lensing Event")
        for cau in caustics:
            ax1.plot(cau[0], cau[1], "r", lw=1.2)
        for crit in criticalcurves:
            ax1.plot(crit[0], crit[1], "k--", lw=0.8)
        x1 = -self.s * self.q / (1 + self.q)
        x2 = self.s / (1 + self.q)
        ax1.plot([x1, x2], [0, 0], "ko")
        ax1.set_ylabel(r"Y ($\theta_E$)")
        ax1.set_xlabel(r"X ($\theta_E$)")
        ax1.legend(
            handles=[
                lens_handle,
                caustic_handle,
                crit_curve_handle,
                q_handle,
                s_handle,
            ],
            loc="upper right",
            prop={"size": 8},
        )

        source_dots, tracer_dots, image_dots = [], [], []
        for system in self.systems:
            ax1.plot(system["x_src"], system["y_src"], "--", color=system["color"], alpha=0.4)
            (src_dot,) = ax1.plot([], [], "*", color=system["color"], markersize=10)
            source_dots.append(src_dot)

            dots = []
            for _ in range(5):
                (dot,) = ax1.plot([], [], ".", color=system["color"], alpha=0.6, markersize=4)
                dots.append(dot)
            image_dots.append(dots)

        # --- Top Right: Light Curve ---
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.set_xlim(self.tau[0], self.tau[-1])
        all_mag = np.concatenate([s["mag"] for s in self.systems])
        ax2.set_ylim(min(all_mag) * 0.95, max(all_mag) * 1.05)
        ax2.set_ylabel("Magnification")
        ax2.set_title("Light Curve")
        ax2.set_xlabel(r"Time ($\tau$)")

        for system in self.systems:
            ax2.plot(
                self.tau,
                system["mag"],
                color=system["color"],
                label=rf"$u_0$ = {system['u0']}",
            )
            (dot,) = ax2.plot([], [], "o", color=system["color"], markersize=6)
            tracer_dots.append(dot)
            ax2.legend(prop={"size": 8})

        # --- Bottom Left: Centroid Trajectory ---
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.set_box_aspect(1)

        for system in self.systems:
            dx = system["cent_x_hr"] - system["x_src_hr"]
            dy = system["cent_y_hr"] - system["y_src_hr"]
            ax3.plot(dx, dy, color=system["color"], label=rf"$\rho$ = {self.rho}")
        # ax3.set_xlim(-1, 1)
        # ax3.set_ylim(-1, 1)
        ax3.set_title("Centroid Shift Trajectory")
        ax3.set_xlabel(r"$\delta \Theta_1$")
        ax3.set_ylabel(r"$\delta \Theta_2$")
        ax3.grid(True)
        ax3.set_aspect("equal")
        ax3.legend(prop={"size": 8})

        # --- Bottom Right: Centroid Shift vs Tau ---
        ax4 = fig.add_subplot(gs[1, 1])
        for system in self.systems:
            dx = system["cent_x_hr"] - system["x_src_hr"]
            dy = system["cent_y_hr"] - system["y_src_hr"]
            dtheta = np.sqrt(dx**2 + dy**2)
            ax4.plot(self.tau_hr, dtheta, color=system["color"])
        ax4.set_xlabel(r"Time ($\tau$)")
        ax4.set_ylabel(r"$|\delta \vec{\Theta}|$")
        ax4.set_title(r"Centroid Shift over Time ($\tau$)")
        ax4.grid(True)

        # fig.subplots_adjust(hspace=0.2, wspace=0.2)

        # --- Animate function ---
        def update(i):
            artists = []
            for j, system in enumerate(self.systems):
                x_s = system["x_src"][i]
                y_s = system["y_src"][i]
                source_dots[j].set_data([x_s], [y_s])
                tracer_dots[j].set_data([self.tau[i]], [system["mag"][i]])
                artists.extend([source_dots[j], tracer_dots[j]])

                images = self.VBM.ImageContours(self.s, self.q, x_s, y_s, self.rho)
                for k, dot in enumerate(image_dots[j]):
                    if k < len(images):
                        dot.set_data(images[k][0], images[k][1])
                        dot.set_alpha(0.6)
                    else:
                        dot.set_data([], [])
                        dot.set_alpha(0)
                    artists.append(dot)
            return artists

        ani = animation.FuncAnimation(fig, update, frames=len(self.t), interval=50, blit=True)
        plt.close(fig)
        return HTML(ani.to_jshtml())


class ThreeLens1SVBM:
    """Triple-lens, single-source model using VBMicrolensing.

    Examples
    --------
    >>> model = ThreeLens1SVBM(t0=0.0, tE=20.0, rho=0.01, u0_list=[0.1],
    ...                        q2=0.1, q3=0.1, s12=1.2, s23=1.0,
    ...                        alpha=45.0, psi=30.0)
    >>> model.plot_light_curve()
    """

    def __init__(self, t0, tE, rho, u0_list, q2, q3, s12, s23, alpha, psi):
        """Initialise the VBMicrolensing triple-lens model.

        Parameters
        ----------
        t0 : float
            Time of closest approach.
        tE : float
            Einstein crossing time.
        rho : float
            Source size in Einstein radii.
        u0_list : list of float
            Impact parameters to compute.
        q2 : float
            Mass ratio of lens 2 relative to lens 1.
        q3 : float
            Mass ratio of lens 3 relative to lens 1.
        s12 : float
            Separation between lens 1 and 2 in Einstein radii.
        s23 : float
            Separation between lens 2 and 3 in Einstein radii.
        alpha : float
            Source trajectory angle in degrees.
        psi : float
            Angle between the second and third lens in degrees.
        """
        self.t0 = t0
        self.tE = tE
        self.rho = rho
        self.u0_list = u0_list
        self.q2 = q2
        self.q3 = q3
        self.s12 = s12
        self.s23 = s23
        self.alpha = alpha
        self.tau = np.linspace(-2, 2, 100)
        self.t = self.t0 + self.tau * self.tE
        self.theta = np.radians(self.alpha)
        self.psi = psi
        self.phi = np.radians(self.psi)

        self.VBM = VBMicrolensing.VBMicrolensing()
        self.VBM.RelTol = 1e-3
        self.VBM.Tol = 1e-3
        self.VBM.astrometry = True
        self.VBM.SetMethod(self.VBM.Method.Nopoly)

        # Initialize TripleLensing for image position calculations
        self.TRIL = TripleLensing()

        self.colors = [plt.colormaps["BuPu"](i) for i in np.linspace(1.0, 0.4, len(u0_list))]
        self.systems = self._prepare_systems()

    def _prepare_systems(self):
        """Assemble source trajectories and magnifications."""
        systems = []
        for u0, color in zip(self.u0_list, self.colors):
            param_vec = [
                np.log(self.s12),
                np.log(self.q2),
                u0,
                self.alpha,
                np.log(self.rho),
                np.log(self.tE),
                self.t0,
                np.log(self.s23),
                np.log(self.q3),
                self.phi,
            ]

            mag, *_ = self.VBM.TripleLightCurve(param_vec, self.t)

            x_src = self.tau * np.cos(self.theta) - u0 * np.sin(self.theta)
            y_src = self.tau * np.sin(self.theta) + u0 * np.cos(self.theta)

            systems.append({"u0": u0, "color": color, "mag": mag, "x_src": x_src, "y_src": y_src})

        return systems

    def _setting_parameters(self):
        """Initialise the lens geometry in the VBM solver."""
        param = [
            np.log(self.s12),
            np.log(self.q2),
            self.u0_list[0],
            self.alpha,
            np.log(self.rho),
            np.log(self.tE),
            self.t0,
            np.log(self.s23),
            np.log(self.q3),
            self.phi,
        ]
        _ = self.VBM.TripleLightCurve(param, self.t)

    def _compute_lens_positions(self):
        """Return Cartesian positions of the three lenses."""
        x1, y1 = 0, 0
        x2, y2 = x1 + self.s12, y1
        x3 = self.s23 * np.cos(self.phi)
        y3 = self.s23 * np.sin(self.phi)
        return [(x1, y1), (x2, y2), (x3, y3)]

    def _calculate_image_positions(self, xs, ys):
        """Solve the lens equation for a given source position.

        Parameters
        ----------
        xs, ys : float
            Coordinates of the source in units of the Einstein radius.

        Returns
        -------
        list[complex]
            Complex coordinates of the image positions.
        """
        mlens = [1 - self.q2 - self.q3, self.q2, self.q3]
        zlens = self._compute_lens_positions()
        zlens_cpp_format = [coord for pair in zlens for coord in pair]
        nlens = len(mlens)

        zrxy_flat = self.TRIL.solv_lens_equation(mlens, zlens_cpp_format, xs, ys, nlens)
        degree = nlens * nlens + 1
        real_parts = zrxy_flat[:degree]
        imag_parts = zrxy_flat[degree : 2 * degree]

        return [complex(re, im) for re, im in zip(real_parts, imag_parts)]

    def _true_solution(self, z_image, xs, ys, so_leps=1e-10):
        """Check if ``z_image`` solves the lens equation.

        Parameters
        ----------
        z_image : complex
            Candidate image coordinate.
        xs, ys : float
            Source coordinates.
        so_leps : float, optional
            Numerical tolerance for the solution test.

        Returns
        -------
        bool
            ``True`` if the lens equation is satisfied.
        """
        mlens = [1 - self.q2 - self.q3, self.q2, self.q3]
        zlens = [complex(x, y) for x, y in self._compute_lens_positions()]
        zs = complex(xs, ys)
        dzs = zs - z_image
        for m, zl in zip(mlens, zlens):
            dzs += m / np.conj(z_image - zl)
        return abs(dzs) < so_leps

    def plot_caustic_critical_curves(self):
        """Visualise caustics and critical curves."""
        self._setting_parameters()
        caustics = self.VBM.Multicaustics()
        criticalcurves = self.VBM.Multicriticalcurves()

        plt.figure(figsize=(6, 6))
        lens_handle = Line2D(
            [0],
            [0],
            marker="o",
            color="k",
            linestyle="None",
            label="Lens",
            markersize=6,
        )
        caustic_handle = Line2D([0], [0], color="r", lw=1.2, label="Caustic")
        crit_curve_handle = Line2D(
            [0], [0], color="k", linestyle="--", lw=0.8, label="Critical Curve"
        )

        for cau in caustics:
            plt.plot(cau[0], cau[1], "r", lw=1.2)
        for crit in criticalcurves:
            plt.plot(crit[0], crit[1], "k--", lw=0.8)

        for system in self.systems:
            plt.plot(system["x_src"], system["y_src"], "--", color=system["color"], alpha=0.6)

        lens_positions = self._compute_lens_positions()
        for x, y in lens_positions:
            plt.plot(x, y, "ko", label="Lens")

        plt.xlim(-2, 2)
        plt.ylim(-2, 2)
        plt.xlabel(r"$\theta_x$ ($\theta_E$)")
        plt.ylabel(r"$\theta_y$ ($\theta_E$)")
        plt.title("3L1S Lensing Event")
        plt.gca().set_aspect("equal")
        plt.legend(handles=[lens_handle, caustic_handle, crit_curve_handle], loc="upper right")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_light_curve(self):
        """Plot the triple-lens light curve."""
        plt.figure(figsize=(6, 4))
        for system in self.systems:
            plt.plot(
                self.tau,
                system["mag"],
                color=system["color"],
                label=rf"$u_0$ = {system['u0']}",
            )
        plt.xlabel(r"Time ($\tau$)")
        plt.ylabel("Magnification")
        plt.title("Triple Lens Light Curve")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_different_q3_lc(self, q3_values, reference_q3=None, colormap="RdPu"):
        """Compare light curves for multiple ``q3`` values.

        Parameters
        ----------
        q3_values : sequence of float
            Values of the third mass fraction to compute light curves for.
        reference_q3 : float, optional
            Value used as a baseline when plotting residuals. If ``None`` the
            first entry of ``q3_values`` is used.
        colormap : str, optional
            Name of a matplotlib colormap for the different curves.
        """
        colors = [plt.colormaps[colormap](i) for i in np.linspace(0.5, 1, len(q3_values))]

        plt.figure(figsize=(8, 6))
        gs = plt.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.05)
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1], sharex=ax1)

        ref_q3 = reference_q3 if reference_q3 is not None else q3_values[0]
        ref_param = [
            np.log(self.s12),
            np.log(self.q2),
            self.u0_list[0],
            self.alpha,
            np.log(self.rho),
            np.log(self.tE),
            self.t0,
            np.log(self.s23),
            np.log(ref_q3),
            self.phi,
        ]
        ref_mag, *_ = self.VBM.TripleLightCurve(ref_param, self.t)

        for idx, q3 in enumerate(q3_values):
            color = colors[idx]
            param_vec = [
                np.log(self.s12),
                np.log(self.q2),
                self.u0_list[0],
                self.alpha,
                np.log(self.rho),
                np.log(self.tE),
                self.t0,
                np.log(self.s23),
                np.log(q3),
                self.phi,
            ]
            mag, *_ = self.VBM.TripleLightCurve(param_vec, self.t)

            label = rf"$q_3$ = {q3:.2e}"
            ax1.plot(self.tau, mag, label=label, color=color)
            residual = np.array(ref_mag) - np.array(mag)
            ax2.plot(self.tau, residual, color=color)

        ax1.set_ylabel("Magnification")
        ax1.set_title("Light Curve for Varying $q_3$")
        ax1.grid(True)
        ax1.legend()

        ax2.set_xlabel(r"Time ($\tau$)")
        ax2.set_ylabel("Residuals")
        ax2.axhline(0, color="gray", lw=0.5, ls="--")
        ax2.grid(True)

        plt.tight_layout()
        plt.show()


class ThreeLens1S:
    """Triple-lens model using a direct solver.

    Examples
    --------
    >>> model = ThreeLens1S(t0=0.0, tE=20.0, rho=0.01, u0_list=[0.1],
    ...                     q2=0.1, q3=0.1, s2=1.2, s3=1.0,
    ...                     alpha_deg=45.0, psi_deg=30.0,
    ...                     rs=0.01, secnum=10, basenum=50, num_points=100)
    >>> model.plot_light_curve()
    """

    def __init__(
        self,
        t0,
        tE,
        rho,
        u0_list,
        q2,
        q3,
        s2,
        s3,
        alpha_deg,
        psi_deg,
        rs,
        secnum,
        basenum,
        num_points,
    ):
        """Initialise the direct triple-lens solver.

        Parameters
        ----------
        t0 : float
            Time of closest approach.
        tE : float
            Einstein crossing time.
        rho : float
            Source radius in Einstein units.
        u0_list : list of float
            Impact parameters for which to compute trajectories.
        q2 : float
            Mass ratio of lens 2 relative to lens 1.
        q3 : float
            Mass ratio of lens 3 relative to lens 1.
        s2 : float
            Separation of lens 2 from lens 1 in Einstein radii.
        s3 : float
            Separation of lens 3 from lens 1 in Einstein radii.
        alpha_deg : float
            Source trajectory angle in degrees.
        psi_deg : float
            Orientation angle of the third lens in degrees.
        rs : float
            Source radius used by the solver.
        secnum : int
            Number of annuli used in contour integration.
        basenum : int
            Number of base points used in integration.
        num_points : int
            Number of time samples for the source trajectory.
        """
        self.t0 = t0
        self.tE = tE
        self.rho = rho
        self.u0_list = u0_list
        self.q2 = q2
        self.q3 = q3
        self.s2 = s2
        self.s3 = s3
        self.alpha_deg = alpha_deg
        self.psi_deg = psi_deg
        self.rs = rs
        self.secnum = secnum
        self.basenum = basenum
        self.num_points = num_points

        self.alpha_rad = np.radians(alpha_deg)
        self.psi_rad = np.radians(psi_deg)
        self.tau = np.linspace(-2, 2, num_points)
        self.t = self.t0 + self.tau * self.tE

        # Initialize TripleLensing for calculations
        self.TRIL = TripleLensing()
        self.colors = [plt.colormaps["BuPu"](i) for i in np.linspace(1.0, 0.4, len(u0_list))]
        self.systems = self._prepare_systems()

        import VBMicrolensing

        self.VBM = VBMicrolensing.VBMicrolensing()
        self.VBM.RelTol = 1e-3
        self.VBM.Tol = 1e-3
        self.VBM.astrometry = True
        self.VBM.SetMethod(self.VBM.Method.Nopoly)

    def get_lens_geometry(self):
        """Return mass fractions and lens coordinates.

        Returns
        -------
        tuple of list
            ``(mlens, zlens)`` where ``mlens`` are the mass fractions and
            ``zlens`` contains the ``x`` and ``y`` coordinates of each lens.
        """
        m1 = 1 / (1 + self.q2 + self.q3)
        m2 = self.q2 * m1
        m3 = self.q3 * m1
        mlens = [m1, m2, m3]
        x1, y1 = 0.0, 0.0
        x2, y2 = self.s2, 0.0
        x3 = self.s3 * np.cos(self.psi_rad)
        y3 = self.s3 * np.sin(self.psi_rad)
        zlens = [x1, y1, x2, y2, x3, y3]
        return mlens, zlens

    def _prepare_systems(self):
        """Generate trajectories and centroid shifts for each ``u0``."""
        systems = []
        mlens, zlens = self.get_lens_geometry()
        z = [[zlens[0], zlens[1]], [zlens[2], zlens[3]], [zlens[4], zlens[5]]]
        critical, caustics = get_crit_caus(mlens, z, len(mlens))
        caus_x = np.array([pt[0] for pt in caustics])
        caus_y = np.array([pt[1] for pt in caustics])

        for idx, u0 in enumerate(self.u0_list):
            y1s = u0 * np.sin(self.alpha_rad) + self.tau * np.cos(self.alpha_rad)
            y2s = u0 * np.cos(self.alpha_rad) - self.tau * np.sin(self.alpha_rad)

            cent_x, cent_y = [], []
            for i in range(self.num_points):
                Phis = getphis_v3(
                    mlens,
                    z,
                    y1s[i],
                    y2s[i],
                    self.rs,
                    2000,
                    caus_x,
                    caus_y,
                    secnum=self.secnum,
                    basenum=self.basenum,
                    scale=10,
                )[0]
                imgXS, imgYS, imgMUs, *_ = get_allimgs_with_mu(
                    mlens, z, y1s[i], y2s[i], self.rs, len(mlens), Phis
                )

                if len(imgMUs) == 0 or sum(imgMUs) == 0:
                    cent_x.append(np.nan)
                    cent_y.append(np.nan)
                else:
                    cx = np.sum(np.array(imgMUs) * np.array(imgXS)) / np.sum(imgMUs)
                    cy = np.sum(np.array(imgMUs) * np.array(imgYS)) / np.sum(imgMUs)
                    cent_x.append(cx)
                    cent_y.append(cy)

            systems.append(
                {
                    "u0": u0,
                    "color": self.colors[idx],
                    "y1s": y1s,
                    "y2s": y2s,
                    "cent_x": np.array(cent_x),
                    "cent_y": np.array(cent_y),
                    "mlens": mlens,
                    "zlens": zlens,
                }
            )

        return systems

    def plot_caustics_and_critical(self):
        """Plot VBM caustics and critical curves."""
        param = [
            np.log(self.s2),
            np.log(self.q2),
            self.u0_list[0],
            self.alpha_deg,
            np.log(self.rho),
            np.log(self.tE),
            self.t0,
            np.log(self.s3),
            np.log(self.q3),
            self.psi_rad,
        ]
        _ = self.VBM.TripleLightCurve(param, self.t)  # sets internal lens geometry

        caustics = self.VBM.Multicaustics()
        criticalcurves = self.VBM.Multicriticalcurves()

        plt.figure(figsize=(6, 6))
        for c in caustics:
            plt.plot(c[0], c[1], "r", lw=1.2)
        for crit in criticalcurves:
            plt.plot(crit[0], crit[1], "k--", lw=0.8)

        lens_pos = self.get_lens_geometry()[1]
        for i in range(0, 6, 2):
            plt.plot(lens_pos[i], lens_pos[i + 1], "ko")

        plt.title("Caustics and Critical Curves (VBM)")
        plt.gca().set_aspect("equal")
        plt.grid(True)
        plt.show()

    def plot_light_curve(self):
        """Plot the light curve computed via VBM."""
        plt.figure(figsize=(6, 4))
        for u0, color in zip(self.u0_list, self.colors):
            param = [
                np.log(self.s2),
                np.log(self.q2),
                u0,
                self.alpha_deg,
                np.log(self.rho),
                np.log(self.tE),
                self.t0,
                np.log(self.s3),
                np.log(self.q3),
                self.psi_rad,
            ]
            mag, *_ = self.VBM.TripleLightCurve(param, self.t)
            plt.plot(self.tau, mag, color=color, label=rf"$u_0$ = {u0}")
        plt.xlabel(r"$\tau$")
        plt.ylabel("Magnification")
        plt.title("Triple Lens Light Curve (VBM)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_centroid_trajectory(self):
        """Plot centroid trajectories for all sources."""
        plt.figure(figsize=(6, 6))
        for system in self.systems:
            dx = system["cent_x"] - system["y1s"]
            dy = system["cent_y"] - system["y2s"]
            plt.plot(dx, dy, color=system["color"], label=rf"$u_0$ = {system['u0']}")
        plt.xlabel(r"$\theta_x$ ($\theta_E$)")
        plt.ylabel(r"$\theta_y$ ($\theta_E$)")
        plt.title("Centroid Shift Trajectories")
        plt.gca().set_aspect("equal")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_shift_vs_time(self):
        """Plot centroid shift amplitude for each source over time."""
        plt.figure(figsize=(8, 5))
        for system in self.systems:
            dx = system["cent_x"] - system["y1s"]
            dy = system["cent_y"] - system["y2s"]
            dtheta = np.sqrt(dx**2 + dy**2)
            plt.plot(
                self.tau,
                dtheta,
                label=rf"$u_0$ = {system['u0']}",
                color=system["color"],
            )
        plt.xlabel(r"$\tau$")
        plt.ylabel(r"$|\delta \vec{\Theta}|$")
        plt.title("Centroid Shift vs Time")
        plt.legend()
        plt.grid(True)
        plt.show()

    def animate(self):
        """Create an animation using the direct solver.

        Returns
        -------
        IPython.display.HTML
            HTML representation of the animation for use in notebooks.
        """
        fig, ax = plt.subplots(figsize=(6, 6))

        def update(i):
            ax.cla()
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_aspect("equal")
            ax.set_title("Triple Lens Event Animation")
            for system in self.systems:
                testing(
                    ax,
                    system["mlens"],
                    system["zlens"],
                    system["y1s"][i],
                    system["y2s"][i],
                    self.rs,
                    secnum=self.secnum,
                    basenum=self.basenum,
                    full_trajectory=(system["y1s"], system["y2s"]),
                    cl=system["color"],
                )
            return (ax,)

        ani = animation.FuncAnimation(fig, update, frames=self.num_points, blit=False)
        plt.close(fig)
        return HTML(ani.to_jshtml())

    def animate_combined(self):
        """Animation overlaying caustics and source motion.

        Returns
        -------
        IPython.display.HTML
            HTML representation of the animation for use in notebooks.
        """
        # First, prepare the caustics and critical curves once using VBM
        param = [
            np.log(self.s2),
            np.log(self.q2),
            self.u0_list[0],
            self.alpha_deg,
            np.log(self.rho),
            np.log(self.tE),
            self.t0,
            np.log(self.s3),
            np.log(self.q3),
            self.psi_rad,
        ]
        _ = self.VBM.TripleLightCurve(param, self.t)  # set lens geometry
        caustics = self.VBM.Multicaustics()
        criticalcurves = self.VBM.Multicriticalcurves()

        fig, ax = plt.subplots(figsize=(6, 6))

        def update(i):
            ax.cla()
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_aspect("equal")
            ax.set_title("Triple Lens Microlensing Event")

            # Plot VBM caustics and criticals
            for c in caustics:
                ax.plot(c[0], c[1], "r", lw=1.2)
            for crit in criticalcurves:
                ax.plot(crit[0], crit[1], "k--", lw=0.8)

            for system in self.systems:
                # Plot the full source trajectory
                ax.plot(system["y1s"], system["y2s"], "--", color=system["color"], alpha=0.5)

                # Plot source position at frame i
                ax.plot(system["y1s"][i], system["y2s"][i], "o", color=system["color"])

                # Plot the lens positions
                zlens = system["zlens"]
                ax.plot(zlens[0], zlens[1], "ko")
                ax.plot(zlens[2], zlens[3], "ko")
                ax.plot(zlens[4], zlens[5], "ko")

                # Optional: Plot image positions (using TripleLensing)
                imgXS, imgYS, imgMUs, *_ = get_allimgs_with_mu(
                    system["mlens"],
                    [[zlens[0], zlens[1]], [zlens[2], zlens[3]], [zlens[4], zlens[5]]],
                    system["y1s"][i],
                    system["y2s"][i],
                    self.rs,
                    len(system["mlens"]),
                    getphis_v3(
                        system["mlens"],
                        [
                            [zlens[0], zlens[1]],
                            [zlens[2], zlens[3]],
                            [zlens[4], zlens[5]],
                        ],
                        system["y1s"][i],
                        system["y2s"][i],
                        self.rs,
                        2000,
                        np.array([pt[0] for pt in caustics[0]]),  # Just using 1st loop
                        np.array([pt[1] for pt in caustics[0]]),
                        secnum=self.secnum,
                        basenum=self.basenum,
                        scale=10,
                    )[0],
                )

                if len(imgXS) > 0:
                    ax.scatter(
                        imgXS,
                        imgYS,
                        s=30,
                        edgecolors="black",
                        facecolors="none",
                        label="Images",
                    )

            return (ax,)

        ani = animation.FuncAnimation(fig, update, frames=self.num_points, blit=False)
        plt.close(fig)
        return HTML(ani.to_jshtml())
