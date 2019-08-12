#!usr/bin/python3
from collections import Counter
import GbtPacketMaker

class GbtPacketChecker:
    def __init__(self, directory, input_gbt):
        self.directory = directory
        self.input_gbt = input_gbt

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
    def track_pl_hit(input_pl_ls):  # KEEP TRACK OF ALL THE MULTIPLE PLANES
        pl_ls = [int(pl) for pl in input_pl_ls]
        count = Counter(pl_ls)
        multiple_hit_pl = {}
        for pl in list(set(pl_ls)):
            if count[pl] > 1:
                multiple_hit_pl[pl] = count[pl]
        return multiple_hit_pl  # {pl: count, ...}

    def extract(self):
        '''
        Extracts specific bits and make them into corresponding lists of Hit Map, ART data, and Region data.
        :return: Hit Map, ART data, Region Number
        '''
        copy =[]
        f = open(self.directory + self.input_gbt, 'r')    # locate and open file
        for line in f:
            if line != '00000001 01':
                copy.append(line[0:8])

        f.close()
        hitmap = copy[1][2:8] + copy[2][0:2]     # read second line 2:7 and third line 0:1 for hit map
        artdata =copy[2][4:] + copy[3]           # third line 4:7 and fourth line 0:7 for art data
        region = copy[0][-2:]
        return hitmap, artdata, region

    def read_hitmap(self):
        '''
        Converts Hit Map into a list that contains information about planes and vmm's hit: e.g. [0.2, 2.1] when the third vmm of the first plane and the second vmm of the third plane are hit.
        '''
        hitmap, artdata, region = GbtPacketChecker.extract(self)
        hitmap_bin =[]
        for each in hitmap:                     # convert hexadecimal digits to integer to binary
            temp = str(bin(int(each, 16))[2:])
            if len(temp) == 4:
                hitmap_bin.append(temp)
            else:
                hitmap_bin.append(((4-len(temp))*"0"+temp))

        hitmap_pl = GbtPacketChecker.chunky(hitmap_bin,2)   # consolidate into groups of two sets of four digits
        hitmap_ls = []
        for each in hitmap_pl:      # e.g. ['00000100', '00000100', '00000101', '00000100']
            hitmap_ls.append(''.join(map(str, each)))

        hitmap_read = []
        for i in range(len(hitmap_ls)):                     # [3.2, 2.2, 1.2, 1.0, 0.2]
            for j in range(len(hitmap_ls[i])):
                if hitmap_ls[i][j] != '0':
                    hitmap_read.append((3-i)+round(.1*(7-j), 1))  # flips the list

        hitmap_read.sort()
        return hitmap_read                                  # return lists of hit vmm's and number of hits

    def read_artdata(self):     # read and convert ART data
        '''
        Converts ART data into a list of hit channels: e.g. [37, 28] when channel numbers 37 and 28 are hit.
        '''
        hitmap, artdata, region = GbtPacketChecker.extract(self)
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
        artdata_read = [int(artdata_six[i],2) for i in range(len(artdata_six))]
        artdata_read.reverse()      #    IMPORTANT TO REVERSE
        return artdata_read

    def check(self, hitmap_intended, artdata_intended):            # check if hit map and art data are correct
        '''
        Checks if the actual GBT packet follow the expected / intended hits pattern by comparing the produced list to the input list.
        Just like the output format of read_hitmap() and read_artdata(), the input format of check() should be [plane.vmm, ...][channel, ...]
        '''
        hitmap_read, artdata_read = GbtPacketChecker.read_hitmap(self), GbtPacketChecker.read_artdata(self)
        hitmap_intended, artdata_intended = zip(*sorted(zip(hitmap_intended, artdata_intended))) # in case not in order
        hitmap_intended, artdata_intended = list(hitmap_intended), list(artdata_intended)
        if len(hitmap_read) != len(artdata_read):
            print("ERROR: The lengths of hit map and ART data read don't match up. Fix the code.")
            exit()
        if hitmap_read== hitmap_intended and artdata_read == artdata_intended:
            print("Hit map read=%s and ART data read=%s match up with intended hits=%s%s." % (hitmap_read, artdata_read, hitmap_intended, artdata_intended))
            return True
        else:
            print("Hit map read=%s and ART data read=%s don't match up with intended hits=%s%s." %(hitmap_read,artdata_read, hitmap_intended, artdata_intended))
            return False

    def identify_vmm(self, hitmap_intended, artdata_intended):     # identify which vmm's are in correctly connected
        '''
        Checks if there are possibility of misconnected fibers:
        If there are only two hits that might be mismatched, the function determines whether the corresponding two planes' fibers are mismatched or not.
        If there are more than two hits that might be mismatched, the function prints which planes has multiple hits in {pl: count, ...} format.::


            # First make a GBT packet
            GbtPacketMaker.GbtPacketMaker([0.2, 1.0, 1.2, 2.2 3.2],[10,10,12,11,10]).make_gbt(32, 20, "test","yes")
            test1 = GbtPacketChecker("GBT_packet_dir_test/","GBT_packet_BC=32_fiber=20_[0.2, 1.0, 1.2, 2.2, 3.2][10, 10, 11, 10, 10]")
            test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 12, 11, 10])
            test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 11, 12, 10] # third and fourth fibers swapped


        '''
        _, _, region = GbtPacketChecker.extract(self)
        hitmap_read, artdata_read = GbtPacketChecker.read_hitmap(self), GbtPacketChecker.read_artdata(self)
        hitmap_intended, artdata_intended = zip(*sorted(zip(hitmap_intended, artdata_intended)))  # in case not in order
        hitmap_intended, artdata_intended = list(hitmap_intended), list(artdata_intended)
        print("Expected hit planes/vmm's = %s, Expected hit channels = %s, GBT Packet's hit planes/vmm's = %s, "
              "GBT Packet's hit channels = %s" %(hitmap_intended, artdata_intended, hitmap_read, artdata_read))
        if GbtPacketChecker.check(self, hitmap_intended, artdata_intended): # Checks if expected and result match up
            print(hitmap_intended, artdata_intended, hitmap_read, artdata_read)
            print("Intended hits and Hit Map and ART data read match up so no need for further investigation.")
            exit()

        truncated_intended_ls = [round(hitmap_intended[i]- int(hitmap_intended[i]),1) for i in range(len(hitmap_intended))]
        truncated_read_ls = [round(hitmap_read[i]- int(hitmap_read[i]), 1) for i in range(len(hitmap_read))]
        if sorted(artdata_read) == sorted(artdata_intended) and sorted(truncated_read_ls) == sorted(truncated_intended_ls):
            print("Possibly misconnected fibers. Next Step is to see if there are multiple hits of the same planes.")
        else:
            print("Not possible that fibers are misconnected although Hit Map and ART data read don't match up with intended hits. Find the cause of the mismatch problem elsewhere.")
            exit()

        if len(GbtPacketChecker.track_pl_hit(hitmap_read)) > 0:
            multiple_hit_pl = list(GbtPacketChecker.track_pl_hit(hitmap_intended).keys())
            print("There are multiple hits on this/these planes :plane %s" % multiple_hit_pl)
            for each in not_matched:
                if int(hitmap_intended[each]) in multiple_hit_pl:
                    print(
                        "Among the possible candidates, there is/are ones with multiple hits on planes which need to be checked.")
                    print(int(hitmap_intended[each]), multiple_hit_pl)

        match = []
        not_matched = []
        for i in range(len(hitmap_read)):
            if [hitmap_intended[i], artdata_intended[i]] == [hitmap_read[i], artdata_read[i]]:   match.append(i)
            else:   not_matched.append(i)

        if len(not_matched) == 2:
            if int(region) % 2 == 0:
                pl_ls = ['x0', 'x1', 'u0', 'v0']
            else:
                pl_ls =  ['u1', 'v1', 'x0', 'x2']
            print("%s are possible candidates of their fibers being swapped."%([pl_ls[i] for i in not_matched]))
        elif len(not_matched) > 2:
            print("More than two planes that are possible candidates of misconnected fibers.")



#GbtPacketMaker.GbtPacketMaker([0.0, 1.0, 2.0, 3.0],[1,2,1,2,13]).make_gbt(32, 20, "test","yes")
#test1 = GbtPacketChecker("GBT_packet_dir_test/","GBT_packet_BC=32_fiber=20_[0.2, 1.0, 1.2, 2.2, 3.2][10, 10, 11, 10, 10]")
# test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 10, 11, 10])
#test1.identify_vmm([0.2, 1.2, 2.2, 1.0, 3.2],[10, 11, 10, 10, 10]
#test1.identify_vmm([0.2, 1.0, 1.2, 2.2, 3.2],[10, 10, 10, 11, 10])  # third and fourth fiber swapped
