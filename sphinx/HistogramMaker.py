#!/usr/local/bin/python3
# #UNCOMMENT BELOW(IMPORT) BEFORE EXECUTING THE CODE
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
        err_msg_ls = []
        readfile = open(self.file, 'r')
        for line in readfile.readlines():
            for slope in line[12:59]:
                if not slope == ' ':        # get rid of blanks & keep the space btwn the parentheses
                    converted_slope = str(slope.strip())
                    ls.append(converted_slope)
            ls_hit_slope.append(ls)
            ls = []

            err_msg_ls.append(line[6:8])

        ls_hit_slope = [x for x in ls_hit_slope if x != []]     # get rid of empty lists
        new_ls = []
        for i in range(len(ls_hit_slope)):  # convert into lists of four digits
            digit_list = HistogramMaker.chunky(ls_hit_slope[i], 4)
            new_ls.append(digit_list)

        slope_ls = HistogramMaker.hex_to_int(new_ls)
        return slope_ls, err_msg_ls

    def slope_each_pl(self, err_msg='eg'):
        '''
        Assigns slope data for each of the eight planes
        '''
        v0, v1, u0, u1, x0, x1, x2, x3 = [], [], [], [], [], [], [], []
        pl = [v0, v1, u0, u1, x0, x1, x2, x3]
        slope_ls, err_msg_ls = HistogramMaker.lines_to_lists(self)
        if err_msg == 'eg':skip = True # default is 'eg' which then looks at every line with all types of error messages
        else: skip = False

        for i in range(len(slope_ls)):
            for j in range(len(slope_ls[i])):
                if slope_ls[i][j] != 0:
                    if skip:
                        pl[j].append(slope_ls[i][j])
                    elif not skip and err_msg_ls[i] == err_msg:
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

        if second_file.lower() != "none":  # In case there are two files to be combined for one histogram
            result2 = HistogramMaker(second_file).slope_each_pl()
            second_title = " and " + [x for x in second_file.split('/')][-1][:-4] + " combined"
            for i in range(len(result)):
                result[i].extend(result2[i])
        else:
            second_title = ""

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
            (n, bins, patches) = axs[i].hist(pl[i], align="left", bins=range(int(max(pl[i]) + 10)),
                                             histtype='step')  # histtype=step speeds up plotting process
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
                if n[j] != 0:
                    ls[i].append('  channel=%s, num_hits=%s  ' % (bins[j], int(n[j])))
        print("file = %s \n v0 = %s \n v1 = %s \n x0 = %s \n\n" % (self.file, ls[0], ls[1], ls[4]))
        ax8.set_xlabel('Slope Value', x=1, fontsize=12)
        ax5.set_ylabel('Slope Hits', fontsize=12)
        plt.show()

    def plot_histogram_error(self, second_file="none"):
        '''
        Plots hit slope histograms for all eight planes.::


            # Plotting a histogram of one example simulated GBT file with error messages.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram_error()
            # Plotting one histogram of combined data from two example simulated GBT files.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram_error("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second.txt")


        '''
        _,  err_msg_ls = HistogramMaker.lines_to_lists(self)
        data = {}
        data2 = {}
        dt = {}
        pl = ['v0', 'v1', 'u0', 'u1', 'x0', 'x1', 'x2', 'x3']
        for each in pl:
            dt[each] = {}
        err_sorted = sorted(list(set(err_msg_ls)))
        for err_msg in err_sorted:
            data[err_msg] = HistogramMaker.slope_each_pl(self, err_msg)
            dt["v0"][err_msg], dt["v1"][err_msg], dt["u0"][err_msg], dt["u1"][err_msg], dt["x0"][err_msg],\
            dt["x1"][err_msg], dt["x2"][err_msg], dt["x3"][err_msg] = data[err_msg][0],  data[err_msg][1], \
            data[err_msg][2], data[err_msg][3], data[err_msg][4], data[err_msg][5], data[err_msg][6], data[err_msg][7]

        if second_file.lower() != "none":  # In case there are two files to be combined for one histogram
            second_title = " and " + [x for x in second_file.split('/')][-1][:-4] + " combined"
            for err_msg in err_sorted:
                data2[err_msg] = HistogramMaker(second_file).slope_each_pl(err_msg)
                for i in range(8):
                    dt[pl[i]][err_msg].extend(data2[err_msg][i])
        else:
            second_title= ""


        fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8) = plt.subplots(size(pl), 1, figsize=(15, 7.5))
        plt.subplots_adjust(hspace=1.8)
        title = [x for x in self.file.split('/')][-1][:-4]
        fig.suptitle("Slope Hits Histograms: %s%s" % (title, second_title))
        axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
        k = 0
        data_ls = {}
        for i in range(len(axs)):
            data_ls[pl[i]] = {}
            for err_msg in err_sorted:
                data_ls[pl[i]][err_msg] = {}
                (n, bins, patches) = axs[i].hist(dt[pl[i]][err_msg], align="left", bins=range(int(max(dt[pl[0]][err_msg]) + 10)),
                                             histtype='step', stacked=True, fill=False, label=err_msg)  # histtype=step speeds up plotting process
                data_ls[pl[i]][err_msg] = {"n": n, "bins": bins}

            prev = 0
            for yval, xval in zip(n, bins):
                if yval != 0 and yval != prev:
                    prev = yval
                    axs[i].annotate(int(yval), xy=(xval, 0))

            axs[i].set_title("%s Plane" % pl[k], fontsize=10)
            k = k + 1

        axs[0].legend(loc='best', bbox_to_anchor=(0.6, 0., 0.5, 0.5))
        print("file = %s\n" % self.file)
        print(err_sorted)
        for i in range(len(axs)):
            for err_msg in err_sorted:
                print("------------------ plane = %s ||| error message = %s ------------------" % (pl[i], err_msg))
                for n_each, bins_each in zip(data_ls[pl[i]][err_msg]["n"], data_ls[pl[i]][err_msg]["bins"]):
                    if int(n_each) != 0:
                        print("(channel= %s, num_hits = %s)" %(bins_each, int(n_each)), end='  ')
                print("\n")

        ax8.set_xlabel('Slope Value', x=1, fontsize=12)
        ax5.set_ylabel('Slope Hits', fontsize=12)
        plt.show()


#HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first_check.txt").plot_histogram_error()
#HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first_check.txt").plot_histogram_error("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second_check.txt")
