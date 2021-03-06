import numpy as np
import matplotlib.pyplot as plt

from scipy.special import lambertw
from numpy import exp, log, e
from tqdm import tqdm


def lambertDecay(t, alpha, tau, sigma_21, n, n20):

    arg = -alpha*sigma_21*n20*exp(-(t+alpha*sigma_21*n20*tau)/tau)

    # Check that result is real
    assert min(arg) >= -1/e, \
    'Lambert W Argument will give an imaginary result.'

    return -lambertw(arg).real/(alpha*sigma_21)



def decayTime(t, alpha, tau, sigma_21, n, n20):
    data = lambertDecay(t, alpha, tau, sigma_21, n, n20)
    data = data/max(data)
    ind = np.where(data <  1/e)
    ind = ind[0][0]
    decay = t[ind]
    # try:
    #     ind = ind[0][0]
    #     decay = t[ind]
    # except:
    #     decay = 0
    
    return decay


def differentAlphas(t, tau, sigma_21, n, n20):
    """
    Fit the function with different Alpha values
    """

    plt.figure()
    plt.axhline(1/np.e, ls='--', color='k')
    plt.ylabel('$n_2$/max($n_2$)')
    plt.xlabel('time (ms)')

    for alpha in [0.002, 0.1, 0.3, 1, 2, 5]:
        y = lambertDecay(t, alpha,tau,sigma_21,n20)

        # Select only part of curve that is completely real
    #     index = np.where(np.isreal(n))
    #     t = t[index]
    #     n = n[index].real

        plt.plot(t,y/max(y), label=alpha)

    plt.xlim(min(t),max(t))
    plt.yscale('log')
    plt.legend(loc='best', title='alpha')
    import os
    fname = os.path.join('Images', 'decaysVsAlphan20_0p9.png')
    plt.savefig(fname, dpi=300)
    plt.show()

def Warg(t, tau, sigma_21, n, n20):
    """ 
    Plot the argument of the lambert W function vs alpha or n20
    """

    alpha = 1
    Warg = []
    n = np.linspace(0.5,1, 100)
    for n20 in n:
        arg = -alpha*sigma_21*n20*exp(-(t+alpha*sigma_21*n20*tau)/tau)
        Warg.append(min(arg))
    plt.plot(n,Warg, '.-')
    plt.axhline(-1/e, ls='--', color='k')
    plt.xlabel('$n_{2,0}$ value')
    plt.ylabel('Argument of the Lambert W function')
    import os
    fname = os.path.join('Images', 'Warg_n.png')
    plt.savefig(fname, dpi=300)
    plt.show()


def video(t, tau, sigma_21, n, n20):
    """
    Save multiple plots which can then be converted to a video using ffmpeg.

    https://trac.ffmpeg.org/wiki/Create%20a%20video%20slideshow%20from%20images

    in ffmpeg bash type: 

    # On Linux
    ffmpeg -framerate 2 -i file%04d.png -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4

    # On Windows
    set PATH=%PATH%;C:\ffmpeg\bin
    ffmpeg -framerate 10 -i file%04d.png out.wmv

    ## For 400 second film
    ffmpeg -t 400 -loop_input -i input.png output.wmv
    """

    i = 0
    for alpha in tqdm(np.linspace(0.01, 10, 500)):
        i +=1
        y = lambertDecay(t, alpha,tau,sigma_21,n20)
        
        plt.figure()
        plt.axhline(1/np.e, ls='--', color='k')
        plt.ylabel('$n_2$/max($n_2$)')
        plt.xlabel('time (ms)')
        plt.xlim(min(t),max(t))
        plt.ylim(1E-3,1)
        plt.yscale('log')
        plt.plot(t,y/max(y), label=alpha)
        plt.title('tau %.1f, sigma_21 %.1f, n %.1f, n20 %.1f' % (tau, sigma_21, n, n20))
        plt.legend(loc='lower left', title='alpha')
        plt.savefig('Images/file%04d.png' % i, dpi=300)
        plt.close()


def contourPlot(t, tau, sigma_21, n):
    plt.figure()
    x = np.linspace(0.01, 6, 200)  # Alpha
    y = np.linspace(0.01, 1, 200)  # n20
    X, Y = np.meshgrid(x, y)

    zs = np.array([decayTime(t, alpha, tau, sigma_21, n, n20) \
        for alpha,n20 in zip(np.ravel(X), np.ravel(Y))])

    Z = zs.reshape(X.shape)

    origin = 'lower'
    # origin = 'upper'
    lv = 40
    CS = plt.contourf(X, Y, Z, lv,
                # levels=np.arange(0,100,5),
                cmap=plt.cm.inferno,
                origin=origin)

    CS2 = plt.contour(CS, levels=CS.levels[::4],
                  colors='k',
                  origin=origin,
                  hold='on')


    plt.xlabel('Alpha')
    plt.ylabel('$n_{2,0}$')
    # Make a colorbar for the ContourSet returned by the contourf call.
    cbar = plt.colorbar(CS)
    cbar.ax.set_ylabel('Single Exp. lifetime')
    # Add the contour line levels to the colorbar
    cbar.add_lines(CS2)

    plt.title('tau %.1f, sigma_21 %.1f, n %.1f' \
            % (tau, sigma_21, n))
    plt.savefig('Images/contourfplotPopInv.png', dpi=300)

    plt.show()



if __name__ == "__main__":

    # Define parameters
    t = np.linspace(0,100,1000)
    tau = 10
    sigma_21 = 1
    n = 1
    n20 = 0.9

    # differentAlphas(t, tau, sigma_21, n, n20)
    # Warg(t, tau, sigma_21, n, n20)
    # video(t, tau, sigma_21, n, n20)
    contourPlot(t, tau, sigma_21, n)