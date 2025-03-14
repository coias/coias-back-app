#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 17:00 sugiura
###################################################################################
# precise_orbit_directories.txtに記載のディレクトリ以下にあるsearch_astB.txtたち
# を集めて, カレントディレクトリにまとめて1つにしたsearch_astB.txtを生成する.
# ただし, precise_orbit_directories.txtに記載のディレクトリ以下のsearch_astB.txtは
# 汎用的にするために各行に画像番号の情報が付与されていないため,
# 行末に画像番号の情報を付加しながらカレントに集めてsearch_astB.txtを生成する.
# また1枚目の画像に対応するprecise_orbit_directories.txtに記載のディレクトリから
# bright_asteroid_MPC_names_in_the_field.txtとname_conversion_list_in_the_field.txtを
# カレントディレクトリにコピーする.
# 入力: precise_orbit_directories.txtに記載のディレクトリ以下にあるsearch_astB.txtたち
# 出力: search_astB.txt
# 　　    書式: 確定番号or仮符号 jd ra[degree] dec[degree] mag 画像番号
# 　　  bright_asteroid_MPC_names_in_the_field.txt
# 　　  name_conversion_list_in_the_field.txt
###################################################################################
import os
import subprocess
import traceback
import print_detailed_log

try:
    #---read precise_orbit_directories.txt---------------------------------------
    directoryNames = []
    isCorrectDirectory = []
    preciseOrbitDirectoriesFile = open("precise_orbit_directories.txt","r")
    lines = preciseOrbitDirectoriesFile.readlines()
    Ndata = len(lines)
    for line in lines:
        content = line.split()
        directoryNames.append(content[0])
        isCorrectDirectory.append(int(content[1]))
    preciseOrbitDirectoriesFile.close()
    #----------------------------------------------------------------------------

    #---check all directories have ra_dec_jd_time.txt and search_astB.txt--------
    for i in range(Ndata):
        if not os.path.isfile(directoryNames[i]+"/ra_dec_jd_time.txt"):
            print("There is no ra_dec_jd_time.txt in {}".format(directoryNames[i]))
            raise FileNotFoundError
        if not os.path.isfile(directoryNames[i]+"/search_astB.txt"):
            print("There is no search_astB.txt in {}".format(directoryNames[i]))
            raise FileNotFoundError
    #----------------------------------------------------------------------------

    #---add image number to all data in search_astB.txt in each directory--------
    for i in range(Ndata):
        inputFile = open(directoryNames[i]+"/search_astB.txt","r")
        outputFile = open("search_astB_{0:02d}.txt".format(i),"w",newline="\n")
        lines = inputFile.read().splitlines()
        for l in range(len(lines)):
            outputFile.write(lines[l]+" {0:d} ".format(i)+"\n")
        inputFile.close()
        outputFile.close()
    #----------------------------------------------------------------------------

    #---gather all search_astB_*.txt in the currrent directory to search_astB.txt in the current directory while sorting-
    errorList=[]
    command = "cat "
    for i in range(Ndata):
        command = command + "search_astB_{0:02d}.txt ".format(i)
    command = command + "|sort -n > search_astB.txt"
    completed_process = subprocess.run(command, shell=True)
    errorList.append(completed_process.returncode)
    #--------------------------------------------------------------------------------------------------------------------

    #---copy asteroid name list stored in ~/.coias/orbit_data to the current directory-----------------------------------
    completed_process = subprocess.run("cp {0}/bright_asteroid_MPC_names_in_the_field.txt ./".format(directoryNames[0]),shell=True)
    errorList.append(completed_process.returncode)
    completed_process = subprocess.run("cp {0}/name_conversion_list_in_the_field.txt ./".format(directoryNames[0]),shell=True)
    errorList.append(completed_process.returncode)
    #--------------------------------------------------------------------------------------------------------------------

    for e in errorList:
        if e!=0:
            raise FileNotFoundError

except FileNotFoundError:
    print("Some previous files are not found in make_gathered_search_astB.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in make_gathered_search_astB.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 502 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
