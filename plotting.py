import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


"""
Standard plotting script for consistent plotting styles

    accepts a dictionary containing plot information
    ------------------------------------------------

    journal: Use to mimic the style of the journal published in
    dim: number of dimensions to the plot, including all variables (e.g. a line is 2D, a surface is 3D)
    type: data source which selects colormap, measured data or numerical model?

"""

x = np.linspace(-1,1,256)
y = np.linspace(-1,1,256)
x,y = np.meshgrid(x,y)
r = np.sqrt(x**2 + y**2)
th = np.arctan2(y,x)
data = r**2 * np.cos(2*th)

plotdict = {'jounral':'SPIE',
            'type':'model',
            'plotdim':[1],
            'figsize':[4,4],
            'linelabels':'Zernike11',
            'data':[x,y,data],
            'title':'Sample Title',
            'xticks':[-1,0,1],
            'yticks':[-1,0,1]}

class masterplot():

    def __init__(self,plotdict):

        self.journal = plotdict['journal']
        self.type    = plotdict['model']
        self.plotdim = plotdict['plotdim']
        self.figsize = plotdict['figsize']
        self.linelabels = plotdict['linelabels']
        self.data = plotdict['data']

    def makeplot(self):

        # """
        # Font
        # --------------
        # """
        if (self.journal == 'SPIE') or (self.journal == 'OSA'):

            plt.rcParams.update({'font.family':'Times New Roman'})
            # font = {'fontname':'Times New Roman'}

        else:
            plt.rcParams.update({'font.family':'Helvetica'})

        # """
        # colors
        # ------
        # """"
        if self.linelabels == 'Zernike11':
            self.linelabels = ['Z1','Z2','Z3','Z4','Z5','Z6','Z7','Z8','Z9','Z10','Z11']

        colors = mpl.cm.rainbow(np.linspace(0, 1, len(self.linelabels)))

        # """
        # Dimension
        # --------------
        # """
        if self.plotdim == 1:

            fix,ax = plt.figure(figsize=self.figsize)

        elif len(self.plotdim) > 1:

            fig,ax = plt.subplots(nrows=self.plotdim[0],
                                  ncols=self.plotdim[1],
                                  figsize=self.figsize)

        else:
            raise Exception('Invalid plot dimension').with_traceback(self.plotdim)

        # """
        # Construct plot
        # --------------
        # """

        if len(self.data) == 2:

            ax.plot(self.data[0],self.data[1],
                    color=colors,
                    label=self.linelabels)
            ax.legend()
            plt.show()

        if len(self.data) == 3:

            ax.imshow(self.data[3])
            plt.show()
