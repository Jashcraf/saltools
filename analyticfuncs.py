import numpy as np 
import scipy

def zernike(n, m, N):
    """
     Creates the Zernike polynomial with radial index, n, and azimuthal index, m.
     Args:
        n (int): The radial order of the zernike mode
        m (int): The azimuthal order of the zernike mode
        N (int): The diameter of the zernike more in pixels
     Returns:
        ndarray: The Zernike mode
     """
    import numpy
    coords = (numpy.arange(N) - N / 2. + 0.5) / (N / 2.)
    X, Y = numpy.meshgrid(coords, coords)
    R = numpy.sqrt(X**2 + Y**2)
    theta = numpy.arctan2(Y, X)

    if m==0:
        Z = numpy.sqrt(n+1)*zernikeRadialFunc(n, 0, R)
    else:
        if m > 0: # j is even
            Z = numpy.sqrt(2*(n+1)) * zernikeRadialFunc(n, m, R) * numpy.cos(m*theta)
        else:   #i is odd
            m = abs(m)
            Z = numpy.sqrt(2*(n+1)) * zernikeRadialFunc(n, m, R) * numpy.sin(m * theta)

    # clip
    Z = Z*numpy.less_equal(R, 1.0)

    return Z

def zernikeRadialFunc(n, m, r):
    """
    Fucntion to calculate the Zernike radial function
    Parameters:
        n (int): Zernike radial order
        m (int): Zernike azimuthal order
        r (ndarray): 2-d array of radii from the centre the array
    Returns:
        ndarray: The Zernike radial function
    """
    import numpy
    R = numpy.zeros(r.shape)
    for i in range(0, int((n - m) / 2) + 1):

        R += numpy.array(r**(n - 2 * i) * (((-1)**(i)) *
                         numpy.math.factorial(n - i)) /
                         (numpy.math.factorial(i) *
                          numpy.math.factorial(int(0.5 * (n + m) - i)) *
                          numpy.math.factorial(int(0.5 * (n - m) - i))),
                         dtype='float')
    return R
    
def j2nmIndexConvert(j):
    # steal method from AOTools https://github.com/AOtools/aotools/blob/master/aotools/functions/zernike.py
    n = int((-1.+np.sqrt(8*(j-1)+1))/2.)
    p = (j-(n*(n+1))/2.)
    k = n%2
    m = int((p+k)/2.)*2 - k

    if m!=0:
        if j%2==0:
            s=1
        else:
            s=-1
        m *= s

    if j == 1:
        n = 0
        m = 0

    return [n,m]

def nm2jIndexConvert(n,m):

    j = int(n*(n+1)/2 +np.abs(m))

    return j


def kolphase(s):

	"""Returns kolmogorov phase from FT of random 

	Parameters
	----------

	s: int
		Side length of square array

	Returns
	-------
	ph: ndarray()
		s x s array

	Author: Charlotte Guthery, with edits from Jaren Ashcraft

	"""

    #phase=kolphaseClass(s)
    # Returns a random Kolmogorov phase screen of dimension s x s computed 
    # from the FT of random complex numbers with appropriate amplitudes. 
    # Screens are computed on a grid of size 2s, with a s x s piece cut out. 
    # This helps overcome the problem with this techniqe of under-representing 
    # tilt. Tandom tilts are also explicity added to give a reasonable 
    # approximation of the overall Kolmogorav structure function on all scales.

    import numpy as np
    import matplotlib.pyplot as plt

    ph=np.zeros([s,s,2]) #initialize phase variable
    [x,y]=np.meshgrid(range(-s,s),range(-s,s))
    r=np.sqrt(np.multiply(x,x)+np.multiply(y,y)) #make a radial ordinate

    f1=np.random.randn(2*s,2*s) #make two sets of gaussian random numbers
    f2=np.random.randn(2*s,2*s)

    f=f1+1j*f2 #turn the two random numbers into a complex random number
    ps=np.power(r,-11/6) #Kolomogorov power spectrum amplitude
    ps[s][s]=0; #setting the centr of the power spectrum (DC term) to zero

    scale=15.2 #this number makes the tilts work out 

    xt=np.random.randn(2)*(scale/s) #random amplitudes for tip and tilt to 
    yt=np.random.randn(2)*(scale/s) #mitigate power spectral rolloff at low frequencies 

    #This has Kolmogorov phases in real and imaginary parts
    sc= np.fft.fft2(np.fft.fftshift(np.multiply(np.multiply(np.abs(f),ps),np.exp(1j*np.angle(f))))) 

    #seperating the real and imaginary parts
    ph[:,:,0]=np.real(sc[0:s,0:s])+xt[0]*x[0:s,0:s]+yt[0]*y[0:s,0:s]
    ph[:,:,1]=np.real(sc[0:s,0:s])+xt[1]*x[0:s,0:s]+yt[1]*y[0:s,0:s]

    #make the mean phase zero
    ph[:,:,0]=ph[:,:,0]-np.mean(ph[:,:,0])
    ph[:,:,1]=ph[:,:,1]-np.mean(ph[:,:,1])

    #pick just one of the two phase screens for present purposes scale to 
    #something that will give reasonable ansewrs on a 1024 grid with 256 pupil
    ph=ph[:,:,1]*3

    return ph