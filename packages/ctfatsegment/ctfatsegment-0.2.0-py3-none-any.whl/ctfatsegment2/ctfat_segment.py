import copy
import csv
import math
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from collections.abc import Sequence

import nibabel as nib
import numpy as np
from PIL import Image
from scipy import interpolate

#from scipy.ndimage import measurements as ndm
from scipy import ndimage as ndi
from skimage.draw import disk

from ctfatsegment2 import __version__

VALUES = {
    "file" : "",
    "file2":"",
    "img" : 0,
    "useDB": True,

    "innerContour" : 0,
    "bodyContour" : 0,

    "vatMask" : 0,
    "satMask" : 0,

    # includeBottomVoxels fv
    "emptyRectMargin" : 5,

    # isTopVoxels fv
    "yTopvoxelBorder" : 50,

    # findCanal fv
    "zBottomMargin" : 50,
    "xSpinalBorder" : 30,
    "xSpinalBorder_mm" : 30,

    # createMask fv
    "canalSize" : 24,
    "rectMargin" : 10,
    "rectMargin2" : 15,
    "yTopBorder" : 20,
    "yBottomBorder" : 10,
    "rectHeight" : 18,
    "verticalBorder" : 5,
    "xBorder" : 10,
    "maxHeight" : 29,

    "redius" : 5,

    # createIntensityProfile fv
    "cprSpinalBorder" : 35,
    "cprSpinalBorder_mm" : 30,

    # mm konstansok
    "zThickness" : 5,
    "dDiff" : 5,

    "emptyRectSize" : 10,
    "emptyRectSize_mm" : 8,

    "zShiftMaxIntSlice" : 20,
    "zShiftMaxIntSlice_mm" : 100,
    "zShiftStartVertebraBorder" : 3,
    "zShiftStartVertebraBorder_mm" : 15,
    "zRefDiff1stBorder" : 6,
    "zRefDiff1stBorder_mm" : 30,
    "zRefDiffBorders" : 10,
    "zRefDiffBorders_mm" : 50,
    "zDiff" : 4,
    "zDiff_mm" : 20,

    "n" : 1
}


def computeParameters():
    dz = VALUES["img"].header["pixdim"][3]

    VALUES["zThickness"] = int(dz)

def emptyCenter(size, m, n, img):
    for x in range(m, m + size):
        for y in range(n, n + size):
            if img[x][y] == 1:
                return False

    return True

def includeBottomVoxels(size, m, n, img):
    if img[m - VALUES["emptyRectMargin"]][n - VALUES["emptyRectMargin"]] == 1 and img[m+size+VALUES["emptyRectMargin"]][n-VALUES["emptyRectMargin"]] == 1:
        return True
    #for x in range(m-5, m + size):
        #for y in range(n-5, n):
           # if img[x][y] == 1:
    return False

def isTopVoxels(size, m, n, data):
    for y in range(int(n+size/2), int(n+size/2) + VALUES["yTopvoxelBorder"]):
        if y == data.shape[1]:
            break
        if data[int(m+size/2)][y] == 1:
            return True

    for y in range(int(n+size/2), int(n+size/2) + VALUES["yTopvoxelBorder"]):
        if y == data.shape[1]:
            break
        if data[m][y] == 1:
            return True

    return False

def createMask(size, m, n, data):
    topy = n + size + VALUES["rectMargin"]
    bottomy = -1
    #bottomy = topy - VALUES["canalSize"]

    leftx = m + size + VALUES["rectMargin"]
    rightx = m - VALUES["rectMargin"]

    topinit = False

    for x in range(int(m+size/2), leftx):
        for y in range(int(n+size), int(n+size) + VALUES["yTopBorder"]):
            if y == data.shape[1]:
                break
            if data[x][y] == 1:
                topy = y
                bottomy = int(y - 2*(y - (n+size/2)))
                topinit = True
                break
        if topinit:
            break


    """for y in range(int(n+size/2), int(n+size/2) + 20):
        if y == data.shape[1]:
            break
        if data[int(m+size/2)][y] == 1:
            topy = y
            bottomy = int(y - 2*(y - (n+size/2)))
            topinit = True
            break"""

    if not topinit:
        for y in range(topy, topy - VALUES["canalSize"], -1):
            count = 0
            for x in range(rightx, leftx):
                if data[x][y] == 1:
                    count += 1
                    if count == 3:
                        topy = y
                        bottomy = int(y - 2*(y - (n+size/2)))
                        break
            if count == 3:
                break

    for y in range(int(n+size/2), int(n+size/2) - VALUES["yBottomBorder"], -1):
        if y == 0:
            break
        if data[int(m+size/2)][y] == 1:
            bottomy = y
            break

    if bottomy == -1:
        bottomy = topy - VALUES["rectHeight"]
    #print(topy)
    #print(bottomy)
    leftx = m + size + VALUES["rectMargin2"]
    rightx = m - VALUES["rectMargin2"]

    vCenter = bottomy + int((topy - bottomy)/2)
    hCenter = rightx + int((leftx - rightx)/2)
    leftSpace = []
    rightSpace = []
    holeLeft = False
    holeRight = False
    for i in range(vCenter, vCenter - VALUES["verticalBorder"], -1):
        countRight = 0
        countLeft = 0

        if data[hCenter][i] == 1:
            break

        for j in range(hCenter, leftx):
            if data[j][i] == 0:
                countLeft += 1
                if j == (leftx-1):
                    holeLeft = True
            else:
                break

        for j in range(hCenter, rightx, -1):
            if data[j][i] == 0:
                countRight += 1
                if j == (rightx+1):
                    holeRight = True
            else:
                break

        leftSpace.append(countLeft)
        rightSpace.append(countRight)


    for i in range(vCenter, vCenter + VALUES["verticalBorder"]):
        countRight = 0
        countLeft = 0

        if data[hCenter][i] == 1:
            break

        for j in range(hCenter, leftx):
            if data[j][i] == 0:
                countLeft += 1
                if j == (leftx-1):
                    holeLeft = True
            else:
                break

        for j in range(hCenter, rightx, -1):
            if data[j][i] == 0:
                countRight += 1
                if j == (rightx+1):
                    holeRight = True
            else:
                break

        leftSpace.append(countLeft)
        rightSpace.append(countRight)

    if len(leftSpace) > 0:
        if not holeLeft:
            leftx = hCenter + max(leftSpace)
        else:
            leftx = hCenter + int((topy - bottomy) / 2)

    if len(rightSpace) > 0:
        if not holeRight:
            rightx = hCenter - max(rightSpace)
        else:
            rightx = hCenter - int((topy - bottomy) / 2)

    if data[rightx][topy - int((topy-bottomy)/2)] == 1 and data[leftx][topy - int((topy-bottomy)/2)] == 0:
        for x in range(leftx, leftx + VALUES["xBorder"]):
            if data[x][topy - int((topy-bottomy)/2)] == 1:
                leftx = x
                break

    if topy - bottomy > VALUES["maxHeight"]:
        bottomy = topy - VALUES["rectHeight"]

    for x in range(rightx, leftx):
        for y in range(bottomy, topy):
            #if data[x][y] == 0:
                data[x][y] = 2

def findCanal(size, z, data):
    for y in range(10, data.shape[1]-20):
        start = 10
        end = data.shape[0]-30
        if z < VALUES["zBottomMargin"]:
            start = int(data.shape[0]/2) - VALUES["xSpinalBorder"]
            end = int(data.shape[0]/2) + VALUES["xSpinalBorder"]
        for x in range(start, end):
            if emptyCenter(size, x, y, data) and includeBottomVoxels(size, x, y, data) and isTopVoxels(size, x, y, data):
                createMask(size, x, y, data)
                return

    for y in range(10, data.shape[1]-20):
        start = 10
        end = data.shape[0]-30
        if z < VALUES["zBottomMargin"]:
            start = int(data.shape[0]/2) - VALUES["xSpinalBorder"]
            end = int(data.shape[0]/2) + VALUES["xSpinalBorder"]
        for x in range(start, end):
            if emptyCenter(size, x, y, data) and includeBottomVoxels(size, x, y, data):
                n = y + 1
                while emptyCenter(size, x, n, data) and includeBottomVoxels(size, x, n, data):
                    n += 1
                createMask(size, x, n, data)
                return

def largestComponent(data, thresh = 200):
    filtered_data = np.zeros_like(data)
    filtered_data[data>thresh]=1

    labeledData, _ = ndi.label(filtered_data)
    unique,counts = np.unique(labeledData,return_counts=True)
    counts = zip(unique,counts)
    counts = sorted(counts, key=lambda x: x[1], reverse=True)
    del(counts[0])

    mask = np.zeros(shape=(data.shape[0], data.shape[1], data.shape[2]), dtype=float)
    for x in range(labeledData.shape[0]):
        for y in range(labeledData.shape[1]):
            for z in range(labeledData.shape[2]):
                if labeledData[x][y][z] == counts[0][0]:
                    mask[x][y][z] = 1

    return filtered_data, mask

def largestComponent2D(data):
    #filtered_data = np.zeros_like(data)
    #filtered_data[data>thresh]=1

    labeledData, _ = ndi.label(data)
    unique,counts = np.unique(labeledData,return_counts=True)
    counts = zip(unique,counts)
    counts = sorted(counts, key=lambda x: x[1], reverse=True)
    #delete background
    for i in range(len(counts)):
        if counts[i][0] == 0:
            del(counts[i])
            break
    #del(counts[0])
    mask = np.zeros(shape=(data.shape[0], data.shape[1]), dtype=float)
    for x in range(labeledData.shape[0]):
        for y in range(labeledData.shape[1]):
            if len(counts) > 0:
                if labeledData[x][y] == counts[0][0]:
                    mask[x][y] = 1

    return mask

def labelFilter(data, size = 100):
    labeledData, _ = ndi.label(data)
    unique,counts = np.unique(labeledData,return_counts=True)
    counts = zip(unique,counts)
    counts = sorted(counts, key=lambda x: x[1], reverse=True)
    #delete background
    for i in range(len(counts)):
        if counts[i][0] == 0:
            del(counts[i])
            break
    #del(counts[0])
    mask = np.zeros(shape=(data.shape[0], data.shape[1]), dtype=float)
    for i in range(len(counts)):
        if counts[i][1] > size:
            for x in range(labeledData.shape[0]):
                for y in range(labeledData.shape[1]):
                    if len(counts) > 0:
                        if labeledData[x][y] == counts[i][0]:
                            mask[x][y] = 1

    return mask

# er-e csontot a kor a z. szeleten
def isCollision(mask, circleSlice, z, cx, cy, r):
    for x in range(cx - r, cx + r):
        for y in range(cy - r, cy + r):
            if circleSlice[x][y] == 1 and mask[x][y][z] == 1:
                return True
    return False

def getRectCorners(rect, z):
    p1 = []
    p2 = []
    for x in range(rect.shape[0]):
        for y in range(rect.shape[1]):
            if rect[x][y][z] == 1:
                p1 = [x, y]
                for m in range(x, rect.shape[0]):
                    if  rect[m][y][z] == 0:
                        p2.append(m)
                        break
                for n in range(y, rect.shape[1]):
                    if  rect[x][n][z] == 0:
                        p2.append(n)
                        break
                return p1, p2
    return [0,0], [0,0]

# a teglalap mask minden pontjan ami nem csont voxel, egy r sugaru kort rajzolunk, es novelunk addig,
# amig a kor csontba nem utkozik. A legnagyobb sugaru kor lesz a velo mask.
def findCanalByCircle(mask, rect):
    r = VALUES["redius"]
    canalAreaCircle = np.zeros(shape=(rect.shape[0],rect.shape[1],rect.shape[2]), dtype=float)
    centers = []
    for z in range(rect.shape[2]):
        points = {}
        p1, p2 = getRectCorners(rect, z)

        if p1[0] == 0:
            centers.append([0, 0, z, 0])
            continue

        for x in range(p1[0], p2[0]):
            for y in range(p1[1], p2[1]):
                if mask[x][y][z] == 0:
                    #print(str(x)+" "+str(y)+" "+str(z))
                    circleSlice = np.zeros(shape=(rect.shape[0],rect.shape[1]), dtype=float)
                    rr, cc = disk((x, y), r)
                    circleSlice[rr, cc] = 1
                    while not isCollision(mask, circleSlice, z, x, y, r):
                        r += 1
                        rr, cc = disk((x, y), r)
                        circleSlice[rr, cc] = 1
                    points[r] = [x, y]
                    r = VALUES["redius"]

        if len(points) == 0:
            centers.append([0, 0, z, 0])
            continue
        circleSlice = np.zeros(shape=(rect.shape[0],rect.shape[1]), dtype=float)
        keys = list(reversed(sorted(points.keys())))
        cx = points[keys[0]][0]
        cy = points[keys[0]][1]
        rr, cc = disk((cx, cy), keys[0])
        circleSlice[rr, cc] = 1
        centers.append([cx, cy, z, keys[0]])

        for x in range(cx - keys[0], cx + keys[0]):
            for y in range(cy - keys[0], cy + keys[0]):
                canalAreaCircle[x][y][z] = circleSlice[x][y]

        #print(z)

    #out = nib.Nifti1Image(canalAreaCircle, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_canalCircle_mask.nii")
    return centers, canalAreaCircle

def label(data):
    s = [[1,1,1],
         [1,1,1],
         [1,1,1]]
    labeledData, _ = ndi.label(data, structure=s)
    unique,counts = np.unique(labeledData,return_counts=True)
    counts = zip(unique,counts)
    counts = sorted(counts, key=lambda x: x[1], reverse=True)
    del(counts[0])

    return labeledData, counts

# minden pontra kiszamolja az adott pont, es az elozo szeleten levo pont tavolsagat mm-ben
def getDist(centers):
    #dist = [0]
    centers[0].append(0)
    for i in range(1, len(centers)):
        p1 = centers[i]
        p2 = centers[i-1]
        if centers[i-1][0] == 0:
            p1.append(-1)
            continue
        mmP1 = nib.affines.apply_affine(VALUES["img"].affine, [p1[0], p1[1], p1[2]])
        mmP2 = nib.affines.apply_affine(VALUES["img"].affine, [p2[0], p2[1], p2[2]])
        d = math.sqrt(pow(mmP1[0]-mmP2[0], 2) + pow(mmP1[1]-mmP2[1], 2))
        p1.append(d)

# visszaadja annak a szeletnek az indexet amelyiken y iranyban a legnagyobb a csipocsont
def getLargestHipSlice(boneMask):
    maxHightSlice = 0
    zindex = 0
    for z in range(int(boneMask.shape[2] - boneMask.shape[2]/3)):
        slice = np.zeros(shape=(boneMask.shape[0], boneMask.shape[1]), dtype=float)
        for x in range(boneMask.shape[0]):
            for y in range(boneMask.shape[1]):
                slice[x][y] = boneMask[x][y][z]
        labeledSlice, counts = label(slice)
        max = 0
        for item in counts:
            height = 0
            for y in range(slice.shape[1]):
                for x in range(slice.shape[0]):
                    if labeledSlice[x][y] == item[0]:
                        #print(str(x) + " " + str(y) + " " + str(item[0]))
                        height += 1
                        break
            if height > max:
                max = height
        if max > maxHightSlice:
            maxHightSlice = max
            zindex = z

    return zindex

def getSmoothingStart(boneMask, centers):
    zIndex = getLargestHipSlice(boneMask)
    #print(zIndex)
    count = 0
    for z in range(zIndex + 15, len(centers)):
        if float(centers[z][4]) != -1 and float(centers[z][4]) <= VALUES["dDiff"]:
            count += 1
        else:
            count = 0

        if count == 3:
            return z - 1

    return -1

# a megelozo szelethez kepest adott tavolsagnal nagyobb tavolsagu pont eseten az adott szeleten
# ujrakeresi a velot, a megelozo szelet teglalap maskja alapjan
def smoothCenterLine(boneMask, rectMask, circleMask, csvrows):
    r = VALUES["redius"]
    start = getSmoothingStart(boneMask, csvrows)
    #print("smoothing start:")
    #print(start)
    for z in range(start, len(csvrows)):
        if float(csvrows[z][4]) > VALUES["dDiff"]:
            points = {}
            #p1, p2 = getRectCorners(rectMask, z-1)

            cx = 0
            cy = 0
            rad = 0
            if float(csvrows[z][0]) > 0:
                #for x in range(p1[0], p2[0]):
                    #for y in range(p1[1], p2[1]):
                for x in range(circleMask.shape[0]):
                    for y in range(circleMask.shape[1]):
                        if boneMask[x][y][z] == 0 and circleMask[x][y][z-1] == 1:
                            #if x > 16 and x < boneMask.shape[0] - 16 and y > 16 and y < boneMask.shape[1] - 16:
                                #return
                            circleSlice = np.zeros(shape=(rectMask.shape[0],rectMask.shape[1]), dtype=float)
                            rr, cc = disk((x, y), r)
                            circleSlice[rr, cc] = 1
                            while not isCollision(boneMask, circleSlice, z, x, y, r) and r < 15:
                                r += 1
                                rr, cc = disk((x, y), r)
                                circleSlice[rr, cc] = 1
                            points[r] = [x, y]
                            r = VALUES["redius"]

                if len(points) == 0:
                    break
                circleSlice = np.zeros(shape=(rectMask.shape[0],rectMask.shape[1]), dtype=float)
                keys = list(reversed(sorted(points.keys())))
                cx = points[keys[0]][0]
                cy = points[keys[0]][1]
                rad = keys[0]
                rr, cc = disk((cx, cy), rad)
                circleSlice[rr, cc] = 1

                imgCenterX = int(rectMask.shape[0]/2)
                imgCenterY = int(rectMask.shape[1]/2)
                if cx > imgCenterX + 60 or cx < imgCenterX - 60 or cy > imgCenterY + 60 or cy < imgCenterY - 150:
                    break

                for x in range(circleMask.shape[0]):
                    for y in range(circleMask.shape[1]):
                        circleMask[x][y][z] = circleSlice[x][y]
            else:
                cx = int(csvrows[z-1][0])
                cy = int(csvrows[z-1][1])
                rad = 0
                for x in range(cx, cx+30):
                    if circleMask[x][cy][z-1] == 1:
                        rad += 1
                    else:
                        break
                for x in range(circleMask.shape[0]):
                    for y in range(circleMask.shape[1]):
                        circleMask[x][y][z] = circleMask[x][y][z-1]

            for x in range(rectMask.shape[0]):
                for y in range(rectMask.shape[1]):
                    rectMask[x][y][z] = 0
                    if x >= cx - rad and x <= cx + rad and y >= cy - rad and y <= cy + rad:
                        rectMask[x][y][z] = 1

            p1 = [float(csvrows[z-1][0]), float(csvrows[z-1][1]), float(csvrows[z-1][2])]
            p2 = [cx, cy, z]
            mmP1 = nib.affines.apply_affine(VALUES["img"].affine, [p1[0], p1[1], p1[2]])
            mmP2 = nib.affines.apply_affine(VALUES["img"].affine, [p2[0], p2[1], p2[2]])
            d = math.sqrt(pow(mmP1[0]-mmP2[0], 2) + pow(mmP1[1]-mmP2[1], 2))
            csvrows[z][4] = d

            csvrows[z][0] = cx
            csvrows[z][1] = cy
            csvrows[z][2] = z
            csvrows[z][3] = rad

            if z+1 >= len(csvrows):
                continue

            p1 = [float(csvrows[z+1][0]), float(csvrows[z+1][1]), float(csvrows[z+1][2])]
            p2 = [cx, cy, z]
            mmP1 = nib.affines.apply_affine(VALUES["img"].affine, [p1[0], p1[1], p1[2]])
            mmP2 = nib.affines.apply_affine(VALUES["img"].affine, [p2[0], p2[1], p2[2]])
            d = math.sqrt(pow(mmP1[0]-mmP2[0], 2) + pow(mmP1[1]-mmP2[1], 2))
            csvrows[z+1][4] = d

    #print("smooth down")

    for z in range(start, 20, -1):
        if float(csvrows[z][4]) > VALUES["dDiff"]:
            #print (z)
            points = {}
            #p1, p2 = getRectCorners(rectMask, z+1)

            cx = 0
            cy = 0
            rad = 0
            if float(csvrows[z][0]) > 0:
                #for x in range(p1[0], p2[0]):
                    #for y in range(p1[1], p2[1]):
                        #if boneMask[x][y][z] == 0:
                for x in range(circleMask.shape[0]):
                    for y in range(circleMask.shape[1]):
                        if boneMask[x][y][z] == 0 and circleMask[x][y][z-1] == 1:
                            circleSlice = np.zeros(shape=(rectMask.shape[0],rectMask.shape[1]), dtype=float)
                            rr, cc = disk((x, y), r)
                            circleSlice[rr, cc] = 1
                            while not isCollision(boneMask, circleSlice, z, x, y, r) and r < 15:
                                r += 1
                                rr, cc = disk((x, y), r)
                                circleSlice[rr, cc] = 1
                            points[r] = [x, y]
                            r = VALUES["redius"]

                if len(points) == 0:
                    break
                circleSlice = np.zeros(shape=(rectMask.shape[0],rectMask.shape[1]), dtype=float)
                keys = list(reversed(sorted(points.keys())))
                cx = points[keys[0]][0]
                cy = points[keys[0]][1]
                rad = keys[0]
                rr, cc = disk((cx, cy), rad)
                circleSlice[rr, cc] = 1

                imgCenterX = int(rectMask.shape[0]/2)
                imgCenterY = int(rectMask.shape[1]/2)
                if cx > imgCenterX + 60 or cx < imgCenterX - 60 or cy > imgCenterY + 60 or cy < imgCenterY - 150:
                    break

                for x in range(circleMask.shape[0]):
                    for y in range(circleMask.shape[1]):
                        circleMask[x][y][z] = circleSlice[x][y]
            else:
                cx = int(csvrows[z+1][0])
                cy = int(csvrows[z+1][1])
                rad = 0
                for x in range(cx, cx+30):
                    if circleMask[x][cy][z+1] == 1:
                        rad += 1
                    else:
                        break
                for x in range(circleMask.shape[0]):
                    for y in range(circleMask.shape[1]):
                        circleMask[x][y][z] = circleMask[x][y][z+1]

            for x in range(rectMask.shape[0]):
                for y in range(rectMask.shape[1]):
                    rectMask[x][y][z] = 0
                    if x >= cx - rad and x <= cx + rad and y >= cy - rad and y <= cy + rad:
                        rectMask[x][y][z] = 1

            p1 = [float(csvrows[z+1][0]), float(csvrows[z+1][1]), float(csvrows[z+1][2])]
            p2 = [cx, cy, z]
            mmP1 = nib.affines.apply_affine(VALUES["img"].affine, [p1[0], p1[1], p1[2]])
            mmP2 = nib.affines.apply_affine(VALUES["img"].affine, [p2[0], p2[1], p2[2]])
            d = math.sqrt(pow(mmP1[0]-mmP2[0], 2) + pow(mmP1[1]-mmP2[1], 2))
            csvrows[z][4] = d

            csvrows[z][0] = cx
            csvrows[z][1] = cy
            csvrows[z][2] = z
            csvrows[z][3] = rad

            #if z+1 >= len(csvrows): continue

            p1 = [float(csvrows[z-1][0]), float(csvrows[z-1][1]), float(csvrows[z-1][2])]
            p2 = [cx, cy, z]
            mmP1 = nib.affines.apply_affine(VALUES["img"].affine, [p1[0], p1[1], p1[2]])
            mmP2 = nib.affines.apply_affine(VALUES["img"].affine, [p2[0], p2[1], p2[2]])
            d = math.sqrt(pow(mmP1[0]-mmP2[0], 2) + pow(mmP1[1]-mmP2[1], 2))
            csvrows[z-1][4] = d

    #out = nib.Nifti1Image(rectMask, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_canalRect_mask.nii")

    #out = nib.Nifti1Image(circleMask, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_canalCircle_mask.nii")

    myFile = open(VALUES["file"] + "_spinalData.csv", "w")
    with myFile:
        writer = csv.writer(myFile, lineterminator="\n")
        writer.writerows(csvrows)

def createCpr(data, centers):
    corCpr = np.zeros(shape=(data.shape[0], data.shape[2]), dtype=float)
    sagCpr = np.zeros(shape=(data.shape[1], data.shape[2]), dtype=float)
    corLine = np.zeros(shape=(data.shape[0], data.shape[2]), dtype=float)
    sagLine = np.zeros(shape=(data.shape[1], data.shape[2]), dtype=float)

    for point in centers:
        cx = int(float(point[0]))
        cy = int(float(point[1]))
        cz = int(float(point[2]))
        r = int(point[3])

        """for x in range(data.shape[0]):
            corCpr[x][cz] = data[x][cy + int((r/3)*2)][cz]
        corLine[cx][cz] = 1"""

        min = 999999
        minIndex = 0
        sumInt = 0
        for i in range(cy - r, cy + r):
            for n in range(cx - VALUES["cprSpinalBorder"], cx + VALUES["cprSpinalBorder"]):
                sumInt += data[n][i][cz]
            if sumInt < min:
                min = sumInt
                minIndex = i
            sumInt = 0

        for x in range(data.shape[0]):
            corCpr[x][cz] = data[x][minIndex][cz]
        corLine[cx][cz] = 1

        for y in range(data.shape[1]):
            sagCpr[y][cz] = data[cx][y][cz]
        sagLine[cy][cz] = 1

    #print(VALUES["img"].header)
    #cprImg = copy.deepcopy(VALUES["img"])
    #cprImg.affine[1][1] = VALUES["zThickness"]
    #print(cprImg.header)
    #out = nib.Nifti1Image(corCpr, cprImg.affine)
    #nib.save(out, VALUES["file"] + "_corCpr.nii")
    #out = nib.Nifti1Image(sagCpr, cprImg.affine)
    #nib.save(out, VALUES["file"] + "_sagCpr.nii")

    #out = nib.Nifti1Image(corLine, cprImg.affine)
    #nib.save(out, VALUES["file"] + "_corLine.nii")
    #out = nib.Nifti1Image(sagLine, cprImg.affine)
    #nib.save(out, VALUES["file"] + "_sagLine.nii")

    return corCpr, sagCpr

def createIntensityProfile(corCpr, centers):
    intensityArry = []
    arr = []
    for i in range(len(centers)):
        cprx = int(centers[i][0])
        cpry = int(centers[i][2])
        intensity = 0
        for x in range(cprx - VALUES["cprSpinalBorder"], cprx + VALUES["cprSpinalBorder"]):
            intensity += corCpr[x][cpry]
        intensityArry.append(intensity)
        arr.append([intensity])

    myFile = open(VALUES["file"] + "_intensityProfile.csv", "w")
    with myFile:
        writer = csv.writer(myFile, lineterminator="\n")
        writer.writerows(arr)

    """mpl.rcParams['savefig.pad_inches'] = 0
    t = np.linspace(0, len(intensityArry), len(intensityArry))
    plt.figure(figsize=(10,4))
    plt.bar(t, intensityArry)
    plt.xticks(np.arange(0, len(intensityArry), 5))
    plt.yticks(np.arange(0, max(intensityArry), 1000))
    plt.axis([0, len(intensityArry), 0, max(intensityArry)])
    plt.savefig(VALUES["file"] + "_intProfile.png", bbox_inches='tight')"""

    return intensityArry

def getLocals(intensityArry, mode="min", neighbours = 3):
    res = []
    #resValues = []

    for i in range(0, len(intensityArry) - neighbours):
        isOk = True
        for j in range(1, neighbours + 1):
            """if intensityArry[i] <= 0:
                isOk = False
                break"""
            if i < neighbours:
                if mode == "min" and (intensityArry[i+j] < intensityArry[i]):
                    isOk = False
                    break
                elif mode == "max" and (intensityArry[i+j] > intensityArry[i]):
                    isOk = False
                    break
                continue
            if mode == "min" and (intensityArry[i-j] < intensityArry[i] or intensityArry[i+j] < intensityArry[i]):
                isOk = False
                break
            elif mode == "max" and (intensityArry[i-j] > intensityArry[i] or intensityArry[i+j] > intensityArry[i]):
                isOk = False
                break
        if isOk:
           res.append(i)
           #resValues.append(intensityArry[i])

    # ha lok min van egymas utan, az egyiket torolni kell
    """res2 = []
    for i in range(len(res) - 1):
        if res[i+1] - res[i] > 1:
            res2.append(res[i])
    res2.append(res[len(res)-1])"""

    #print(res)
    #ha tobb lok min van egymas mellet, akkor a középsőt választjuk
    res2 = []
    n = 0
    for i in range(len(res) - 1):
        if res[i+1] - res[i] == 1:
            n += 1
        else:
            if n > 0:
                index = int(n / 2)
                res2.append(res[i-index])
            else:
                res2.append(res[i])
            n = 0
    res2.append(res[-1])

    #print(res2)

    return res2

# detektalja a csigolyak kozotti rest
def findVertebras(intensityArry, boneMask, centers, data):
    locals3D = np.zeros(shape=(data.shape[0], data.shape[1], data.shape[2]), dtype=float)
    #locals3D = copy.deepcopy(VALUES["img"].get_fdata())
    minslices = getLocals(intensityArry, "min")
    vertebraSpaceSlices = []

    """for x in range(locals3D.shape[0]):
        for y in range(locals3D.shape[1]):
            for z in range(locals3D.shape[2]):
                locals3D[x][y][z] = 0"""

    max = 0
    maxIntSlice = 0
    for i in range(0, len(intensityArry) - int(len(intensityArry)/3)):
        if intensityArry[i] > max:
            max = intensityArry[i]
            maxIntSlice = i

    secondMax = 0
    for i in range(len(intensityArry)):
        if intensityArry[i] > secondMax and intensityArry[i] < max:
            secondMax = intensityArry[i]

    intSlice = maxIntSlice

    """if (max - secondMax) < ((max / 100) * 2):
        z = maxIntSlice if maxIntSlice < secondMaxIntSlice else secondMaxIntSlice
        vertebraSpaceSlices.append(z + 1)
        intSlice = maxIntSlice if maxIntSlice > secondMaxIntSlice else secondMaxIntSlice
        for x in range(VALUES["img"].shape[0]):
            for y in range(VALUES["img"].shape[1]):
                locals3D[x][y][z - 1] = 1"""

    intSlice = getStartZ(boneMask, centers) - VALUES["zShiftStartVertebraBorder"]

    #print("!!!!!")
    #print(intSlice)
    #print(minslices)
    index = 0
    for i in range(len(minslices)):
        if minslices[i] > intSlice:
            """if minslices[i] - intSlice > VALUES["zDiff"]:
                index = i
            else:
                index = i + 1
            break"""
            index = i
            break

    minslices = minslices[index:len(minslices)]

    for i in range(len(minslices)):
        """if i < 3:
            vertebraSpaceSlices.append(minslices[i] - 1)
            for x in range(VALUES["img"].shape[0]):
                for y in range(VALUES["img"].shape[1]):
                    locals3D[x][y][minslices[i] - 1] = 1
        else:"""
        vertebraSpaceSlices.append(minslices[i])
        for x in range(VALUES["img"].shape[0]):
            for y in range(VALUES["img"].shape[1]):
                locals3D[x][y][minslices[i]] = 1

    # a 1. es 2. csigolya kozti hatar megvan e? (ha nincs berakjuk)
    vertebraSpaceSlices2 = []
    if minslices[0] - intSlice > VALUES["zRefDiff1stBorder"]:
        vertebraSpaceSlices2.append(minslices[0] - 7)
        vertebraSpaceSlices.insert(0, minslices[0] - 7)
        for x in range(VALUES["img"].shape[0]):
            for y in range(VALUES["img"].shape[1]):
                locals3D[x][y][minslices[0] - 7] = 1

    # nem hagy e ki egy hatar szeletet? (ha 2 hatar kozott tul nagy a tavolsag, a ketto koze berak egy hatart)
    for i in range(len(vertebraSpaceSlices) - 1):
        vertebraSpaceSlices2.append(vertebraSpaceSlices[i])
        if vertebraSpaceSlices[i+1] - vertebraSpaceSlices[i] > VALUES["zRefDiffBorders"]:
            vertebraSpaceSlices2.append(vertebraSpaceSlices[i] + int((vertebraSpaceSlices[i+1] - vertebraSpaceSlices[i])/2))
            for x in range(VALUES["img"].shape[0]):
                for y in range(VALUES["img"].shape[1]):
                    locals3D[x][y][vertebraSpaceSlices2[len(vertebraSpaceSlices2)-1]] = 1

    vertebraSpaceSlices2.append(vertebraSpaceSlices[len(vertebraSpaceSlices)-1])

    #out = nib.Nifti1Image(locals3D, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_loc_mins.nii")

    file = VALUES["file"] + "_vertBorders.csv"
    outFile = open(file, "w")
    for item in vertebraSpaceSlices2:
        outFile.write(str(item * VALUES["n"])+"\n")

    return vertebraSpaceSlices2

#
def getStartZ(boneMask, centers):
    #print(centers)
    for z in range(int(len(centers)/2) + VALUES["zShiftMaxIntSlice"], 0, -1):
        width1 = 0
        space = 0
        bone = False
        #print(z)
        for x in range(centers[z][0], boneMask.shape[0]):
            for y in range(centers[z][1] - 60, centers[z][1] + 50):
                if boneMask[x][y][z] == 1:
                    width1 += 1
                    #print(str(x) + " " + str(y))
                    space = 0
                    bone = True
                    break
            if not bone:
                space += 1
            bone = False
            if space == 1:
                break

        #print("---")
        space = 0
        bone = False
        width2 = 0
        for x in range(centers[z][0], 0, -1):
            for y in range(centers[z][1] - 60, centers[z][1] + 50):
                if boneMask[x][y][z] == 1:
                    width2 += 1
                    #print(str(x) + " " + str(y))
                    space = 0
                    bone = True
                    break
            if not bone:
                space += 1
            bone = False
            if space == 1:
                break

        if width1 > 100 and width2 > 100:
            #print(centers[z])
            return z

    return int(len(centers)/2)

#### detect T12 ####

def getVertebraLeftBorder(data, spinalCenterX, spinalCenterY, z):
    yb = 25
    xspace = 0
    for x in range(spinalCenterX-10, 0, -1):
        isVertebraVoxel = False
        xspace = xspace + 1
        for y in range(spinalCenterY-50, spinalCenterY+yb):
            if data[x][y][z] == 1:
                isVertebraVoxel = True
                xspace = 0
                break
        if not isVertebraVoxel and xspace > 2:
            return x + xspace - 1


regionSize = 0
sys.setrecursionlimit(10000)
def growRegion(mask, regionMask, x, y):
    global regionSize
    if mask[x][y] != 1 or regionMask[x][y] != 0:
        return
    regionMask[x][y] = 1
    regionSize = regionSize + 1
    growRegion(mask, regionMask, x+1, y)
    growRegion(mask, regionMask, x-1, y)
    growRegion(mask, regionMask, x, y+1)
    growRegion(mask, regionMask, x, y-1)
    growRegion(mask, regionMask, x+1, y+1)
    growRegion(mask, regionMask, x-1, y-1)
    growRegion(mask, regionMask, x-1, y+1)
    growRegion(mask, regionMask, x+1, y-1)

def getSlice(data, z):
    slice = np.zeros(shape=(data.shape[0], data.shape[1]), dtype=float)
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            slice[x][y] = data[x][y][z]

    return slice

def findFirstRibRegion(mask, vbx, spinalCenterX, spinalCenterY):
    yb = 50
    shiftX = 40 if spinalCenterX - vbx < 50 else 25
    regionMask = np.zeros(shape=(mask.shape[0], mask.shape[1]), dtype=float)
    for x in range(vbx, vbx-shiftX, -1):
        for y in range(spinalCenterY-yb, spinalCenterY-5):
            if mask[x][y] == 1:
                growRegion(mask, regionMask, x, y)
                return regionMask

    return regionMask


def findRibRegion(mask, rect):
    regionMask = np.zeros(shape=(mask.shape[0], mask.shape[1]), dtype=float)
    for x in range(rect[0], rect[2]+5):
        for y in range(rect[1], rect[3]+5):
            if mask[x][y] == 1:
                growRegion(mask, regionMask, x, y)
                return regionMask

    return regionMask


def getRect(region):
    rect = []

    for x in range(region.shape[0]):
        for y in range(region.shape[1]):
            if region[x][y] == 1:
                rect.append(x)
                break
        if len(rect) == 1:
            break

    for y in range(region.shape[1]):
        for x in range(region.shape[0]):
            if region[x][y] == 1:
                rect.append(y)
                break
        if len(rect) == 2:
            break

    for x in range(region.shape[0]-1, 0, -1):
        for y in range(region.shape[1]):
            if region[x][y] == 1:
                rect.append(x)
                break
        if len(rect) == 3:
            break

    for y in range(region.shape[1]-1, 0, -1):
        for x in range(region.shape[0]):
            if region[x][y] == 1:
                rect.append(y)
                break
        if len(rect) == 4:
            break

    return rect


def detectT12(boneMask, startZ, centers):
    global regionSize

    rect = []
    ribZ = 0

    for z in range(startZ, boneMask.shape[2]):
        #if z == 56: continue
        regionSize = 0
        cx = centers[z][0]
        cy = centers[z][1]
        if cx == 0:
            continue
        vertebraBorderX = getVertebraLeftBorder(boneMask, cx, cy, z)
        slice = getSlice(boneMask, z)
        slice = labelFilter(slice, 25)
        #print(centers[z])
        #print(vertebraBorderX)
        region = findFirstRibRegion(slice, vertebraBorderX, cx, cy)
        #out = nib.Nifti1Image(region, VALUES["img"].affine)
        #nib.save(out, VALUES["file"] + "_region.nii")
        #print(regionSize)
        if regionSize > 20:
            rect = getRect(region)

            slice = getSlice(boneMask, z+1)
            slice = labelFilter(slice, 25)
            regionSize = 0
            region = findRibRegion(slice, rect)
            #print(rect)
            #print(regionSize)
            if regionSize > 400 or regionSize < 25:
                #print("regionSize > 400 ... continue")
                continue

            ribZ = z
            #print("ribZ")
            #print(ribZ)
            #print(centers[z])
            break

    T12_z = 0
    #print("-----------")
    for z in range(ribZ+1, boneMask.shape[2]):
        #if z == 56: continue
        if centers[z][0] == 0:
            continue
        regionSize = 0
        slice = getSlice(boneMask, z)
        slice = labelFilter(slice, 20)
        region = findRibRegion(slice, rect)
        #print(rect)
        #print(regionSize)
        if regionSize > 400 or regionSize == 0:
            T12_z = z
            break
        rect = getRect(region)


    #print("T12 z")
    #print(T12_z)
    return T12_z

#### ####

# visszaadja a vertebra alatti csigolya kozepso szeletenek (z) indexet
def getNextVertebraSlice(vertebra, locMinSlices):
    nextVertebra = 0
    if vertebra in locMinSlices:
        nextVertebra = vertebra - 5
    else:
        for i in range(len(locMinSlices)):
            if locMinSlices[i] > vertebra:
                nextVertebra = int(locMinSlices[i-2] + (locMinSlices[i-1] - locMinSlices[i-2]) / 2)
                break
        if nextVertebra == 0:
            i = len(locMinSlices)-1
            nextVertebra = int(locMinSlices[i-1] + (locMinSlices[i] - locMinSlices[i-1]) / 2)

    """data = copy.deepcopy(VALUES["img"].get_fdata())
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            data[x][y][nextVertebra] = 2000

    out = nib.Nifti1Image(data, VALUES["img"].affine)
    nib.save(out, VALUES["file"] + "_" + str(nextVertebra) + "_ct_result.nii")"""

    return nextVertebra

# Letrehozza az adott szeleten levo test maskot
def createBodyMask(data):
    slice = copy.deepcopy(data)

    filtered_data = np.zeros_like(slice)
    filtered_data[data>-200] = 1

    body = largestComponent2D(filtered_data)
    body = ndi.binary_fill_holes(body).astype(float)

    #out = nib.Nifti1Image(body, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_bodymask.nii")

    bodyContour = np.zeros(shape=(data.shape[0],data.shape[1]), dtype=float)
    for x in range(body.shape[0]):
        for y in range(body.shape[1]):
            if body[x][y] == 1:
                bodyContour[x][y] = 1
                break
        for y in range(body.shape[1]-1, 0, -1):
            if body[x][y] == 1:
                bodyContour[x][y] = 1
                break

    for y in range(body.shape[1]):
        for x in range(body.shape[0]):
            if body[x][y] == 1:
                bodyContour[x][y] = 1
                break
        for x in range(body.shape[0]-1, 0, -1):
            if body[x][y] == 1:
                bodyContour[x][y] = 1
                break

    VALUES["bodyContour"] = copy.deepcopy(bodyContour)

    return body

def getTopShift(data, x, topy):
    n = 0
    for y in range(topy - 3, topy - 15, -1):
        if data[x][y] < -30:
            n += 1
        else:
            n = 0

        if n == 3:
            return topy - y

    return 5

def getBottomShift(data, x, bottomy):
    n = 0
    for y in range(bottomy + 3, bottomy + 15):
        if data[x][y] < -30:
            n += 1
        else:
            n = 0

        if n == 3:
            return y - bottomy

    return 5

def getLeftShift(data, y, leftx):
    n = 0
    for x in range(leftx - 3, leftx - 15, -1):
        if data[x][y] < -30:
            n += 1
        else:
            n = 0

        if n == 3:
            return leftx - x

    return 5

def getRightShift(data, y, rightx):
    n = 0
    for x in range(rightx + 3, rightx + 15):
        if data[x][y] < -30:
            n += 1
        else:
            n = 0

        if n == 3:
            return x - rightx

    return 5

def getXBorders(mask):
    leftx = -1
    rightx = -1

    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            if mask[x][y] == 1:
                rightx = x
                break
        if rightx > -1:
            break

    for x in range(mask.shape[0]-1, 0, -1):
        for y in range(mask.shape[1]):
            if mask[x][y] == 1:
                leftx = x
                break
        if leftx > -1:
            break

    width = leftx - rightx
    cuttedW = int(width / 5)

    return leftx - cuttedW, rightx + cuttedW

def smoothSideBorder(border):
    rows = []
    row = []
    for i in range(0, len(border)-1):
        if border[i][0] > border[i+1][0] - 8 and border[i][0] < border[i+1][0] + 8:
            row.append(border[i])
            if i == len(border)-2:
                row.append(border[i+1])
                c = copy.deepcopy(row)
                rows.append(c)
        else:
            row.append(border[i])
            c = copy.deepcopy(row)
            rows.append(c)
            row.clear()

    #serie = max(rows, key=len)

    smoothedBorder = []
    for row in rows:
        if len(row) > 4:
            for point in row:
                smoothedBorder.append(point)

    return smoothedBorder

def smoothLeftBorder(borderLeft):
    borderLeft2 = []
    if borderLeft[0][0] < borderLeft[1][0] + 1 and borderLeft[0][0] > borderLeft[1][0] - 8:
        borderLeft2.append(borderLeft[0])

    for i in range(1, len(borderLeft)-1):
        if borderLeft[i][0] > borderLeft[i-1][0] + 1 and borderLeft[i][0] > borderLeft[i+1][0] + 1:
            continue
        if borderLeft[i][0] < borderLeft[i-1][0] - 1 and borderLeft[i][0] < borderLeft[i+1][0] - 1:
            continue
        borderLeft2.append(borderLeft[i])

    if borderLeft[len(borderLeft)-1][0] > borderLeft[len(borderLeft)-2][0] - 8 and borderLeft[len(borderLeft)-1][0] < borderLeft[len(borderLeft)-2][0] + 1:
        borderLeft2.append(borderLeft[len(borderLeft)-1])

    return smoothSideBorder(borderLeft2)

def smoothRightBorder(borderRight):
    borderRight2 = []
    if borderRight[0][0] < borderRight[1][0] + 8 and borderRight[0][0] > borderRight[1][0] + 1:
        borderRight2.append(borderRight[0])

    for i in range(1, len(borderRight)-1):
        if borderRight[i][0] > borderRight[i-1][0] + 1 and borderRight[i][0] > borderRight[i+1][0] + 1:
            continue
        if borderRight[i][0] < borderRight[i-1][0] - 1 and borderRight[i][0] < borderRight[i+1][0] - 1:
            continue
        borderRight2.append(borderRight[i])

    if borderRight[len(borderRight)-1][0] < borderRight[len(borderRight)-2][0] + 8 and borderRight[len(borderRight)-1][0] > borderRight[len(borderRight)-2][0] - 1:
        borderRight2.append(borderRight[len(borderRight)-1])

    return smoothSideBorder(borderRight2)

def smoothTopBorder(border):
    rows = []
    row = []
    for i in range(0, len(border)-1):
        if border[i][1] > border[i+1][1] - 8 and border[i][1] < border[i+1][1] + 8:
            row.append(border[i])
            if i == len(border)-2:
                row.append(border[i+1])
                c = copy.deepcopy(row)
                rows.append(c)
        else:
            row.append(border[i])
            c = copy.deepcopy(row)
            if len(row) > 2:
                rows.append(c)
            row.clear()

    #serie = max(rows, key=len)

    smoothedBorder = []
    smoothedRowsTemp = copy.deepcopy(rows)
    smoothedRows = copy.deepcopy(rows)
    re = True
    while re:
        re = False
        smoothedRowsTemp = []
        for i in range(len(smoothedRows)-1):
            if smoothedRows[i][-1][1] > (smoothedRows[i+1][0][1] - 8):
                smoothedRowsTemp.append(smoothedRows[i])
            else:
                re = True
        if re:
            smoothedRowsTemp.append(smoothedRows[-1])
        smoothedRows = copy.deepcopy(smoothedRowsTemp)

    for row in smoothedRows:
        #if len(row) < 2:
            #continue
        for point in row:
            smoothedBorder.append(point)

    if len(rows) < 2:
        for row in rows:
            for point in row:
                smoothedBorder.append(point)
        return smoothedBorder[2:-2]

    if rows[-1][0][1] > (rows[-2][-1][1] - 8):
        for point in rows[-1]:
            smoothedBorder.append(point)

    return smoothedBorder[2:-2]

def smoothBottomBorder(border):
    rows = []
    row = []
    for i in range(0, len(border)-1):
        if border[i][1] > border[i+1][1] - 8 and border[i][1] < border[i+1][1] + 8:
            row.append(border[i])
            if i == len(border)-2:
                row.append(border[i+1])
                c = copy.deepcopy(row)
                rows.append(c)
        else:
            row.append(border[i])
            c = copy.deepcopy(row)
            rows.append(c)
            row.clear()

    #serie = max(rows, key=len)

    smoothedRows = []

    for i in range(len(rows)-1):
        if rows[i][-1][1] < (rows[i+1][0][1] + 30):
            smoothedRows.append(rows[i])

    smoothedRows.append(rows[-1])

    smoothedBorder = []
    for row in smoothedRows:
        if len(row) > 4:
            for point in row:
                smoothedBorder.append(point)

    return smoothedBorder

# detektalja a belso hatart
def getInnerBorderPoints(data, mask):

    borderTop = []
    borderBottom = []
    borderLeft = []
    borderRight = []
    border = []
    #shift = 15

    leftx, rightx = getXBorders(mask)

    for x in range(leftx, rightx, -1):
        if x % 4 != 0:
            continue

        maskTopy = -1
        maskBottomy = -1

        for y in range(data.shape[1]-1, 0, -1):
            if mask[x][y] == 1:
                maskTopy = y
                break

        if maskTopy == -1:
            continue

        for y in range(data.shape[1]):
            if mask[x][y] == 1:
                maskBottomy = y
                break

        if maskTopy == maskBottomy:
            continue

        topShift = getTopShift(data, x, maskTopy)
        bottomShift = getBottomShift(data, x, maskBottomy)
        for y in range(maskTopy - topShift, maskBottomy + bottomShift, -1):
            if data[x][y] < -500:
                break
            if data[x][y] > -30:
                borderTop.append([x, y])
                break

    avg = 0
    for x in range(rightx, leftx):
        if x % 4 != 0:
            continue

        maskTopy = -1
        maskBottomy = -1

        for y in range(data.shape[1]-1, 0, -1):
            if mask[x][y] == 1:
                maskTopy = y
                break

        if maskTopy == -1:
            continue

        for y in range(data.shape[1]):
            if mask[x][y] == 1:
                maskBottomy = y
                break

        if maskTopy == maskBottomy:
            continue

        topShift = getTopShift(data, x, maskTopy)
        bottomShift = getBottomShift(data, x, maskBottomy)

        n = 0
        for y in range(maskBottomy + bottomShift, maskTopy - topShift):
            if data[x][y] < -500:
                break
            if data[x][y] > -30:
                n += 1
            else:
                n = 0

            if n == 3:
                borderBottom.append([x, y])
                avg += data[x][y]
                break

    smoothedBorderTop = smoothTopBorder(borderTop)
    #smoothedBorderTop = borderTop
    topy = smoothedBorderTop[0][1] if smoothedBorderTop[0][1] < smoothedBorderTop[-1][1] else smoothedBorderTop[-1][1]

    smoothedBorderBottom = smoothBottomBorder(borderBottom)
    bottomy = smoothedBorderBottom[0][1] if smoothedBorderBottom[0][1] > smoothedBorderBottom[-1][1] else smoothedBorderBottom[-1][1]

    topy -= 5
    bottomy += 5

    for y in range(bottomy, topy):
        if y % 4 != 0:
            continue

        maskLeftx = -1
        maskRightx = -1
        for x in range(data.shape[0]-1, 0, -1):
            if mask[x][y] == 1:
                maskLeftx = x
                break

        for x in range(data.shape[0]):
            if mask[x][y] == 1:
                maskRightx = x
                break

        if maskLeftx == maskRightx:
            continue

        leftShift = getLeftShift(data, y, maskLeftx)
        rightShift = getRightShift(data, y, maskRightx)
        n = 0
        for x in range(maskLeftx - leftShift, maskRightx + rightShift, -1):
            if data[x][y] < -500:
                break
            if data[x][y] > -30:
                n += 1
            else:
                n = 0

            if n == 2:
                borderLeft.append([x, y])
                break

    for y in range(topy, bottomy, -1):
        if y % 4 != 0:
            continue

        maskLeftx = -1
        maskRightx = -1
        for x in range(data.shape[0]-1, 0, -1):
            if mask[x][y] == 1:
                maskLeftx = x
                break

        for x in range(data.shape[0]):
            if mask[x][y] == 1:
                maskRightx = x
                break

        if maskLeftx == maskRightx:
            continue

        leftShift = getLeftShift(data, y, maskLeftx)
        rightShift = getRightShift(data, y, maskRightx)
        n = 0
        for x in range(maskRightx + rightShift, maskLeftx - leftShift):
            if data[x][y] < -500:
                break
            if data[x][y] > -30:
                n += 1
            else:
                n = 0

            if n == 2:
                borderRight.append([x, y])
                break

    smoothedBorderLeft = smoothLeftBorder(borderLeft)
    smoothedBorderRight = smoothRightBorder(borderRight)

    border = smoothedBorderTop + smoothedBorderRight + smoothedBorderBottom + smoothedBorderLeft

    return border

def createInnerBorder(border):
    x = []
    y = []
    for p in border:
        x.append(p[0])
        y.append(p[1])
    x = np.array(x)
    y = np.array(y)

    x = np.r_[x, x[0]]
    y = np.r_[y, y[0]]
    tck, u = interpolate.splprep([x, y], s=100, per=True)
    xi, yi = interpolate.splev(np.linspace(0, 1, 10000), tck)

    outdata = np.zeros(shape=(VALUES["img"].get_fdata().shape[0], VALUES["img"].get_fdata().shape[1]), dtype=float)
    for i in range(len(xi)):
        outdata[int(xi[i])][int(yi[i])] = 1

    VALUES["innerContour"] = copy.deepcopy(outdata)

    outdata = ndi.binary_fill_holes(outdata).astype(float)
    #out = nib.Nifti1Image(outdata, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_innerFatMask2.nii")

    return outdata

def separateTissue(data, sliceIndex, vertebra):
    slice = np.ndarray(shape=(data.shape[0],data.shape[1]), dtype=float)
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            slice[x][y] = data[x][y][sliceIndex]

    out = nib.Nifti1Image(slice, VALUES["img"].affine)
    nib.save(out, VALUES["file"] + "_" + vertebra + "_" + str(sliceIndex * VALUES["n"]) + "_slice.nii")

    mask = createBodyMask(slice)
    out = nib.Nifti1Image(VALUES["bodyContour"], VALUES["img"].affine)
    nib.save(out, VALUES["file"] + "_" + vertebra + "_" + str(sliceIndex * VALUES["n"]) + "_bodyContour.nii")

    border = getInnerBorderPoints(slice, mask)

    outdata = np.zeros(shape=(slice.shape[0],slice.shape[1]), dtype=float)
    for point in border:
        outdata[point[0]][point[1]] = 1

    #out = nib.Nifti1Image(outdata, VALUES["img"].affine)
    #nib.save(out, VALUES["file"] + "_abdominalBorderPoints.nii")

    innerMask = createInnerBorder(border)
    out = nib.Nifti1Image(VALUES["innerContour"], VALUES["img"].affine)
    nib.save(out, VALUES["file"] + "_" + vertebra + "_" + str(sliceIndex * VALUES["n"]) + "_innerContour.nii")

    return mask, innerMask, slice

def createDataHeader():
    csvdata = [["id","weight","height","perimeter","maxWidth","maxHeight","outerArea","innerArea","VATArea","SATArea","VATVol","SATVol","vertebra","VATAVG","SATAVG","VATStdev","SATStdev"]]
    myFile = open(VALUES["file"] + "_data.csv", "a")
    with myFile:
        writer = csv.writer(myFile, lineterminator="\n")
        writer.writerows(csvdata)

def createOutData(outerMask, innerMask, ctdata, idx, vertebra):
    #csvdata = [["id","weight","height","perimeter","maxWidth","maxHeight","outerArea","innerArea","VATArea","SATArea","VATVol","SATVol","vertebra"]]
    data = []

    dx = VALUES["img"].header["pixdim"][1]
    dy = VALUES["img"].header["pixdim"][2]
    dz = VALUES["img"].header["pixdim"][3]

    """s = [[0,1,1],
         [1,1,1],
         [1,0,1]]
    s = np.array(s)
    p = measure.perimeter(outerMask, neighbourhood=4)"""

    overlap = False
    perimeter = 0
    for x in range(outerMask.shape[0]):
        for y in range(outerMask.shape[1]):
            if outerMask[x][y] == 1:
                if x == 0:
                    overlap = True
                if x + 1 == outerMask.shape[0]:
                    overlap = True
                if y == 0:
                    overlap = True

                if x+1 in range(len(outerMask)) and outerMask[x+1][y] == 0:
                    perimeter += dx
                if x-1 in range(len(outerMask)) and outerMask[x-1][y] == 0:
                    perimeter += dx
                if y+1 in range(len(outerMask)) and outerMask[x][y+1] == 0:
                    perimeter += dx
                if y+1 in range(len(outerMask)) and outerMask[x][y-1] == 0:
                    perimeter += dx
    data.append(perimeter)

    leftx = -1
    rightx = -1
    for x in range(outerMask.shape[0]):
        for y in range(outerMask.shape[1]):
            if outerMask[x][y] == 1:
                rightx = x
                break
        if rightx > -1:
            break

    for x in range(outerMask.shape[0]-1, 0, -1):
        for y in range(outerMask.shape[1]):
            if outerMask[x][y] == 1:
                leftx = x
                break
        if leftx > -1:
            break

    maxBodyWidth = leftx - rightx
    data.append(maxBodyWidth * dx)

    topy = -1
    bottomy = -1
    for y in range(outerMask.shape[1]):
        for x in range(outerMask.shape[0]):
            if outerMask[x][y] == 1:
                bottomy = y
                break
        if bottomy > -1:
            break

    for y in range(outerMask.shape[1]-1, 0, -1):
        for x in range(outerMask.shape[0]):
            if outerMask[x][y] == 1:
                topy = y
                break
        if topy > -1:
            break

    maxBodyHeight = topy - bottomy
    data.append(maxBodyHeight * dy)

    numOfVoxels = np.count_nonzero(outerMask)
    data.append(numOfVoxels * dx * dy)

    numOfVoxels = np.count_nonzero(innerMask)
    data.append(numOfVoxels * dx * dy)

    vatMask = np.zeros(shape=(innerMask.shape[0], innerMask.shape[1]), dtype=float)
    for x in range(innerMask.shape[0]):
        for y in range(innerMask.shape[1]):
            if innerMask[x][y] == 1 and ctdata[x][y] > -274 and ctdata[x][y] < -49:
                vatMask[x][y] = 1

    out = nib.Nifti1Image(vatMask, VALUES["img"].affine)
    nib.save(out, VALUES["file"] + "_" + vertebra + "_" + str(idx * VALUES["n"]) + "_VAT_Mask.nii")

    VALUES["vatMask"] = vatMask

    satMask = np.zeros(shape=(outerMask.shape[0], outerMask.shape[1]), dtype=float)
    for x in range(outerMask.shape[0]):
        for y in range(outerMask.shape[1]):
            if outerMask[x][y] == 1 and innerMask[x][y] == 0 and ctdata[x][y] > -274 and ctdata[x][y] < -49:
                satMask[x][y] = 1

    #satMask = largestComponent2D(satMask)
    satMask = labelFilter(satMask, 200)
    out = nib.Nifti1Image(satMask, VALUES["img"].affine)
    nib.save(out, VALUES["file"] + "_" + vertebra + "_" + str(idx * VALUES["n"]) + "_SAT_Mask.nii")

    VALUES["satMask"] = satMask

    numOfVoxels = np.count_nonzero(vatMask)
    vatArea = numOfVoxels * dx * dy
    vatVol = (numOfVoxels * dx * dy * dz)/1000

    numOfVoxels = np.count_nonzero(satMask)
    satArea = numOfVoxels * dx * dy
    satVol = (numOfVoxels * dx * dy * dz)/1000

    data.append(vatArea)
    data.append(satArea)
    data.append(vatVol)
    data.append(satVol)

    data.append(vertebra)

    if overlap:
        data.append("1")
    else:
        data.append("0")

    #csvdata.append(data)

    values = ctdata[vatMask == 1]
    vatavg = round(sum(values) / len(values), 4) if len(values) > 0 else "NaN"
    vat_stdev = round(np.std(values), 4) if len(values) > 0 else "NaN"

    values = ctdata[satMask == 1]
    satavg = round(sum(values) / len(values), 4) if len(values) > 0 else "NaN"
    sat_stdev = round(np.std(values), 4) if len(values) > 0 else "NaN"

    data.append(vatavg)
    data.append(satavg)
    data.append(vat_stdev)
    data.append(sat_stdev)

    myFile = open(VALUES["file"] + "_data.csv", "a")
    with myFile:
        writer = csv.writer(myFile, lineterminator="\n")
        #writer.writerows(csvdata)
        writer.writerow(data)


def createPNG(slice, idx, vertebra):
    slicePng = np.zeros([slice.shape[0], slice.shape[1], 3], dtype=np.uint8)

    for x in range(slice.shape[0]):
        for y in range(slice.shape[1]):
            if slice[x][y] > 100:
                slicePng[y,x] = [255,255,255]
            elif slice[x][y] >= -200 and slice[x][y] <= 100:
                ratio = 256 / 300
                c = min(255, int(ratio * (slice[x][y] + 200)))
                slicePng[y,x] = [c, c, c]

    contours = copy.deepcopy(slicePng)
    fat = copy.deepcopy(slicePng)

    for x in range(slice.shape[0]):
        for y in range(slice.shape[1]):
            if VALUES["innerContour"][x][y] == 1:
                contours[y,x] = [255,0,0]
            if VALUES["bodyContour"][x][y] == 1:
                contours[y,x] = [0,255,0]

    im = Image.fromarray(contours).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    im.save(VALUES["file"] + "_" + vertebra + "_" + str(idx * VALUES["n"]) + "_contours.png")

    for x in range(slice.shape[0]):
        for y in range(slice.shape[1]):
            if VALUES["vatMask"][x][y] == 1:
                fat[y,x] = [255,0,0]
            if VALUES["satMask"][x][y] == 1:
                fat[y,x] = [0,0,255]

    im = Image.fromarray(fat).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    im.save(VALUES["file"] + "_" + vertebra + "_" + str(idx * VALUES["n"]) + "_fat.png")

def generateData(origdata):
    n = math.trunc(5 / VALUES["zThickness"])
    VALUES["n"] = n
    newData = np.zeros(shape=(origdata.shape[0],origdata.shape[1], math.trunc(origdata.shape[2]/n)), dtype=float)
    for z in range(newData.shape[2]):
        for x in range(newData.shape[0]):
            for y in range(newData.shape[1]):
                newData[x][y][z] = origdata[x][y][z*n]

    return newData


def parseArguments(args: Sequence[str] | None = None):
    """Argument parser for the CLI."""
    parser = ArgumentParser(description="Run CT body fat segmentation", add_help=False, formatter_class=RawTextHelpFormatter)

    arg_positional = parser.add_argument_group("positional arguments")
    arg_positional.add_argument(
        "CT_image",
        help="Input body CT Nifti image file",
        type=str,
    )
    arg_optional = parser.add_argument_group("options")
    arg_optional.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    arg_optional.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this help message and exit"
    )
    arguments = parser.parse_args(args)
    return arguments


def segmProcess(args: Sequence[str] | None = None):

    arguments = parseArguments(args)
    file = arguments.CT_image

    img = nib.load(file)
    origdata = img.get_fdata()

    file = file[0:file.find(".")]
    VALUES["file"] = file
    VALUES["img"] = img

    computeParameters()

    if VALUES["zThickness"] < 5:
        origdata = generateData(origdata)

    boneMask, data = largestComponent(origdata,170)

    largestUncutBoneMask = copy.deepcopy(data)

    #data = data[int(data.shape[0]/4):int(data.shape[0]-data.shape[0]/4), int(data.shape[1]/4):int(data.shape[1]-data.shape[1]/4)]
    data = data[int(data.shape[0]/4):int(data.shape[0]-data.shape[0]/4), 0:int(data.shape[1]-data.shape[1]/4)]

    #canalMask = np.zeros(shape=(origdata.shape[0],origdata.shape[1], origdata.shape[2]), dtype=float)
    canalAreaMask = np.zeros(shape=(origdata.shape[0],origdata.shape[1], origdata.shape[2]), dtype=float)

    for z in range(0, data.shape[2]):
        slice = np.zeros(shape=(data.shape[0],data.shape[1]), dtype=int)
        for x in range(data.shape[0]):
            for y in range(data.shape[1]):
                slice[x][y] = data[x][y][z]
        findCanal(VALUES["emptyRectSize"], z, slice)
        for x in range(slice.shape[0]):
            for y in range(slice.shape[1]):
                #data[x][y][z] = slice[x][y]
                if slice[x][y] == 2:
                    canalAreaMask[x+128][y][z] = 1

    centers, circleMask = findCanalByCircle(largestUncutBoneMask, canalAreaMask)

    getDist(centers)

    smoothCenterLine(largestUncutBoneMask, canalAreaMask, circleMask, centers)

    corCpr, sagCpr = createCpr(boneMask, centers)

    intProfile = createIntensityProfile(corCpr, centers)

    vertebraSpaceSlices = findVertebras(intProfile, boneMask, centers, origdata)

    startZ = getStartZ(boneMask, centers) + 10

    boneMask, data = largestComponent(origdata,150)
    T12 = detectT12(boneMask, startZ, centers)

    L1SliceIndex = getNextVertebraSlice(T12, vertebraSpaceSlices)
    L2SliceIndex = getNextVertebraSlice(L1SliceIndex, vertebraSpaceSlices)
    L3SliceIndex = getNextVertebraSlice(L2SliceIndex, vertebraSpaceSlices)

    out = nib.Nifti1Image(boneMask, img.affine)
    nib.save(out, VALUES["file"] + "_boneMask.nii")

    createDataHeader()
    for i in [[L1SliceIndex, "L1"], [L2SliceIndex, "L2"], [L3SliceIndex, "L3"]]:
        sliceIdx = i[0]
        vertebra = i[1]
        outerMask, innerMask, slice = separateTissue(origdata, sliceIdx, vertebra)
        createOutData(outerMask, innerMask, slice, sliceIdx, vertebra)
        createPNG(slice, sliceIdx, vertebra)


if __name__ == "__main__":
    import sys
    segmProcess(sys.argv[1])
