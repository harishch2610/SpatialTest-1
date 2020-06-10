import os

from random import *

from django.shortcuts import render
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from osgeo import ogr
from numpy import double
import numpy as np
import time



# Create your views here.

mc1Array=[]
mc2Array=[]
mcDiffArray = []
mcNullArray = []

def index(request):
    # print("here")
    if "GET" == request.method:
        # print("entering indexx get method")
        return render(request, 'fileupload/index.html', {})
    elif "POST" == request.method:
        # print("entering index post method")
        startTime = time.time()
        shape_files1 = request.FILES["shape_file1"]  #Dataset1 points shape file
        shape_files2 = request.FILES["shape_file2"]  #Dataset2 points shape file
        shape_files3 = request.FILES["shape_file3"]  #Area shape file  #area_shape_files = request.FILES["shape_file3"]
        shape_files4 = request.FILES["shape_file4"]  #Output shape file to get the name
        outputShapeFileName = shape_files4.name    #(request.POST.get("OutputData"))+'.shp'

        shape_files1_path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), shape_files1.name))
        shape_files2_path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), shape_files2.name))
        shape_files3_path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), shape_files3.name))

        shape_files1_reference = gpd.read_file(shape_files1_path)   #Points1 Shapefile
        shape_files2_reference = gpd.read_file(shape_files2_path)   #Points2 Shapefile
        shape_files3_reference = gpd.read_file(shape_files3_path)   #AREA Shapefile

        # head, sep, tail = shape_files1.name.partition('.')
        # outputShapeFileName = head + "to" + shape_files2.name
        # shape_files3_reference.to_file(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'outputData'), outputShapeFileName)))
        # shape_files3_reference.to_file(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'outputData'), outputShapeFileName)))
        shape_files3_reference.to_file(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), outputShapeFileName)))
        shape_files3_reference.to_file(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), outputShapeFileName)))

        # newShpPath = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'outputData'), outputShapeFileName))
        newShpPath = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), outputShapeFileName))

        try:
            dataset1Geometries = shape_files1_reference.geometry
            dataset2Geometries = shape_files2_reference.geometry

            totalDatasetPoints = dataset1Geometries.size  # shape_files1_reference.size
            absTotalTestPoints = dataset2Geometries.size  # shape_files2_reference.size
            globalD = 0
            area = shape_files3_reference.geometry  # shape_files3_reference.area

            try:
                monteCarlo = int(request.POST.get("Montecarlo Runs"))
            except:
                monteCarlo = 1

            try:
                pvalueThreshold = float(request.POST.get("p-value threshold"))
            except:
                pvalueThreshold = 0.05

            #adding code to save output shapefile
            newIdcount = 0
            # Open a Shapefile, and get field names
            try:
                source = ogr.Open(newShpPath, 1)  #update=True)
                layer = source.GetLayer()
                # layer_defn = layer.GetLayerDefn()
                # field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
                # print len(field_names), 'MYFLD' in field_names
                # print(field_names)

                # Add a new field
                new_field1 = ogr.FieldDefn('NumDat1Pts', ogr.OFTInteger)
                layer.CreateField(new_field1)
                new_field2 = ogr.FieldDefn('NumDat2Pts', ogr.OFTInteger)
                layer.CreateField(new_field2)
                new_field3 = ogr.FieldDefn('pVal', ogr.OFTReal)
                layer.CreateField(new_field3)
                new_field4 = ogr.FieldDefn('dVal', ogr.OFTInteger)
                layer.CreateField(new_field4)
                new_field5 = ogr.FieldDefn('largerSet', ogr.OFTInteger)
                layer.CreateField(new_field5)
                new_field5 = ogr.FieldDefn('colFlag', ogr.OFTString)
                layer.CreateField(new_field5)

                # Close the Shapefile
            except Exception as e:
                print(e)


            for a in area:

                shp1Points = finfPontsWithInArea(a, dataset1Geometries)
                shp2Points = finfPontsWithInArea(a, dataset2Geometries)
                sumPoints = shp1Points + shp2Points
                diffPoints = abs(shp1Points - shp2Points)
                r = 0

                mc1 = [0]*monteCarlo
                mc2 = [0]*monteCarlo
                mcNull = [0]*monteCarlo
                mcDiff = [0]*monteCarlo

                try:
                    monteCarloArray = np.arange(monteCarlo)
                    mc1Array = [0]*monteCarlo
                    mc2Array = [0]*monteCarlo
                    mcDiffArray = [0]*monteCarlo    #np.array(mcDiff)
                    mcNullArray = [0]*monteCarlo    #np.array(mcNull)

                    vfunc1 = np.vectorize(monteCarloRuns, otypes=[np.int])
                    mr = vfunc1(monteCarloArray, r, monteCarlo, sumPoints, diffPoints)

                    # return r, mc1, mc2, mcNull, mcDiff
                    mrArray = np.array(mr)
                    vfunc2 = np.vectorize(sumRValue, otypes=[np.int])
                    sr=0
                    sr = vfunc2(mrArray, sr)
                    r = np.sum(sr)
                except Exception as e:
                    print(e)

                apVal = (double)(r + 1) / (double)(monteCarlo + 1)
                if (apVal >= pvalueThreshold):
                    adVal = 1
                    globalD = globalD + 1
                    aLargerSet = 0
                else:
                    adVal = 0
                    if (shp1Points > shp2Points):
                        aLargerSet = 1
                    elif (shp1Points < shp2Points):
                        aLargerSet = 2
                    else:
                        aLargerSet = -1

                # cFlag = 'w'
                if ((shp1Points > shp2Points) and (apVal<=0.05)):
                    cFlag = 'b'
                elif (shp1Points < shp2Points and (apVal<=0.05)):
                    cFlag = 'r'
                elif (apVal>0.05):
                    cFlag = 'w'
                else:
                    cFlag = 'w'

                feature = layer.GetFeature(newIdcount)

                feature.SetField(feature.GetFieldIndex("NumDat1Pts"), shp1Points)
                feature.SetField(feature.GetFieldIndex("NumDat2Pts"), shp2Points)
                feature.SetField(feature.GetFieldIndex("pVal"), apVal)
                feature.SetField(feature.GetFieldIndex("dVal"), adVal)
                feature.SetField(feature.GetFieldIndex("largerSet"), aLargerSet)
                feature.SetField(feature.GetFieldIndex("colFlag"), cFlag)
                layer.SetFeature(feature)

                newIdcount = newIdcount + 1

            source = None
            globalD = globalD / area.size
            inverseGlobalD = 1-globalD
            #globalD = 1- globalD
            print("Found global D value:", globalD)
        except Exception as e:
            print(e)
            print("Error occured in Monte Carlo Code")

        # end of monte carlo code

        #Plotting of the shapefiles and saving the plot starts

        try:
            fig, ax = plt.subplots(1)
            red_patch = mpatches.Patch(color='red', label='red points are the Test Dataset')
            blue_patch = mpatches.Patch(color='blue', label='blue points are the Base Dataset')
            white_patch = mpatches.Patch(color='black', label='blue points are the Base Dataset')
            shape_files3_reference.boundary.plot(ax=ax, edgecolor='black', figsize=(90, 90),)
            shape_files1_reference.plot(ax=ax, facecolor='blue', markersize=1)
            shape_files2_reference.plot(ax=ax, facecolor='red', markersize=1)


            savePath = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'ShapePlot2.png'))
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102),handles=[red_patch, blue_patch, white_patch],loc='upper center')
            plt.xticks(rotation=45)
            plt.savefig(savePath)

            outPut_Reference = gpd.read_file(newShpPath)
            st = 'colFlag'
            fig, ax = plt.subplots(1)
            outPut_Reference.boundary.plot(ax=ax, facecolor=outPut_Reference[st], edgecolor='black' )
            savePath1 = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'shapeAreas.png'))
            plt.xticks(rotation=45)
            plt.savefig(savePath1)
        except Exception as ex:
            print(ex)

        endTime = time.time()
        print("time in seconds below")
        print(endTime-startTime)
        # Plotting of the shapefile and saving the plot ends

        context = {
            "shape_files1" : shape_files1.name,
            "shape_files2" : shape_files2.name,
            "shape_files3" : shape_files3.name,
            "globalD" : globalD,
            "inverseGlobalD" : inverseGlobalD
        }
        return render(request,'fileupload/success.html',context )




#MonteCarlo runs method to find number of points within an area
def finfPontsWithInArea(a, b):
    numOfPoints = 0
    for x in b:
        if (a.contains(x)):
            numOfPoints = numOfPoints + 1
    return numOfPoints


def sumRValue(mrArray, r):
    r = r+np.sum(mrArray)
    return r


def monteCarloRuns(montecarloArray, r, montecarlo, sumPoints, diffPoints):

    try:
        cnt1 = 0
        cnt2 = 0
        cnt3 = 0
        mc1Array = [0] * montecarlo
        mc2Array = [0] * montecarlo
        mcNullArray = [0] * montecarlo
        mcDiffArray = [0] * montecarlo

        vfunc = np.vectorize(threaded_process, otypes=[np.int, np.int, np.int])
        random_float_array = np.random.rand(sumPoints, 1)
        vr = vfunc(random_float_array, cnt1, cnt2, cnt3)

        mc1Array[montecarloArray] = np.sum(vr[0])
        mc2Array[montecarloArray] = np.sum(vr[1])
        mcNullArray[montecarloArray] = np.sum(vr[2])
        mcDiffArray[montecarloArray] = abs(mc1Array[montecarloArray] - mc2Array[montecarloArray])
        if (mcDiffArray[montecarloArray] >= diffPoints):
            r = r + 1
        return r
    except Exception as e:
        print(e)


def threaded_process(xi, mc1, mc2, mcNull):

    if (xi < 0.5):
        mc1 = mc1 + 1
    elif (xi > 0.5):
        mc2 = mc2 + 1
    else:
        mcNull = mcNull + 1

    return mc1, mc2, mcNull



###################################################################SUCCESS

def success(request):

    if "GET" == request.method:
        # print("entered success get")
        return render(request,'fileupload/success.html',{})
    elif "POST" == request.method:
        return render(request,'fileupload/index.html',{})


