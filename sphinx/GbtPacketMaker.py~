import os
import errno
import re
import sys


class GbtPacketMaker:
    '''
    This is a class to make GBT packets.
    '''
    def __init__(self, input_vmm_list, input_channel_list):
        '''
        Initializes GbtPacketMaker object.

        '''
        vmm_list, channel_list = zip(*sorted(zip(input_vmm_list, input_channel_list)))  # IMPT: sort the input vmm and channel pairs from smallest to largest
        self.vmm_list = list(vmm_list)
        self.channel_list = list(channel_list)

    @staticmethod
    def align(ls):
        '''
        Concatenates lists within lists into one list.
        '''
        aligned = []
        for plane in ls:
            for vmm_num in plane:
                aligned.append(vmm_num)
        return aligned

    @staticmethod
    def chunky(ls, n):
        '''                                                                                                                                                                  
        Divides a list into a list containing a lists of n number of elements.
                                                                                                                                                                             
        :param list ls: a list to be divided
        :param int n: a number of elements
        '''
        while len(ls)%n != 0:
            ls.insert(0, 0)
        return [ls[i * n:(i + 1) * n] for i in range((len(ls) + n - 1)//n)]

    @staticmethod
    def read_chunks(ls):
        '''
        Converts a list of lists of four integers into a list of binary numbers.
        '''
        chunks_read = []    # e.g. [[1,1,0,1],[0,0,1,0]] would be translated into [13, 2]
        for each in ls:
            count = 3 # NEED TO BE CHANGED TO ACCOMMODATE FOR N'S; currently only works for converting into 4 elements
            num = 0
            for digit in each:
                num += digit * (2**count)
                count -= 1

            chunks_read.append(num)

        return chunks_read

    @staticmethod
    def to_hex(ls):
        '''
        Converts a list of integers into a list of hexadecimal strings.
        '''
        final = hex(0)
        for each in ls:
            final += hex(each)[2:]      # changes from 0xf to f

        final = final[3:]               # subtract the first three digits b/c other wise extra "0x0"
        return final

    @staticmethod
    def sorted_alphanumeric(ls):      # sort in alphanumerical way
        '''
        Sorts list of files in alphanumerical way. It is necessary to align GBT packets in an ascending order of BC
        and pair numbers when combining GBT packets to minimize the running time for simulation.
        '''
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(ls, key=alphanum_key)

    @staticmethod
    def combine_gbt(dir_name, typ, num_regions):
        '''
        Combines all GBT files of a specific pattern of regions.

        :param str dir_name: directory where GBT packets are stored
        :param "all"/"pair" typ: If typ is "all", all GBT packets are combined
            into one file with a single finish command  ( or '00000001 01'). If typ is "pair", individual GBT pairs are combined
            into one file each pairs with finish command. If typ is neither of those, exit() is executed.
        :param int num_regions: number of regions e.g. Regions 20, 21 are two regions
        :return: a single file if typ is "all" and a set of files if typ is "pair"
        '''
        file_ls = GbtPacketMaker.sorted_alphanumeric(os.listdir(dir_name))  # sort the files in the same directory
        if typ == "all":    #if combining all in the directory
            file_ls = [dir_name + file for file in file_ls]                       # add directory path
            with open('combined_%s' % dir_name[:-1], 'w') as out_file:
                for file in file_ls:
                    with open(file) as in_file:
                        out_file.write(in_file.read())

                fin_line = '00000001 01'
                out_file.write(fin_line)
                out_file.close()

        elif typ == "pair":     # if individual packet pair

            ls = GbtPacketMaker.chunky(file_ls, num_regions)
            directory = "combined_" + dir_name
            if not os.path.exists(os.path.dirname(directory)):
                try:
                    os.makedirs(os.path.dirname(directory))  # only creates a new directory if it doesn't exist already
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise

            for j in range(len(ls[0])//2):
                if len(ls[0]) % 2!=0:
                    print("Some fibers don't have their pairs.")

                for i in range(len(ls)):
                    file_ls = [dir_name + file_temp for file_temp in ls[i][2*j:2*j + 2]]
                    print(file_ls)
                    with open(os.path.join(directory, file_ls[0].split("/")[1]), 'w') as out_file:
                        for file in file_ls:
                            with open(file) as in_file:
                                out_file.write(in_file.read())

                        fin_line = '00000001 01'
                        out_file.write(fin_line)
                        out_file.close()

        else:
            print("Wrong type input for the combine.gbt function")
            exit()


    def align_vmm(self):
        # visualize aligned vmm of all planes
        '''
        Returns a list of 0's and 1's to help visualize hit vmm's of all planes.
        The list reads right to left: The last 8th vmm of the fourth plane is the first element of the list and the
        first vmm of the first plane is the last element of the list.
        '''
        vmm_each_plane = [[], [], [], [], [], [], [], []]  # separates into each plane

        for i in range(len(self.vmm_list)):
            vmm_str = str(self.vmm_list[i])                # convert into string
            plane_int = int(vmm_str[0])                    # extract plane info in int
            vmm_int = int(vmm_str[2])                      # extract vmm info in int
            vmm_each_plane[plane_int].append(vmm_int)      # make a list of vmm's by each plane
        # create empty vmm bin
        vmm_bin = []
        for i in range(4): # four planes (2 x planes 2 stereo - u and v - planes
            vmm_bin.append([0, 0, 0, 0, 0, 0, 0, 0])

        for i in range(len(vmm_each_plane)):
            for vmm in vmm_each_plane[i]:
                vmm_bin[i][-(vmm + 1)] = 1                 # CHANGE 1 TO "1" IF WANTS STRING

        vmm_bin.reverse()
        vmm_aligned = GbtPacketMaker.align(vmm_bin)
        return vmm_aligned

    def read_vmm(self):
        '''
        Returns a string of Hit Map that corresponds to the input of the class instance or input list of hit planes and vmm's.
        '''
        vmm = GbtPacketMaker.align_vmm(self)
        vmm_chunks = GbtPacketMaker.chunky(vmm, 4)
        hit_map_almost = GbtPacketMaker.read_chunks(vmm_chunks)

        if len(hit_map_almost) > 8:                        # remove extra lists/empty lists filled with zero's
            hit_map_almost = hit_map_almost[len(vmm_chunks)-8:len(vmm_chunks)]
        if len(hit_map_almost) < 8:
            for n in range(8-len(hit_map_almost)):
                hit_map_almost.insert(0, 0)

        hit_map = GbtPacketMaker.to_hex(hit_map_almost)
        hit_map = hit_map.upper()
        return hit_map

    def read_channel(self):  # ART data Creator
        '''
        Returns a string of ART DATA that corresponds to the input of the class instance or input list of hit channels.
        '''
        channel = []
        channel_ls = self.channel_list[::-1]            # same as reverse function (by slicing)

        for ch in channel_ls:
            six_digit = '{0:06b}'.format(ch)            # f'{channel:08b}' if python 3.6 or above
            channel.append(six_digit)

        channel_aligned = GbtPacketMaker.align(channel)

        new_channel = []
        for digit in channel_aligned:                   # change all binary digit to int
            new_channel.append(int(digit))

        channel_chunks = GbtPacketMaker.chunky(new_channel, 4)
        art_data_chunks = GbtPacketMaker.read_chunks(channel_chunks)
        art_data_almost = GbtPacketMaker.to_hex(art_data_chunks)
        art_data = art_data_almost.zfill(12).upper()
        return art_data

    def find_parity(self):
        '''
        Returns a string of parity by interpreting hit channels.
        '''
        ls = []
        for channel in self.channel_list:
            channel_bin = '{0: 04b}'.format(channel)
            count =0

            for i in range(len(channel_bin)):
                if channel_bin[i] == '1':
                    count += 1
            if count % 2 == 0:
                ls.append(1)
            if count % 2 != 0:
                ls.append(0)

        ls.reverse()    # reverse the order

        before_hex = GbtPacketMaker.chunky(ls, 4)
        chunks_read = GbtPacketMaker.read_chunks(before_hex)
        parity = GbtPacketMaker.to_hex(chunks_read).upper()
        return parity

    def make_gbt(self, BCID, region, directory_name, add_line, second_dir="none"):
        '''
        Creates a GBT packet file with a corresponding input information. If a directory doesn't exist already,
        the function will create a new directory.

        :param int BCID: BC number. Preferably a multiple of 32.
        :param int region: Region. e.g. 20 for first region.
        :param str directory_name: Name of directory to store the GBT packet.
        :param "yes"/"no" add_line: If creating a single GBT file to be simulated, then add_line should be "yes", which adds a finish command line. If creating a multiple GBT files of one more more regions to be combined later, add_line should be "no".
        :param "none"/str/optional second_dir: a name of the second directory if necessary when storing multiple GBT files.

        '''
        bcid_converted = hex(BCID)[2:].upper()
        if len(bcid_converted) > 3:          # Important
            print("BC %s is too large. Fix the pattern code to limit BC number maximum." %BCID)
            sys.exit()

        bcid_converted  = bcid_converted.zfill(3)
        header = "0000A" + bcid_converted  # e.g. "0000A00A" where "00A" is a bunch crossing id
        error = "00"
        tag = str(self.vmm_list) + str(self.channel_list)
        hit_map = str(GbtPacketMaker.read_vmm(self))
        parity = str(GbtPacketMaker.find_parity(self))
        if len(parity) != 2:
            parity = "0" +parity # IS THIS CORRECT TO INSERT IT IN FRONT INSTEAD OF BACK?
        art_data = str(GbtPacketMaker.read_channel(self))
        final = header + error + hit_map+ parity+ art_data
        # print("hit map = %s parity = %s art data = %s " %(hit_map, parity,art_data))

        add = str(region)   # e.g." 20"
        output_file = "GBT_packet_BC=%s_region=%s_%s" % (BCID, region, tag)
        if second_dir.lower() == "none":
            directory = "GBT_packet_dir_%s/" % directory_name
        else:
            directory = "GBT_packet_dir_%s_%s/" % (directory_name, second_dir)

        if not os.path.exists(os.path.dirname(directory+output_file)):
            try:
                os.makedirs(os.path.dirname(directory+output_file)) # only creates a new directory if it doesn't exist already
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        #else:
            #print("directory %s exists" %directory+output_file)

        f = open(directory + output_file, 'w')  # 'w' instead of 'a' : each time this is opened it overwrites the file
        if len(final) % 8 == 0:
            for i in range(int(len(final) // 8)):
                line = final[i * 8:(i + 1) * 8] + ' ' + add
                f.write(line)
                f.write("\n")

            if add_line == "yes":
                fin_line = '00000001 01' # do this while combining -> IF individual packet needs this, add this, but make sure to change other parts of the code that combines all GDP packets
                f.write(fin_line)
            f.close()
            print("gbt file named {} created".format(output_file))
        else:
            print("GBT for {} not created correctly. Check if BC number is larger than 4095.".format(output_file))
            print("Not created file content is %s" % final)

    @staticmethod
    def vertical_pattern(section, regions, offset, bc_gap=32, bc_gap_region=0, bc_gap_pl=0, second_dir_name="second"):
        '''
        Creates GBT packet files in a new directory and a combined file that has all GBT packets in a current directory
        to simulate a vertical pattern of hits in detector. If BC ID exceeds 4095, then a second directory is created
        and rest of the files necessary to generate a pattern have BC ID = (BC ID - 4095) and stored in a second directory.::


            GbtPacketMaker.vertical_pattern("upper", [20,21, 22, 23], 4, bc_gap=96, second_dir_name='2')


        :param "upper"/"lower"/"upper_specific"/"lower_specific" section: "lower" if channels hit should be of lower section or [0, 1, 2, 3, 8, 9, ...] and "upper" if channels are from [4, 5, 6, 7, 12, 13, 14, ...]. If "*_specific", then GBT packets are combined into pairs insteand of one combined file.
        :param list regions: regions for hits e.g. [20, 21]
        :param int offset: Hit channel offset for x planes. 0, 1, 2, or 3 if section = "lower", 4, 5, 6, or 7 if section = "upper".
        :param 32/int/optional bc_gap: BC ID difference between each GBT packets within the same region.
        :param 0/int/optional bc_gap_region: BC ID difference between different regions. The default value is 0.
        :param 0/int/optional bc_gap_pl:  BC ID difference between planes. The default value is 0.
        :param "second"/str/optional second_dir_name: name of second directory if second directory is necessary.
        '''

        if "lower" in section and offset in [0, 1, 2, 3]:        # e.g. offset = 2
            pass
        elif "upper" in section and offset in [4, 5, 6, 7]:     # e.g. offset = 4
            pass
        else:
            print("Wrong section or offset")
            exit()

        channels = [offset + 8 * i for i in range(8)]
        dir_name = 'vert_%s_%s_offset%s_bc_gap_%s_%s_bc_gap_pl_%s' % (section, regions, offset, bc_gap_region, bc_gap, bc_gap_pl)
        path = "GBT_packet_dir_%s/" % dir_name
        path2 = "GBT_packet_dir_%s_%s/" % (dir_name, second_dir_name)
        k = 0
        for i in range(len(regions)):
            bc = bc_gap + k  # impt to place this here for the regions to have the symmetrical list of BC's
            for ch in channels:
                pl = [[],[],[],[]]
                for n in range(8):  # repeat as many as the number of vmm's in each region = 8 vmm's in one fiber
                    pl[0] = 0.0 + round(n * (10 ** (-1)), 1)
                    pl[1] = 1.0 + round(n * (10 ** (-1)), 1)
                    pl[2] = 2.0 + round(n * (10 ** (-1)), 1)
                    pl[3] = 3.0 + round(n * (10 ** (-1)), 1)
                    if bc < 4096:       # max number of bc is 4095
                        if bc_gap_pl == 0:
                            GbtPacketMaker(pl,[ch,ch,ch,ch]).make_gbt(bc, regions[i], dir_name, "no")
                        else:
                            for j in range(4):
                                GbtPacketMaker([pl[j]],[ch]).make_gbt(bc+j, regions[i], dir_name, "no")

                    else:
                        temp_bc = bc - 4095             # add a separate directory for BC that are too large
                        if bc_gap_pl == 0:
                            GbtPacketMaker(pl, [ch,ch,ch,ch]).make_gbt(temp_bc, regions[i], dir_name, "no", second_dir_name)
                        else:
                            for j in range(4):
                                GbtPacketMaker([pl[j]],[ch]).make_gbt(temp_bc+j, regions[i], dir_name, "no", second_dir_name)

                    bc += bc_gap

            if i % 2 != 0:
                 k += bc_gap_region

        if "specific" in section:
            GbtPacketMaker.combine_gbt(path, "pair", len(regions))
            print("Combined file created")
            if os.path.exists(os.path.dirname(path2)):
                GbtPacketMaker.combine_gbt(path2, "pair", len(regions))
                print("Combined file 2 created")
        else:
            GbtPacketMaker.combine_gbt(path, "all", len(regions))    # CHANGE TO "pair" if wanting to combine in gbt pairs not all produced
            print("Combined file created")
            if os.path.exists(os.path.dirname(path2)):
                GbtPacketMaker.combine_gbt(path2, "all", len(regions)) # combine the second file as well
                print("Combined file 2 created")

    @staticmethod
    def horizontal_pattern(section, regions, offset, x_vmm, x_ch_idx, input_uv_offset, uv_dir="none",
                           bc_gap=32, bc_gap_region=0, bc_gap_pl=0, second_dir_name="second"):
        '''
        Creates GBT packet files in a new directory and a combined file that has all GBT packets in a current directory
        to simulate a horizontal pattern of hits in detector. If BC ID exceeds 4095, then a second directory is created
        and rest of the files necessary to generate a pattern have BC ID = (BC ID - 4095) and stored in a second directory.::


            GbtPacketMaker.horizontal_pattern("lower", [20,21], 2, 3, 4, 2, uv_dir="right")


        :param "upper"/"lower"/"upper_specific"/"lower_specific" section: Look vertical_pattern documentation.
        :param int regions: Look vertical_pattern documentation.
        :param int offset: Look vertical_pattern documentation.
        :param int x_vmm: Choose a vmm of x planes for a center point of a horizontal pattern. Ranges from 0 to 7.
        :param int x_ch_idx: Choose an index of a list of x plane channels with an input offset of a horizontal pattern. Generally ranges from 0 to 7, but not necessarily.
        :param int input_uv_offset: An equivalent of offset for u and v planes instead of x planes.
        :param "none"/"left"/"right"/optional uv_dir: Section.
        :param 32/int/optional bc_gap: Look vertical_pattern documentation.
        :param 0/int/optional bc_gap_region: Look vertical_pattern documentation.
        :param 0/int/optional bc_gap_pl: Look vertical_pattern documentation.
        :param "second"/str/optional second_dir_name: Look vertical_pattern documentation.
        '''
        def make_hor():
            uv_offset= input_uv_offset
            if "diagonal" in section:
                if input_uv_offset == 0 or (uv_dir != "left" and uv_dir != "right"):
                    exit()
                if uv_dir == "right":
                    uv_offset = -1 * input_uv_offset

            if "lower" in section and offset in [0, 1, 2, 3]:  # e.g. offset = 2
                pass
            elif "upper" in section and offset in [4, 5, 6, 7]:  # e.g. offset = 4
                pass
            else:
                print("wrong section")
                exit()

            interval = 8
            channels = [offset + interval * i for i in range(8)] # interval = 8
            if x_vmm in [i for i in range(8)]:
                x_ch = x_vmm * 64 + channels[x_ch_idx]
            else:
                print("Your x_vmm = %s  or x_ch_num = %s are out of range. x_ch_num should from "
                          "be %s and x_vmm should be in a range of 0 to 7" % (x_vmm, x_ch_num, channels))
                exit()

            if x_ch <= 510 // 2:
                num = range(x_ch // interval + 1)
            else:
                num = range((512 - x_ch) // interval + 1)

            # add left and right channels and minus the duplicated center
            u_ch_ls = list(reversed([- uv_offset + x_ch - interval * i for i in num])) + \
                      [- uv_offset + x_ch + interval * i for i in num][1:]
            v_ch_ls = list(reversed([i+ 2 * uv_offset for i in u_ch_ls]))
            return x_ch, u_ch_ls, v_ch_ls

        x_ch, u_ch_ls, v_ch_ls = make_hor()

        dir_name = "hor_%s_ch%s_pair%s_%s_bc_gap_%s_bc_gap_pl_%s" % (section, x_ch, regions, uv_dir, bc_gap, bc_gap_pl)  # CHANGE THE DIR NAME
        path = "GBT_packet_dir_%s/" % dir_name
        path2 = "GBT_packet_dir_%s_%s/" % (dir_name, second_dir_name)
        k = 0
        for i in range(len(regions)):
            bc = bc_gap + k
            pl = [[], [], [], []]           # [x0, x1, u0, v0]
            for n in range(len(u_ch_ls)):
                if regions[i] in [20, 22, 24, 26, 28]:
                    ch = [x_ch % 64, x_ch % 64, u_ch_ls[n] % 64, v_ch_ls[n] % 64]
                    x0 = round((x_ch // 64) * .1, 1)
                    x1 = x0 + 1
                    u0 = round((u_ch_ls[n] // 64) * .1 + 2, 1)
                    v0 = round((v_ch_ls[n] // 64) * .1 + 3, 1)
                    pl = [x0, x1, u0, v0]
                elif regions[i] in [21, 23, 25, 27, 29]:
                    ch = [u_ch_ls[n] % 64, v_ch_ls[n] % 64, x_ch % 64, x_ch % 64]
                    x0 = round((x_ch // 64) * .1 + 2, 1)
                    x1 = x0 + 1
                    u0 = round((u_ch_ls[n] // 64) * .1, 1)
                    v0 = round((v_ch_ls[n] // 64) * .1 + 1, 1)
                    pl = [u0, v0, x0, x1]

                if bc < 4096:
                    if bc_gap_pl == 0:
                        GbtPacketMaker(pl,ch).make_gbt(bc, regions[i], dir_name, "no")
                    #print(bc, [x_ch, u_ch_ls[n], v_ch_ls[n]], [pl[0],pl[1],pl[2],pl[3]], [x_ch % 64, x_ch % 64, u_ch_ls[n] % 64, v_ch_ls[n] % 64])
                    else:
                        for j in range(4):
                            GbtPacketMaker([pl[j]],[ch[j]]).make_gbt(bc+j, regions[i], dir_name, "no")

                else:
                    temp_bc = bc - 4095             # add a separate directory for BC that are too large
                    if bc_gap_pl == 0:
                        GbtPacketMaker(pl,ch).make_gbt(temp_bc, regions[i], dir_name, "no", second_dir_name)
                    else:
                        for j in range(4):
                            GbtPacketMaker([pl[j]],[ch[j]]).make_gbt(temp_bc+j, regions[i], dir_name, "no"), second_dir_name

                bc += bc_gap

            if i % 2 != 0:
                k += bc_gap_region

        if "specific" in section:
            GbtPacketMaker.combine_gbt(path, "pair", len(regions))
            print("Combined file created")
            if os.path.exists(os.path.dirname(path2)):
                GbtPacketMaker.combine_gbt(path2, "pair", len(regions))
                print("Combined file 2 created")
        else:
            GbtPacketMaker.combine_gbt(path, "all", len(regions))  # CHANGE TO "pair" if wanting to combine in gbt pairs not all produced
            print("Combined file created")
            if os.path.exists(os.path.dirname(path2)):
                GbtPacketMaker.combine_gbt(path2, "all", len(regions))  # combine the second file as well
                print("Combined file 2 created")




#GbtPacketMaker([0.0, 0.4, 1.5, 2.6, 3.7],[1,2,4,8,13]).make_gbt(32, 20, "test","yes")
#GbtPacketMaker.vertical_pattern("upper", [20, 21], 4, 0, bc_gap=96, bc_gap_pl=1)
#GbtPacketMaker.horizontal_pattern("upper", 4, 3, 7, [20, 21], 0,  bc_gap_pl=1)
# # # BELOW ARE THE UPPER :
# #[4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 30, 31, 36, 37, 38, 39, 44, 45, 46, 47, 52, 53, 54, 55, 60, 61, 62, 63]
