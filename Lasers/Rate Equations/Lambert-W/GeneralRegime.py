import matplotlib.pyplot as plt
import numpy as np
from numpy import exp, e
from scipy.special import lambertw
from tqdm import tqdm


def lambert_decay(r, n20):

    alpha = (1 + r/2) * rho * d
    a = alpha * (sigma_12 + sigma_21)
    b = 1 + alpha * sigma_12 * n

    x = (t / (b * tau)) + (a * n20 / b)
    arg = -a * n20 * exp(-x) / b

    assert min(arg) >= -1 / e, 'Lambert W Argument will give an imaginary result.'
    return -b * lambertw(arg).real / a


def fit_decay(r, n20):
    from scipy.optimize import curve_fit

    # Create the simulated y dataa
    y = lambert_decay(r, n20)

    # Define the model function to fit (mono-exponential decay)
    def model_func(x, a, b, c):
        return a*exp(-x/b)+c

    # Guess for a, b, c coefficients
    guess = [max(y) - min(y), tau, 0]

    # Fit using Levenberg-Marquardt algorithm
    popt, pcov = curve_fit(model_func, t, y, guess)

    # Return the fit [a, b, c]
    return popt


def varyFeedback(t, tau, sigma_12, sigma_21, n, n20, rho, d):
    """
    Fit the function with different r values
    """

    plt.figure()
    plt.axhline(1/e, ls='--', color='k')
    plt.ylabel('$n_2$/max($n_2$)')
    plt.xlabel('time (ms)')

    for r in [0.001, 0.5, 1]:
        y = lambert_decay(t, tau, sigma_12, sigma_21, n, n20, r, rho, d)
        # y = y/max(y)
        plt.plot(t, y, label=r)

    plt.title('$\\tau$ %.1f, $\\sigma_{12}$ %.1f, $\\sigma_{21}$ %.1f, n %.1f, d %.4f cm, $\\rho$ %.2f'
              % (tau, sigma_12, sigma_21, n, d, rho))
    plt.xlim(min(t), 25)
    # plt.ylim(0.01, 1)
    # plt.yscale('log')
    plt.legend(loc='best', title='r')
    plt.savefig('Images/varyFeedbackLog.png', dpi=900)
    plt.show()


def video(t, tau, sigma_12, sigma_21, n, n20, r, rho, d):
    """
    Save multiple plots which can then be converted to a video using ffmpeg.

    https://trac.ffmpeg.org/wiki/Create%20a%20video%20slideshow%20from%20images

    in ffmpeg bash type:

    # On Linux
    ffmpeg -framerate 2 -i file%04d.png -c:v libx264 -r 30 -pix_fmt yuv420p
     x.mp4

    # On Windows
    set PATH=%PATH%;C:\ffmpeg\bin
    ffmpeg -framerate 10 -i file%04d.png out.wmv

    ## For 400 second film
    ffmpeg -t 400 -loop_input -i input.png output.wmv
    """

    i = 0
    for r in tqdm(np.linspace(1E-4, 1, 200)):
        i += 1
        y = lambert_decay(t, tau, sigma_12, sigma_21, n, n20, r, rho, d)

        plt.figure()
        plt.axhline(1/np.e, ls='--', color='k')
        plt.ylabel('$n_2$/max($n_2$)')
        plt.xlabel('time (ms)')
        plt.xlim(min(t), 50)
        plt.ylim(1E-2, 1)
        plt.yscale('log')
        plt.plot(t, y/max(y), label=r)
        plt.title('tau %.1f, sigma_12 %.1f, sigma_21 %.1f, n %.1f, n20 %.1f' %
                  (tau, sigma_12, sigma_21, n, n20))
        plt.title('$\\tau$ %.1f, $\\sigma_{12}$ %.1f, $\\sigma_{21}$ %.1f, n %.1f, $n_{20}$ %.1f, d %.1f cm, '
                  '$\\rho$ %.2f' % (tau, sigma_12, sigma_21, n, n20, d, rho))
        plt.legend(loc='lower left', title='r')
        plt.savefig('Images/file%04d.png' % i, dpi=300)
        plt.close()


def threedPlot(t, tau, sigma_12, sigma_21, n, n20, r, rho, d):
    # from matplotlib import cm

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x = np.linspace(0.01, 8, 200)
    y = np.linspace(0.1, 1, 200)
    X, Y = np.meshgrid(x, y)

    zs = np.array([fit_decay(t, r, tau, sigma_12, sigma_21, n, n20)
                   for r, n20 in zip(np.ravel(X), np.ravel(Y))])

    Z = zs.reshape(X.shape)

    ax.plot_surface(X, Y, Z)
    # cset = ax.contour(X, Y, Z, zdir='z', offset=-0, cmap=cm.coolwarm)
    # cset = ax.contour(X, Y, Z, zdir='x', offset=-8, cmap=cm.coolwarm)
    # cset = ax.contour(X, Y, Z, zdir='y', offset=1, cmap=cm.coolwarm)

    ax.set_xlabel('r')
    ax.set_ylabel('$n_{2,0}$')
    ax.set_zlabel('Decay Time')

    plt.show()


def contour_plot():
    ########################################
    # Calculate popt
    ########################################
    x = np.linspace(1E-4, 1, 200)  # r
    y = np.linspace(1E-4, 0.15, 200)     # n20
    X, Y = np.meshgrid(x, y)
    res = [fit_decay(r, n20) for r, n20 in zip(np.ravel(X), np.ravel(Y))]
    res = np.array(res)

    ########################################
    # Plot lifetime contour plot
    ########################################
    zs = res[:, 1]
    Z = zs.reshape(X.shape)
    fig, ax = plt.subplots()
    origin = 'lower'
    # origin = 'upper'
    lv = 1000  # Levels of colours
    CS = plt.contourf(X * 100, Y, Z, lv,
                      # levels=np.linspace(0, 0.15, num=100, endpoint=True),
                      origin=origin)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Reflectance (%)')
    ax.set_ylabel('N$_1$(0)/N')
    cbar = plt.colorbar(CS, format='%.2f')
    cbar.ax.set_ylabel('Lifetime (ms)')
    # plt.savefig('Images/contour_plot_tau')

    ########################################
    # Plot amplitude contour plot
    ########################################
    zs = res[:, 0]
    Z = zs.reshape(X.shape)
    fig, ax = plt.subplots()
    origin = 'lower'
    # origin = 'upper'
    lv = 1000  # Levels of colours
    CS = plt.contourf(X * 100, Y, Z, lv,
                      levels=np.linspace(0, 0.15, num=100, endpoint=True),
                      origin=origin)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Reflectance (%)')
    ax.set_ylabel('N$_1$(0)/N')
    cbar = plt.colorbar(CS, format='%.2f')
    cbar.ax.set_ylabel('Amplitude (A.U.)')
    plt.savefig('Images/contour_plot_A')
    plt.show()


def journal_plotting():
    # Set figure size
    WIDTH = 246.0  # the number (in pt) latex spits out when typing: \the\linewidth
    FACTOR = 0.9  # the fraction of the width you'd like the figure to occupy
    fig_width_pt = WIDTH * FACTOR

    inches_per_pt = 1.0 / 72.27
    golden_ratio = (np.sqrt(5) - 1.0) / 2.0  # because it looks good

    fig_width_in = fig_width_pt * inches_per_pt  # figure width in inches
    fig_height_in = fig_width_in * golden_ratio  # figure height in inches
    fig_dims = [fig_width_in, fig_height_in]  # fig dims as a list

    # Update rcParams for figure size
    params = {
        'font.size': 9.0,
        'text.usetex': True,
        'savefig.dpi': 1200,
        'savefig.format': 'pdf',
        'savefig.bbox': 'tight',
        'figure.figsize': fig_dims,
    }
    plt.rcParams.update(params)


if __name__ == "__main__":
    # journal_plotting()

    # Time to simulate over
    t = np.linspace(0, 100, 100)

    # Define material parameters:
    tau = 10  # Radiative decay rate
    rho = 0.217         # Density of Er ions (*1E21 cm^-3)
    n = 1  # Total number of active ions (i.e.,clustering)
    d = 0.98E-4         # Thickness of slab (cm)
    sigma_12 = 4.1      # Absorption cross-section (*1E-21 cm^2)
    sigma_21 = 5.0      # Emission cross-section (*1E-21 cm^2)

    # Multiply photon path length
    d *= 250

    contour_plot()
    #
    # n20 = 0.2*n         # Fraction of excited ions at t=0
    # r = 0.5             # Reflectivity of top layer
    # varyFeedback(t, tau, sigma_12, sigma_21, n, n20, rho, d)
    # video(t, tau, sigma_12, sigma_21, n, n20, r, rho, d)
    # threedPlot(t, tau, sigma_12, sigma_21, n, n20, r, rho, d)
