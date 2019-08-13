'''
HistogramMaker is a class that reads simulated GBT files (after creating GBT files using GbtPacketMaker class, feed the combined/individual packet files into the simulator).
HistogramMaker can generate two different types of histograms: one without an error message, which takes less amount of time to execute and another with error messages indicated by the colors of the bins. Both types of histograms require an input of a list with indices that tells the class which byte should be considered for making histograms.

For instance, the default input is [2,3,4,5,6,7,8,9] which are translated into collecting data for all planes or v0, v1, u0, u1, x0, x1, x2, x3 planes.   
Indices range from 0 to 17 as the number of bytes for each line of the simulated GBT packet is 18 bytes long (this translates into header, error message and BCID, v0, v1, u0, u1, x0, x1, x2, x3, fitting info #1, fitting info #2, fitting info #3, fitting info #4, fitting info #5, fitting info #6, fitting info #7, fitting info #8.

When creating an instance of the class, make sure the input datafile (simulated GBT data) is either within the same directory, or include the path to the file. e.g.HistogramMaker("<directory>/<filename>").
'''
#!/usr/local/bin/python3
# #UNCOMMENT BELOW(IMPORT) BEFORE EXECUTING THE CODE
#from matplotlib.pylab import *
import GbtPacketMaker


class HistogramMaker:

    def __init__(self, file):
        self.file = "./"+str(file)

    def check(self):
        '''
        Checks if there are headers (in other words, whether the file starts with "a3" or "A3".)
        '''
        datafile = open(self.file, 'r')
        for line in datafile:
            if line[0:2] != ("a3" and "A3"):
                print("\n We can't find the header and we expect it! \n")
                print(line[0:2])
                exit()

    def extract(self):
        '''
        Extracts lines from the simulated data file and converts them into a list of four bits after checking if there are headers For all plane channel information.
        e.g. [['A3FF', '0027', '0004', '0004', ...],['A3DE',...],...]
        :return: a list of elements which are each lines of simulated data
        '''
        HistogramMaker.check(self)
        line_ls = []
        with open(self.file, 'r') as f:
            for line in f.readlines():
                line_condensed = ""
                for letter in line:
                    if letter != " " and letter !="\n":
                        line_condensed += letter

                line_chunks = GbtPacketMaker.GbtPacketMaker.chunky(line_condensed,4)
                line_ls.append(line_chunks)

        print(line_ls)
        exit()
        return line_ls

    def select(self, idx_info=[2,3,4,5,6,7,8,9]):
        '''
        Selects specific information with user input's idx_info of each line of simulated data.
        :param [2,3,4,5,6,7,8,9]/list/optional idx_info: indices of information when lines of simulated data are divided into separate 2-bits e.g. v0 plane channel/strip information is idx_info=[2]
        '''
        selected_ls = []
        err_msg_ls = []
        info = HistogramMaker.extract(self)
        for i in range(len(info)):
            selected = []
            for idx in idx_info:
                if idx in [2,3,4,5,6,7,8,9]:
                    selected.append(int(info[i][idx], 16))
                else:
                    selected.append(info[i][idx])

            selected_ls.append(selected)
            err_msg_ls.append(info[i][1][0])

        return selected_ls, err_msg_ls

    def categorize(self, idx_info=[2,3,4,5,6,7,8,9], err_msg='g'):
        '''
        Organizes selected lists of information corresponding to a user input variables (indicated by indices) and makes a dictionary with keys named after variables and all of their values.
        If err_msg is not default value 'g', then, it only selects and organizes the values with corresponding error message digit.
        '''
        if err_msg == 'g':skip = True  # default is 'eg' which then looks at every line with all types of error messages
        else:skip = False
        selected_ls, err_msg_ls = HistogramMaker.select(self, idx_info)
        variables = ['Header', 'Error message and BCID', 'v0', 'v1', 'u0', 'u1', 'x0', 'x1', 'x2', 'x3',
                     'Fitting info #1', 'Fitting info #2', 'Fitting info #3', 'Fitting info #4',
                     'Fitting info #5', 'Fitting info #6', 'Fitting info #7', 'Fitting info #8']
        var_sel = [variables[i] for i in idx_info]
        var_dict = {}
        for i in range(len(var_sel)):
            var_dict[var_sel[i]] = []

        for i in range(len(selected_ls)):
            for j in range(len(selected_ls[i])):
                if selected_ls[i][j] != 0:
                    if skip:
                        var_dict[var_sel[j]].append(selected_ls[i][j])
                    elif not skip and err_msg_ls[i] == err_msg:
                        var_dict[var_sel[j]].append(selected_ls[i][j])

        for each in var_dict:
            var_dict[each].sort()

        return var_dict, err_msg_ls, err_msg

    def plot_histogram(self, idx_info=[2,3,4,5,6,7,8,9], second_file="none"):
        '''
        Plots hit slope histograms for all eight planes. If a second file name is not "none" and the file exists, the two files are combined to make the same histograms.::


            # Plotting a histogram of one example simulated GBT file.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_slope_histogram()

            # Plotting one histogram of combined data from two example simulated GBT files.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_slope_histogram("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second.txt")


        '''
        var_dict, err_msg_ls, _ = HistogramMaker.categorize(self, idx_info)
        var_sel = [each for each in var_dict]
        err_sorted = sorted(list(set(err_msg_ls)))

        if second_file.lower() != "none":  # In case there are two files to be combined for one histogram
            second_title = " and " + [x for x in second_file.split('/')][-1][:-4] + " combined"
            for each in var_sel:
                var_dict_2 = HistogramMaker(second_file).categorize(idx_info)
                var_dict[each].extend(var_dict_2[each])

        else:
            second_title = ""

        fig, axs = plt.subplots(len(idx_info), 1, figsize=(15, 7.5)) #figsize=(15,1 *len(idx_info)))
        plt.subplots_adjust(hspace=1.8)
        title = [x for x in self.file.split('/')][-1][:-4]
        fig.suptitle("%s Histograms" % var_sel)
        data_ls = {}
        for i in range(len(var_dict)):
            data_ls[var_sel[i]] = {}
            print(var_dict[var_sel[i]])
            if var_sel[i] in ['v0','v1','u0','u1','x0','x1','x2','x3']:
                print(int(max(var_dict[var_sel[i]])))
                (n, bins, patches) = axs[i].hist(var_dict[var_sel[i]], align="left", bins=range(int(max(var_dict[var_sel[i]]))+10),
                                                 histtype='step')
                prev = 0
                for yval, xval in zip(n, bins):     # Informs the user of the y values of x+1 when the y value of x+1 is different than y of x
                    if yval != 0 and yval != prev:
                        prev = yval
                        if isinstance(yval, float):
                            yval = int(yval)
                        axs[i].annotate(yval, xy=(xval,0))

            else:
                (n, bins, patches) = axs[i].hist(var_dict[var_sel[i]], align="left", histtype='step') # histtype=step speeds up plotting process

            data_ls[var_sel[i]] = {"n": n, "bins": bins}
            axs[i].set_xlabel(var_sel[i], x=1, fontsize=12)  # axs[i].set_title("%s" % var_sel[k], fontsize=10)

        axs[0].set_ylabel('Hits', x=1, fontsize=12)
        for i in range(len(axs)):
            print("------------------ plane = %s ------------------" % (var_sel[i]))
            for n_each, bins_each in zip(data_ls[var_sel[i]]["n"], data_ls[var_sel[i]]["bins"]):
                if int(n_each) != 0:
                    print("(channel= %s, num_hits = %s)" % (bins_each, int(n_each)), end='  ')
            print("\n")
        plt.show()

    def plot_histogram_error(self, idx_info=[2,3,4,5,6,7,8,9], second_file="none"):
        '''
        Plots hit slope histograms for all eight planes.::


            # Plotting a histogram of one example simulated GBT file with error messages.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram_error()

            # Plotting one histogram of combined data from two example simulated GBT files.
            HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first.txt").plot_histogram_error("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second.txt")


        '''
        all_dict = {}
        all_dict_2 = {}
        var_dict, err_msg_ls, _ = HistogramMaker.categorize(self, idx_info)
        var_sel = [each for each in var_dict]
        var_dict = {}
        var_dict_2 = {}
        err_sorted = sorted(list(set(err_msg_ls)))
        for err_msg in err_sorted:
            var_dict, _, _ = HistogramMaker.categorize(self, idx_info, err_msg)
            all_dict[err_msg] = var_dict

        if second_file.lower() != "none":  # In case there are two files to be combined for one histogram
            second_title = " and " + [x for x in second_file.split('/')][-1][:-4] + " combined"
            var_dict_2, err_msg_ls_2, _ = HistogramMaker(second_file).categorize(idx_info)
            err_sorted_2 = sorted(list(set(err_msg_ls)))
            for err_msg in err_sorted_2:
                var_dict_2, _, _ = HistogramMaker(second_file).categorize(idx_info, err_msg)
                all_dict_2[err_msg] = var_dict_2
                for each in var_sel:
                    print(all_dict[err_msg][each])
                    all_dict[err_msg][each].extend(all_dict_2[err_msg][each])
        else:
            second_title = ""

        fig, axs = plt.subplots(len(idx_info), 1, figsize=(15, 7.5)) #figsize=(15,1 *len(idx_info)))
        plt.subplots_adjust(hspace=1.8)
        title = [x for x in self.file.split('/')][-1][:-4]
        fig.suptitle("%s Histograms" % var_sel)
        data_ls = {}
        for i in range(len(var_dict)):
            data_ls[var_sel[i]] = {}
            for err_msg in err_sorted:
                if var_sel[i] in ['v0','v1','u0','u1','x0','x1','x2','x3']:
                    (n, bins, patches) = axs[i].hist(all_dict[err_msg][var_sel[i]], align="left", bins=range(int(max(all_dict[err_msg][var_sel[i]])) + 10),
                                                     histtype='step', stacked=True, fill=False, label=err_msg)
                    prev = 0
                    for yval, xval in zip(n, bins):     # Informs the user of the y values of x+1 when the y value of x+1 is different than y of x
                        if yval != 0 and yval != prev:
                            prev = yval
                            if isinstance(yval, float):
                                yval = int(yval)
                            axs[i].annotate(yval, xy=(xval,0))

                else:
                    (n, bins, patches) = axs[i].hist(all_dict[err_msg][var_sel[i]], align="left", histtype='step') # histtype=step speeds up plotting process

                data_ls[var_sel[i]][err_msg] = {"n": n, "bins": bins}

            axs[i].set_xlabel(var_sel[i], x=1, fontsize=12)  # axs[i].set_title("%s" % var_sel[k], fontsize=10)

        axs[0].set_ylabel('Hits', x=1, fontsize=12)
        axs[0].legend(loc='best', bbox_to_anchor=(0.6, 0., 0.5, 0.5))
        print("file = %s\n" % self.file)
        print(err_sorted)
        for i in range(len(axs)):
            for err_msg in err_sorted:
                print("------------------ plane = %s ||| error message = %s ------------------" % (var_sel[i], err_msg))
                for n_each, bins_each in zip(data_ls[var_sel[i]][err_msg]["n"], data_ls[var_sel[i]][err_msg]["bins"]):
                    if int(n_each) != 0:
                        print("(channel= %s, num_hits = %s)" % (bins_each, int(n_each)), end='  ')
                print("\n")
        plt.show()


#HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_first_check.txt").plot_histogram_error([2,3,4,5,6,7], second_file="copied_simdata/vert_upper_offset4_same_bc_gap96_pl_1_pair20_21_second_check.txt")
#HistogramMaker("copied_simdata/vert_upper_offset4_same_bc_gap_pl_1.txt").plot_histogram([2,3,4,5,6,7])
