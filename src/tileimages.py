#!/usr/bin/env python
'''This script composites color thumbnails into larger images
 representing entire lanes and entire flowcells per image'''


import os, sys, glob
from subprocess import check_output, CalledProcessError
import shlex


def execute(execstring):
    print execstring
    sys.stdout.flush()
    try:
        check_output(execstring.split())
    except CalledProcessError, e:
        if e.returncode == 1:
            print "Warning!  some files not found!"
        else:
            sys.exit("Freakout!")


def detecttype(somedir):
   # We are reading these files, used to communicate with MAKE
    try:
        a = open("thumbnailpolish.type").read().strip()
        return a
    except IOError:
        sys.exit("Can't find config file thumbnailimages.type")


def howmanycycles(somedir):
    '''Checks for the existence of directories for cycles, returns int.'''
    try:
        a = int(open("thumbnailpolish.numcycles").read().strip())
        return a
    except IOError:
        sys.exit("Can't find config file thumbnailimages.numcycles.")


def testhiseq(somedir):
    try:
        a = open("thumbnailpolish.tree").read().strip()
        return a
    except IOError:
        sys.exit("Can't find config file thumbnailimages.tree")


def test_func(list_of_file, out_file, MODE, curr_cycle=0):
    if os.path.isfile(list_of_file[0]):
        if MODE == "pieces":
            execute("convert +append -border 1 " + " ".join(list_of_file) + " " + out_file)
        elif MODE in ("gather1", "gather2"):
            execute("convert -append " + " ".join(list_of_file) + " " + out_file)
            if MODE == "gather1":
                str_to_exe = ("convert " + out_file + " -pointsize 120 -draw \"text 25,200 'C" + 
                                                            str(curr_cycle) + "'\" " + out_file)
            elif MODE == "gather2":
                str_to_exe = ("convert " + out_file + " -pointsize 40 -draw \"text 5,75 'C" + 
                                                            str(curr_cycle) + "'\" " + out_file)
            check_output(shlex.split(str_to_exe)) # shlex.split mandatory to have a proper exec
    else:
        print "skipping creating", out_file, "can't find", list_of_file


def main():

    TYPE = detecttype(".")
    TREE = testhiseq("")

    if TYPE == "HISEQ":  # Hiseq with 8 x 6 tiles
        print "Using HISEQ recipe"
        lane = ['1', '2', '3', '4', '5', '6', '7', '8']
        iter1 = ['11', '12', '13', '21', '22', '23']
        iter2 = ['01', '02', '03', '04', '05', '06', '07', '08']
    elif TYPE == "HISEQ2":  # HISEQ with 16 x 6 tiles
        print "Using HISEQ2 recipe"
        lane = ['1', '2', '3', '4', '5', '6', '7', '8']
        iter1 = ['11', '12', '13', '21', '22', '23']
        iter2 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16']
    elif TYPE == "GAII":   # GAII  doesn't count the same way
        print "Using GAII recipe"
        lane = ['1', '2', '3', '4', '5', '6', '7', '8']
        tiles = ["%d" % i for i in range(1, 51)]
        tiles = ["%d" % i for i in range(50, 0, -1)]
        tile2 = ["%d" % i for i in range(100, 50, -1)]
        tile2 = ["%d" % i for i in range(51, 101)]
        iter1 = [""]
        iter2 = ["%d" % i for i in range(1, 51)]    # we use iter2 to name the intermediates
        gaiitiles = zip(tiles, tile2)
    elif TYPE == "MISEQ" and TREE == "MISEQ1": # MISEQ recipe
        print "Using MISEQ1 recipe"
        lane = ["1"]
        iter1 = [""]
        iter2 = ["1", "2", "3", "4", "5", "6", "7", "8"]
    elif TYPE in ("MISEQ", "MISEQ2") and TREE in ("MISEQ2", "HISEQ2", "HISEQ"): # MISEQ2 or HISEQ2 recipe (modif Fe)
        print "Using MISEQ2 recipe"
        lane = ["1"]
        iter1 = ['11', '21']
        iter2 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
    elif TYPE == "NEXTSEQ": # NEXTSEQ
        print "Using NEXTSEQ recipe"
        lane = ["1", "2", "3", "4"]
        iter1 = ['11', '12', '13', '21', '22', '23']
        iter2 = ['101', '106', '112', '201', '206', '212', '301', '306', '312']

    else:
        sys.exit("Can't identify format")

    NUMCYCLES = howmanycycles("L001")
    print "NUMCYCLES", NUMCYCLES
    CYCLES = range(1, NUMCYCLES+1)
    #CYCLES = range(150, 200) # To generate pics for only a portion of all cycles
    for l1 in lane:
        for j in CYCLES:
            filelist, filelist2 = [], []
      #     create set of strips "org"
            srcdir = "L00%s/C%s.1" % (l1, j)
            destdir = "L00%s/C%s.1" % (l1, j)
            if TYPE != "GAII":
                for i2 in iter2:
                    filelist, filelist2 = [], []
                    for i1 in iter1:
                        filelist.append(srcdir + "/s_%s_%s%s_crop.gif" % (l1, i1, i2))
                        filelist2.append(srcdir + "/s_%s_%s%s_crop2.gif" % (l1, i1, i2))
                    tilefileg = destdir + "/org_%02d_%03d.gif" % (int(i2), j)
                    tilefileg2 = destdir + "/org2_%02d_%03d.gif" % (int(i2), j)
                    test_func(filelist, tilefileg, "pieces")
                    test_func(filelist2, tilefileg2, "pieces")
                   
                    
            else:  # TYPE == "GAII"
                for (counter, pair) in enumerate(gaiitiles):
                    filelist = []
                    for i1 in pair:
                        filelist.append(srcdir + "/s_%s_%s_crop.gif" % (l1, i1))
                    tilefileg = destdir + "/org_%02d_%03d.gif" % (counter + 1, j)
                    if not os.path.isfile(tilefileg):
                        if os.path.isfile(filelist[0]):
                            execute("convert +append " + " ".join(filelist) + " " + tilefileg)
                        else:
                            print "skipping creating", tilefileg, "can't find", filelist[0]
                    else:
                        print "skipping creating", tilefileg, "since it already exists"

      #     create set of strips "orh" in wholeimages
            srcdir = "L00%s/C%s.1" % (l1, j)
            destdir = "wholeimages"
            if not os.path.isdir(destdir):
                os.system("mkdir " + destdir)
            filelist, filelist2 = [], []
            for i2 in iter2:
                tilefileg = srcdir + "/org_%02d_%03d.gif" % (int(i2), j)
                tilefileg2 = srcdir + "/org2_%02d_%03d.gif" % (int(i2), j)
                filelist.append(tilefileg) ; filelist2.append(tilefileg2)

            tilefileh = destdir + "/orh-%s_%03d.gif" % (l1, j)
            tilefileh2 = destdir + "/orh2-%s_%03d.gif" % (l1, j)
            test_func(filelist, tilefileh, "gather1", j)
            test_func(filelist2, tilefileh2, "gather2", j)
            #if os.path.isfile(tilefileh):
            #    print "skipping creation of %s since %s already exists" % (tilefileh, tilefileh)
            #elif os.path.isfile(filelist[0]) and not TYPE:
            #    execute("convert -append " + " ".join(filelist) + " "+ tilefileh)
            #elif os.path.isfile(filelist[0]) and TYPE:
            #    execute("convert -append " + " ".join(filelist) + " "+ tilefileh)
            #else:
            #    print "can't find requisite ", filelist[0], "needed to build ", tilefileh

    proceed = False
    if proceed == True:
        #     create whole-cell images cell-
        for j in CYCLES:
            filelist, filelist2 = [], []
            for l1 in lane:
                srcdir = "wholeimages"
                destdir = "wholeimages"
                tilefileh = srcdir + "/orh-%s_%03d.gif" % (l1, j)
                tilefileh2 = srcdir + "/orh2-%s_%03d.gif" % (l1, j)
                filelist.append(tilefileh) ; filelist2.append(tilefileh2)
            if not os.path.isdir(destdir):
                os.system("mkdir " + destdir)
            celltarget = destdir + "/cell-%03d.gif" % (j,)
            cellsmalltarget = destdir + "/cell-%03d.small.gif" % (j,)
            cellinsettarget = destdir + "/cell-%03d.inset.gif" % (j,)
            celltinytarget = destdir + "/cell-%03d.tiny.gif" % (j,)
        # create whole cell images
            rotate = "90"
            if TYPE == "NEXTSEQ":
                rotate = "270"
            if not os.path.isfile(celltarget):
                if os.path.isfile(filelist[0]):
                    execute("convert -border 2 -rotate " + rotate + " -append " + " ".join(filelist) + " " + celltarget)
                else:
                    print "skipping creating", celltarget, "because requisite", filelist[0], "not found"
            else:
                print "skipping creating", celltarget, "because it already exists"
        # create small version
            if not os.path.isfile(cellsmalltarget):
                if os.path.isfile(celltarget):
                    execute("convert -resize 25% " + "%s %s" % (celltarget, cellsmalltarget))
                    execute("convert -resize  5% " + "%s %s" % (celltarget, celltinytarget))
                else:
                    print "skipping creating", cellsmalltarget, "because requisite", celltarget, "not found"
            else:
                print "skipping creating", cellsmalltarget, "because it already exists"
        # create inset
            if not os.path.isfile(cellinsettarget):
                if os.path.isfile(cellsmalltarget):
                    if TYPE == "HISEQ" or TYPE == "HISEQ2":
                        execute("convert %s  -page +700+200 L001/C%d.1/s_1_%s%s_crop2.gif  -mosaic %s" % (cellsmalltarget, j, iter1[0], iter2[0], cellinsettarget))
                    if TYPE == "MISEQ1" or TYPE == "GAII" or TYPE == "MISEQ2":
                        execute("convert -append %s  L001/C%d.1/s_1_%s%s_crop2.gif  -mosaic %s" % (cellsmalltarget, j, iter1[0], iter2[0], cellinsettarget))
                else:
                    print "skipping creating", cellinsettarget, "because requisite", cellsmalltarget, "is missing"
            else:
                print "skipping creating", cellinsettarget, "because it already exists"

                
    for l1 in lane:
        srcdir = "wholeimages"
        destdir = "wholeimages"
        bigtile = destdir + "/tile-lane%s.big.gif" % (l1,)
        bigtile2 = destdir + "/tile-lane%s.big2.gif" % (l1,)
        smalltile = destdir + "/tile-lane%s.small.gif" % (l1,)
        tinytile = destdir + "/tile-lane%s.tiny.gif" % (l1,)
        orhlist, orhlist2 = [], []
        for j in CYCLES:
            orhfile = srcdir + "/orh-%s_%03d.gif" % (l1, j)
            orhfile2 = srcdir + "/orh2-%s_%03d.gif" % (l1, j)
            orhlist.append(orhfile) ; orhlist2.append(orhfile2)
        execute("convert -border 2 " + " ".join(orhlist) + " +append " + bigtile)
        execute("convert -border 2 " + " ".join(orhlist2) + " +append " + bigtile2)
        if not os.path.isfile(smalltile):
            execute("convert -resize 25%" + " -border 3 " + " ".join(filelist) + " +append " + smalltile)
        else:
            print "skipping creating", smalltile, "since it already exists"
        if not os.path.isfile(tinytile):
            execute("convert -resize 12.5%" + " -border 2 " + " ".join(filelist) + " +append " + tinytile)
        else:
            print "skipping creating", smalltile
        
        print "CYCLES TREATED (for big pics):", list(CYCLES)[0], "TO", list(CYCLES)[-1]

    # TOUTE CETTE PARTIE BUGGEE
    # largecellmovie = destdir + "/movie-lg.mp4"
    # smallcellmovie = destdir + "/movie-sm.mp4"
    # insetcellmovie = destdir + "/movie-in.mp4"
    # tinycellmovie = destdir + "/movie-ty.mp4"

    # large_quality = " "
    # if TYPE == "NEXTSEQ":
        # large_quality = " -q 1 "
    # if not os.path.isfile(largecellmovie):
        # execute("avconv -r 5 -i " + destdir + "/cell-%03d.gif  "%j + large_quality + largecellmovie)  # default compression ca. -q 31 ok
    # else:
        # print "skipping creating", largecellmovie

    # if not os.path.isfile(smallcellmovie):
        # execute("avconv -r 5 -i " + destdir + "/cell-%03d.small.gif -q 1   "%j + smallcellmovie) # high quality / no compression
    # else:
        # print "skipping creating", smallcellmovie
    # if not os.path.isfile(insetcellmovie):
        # execute("avconv -r 5 -i " + destdir + "/cell-%03d.inset.gif -q 1  " + insetcellmovie)  # high quality / no compression
    # else:
        # print "skipping creating", insetcellmovie
    # if not os.path.isfile(tinycellmovie):
        # execute("avconv -r 5 -i " + destdir + "/cell-%03d.tiny.gif -q 1  " + tinycellmovie)  # high quality / no compression
    # else:
        # print "skipping creating", tinycellmovie

main()

