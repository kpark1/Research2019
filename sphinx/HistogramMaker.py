#UNCOMMENT BELOW(IMPORT) BEFORE EXECUTING THE CODE
#from matplotlib.pylab import *


class HistogramMaker:
    '''
    This is a class to make histograms from reading simulated GBT files.
    '''
    def __init__(self, file):
        self.file = "./"+str(file)

    @staticmethod
    def chunky(ls, n):
        '''
        Divides a list into a list containing a lists of n number of elements.

        :param list ls: a list to be divided
        :param int n: a number of elements
        '''
        while len(ls) % n != 0:
            ls.insert(0, 0)
        return [ls[i * n:(i + 1) * n] for i in range((len(ls) + n - 1) // n)]

    @staticmethod
    def hex_to_int(ls):
        '''
        Converts a list of hexadecimal strings to integers.
        '''
        new_ls = []

        for i in range(len(ls)):
            new_ls.append([])
            for j in range(len(ls[i])):
                temp_slp = ''
                for k in range(len(ls[i][j])):
                    slope_str = temp_slp + ls[i][j][k]
                    temp_slp = slope_str

                slope = int(temp_slp, 16)
                new_ls[i].append(slope)

        return new_ls

    def check(self):
        '''
        Checks if there are headers (in other words, whether the file starts with "a3" or "A3".)
        '''
        datafile = open(self.file, 'r')
        for line in datafile:
            if line[0:2] != ("a3" and "A3"):
                print("\n We can't find the header and we expect it! \n")
                print(line[0:2])
                sys.exit()

    def lines_to_lists(self):
        '''
        Extracts slope information from a GBT file after checking if there are headers.
        '''
        HistogramMaker.check(self)
        ls = []
        ls_hit_slope = []
        readfile = open(self.file, 'r')
        for line in readfile.readlines():
            for slope in line[12:59]:
                if not slope == ' ':        # get rid of blanks & keep the space btwn the parentheses
                    converted_slope = str(slope.strip())
                    ls.append(converted_slope)
            ls_hit_slope.append(ls)
            ls = []

        ls_hit_slope = [x for x in ls_hit_slope if x != []]     # get rid of empty lists
        new_ls = []
        for i in range(len(ls_hit_slope)):  # convert into lists of four digits
            digit_list = HistogramMaker.chunky(ls_hit_slope[i], 4)
            new_ls.append(digit_list)

        slope_ls = HistogramMaker.hex_to_int(new_ls)
        return slope_ls

    def slope_each_pl(self):
        '''
        Assigns slope data for each of the eight planes
        '''
        v0, v1, u0, u1, x0, x1, x2, x3 = [], [], [], [], [], [], [], []
        pl = [v0, v1, u0, u1, x0, x1, x2, x3]
        slope_ls = HistogramMaker.lines_to_lists(self)
        for i in range(len(slope_ls)):
            for j in range(len(slope_ls[i])):
                if slope_ls[i][j] != 0:
                    pl[j].append(slope_ls[i][j])

        v0, v1, u0, u1 = sorted(v0), sorted(v1), sorted(u0), sorted(u1)
        x0, x1, x2, x3 = sorted(x0), sorted(x1), sorted(x1), sorted(x3)
        return v0, v1, u0, u1, x0, x1, x2, x3

    def plot_histogram(self, second_file="none"):
        '''
        Plots hit slope histograms for all eight planes.::

            # Plotting a histogram of one example simulated GBT file.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram()
            # Plotting one histogram of combined data from two example simulated GBT files.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second.txt")


        '''
        result = HistogramMaker.slope_each_pl(self)
        v0, v1, u0, u1, x0, x1, x2, x3 = result[0], result[1], result[2], result[3], result[4], result[5], \
                                         result[6], result[7]

        if second_file.lower() != "none":   # In case there are two files to be combined for one histogram
            result2 = HistogramMaker(second_file).slope_each_pl()
            second_title = " and "+[x for x in second_file.split('/')][-1][:-4] + " combined"
            for i in range(len(result)):
                result[i].extend(result2[i])
        else: second_title = ""

        pl_names = ['v0', 'v1', 'u0', 'u1', 'x0', 'x1', 'x2', 'x3']
        fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8) = plt.subplots(size(pl_names), 1, figsize=(15, 7.5))
        plt.subplots_adjust(hspace=1.8)
        title = [x for x in self.file.split('/')][-1][:-4]
        fig.suptitle("Slope Hits Histograms: %s%s" % (title, second_title))
        pl = [v0, v1, u0, u1, x0, x1, x2, x3]
        axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
        k = 0
        data_ls = []
        for i in range(len(axs)):
            (n, bins, patches) = axs[i].hist(pl[i], align="left", bins=range(int(max(pl[i])+10)), histtype='step') #histtype=step speeds up plotting process
            axs[i].set_title("%s Plane" % pl_names[k], fontsize=10)
            prev = 0
            for yval, xval in zip(n, bins):
                if yval != 0 and yval != prev:
                    prev = yval
                    axs[i].annotate(int(yval), xy=(xval, 0))

            k = k + 1
            data_ls.append([i, n, bins, patches])

        ls = []
        for i in range(len(data_ls)):
            n = data_ls[i][1]
            bins = data_ls[i][2]
            ls.append([])
            for j in range(len(n)):
                if n[j]!=0:
                    ls[i].append('  channel=%s, num_hits=%s  '%(bins[j], int(n[j])))
        print("file = %s \n v0 = %s \n v1 = %s \n x0 = %s \n\n" %(self.file, ls[0], ls[1], ls[4]))
        ax8.set_xlabel('Slope Value', x=1, fontsize=12)
        ax5.set_ylabel('Slope Hits', fontsize=12)

        plt.show()

#HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second.txt")
#HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second.txt").plot_histogram()
