'''
GbtPacketChecker has two main functions. It can read a GBT packet before its simulation to check whether the intended hit data, which the user feeds in as an input, matches with the user's GBT packet data. GbtPacketChecker's second function includes determining and returning which planes, vmms, and channels are hit in a give GBT packet and comparing them  with the intended hit data. 
'''
#!usr/bin/python3
from collections import Counter
import GbtPacketMaker
import random

class GbtPacketChecker:
    def __init__(self, directory, input_gbt):
        self.directory = directory
        self.input_gbt = input_gbt

    @staticmethod
    def simulate(make=False, dir_name='test', region=20, repeat=0):
        '''
        Option 1: Prints hit track information by simulates a GBT packet by randomly generating a possible number of hit channels and hit track information.
        Option 2: Generates a GBT packet with printed hit track information.
        Recursive if asked to be repeated.::

                # Generates five possible hit track
                GbtPacketChecker.simulate(repeat=5)


        :param False/bool/optional make: If True, makes an actual GBT packet in a directory
        :param "test"/string/optional dir_name: default value is "test" (path is then "./GBT_packet_dir_test" as path is "GBT_packet_dir_%s/" % dir_name )
        :param 20/int/optional region: region number
        :param 0/int/optional repeat: number of packets to be simulated/generated
        :return: a list of vmm's hit and channels' hit in a format of [plane.vmm, ...], [channel_hit,...]
        '''
        vmm_list = []
        channel_list = []
        num_hit = random.choice(range(1, 8))
        for i in range(num_hit):
            vmm_random = random.choice(range(8))
            pl_random = random.choice(range(4))
            ch_random = random.choice(range(64))
            vmm_list.append(pl_random + round(vmm_random * .1, 1))
            channel_list.append(ch_random)
        if make:
            GbtPacketMaker(vmm_list, channel_list).make_gbt(32, region, dir_name, "yes") # "yes" for adding the finish line

        if repeat != 0:                                                  # recursive if asked to be repeated
            GbtPacketChecker.simulate(make, repeat=repeat-1)

        print(vmm_list, channel_list)
        return vmm_list, channel_list

    @staticmethod
    def track_pl_hit(input_pl_ls):                          # returns a dictionary of planes that have more than one hits
        pl_ls = [int(pl) for pl in input_pl_ls]
        count = Counter(pl_ls)
        multiple_hit_pl = {}
        for pl in list(set(pl_ls)):
            if count[pl] > 1:
                multiple_hit_pl[pl] = count[pl]
        return multiple_hit_pl                  # {pl: count, ...}

    def extract(self):
        '''
        Extracts specific bits and make them into corresponding lists of Hit Map, ART data, and region number.
        :return: Hit Map, ART data, region Number
        '''
        copy =[]
        with open(self.directory + self.input_gbt, 'r') as f:    # locates and opens file
            for line in f:
                if line != '00000001 01':
                    copy.append(line[0:8])

        hitmap = copy[1][2:8] + copy[2][0:2]                # reads second line 2:7 and third line 0:1 for Hit Map
        artdata =copy[2][4:] + copy[3]                      # third line 4:7 and fourth line 0:7 for ART data
        region = copy[0][-2:]
        return hitmap, artdata, region

    def read_hitmap(self):
        '''
        Converts Hit Map into a list that contains information about planes and vmm's hit
        :return: a list in a format [plane.vmm,...]
        e.g. Returns [0.2, 2.1] when the third vmm of the first plane and the second vmm of the third plane are hit.
        '''
        hitmap, _, _ = GbtPacketChecker.extract(self)
        hitmap_bin =[]
        for each in hitmap:                                 # converts hexadecimal digits to integer to binary
            temp = str(bin(int(each, 16))[2:])
            if len(temp) == 4:
                hitmap_bin.append(temp)
            else:
                hitmap_bin.append(((4-len(temp))*"0"+temp))

        hitmap_pl = GbtPacketMaker.GbtPacketMaker.chunky(hitmap_bin, 2)     # consolidates into groups of two sets of four digits
        hitmap_ls = []
        for each in hitmap_pl:                              # e.g. ['00000100', '00000100', '00000101', '00000100']
            hitmap_ls.append(''.join(map(str, each)))

        hitmap_read = []
        for i in range(len(hitmap_ls)):                     # [3.2, 2.2, 1.2, 1.0, 0.2]
            for j in range(len(hitmap_ls[i])):
                if hitmap_ls[i][j] != '0':
                    hitmap_read.append((3-i)+round(.1*(7-j), 1))  # reverses the list

        hitmap_read.sort()
        return hitmap_read                                  # returns lists of hit vmm's and number of hits

    def read_artdata(self):                                 # reads and converts ART data
        '''
        Converts ART data into a list of hit channels
        :return: [channel_hit, ...]
        e.g. Returns [37, 28] when channel numbers 37 and 28 are hit.
        '''
        _, artdata, _ = GbtPacketChecker.extract(self)
        artdata_int = []
        artdata_dig = []
        for each in artdata:
            artdata_int.append(int(each, 16))
            artdata_dig.append(bin(int(each, 16))[2:].zfill(4))

        if artdata_dig[0] =='0000':
            for i in range(len(artdata_dig)-1):
                if artdata_dig[i+1] != '0000':
                    artdata_dig = artdata_dig[i+1:]
                    break

        artdata = "".join(artdata_dig)
        if len(artdata) % 6 != 0:
                artdata = "0"*(6-(len(artdata)%6)) + artdata

        artdata_six = [artdata[i: i+6] for i in range(0, len(artdata), 6)]
        artdata_read = [int(artdata_six[i], 2) for i in range(len(artdata_six))]
        artdata_read.reverse()
        return artdata_read

    def check(self, hitmap_intended, artdata_intended, new_hitmap=[], new_artdata=[]):      # checks if hit map and art data are correct
        '''
        Option 1: Checks if the actual GBT packet follow the expected hit pattern by comparing the produced list to the input list.
        Option 2: Checks if the input Hit Map and ART data follow the expected hit pattern after swapping fibers. This option is chosen if new_hitmap and new_artdata are not empty lists and their lenghts are the same.
        The code exits if the lengths of hit vmm's and channel's are not equal.
        Similar to the output format of read_hitmap() and read_artdata(), the input format of check() should be [plane.vmm, ...][channel, ...]
        :return: Returns True if expected hit pattern and the GBT packet has the same hit track and false otherwise.
        '''
        if new_hitmap == [] and new_artdata == []:
            hitmap_read, artdata_read = GbtPacketChecker.read_hitmap(self), GbtPacketChecker.read_artdata(self)
            hitmap_intended, artdata_intended = zip(*sorted(zip(hitmap_intended, artdata_intended))) # sorts in an ascending order
            hitmap_intended, artdata_intended = list(hitmap_intended), list(artdata_intended)
            if len(hitmap_read) != len(artdata_read):
                print("ERROR: The lengths of hit map and ART data read don't match up. Fix the code.")
                exit()
        elif new_hitmap !=[] and new_artdata != [] and len(new_hitmap) == len(new_artdata):
            hitmap_read, artdata_read = new_hitmap, new_artdata
        else:
            print("Wrong input for new_hitmap and new_artdata.")
            exit()

        if hitmap_read == hitmap_intended and artdata_read == artdata_intended:
            print("Hit map read=%s and ART data read=%s match up with intended hits=%s%s." % (hitmap_read, artdata_read, hitmap_intended, artdata_intended))
            return True
        else:
            print("Hit map read=%s and ART data read=%s don't match up with intended hits=%s%s." %(hitmap_read, artdata_read, hitmap_intended, artdata_intended))
            return False

    def identify_vmm(self, hitmap_intended, artdata_intended):     # identify which vmm's are in correctly connected
        '''
        Checks if there are possibilities of misconnected fibers.
        If there are only two hits that might be mismatched, the function determines whether the corresponding two planes' fibers are mismatched or not.
        If there are more than two hits that might be mismatched, the function prints which planes has multiple hits in {pl: count, ...} format.::


            # Make a GBT packet in a directory called "GBT_packet_dir_test"
            GbtPacketMaker.GbtPacketMaker([0.2, 1.0, 1.2, 2.2 3.2],[10,10,12,11,10]).make_gbt(32, 20, "test","yes")

            #Create an instance of the GbtPacketChecker with the created GBT packet
            test1 = GbtPacketChecker("GBT_packet_dir_test/","GBT_packet_BC=32_fiber=20_[0.2, 1.0, 1.2, 2.2, 3.2][10, 10, 11, 10, 10]")

            # Check whether the intended hit data match with the data within the GBT packet
            test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 12, 11, 10])      # Match
            test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 11, 12, 10]       # Third and fourth fibers swapped


        '''
        _, _, region = GbtPacketChecker.extract(self)
        hitmap_read, artdata_read = GbtPacketChecker.read_hitmap(self), GbtPacketChecker.read_artdata(self)
        hitmap_intended, artdata_intended = zip(*sorted(zip(hitmap_intended, artdata_intended)))  # in case not in order
        hitmap_intended, artdata_intended = list(hitmap_intended), list(artdata_intended)
        #print("Expected hit planes/vmm's = %s, Expected hit channels = %s, GBT Packet's hit planes/vmm's = %s,
                #GBT Packet's hit channels = %s" %(hitmap_intended, artdata_intended, hitmap_read, artdata_read))

        if GbtPacketChecker.check(self, hitmap_intended, artdata_intended): # checks if expected hit data and GBT packet hit data match up
            print(hitmap_intended, artdata_intended, hitmap_read, artdata_read)
            print("Intended hits and Hit Map and ART data read match up so no need for further investigation.")
            exit()

        match = {}
        not_match = {}
        match['idx']= []
        not_match['idx'], not_match['pl_intended'], not_match['pl_read'], not_match['vmm_read'], \
            not_match['artdata_intended'], not_match['artdata_read'] = [], [], [], [], [], []
        # collects not matched plane information in GBT packet that don't match with expected channels hit
        for i in range(len(hitmap_read)):
            if [hitmap_intended[i], artdata_intended[i]] == [hitmap_read[i], artdata_read[i]]:
                match['idx'].append(i)
            else:
                not_match['idx'].append(i)
                not_match['pl_intended'].append(int(hitmap_intended[i]))
                not_match['pl_read'].append(int(hitmap_read[i]))
                not_match['vmm_read'].append(round(hitmap_read[i]-int(hitmap_read[i]),1))
                not_match['artdata_read'].append(artdata_read[i])
                not_match['artdata_intended'].append(artdata_intended[i])

        caution = False                                     # checks if unmatched planes are planes that have multiple hits
        if len(GbtPacketChecker.track_pl_hit(hitmap_read)) > 0:
            multiple_hit_pl = list(GbtPacketChecker.track_pl_hit(hitmap_intended).keys())
            print("There are multiple hits on this/these planes :plane %s" % multiple_hit_pl)
            for each in not_match['idx']:
                if int(hitmap_intended[each]) in multiple_hit_pl:
                    print(
                        "Among the possible candidates, there is/are ones with multiple hits on planes which need to be checked.")
                    #print(int(hitmap_intended[each]), multiple_hit_pl)
                    caution = True

        #PREDICT
        new_hitmap = hitmap_intended
        print(not_match)

        # for i in range(len(new_hitmap)):
        #     skip = False
        #     for j in range(len(not_match['pl_read'])):
        #         if int(new_hitmap[i]) == not_match['pl_read'][j]:
        #             skip = True
        #             new_hitmap[i] = not_match['pl_intended'][j] + not_match['vmm_read']

        print(hitmap_intended, new_hitmap)
        if GbtPacketChecker.check(self, hitmap_intended, artdata_intended, new_hitmap, artdata_read):
            print(new_hitmap)

        if len(not_match['idx']) == 2 and not caution:
            if int(region) % 2 == 0:
                pl_ls = ['x0', 'x1', 'u0', 'v0']
            else:
                pl_ls = ['u1', 'v1', 'x0', 'x2']
            print("%s are possible candidates of their fibers being swapped." % ([pl_ls[i] for i in not_match['idx']]))

        elif len(not_match['idx']) > 2:
            print("More than two planes don't match with expected hit patterns.")


#GbtPacketMaker.GbtPacketMaker([0.0, 1.0, 2.0, 3.0],[1,2,1,2,13]).make_gbt(32, 20, "test","yes")
#test1 = GbtPacketChecker("GBT_packet_dir_test/","GBT_packet_BC=32_fiber=20_[0.2, 1.0, 1.2, 2.2, 3.2][10, 10, 11, 10, 10]")
# test1.identify_vmm([0.2, 1.0, 1.2,= 2.2, 3.2],[10, 10, 10, 11, 10])
#test1.identify_vmm([0.2, 1.2, 2.2, 1.0, 3.2],[10, 11, 10, 10, 10])
#test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 10, 11, 10])  # third and fourth fiber swapped
GbtPacketChecker.simulate(repeat=5)
