
class ZOS():
	""" Class for Zemax OpticStudio

	"""

	def __init__(self):
		"""
        Connects to an existing extension of OpticStudio, returns

        LDE = TheSystem.LDE - The lens data editor
        MFE = TheSystem.MFE - The Merit Function editor
        """

        import clr, os, winreg
        from itertools import islice

        # This boilerplate requires the 'pythonnet' module.
        # The following instructions are for installing the 'pythonnet' module via pip:
        #    1. Ensure you are running Python 3.4, 3.5, 3.6, or 3.7. PythonNET does not work with Python 3.8 yet.
        #    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)
        #
        #        python -m pip install pythonnet

        # determine the Zemax working directory
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
        zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
        NetHelper = os.path.join(os.sep, zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
        winreg.CloseKey(aKey)

        # add the NetHelper DLL for locating the OpticStudio install folder
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper

        pathToInstall = ''
        # uncomment the following line to use a specific instance of the ZOS-API assemblies
        #pathToInstall = r'C:\C:\Program Files\Zemax OpticStudio'

        # connect to OpticStudio
        success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall);

        zemaxDir = ''
        if success:
            zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory();
            print('Found OpticStudio at:   %s' + zemaxDir);
        else:
            raise Exception('Cannot find OpticStudio')

        # load the ZOS-API assemblies
        clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI.dll'))
        clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI_Interfaces.dll'))
        import ZOSAPI

        TheConnection = ZOSAPI.ZOSAPI_Connection()
        if TheConnection is None:
            raise Exception("Unable to intialize NET connection to ZOSAPI")

        TheApplication = TheConnection.ConnectAsExtension(0)
        if TheApplication is None:
            raise Exception("Unable to acquire ZOSAPI application")

        if TheApplication.IsValidLicenseForAPI == False:
            raise Exception("License is not valid for ZOSAPI use.  Make sure you have enabled 'Programming > Interactive Extension' from the OpticStudio GUI.")


        # LOOK AT ME DAD
        self.TheSystem = TheApplication.PrimarySystem




        if TheSystem is None:
            raise Exception("Unable to acquire Primary system")

        def reshape(data, x, y, transpose = False):
            """Converts a System.Double[,] to a 2D list for plotting or post processing
            
            Parameters
            ----------
            data      : System.Double[,] data directly from ZOS-API 
            x         : x width of new 2D list [use var.GetLength(0) for dimension]
            y         : y width of new 2D list [use var.GetLength(1) for dimension]
            transpose : transposes data; needed for some multi-dimensional line series data
            
            Returns
            -------
            res       : 2D list; can be directly used with Matplotlib or converted to
                        a numpy array using numpy.asarray(res)
            """
            if type(data) is not list:
                data = list(data)
            var_lst = [y] * x;
            it = iter(data)
            res = [list(islice(it, i)) for i in var_lst]
            if transpose:
                return self.transpose(res);
            return res
            
        def transpose(data):
            """Transposes a 2D list (Python3.x or greater).  
            
            Useful for converting mutli-dimensional line series (i.e. FFT PSF)
            
            Parameters
            ----------
            data      : Python native list (if using System.Data[,] object reshape first)    
            
            Returns
            -------
            res       : transposed 2D list
            """
            if type(data) is not list:
                data = list(data)
            return list(map(list, zip(*data)))

        print('Connected to OpticStudio')

        # The connection should now be ready to use.  For example:
        print('Serial #: ', TheApplication.SerialCode)


	def Zsensitivity(surflist,magdis,magtilt,numtrials,LDE,MFE):
        import ZOSAPI
        import matplotlib.cm as cm
        usecontrast = False

        """
        Surflist is a list of integers that describe what surfaces to perturb
        magdis is a list of displacement magnitudes
        magtilt is a list of displacement tilts
        ntrials is how many perturbations are done
        LDE & MFE are objects generated by the interactive extension
        """
        #numtrials = 10
        magxd = magdis[0]
        magyd = magdis[1]
        magzd = magdis[2]

        magxt = magtilt[0]
        magyt = magtilt[1]
        magzt = magtilt[2]

        # Define perturbation linear spaces
        tolspacexd = np.linspace(-magxd,magxd,numtrials)
        tolspaceyd = np.linspace(-magyd,magyd,numtrials)
        tolspacezd = np.linspace(-magzd,magzd,numtrials)
        tolspacext = np.linspace(-magxt,magxt,numtrials)
        tolspaceyt = np.linspace(-magyt,magyt,numtrials)
        tolspacezt = np.linspace(-magzt,magzt,numtrials)

        # tolerance space tuple
        tolspace = (tolspacexd,tolspaceyd,tolspacezd,tolspacext,tolspaceyt,tolspacezt)

        # Setup system data
        TheLDE = LDE # The Lens Data Editor
        TheMFE = MFE # The Merit Function Editor

        # For loop to iterate through surfaces
        for sind in range(len(surflist)):   

            # Surface Perturbations
            SurfTest = TheLDE.GetSurfaceAt(surflist[sind])
            colVal1 = SurfTest.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par1).Col      # X Decenter index
            colVal2 = SurfTest.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par2).Col      # Y Decenter ''
            colVal3 = SurfTest.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Thickness).Col # Z Decenter (Thickness) ''
            colVal4 = SurfTest.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par3).Col      # X Tilt ''
            colVal5 = SurfTest.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par4).Col      # Y Tilt ''
            colVal6 = SurfTest.GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par5).Col      # Z Tilt (Clocking) ''

            # store the column index values
            colVal = [colVal1,colVal2,colVal3,colVal4,colVal5,colVal6]

            Zlow = [] # predefine tuple for low order modes

            for cind in range(len(colVal)):

                nom =  SurfTest.GetCellAt(colVal[cind]).DoubleValue # nominal tolerance value
                tolspacepick = tolspace[cind]+nom # offset tolerance linear space by initial value

                # Predefine Coefficient Lists - Noll Indexing
                Z1  = []  # Predefine Piston
                Z2  = [] # Predefine Tip
                Z3  = [] # Predefine Tilt
                Z4  = [] # Predefine Focus
                Z5  = [] # Predefine Even Astig
                Z6  = [] # Predefine Odd Astig
                Z7  = [] # Predefine Even Coma
                Z8  = [] # Predefine Odd Coma
                Z11 = [] # Predefine Primary Spherical
                
                surfnom = SurfTest.GetCellAt(colVal[cind]).DoubleValue
                
                # Calculate Zernike Coefficients
                TheMFE.CalculateMeritFunction()
                
                Z1nom =  TheMFE.GetOperandAt(1).ValueCell.DoubleValue
                Z2nom =  TheMFE.GetOperandAt(2).ValueCell.DoubleValue
                Z3nom =  TheMFE.GetOperandAt(3).ValueCell.DoubleValue
                Z4nom =  TheMFE.GetOperandAt(4).ValueCell.DoubleValue
                Z5nom =  TheMFE.GetOperandAt(5).ValueCell.DoubleValue
                Z6nom =  TheMFE.GetOperandAt(6).ValueCell.DoubleValue
                Z7nom =  TheMFE.GetOperandAt(7).ValueCell.DoubleValue
                Z8nom =  TheMFE.GetOperandAt(8).ValueCell.DoubleValue
                Z11nom =  TheMFE.GetOperandAt(11).ValueCell.DoubleValue

                # Sensitivity Calculation Loop
                for zind in range(numtrials):

                    SurfTest.GetCellAt(colVal[cind]).DoubleValue = tolspacepick[zind]

                    # Update Merit Function
                    TheMFE.CalculateMeritFunction()

                    if usecontrast == False:

                        Z1.append(TheMFE.GetOperandAt(1).ValueCell.DoubleValue-Z1nom)
                        Z2.append(TheMFE.GetOperandAt(2).ValueCell.DoubleValue-Z2nom)
                        Z3.append(TheMFE.GetOperandAt(3).ValueCell.DoubleValue-Z3nom)
                        Z4.append(TheMFE.GetOperandAt(4).ValueCell.DoubleValue-Z4nom)
                        Z5.append(TheMFE.GetOperandAt(5).ValueCell.DoubleValue-Z5nom)
                        Z6.append(TheMFE.GetOperandAt(6).ValueCell.DoubleValue-Z6nom)
                        Z7.append(TheMFE.GetOperandAt(7).ValueCell.DoubleValue-Z7nom)
                        Z8.append(TheMFE.GetOperandAt(8).ValueCell.DoubleValue-Z8nom)
                        Z11.append(TheMFE.GetOperandAt(11).ValueCell.DoubleValue-Z11nom)

                    # Converts to coronagraph contrast (hard-coded, integrate with HCIPy later?)    
                    else:
                        Z1.append((TheMFE.GetOperandAt(1).ValueCell.DoubleValue-Z1nom)*(7.126540874314866e-09)*450)
                        Z2.append((TheMFE.GetOperandAt(2).ValueCell.DoubleValue-Z2nom)*(7.126540874314866e-09)*450)
                        Z3.append((TheMFE.GetOperandAt(3).ValueCell.DoubleValue-Z3nom)*(7.126540874314866e-09)*450)
                        Z4.append((TheMFE.GetOperandAt(4).ValueCell.DoubleValue-Z4nom)*(2.964730350198799e-10)*450)
                        Z5.append((TheMFE.GetOperandAt(5).ValueCell.DoubleValue-Z5nom)*(7.126540874314866e-09)*450)
                        Z6.append((TheMFE.GetOperandAt(6).ValueCell.DoubleValue-Z6nom)*(7.126540874314866e-09)*450)
                        Z7.append((TheMFE.GetOperandAt(7).ValueCell.DoubleValue-Z7nom)*(7.126540874314866e-09)*450)
                        Z8.append((TheMFE.GetOperandAt(8).ValueCell.DoubleValue-Z8nom)*(7.126540874314866e-09)*450)
                        Z11.append((TheMFE.GetOperandAt(11).ValueCell.DoubleValue-Z11nom)*(2.964730350198799e-10)*450)

                # Sqrt sum of the squares
                rss = np.sqrt(np.square(Z2) +np.square(Z3) +np.square(Z4) +np.square(Z5) +np.square(Z6) +np.square(Z7) +np.square(Z8) +np.square(Z11))
                
                # Prepare the Zlow list
                Zlow.append([Z2, # tip
                            Z3,  # tilt
                            Z4,  # power
                            Z5,  # astig
                            Z6,  # astig
                            Z7,  # coma
                            Z8,  # coma
                            Z11,
                            rss])  # spherical

                # Reset value of perturbed parameter
                SurfTest.GetCellAt(colVal[cind]).DoubleValue = nom

            # Grab the perturbation spaces
            xd = Zlow[0]
            yd = Zlow[1]
            zd = Zlow[2]
            xt = Zlow[3]
            yt = Zlow[4]
            zt = Zlow[5]

            # define a label list
            label_low = ['Z2 Tip','Z3 Tilt','Z4 Power','Z5 Even Astig','Z6 Odd Astig','Z7 Even Coma','Z8 Odd Coma','Z11 Spherical','RSS Error']
            
            # Set up figure for perturbed surface
            fig,axs = plt.subplots(2,4) # figure number corresponds to surface number
            plt.title('Low Order Terms')
            colors = cm.rainbow(np.linspace(0, 1, len(label_low)))

            # Plot Loop
            for colind in range(len(label_low)):

                axs[0,0].plot(tolspacexd,np.abs(xd[colind]),label=label_low[colind],color=colors[colind])
                axs[0,0].set_ylabel('Coefficient Change')
                axs[0,0].set_xlabel('x decenter [mm]')
                axs[0,0].set_xlim([-magxd,magxd])
                axs[0,0].set_yscale("log")

                axs[0,1].plot(tolspaceyd,np.abs(yd[colind]),label=label_low[colind],color=colors[colind])
                axs[0,1].set_xlabel('y decenter [mm]')
                axs[0,1].set_xlim([-magyd,magyd])
                axs[0,1].set_yscale("log")

                axs[0,2].plot(tolspacezd,np.abs(zd[colind]),label=label_low[colind],color=colors[colind])
                axs[0,2].set_xlabel('z decenter [mm]')
                axs[0,2].set_xlim([-magzd,magzd])
                axs[0,2].set_yscale("log")

                axs[1,0].plot(tolspacext,np.abs(xt[colind]),label=label_low[colind],color=colors[colind])
                axs[1,0].set_ylabel('Contrast Change')
                axs[1,0].set_xlabel('x tilt [deg]')
                axs[1,0].set_xlim([-magxt,magxt])
                axs[1,0].set_yscale("log")

                axs[1,1].plot(tolspaceyt,np.abs(yt[colind]),label=label_low[colind],color=colors[colind])
                axs[1,1].set_xlabel('y tilt [deg]')
                axs[1,1].set_xlim([-magyt,magyt])
                axs[1,1].set_yscale("log")

                axs[1,2].plot(tolspacezt,np.abs(zt[colind]),label=label_low[colind],color=colors[colind])
                axs[1,2].set_xlabel('z tilt [deg]')
                axs[1,2].set_xlim([-magzt,magzt])
                axs[1,2].set_yscale("log")

                def slopecalc(array,mag):
                    zern = 0 # rss slope
                    snag = array[zern]
                    slope = (snag[len(snag)-1]-snag[0])/(2*mag)

                    return slope
                table2print=([[slopecalc(xd,magxd),slopecalc(yd,magyd),slopecalc(zd,magzd)],[slopecalc(xt,magxt),slopecalc(yt,magyt),slopecalc(zt,magzt)]])
                columns = ('X','Y','Z')
                rows = ('Decenters [mm]','Tilts [deg]')
                axs[0,3].axis('tight')
                axs[0,3].axis('off')
                axs[0,3].table(cellText=table2print,rowLabels=rows,colLabels=columns,loc='center')
                axs[1,3].plot(tolspacezt,np.abs(zt[colind]),label=label_low[colind],color=colors[colind])
                axs[1,3].axis('off')
                axs[1,3].legend()
                # bbox_to_anchor=(1.1, 1.5)
            # Position Legend
            plt.show()

class SCV():
	""" Class for Synopsys CODE V

	"""

