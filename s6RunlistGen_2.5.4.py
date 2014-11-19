#!/usr/bin/python

# author: Karlen Shahinyan
# email: shahin@astro.umn.edu
# last updated: 11/12/14
#
# This is a script to convert list of stage 5 files to the format required by stage6 in vegas 2.5
# The first argument is the stage 5 run list file.
# The second argument is the reformatted output file.
#
# For info & listing of all arguments/options use:
# python s6RunlistGen.py --help 
#
# The script only identifies the number of tels, na/oa, and summer/winter.
#
# There is now an automated EA path/filename generation option --EAmatch (based on standard convention).
# When enabled, the script will take user specifiable command-line values (default if not specified)
# for all other parameters required for generating EA filenames.
#
# Contents of CONFIG blocks of each group are left blank. The user should add the desired
# cuts or configs (e.g., S6A_RingSize 0.17)
#
# Format assumed for stage 5 files is /path/to/file/<RUN ID>.stage5.root
#
# Winter atmosphere (ATM21) is from mid November through mid March
# Summer atmosphere (ATM22) is from mid March through mid November
#
# The script does not currently support HFit EA filename generation
# nor does it differentiate between normal runs & reducedHV/filter runs (but will very soon)

import subprocess 
import argparse
import sys

class ListGen(object):
    
  #Dates for array configs
  NA_date = "2009-09-01"
  UA_date = "2012-09-01"

  #Database information
  hostName = "romulus.ucsc.edu"
  portNum = ""

  def __init__(self):
    
    #define months for ATM21/ATM22 distinction
    self.spring_cutoff = 3  #ATM21 goes through this month 
    self.fall_cutoff = 11   #ATM22 goes up to this month (not including)
    self.day_cutoff = 15 # day of month for dividing ATM21/ATM22
    self.matchEA = False
    self.EA_file_dir = "./"  

  def runSQL(self, execCMD, database):
    #runs the mysql command provided and returns the output list of results
    sqlOut = subprocess.Popen(["mysql","-h","%s" %(self.hostName),"-P","%s" %(self.portNum),"-u", "readonly", 
                               "-D","%s" %(database), "--execute=%s" %(execCMD)], stdout=subprocess.PIPE)
    query, err = sqlOut.communicate()
    #return query
    return query.rstrip().split("\n")[1]

  
  def get_tel_cut_mask(self, query):
    #parses query output for tel_cut_mask
    return query

  
  def get_tel_config_mask(self, query):
    #parses query output for config_mask
    return int(query.split("\t")[4])

  def get_tel_combo(self, tel_config_mask):
    #uses config mask to determine telescope participation
    config_mask_ref={0 : "_1234",
                     1 : "_1---",
                     2 : "_-2--",
                     3 : "_12--",
                     4 : "_--3-",
                     5 : "_1-3-",
                     6 : "_-23-",
                     7 : "_123-",
                     8 : "_---4",
                     9 : "_1--4",
                     10 : "_-2-4",
                     11 : "_12-4",
                     12 : "_--34",
                     13 : "_1-34",
                     14 : "_-234",
                     15 : "_1234",
    }

    return config_mask_ref[tel_config_mask]

  def reconcile_tel_masks(self, tel_cut_mask, tel_config_mask):
    #when tel_cut_mask is present, checks it against tel_config_mask
    #and returns the result
    tel_cut_ref_T1 = ["1","2","3","4","5","6","7","NULL","0"]
    tel_cut_ref_T2 = ["1","2","3","8","9","10","11","NULL","0"]
    tel_cut_ref_T3 = ["1","4","5","8","9","12","13","NULL","0"]
    tel_cut_ref_T4 = ["2","4","6","8","10","12","14","NULL","0"]
  
    config_ref_T1 = [1,3,5,7,9,11,13,15]
    config_ref_T2 = [2,3,6,7,10,11,14,15]
    config_ref_T3 = [4,5,6,7,12,13,14,15]
    config_ref_T4 = [8,9,10,11,12,13,14,15]
      
    DQM_tel_config = "_"
    T1 = T2 = T3 = T4 = "-"

    if str(tel_cut_mask) in tel_cut_ref_T1:
      T1="1"
      
    if str(tel_cut_mask) in tel_cut_ref_T2:
      T2="2"
      
    if str(tel_cut_mask) in tel_cut_ref_T3:
      T3="3"
      
    if str(tel_cut_mask) in tel_cut_ref_T4:
      T4="4"
    
    DQM_tel_config += str(T1) + str(T2) + str(T3) + str(T4)

    #observer
    obs_tel_config = self.get_tel_combo(tel_config_mask)
    #check for consistency between DQM & observer reported telescope participation
    if DQM_tel_config == obs_tel_config:
      return DQM_tel_config
    else:
      print "DQM and observer reported telescope participation info do not match!"
      print "DQM reported:", DQM_tel_config, "   observer reported: ", obs_tel_config
      print "Using DQM-reported info."
      return DQM_tel_config


  def get_atm(self, query):
    #parses query result for month (day) and returns appropriate ATM (21 or 22)
    month = int(query.split("\t")[0])
    day = int(query.split("\t")[1]) #can define division for a specific day of month

    if (month <= self.spring_cutoff and day <=self.day_cutoff) or (month >= self.fall_cutoff and day >= self.day_cutoff):
      return "_ATM21"
    else:
      return "_ATM22"

  def get_array_config(self, query):
    #parses query result for difference between run date & NA
    #and run date & UA and returns array config (OA, NA, or UA)
    date_diff_NA = int(query.split("\t")[2])
    date_diff_UA = int(query.split("\t")[3])
    
    #Choose upgrade, new, or old array
    if date_diff_UA >= 0:
      return "V6_PMTUpgrade"
    elif date_diff_NA >= 0:
      return "V5_T1Move"
    elif date_diff_NA < 0:
      return "V4_OldArray"

  def get_EA_file(self, EA_config, *user_configs):
    #EA filename generator based on standard naming conventions
    
    #Get epoch, season, & telescope participation from strings used for grouping
    Epoch = "_" + EA_config[:-11] 
    SeasonID = "_" + EA_config[-10:-5] 
    TelConfig = EA_config[-5:]
    if (TelConfig == "_1234"):
      TelConfig = ""
    
    #read in user-config options
    cuts, SimModel, SimSource, Offset, TelMulti, LZA = user_configs
    TelMulti=TelMulti[1:]
    if LZA == "_":
      LZA = ""

    VegasV = "_vegasv250rc5"
    NumSamples = "_7sam"
    Method = "_std" #HFit not yet enabled

    cuts = user_configs[0]
    #Cut-specific options - real ugly, should be prettied
    if cuts == "_soft":
      if Epoch == "_V6_PMTUpgrade":
        SizeCut = "_s400"
      else:
        SizeCut = "_s200"

      MSW = "_MSW1.1"
      MSL = "_MSL1.3"
      MH = "_MH7"
      ThetaSq = "_ThetaSq0.03"

    elif cuts =="_med":
      if Epoch == "_V6_PMTUpgrade":
        SizeCut = "_s700"
      else:
        SizeCut = "_s400"

      MSW = "_MSW1.1"
      MSL = "_MSL1.3"
      MH = "_MH7"
      ThetaSq = "_ThetaSq0.01"

    elif cuts == "_hard":
      if Epoch == "_V6_PMTUpgrade":
        SizeCut = "_s1200"
      else:
        SizeCut = "_s1000"

      MSW = "_MSW1.1"
      MSL = "_MSL1.4"
      MH = ""
      ThetaSq = "_ThetaSq0.01"

    elif cuts == "_loose":
      if Epoch == "_V6_PMTUpgrade":
        SizeCut = "_s400"
      else:
        SizeCut = "_s200"

      MSW = "_MSW1.3"
      MSL = "_MSL1.4"
      MH = ""
      ThetaSq = "_ThetaSq0.03"

    EAFilename = ("ea" + SimModel + Epoch + SeasonID + SimSource + VegasV + 
                 NumSamples + Offset + SizeCut + TelMulti + Method + MSW + 
                 MSL + MH + ThetaSq + TelConfig + LZA + ".root")

    return EAFilename

  def print_runlist(self,groups,outfile,*user_configs):
    #takes dictionary of run groups and output file and
    #prints them according to the format required by v2.5.1+
    GROUPID = 0
    for EA_config, group_runs in groups.iteritems():
      #handles first group that requires special formatting(not printing config)
      if GROUPID == 0:
        for l in group_runs:
          outfile.write( l+"\n" )
        outfile.write( "[EA ID: %s]\n" % (GROUPID) )
        if self.matchEA == True: 
          EA_config = self.EA_file_dir + self.get_EA_file(EA_config,*user_configs)
        outfile.write( EA_config + "\n" )
        outfile.write( "[/EA ID: %s]\n" % (GROUPID) )
        GROUPID += 1
      #for all other groups
      else:
        outfile.write( "[RUNLIST ID: %s]\n" % (GROUPID) )
        for l in group_runs:
          outfile.write( l +"\n")
        outfile.write( "[/RUNLIST ID: %s]\n" % (GROUPID) )
        if self.matchEA == True: 
          EA_config = self.EA_file_dir + self.get_EA_file(EA_config,*user_configs)
        outfile.write( "[EA ID: %s]\n" % (GROUPID) )
        outfile.write( EA_config +"\n")
        outfile.write( "[/EA ID: %s]\n" % (GROUPID) )
        outfile.write( "[CONFIG ID: %s]\n" % (GROUPID) )
        outfile.write( "[/CONFIG ID: %s]\n" % (GROUPID) )
        GROUPID += 1

def main():

  #parsing arguments
  parser = argparse.ArgumentParser(description='Takes an input file with paths to stage5 files and generates a runlist for stage6. Note: the runlist still needs to be manually edited to fill out the Config blocks with desired cuts/configs and plug in EA paths. Use options --EAmatch and --EAdir /path/to/EAfiles/ if you want to automatically generate and plug in EA paths/names based on standard naming convention.')
  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Input file name with list of stage5 root files, containing paths to the files.")
  parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="Output file for writing formatted runlist. If skipped, will print to screen.") 
  parser.add_argument('--EAmatch', default='False',action='store_true', help="Set option to enable automatic EA filename generation.") 
  parser.add_argument('--EAdir', nargs='?', default='./', help="Path to directory containing EA files") 
  parser.add_argument('--cuts', nargs='?', default='med',choices=['soft','med','hard','loose'], help="Cuts used for the analysis.") 
  parser.add_argument('--SimModel', nargs='?', default='Oct2012', help="'Oct2012' (GrISUDet) or 'MDL10UA' or 'MDL15NA' etc (KASCADE)") 
  parser.add_argument('--SimSource', nargs='?', default='GrISUDet', help="Simulation type ('GrISUDet' or 'KASCADE' or 'CARE') used to generate EAs") 
  parser.add_argument('--Offset', nargs='?', default='Alloff',choices=['Alloff','050off'], help="Specifies Offsets covered by EA ('Alloff' or '050off')") 
  parser.add_argument('--TelMulti', nargs='?', default='t2', help="Telescope Multiplicity (t2, t3, or t4)") 
  parser.add_argument('--LZA', nargs='?', default='LZA',choices=['LZA',''], help="'LZA' or '' if not LZA ") 
  args = parser.parse_args()

  #Define a ListGen object
  runsobj = ListGen() 
  
  #Dictionary to keep track of groups
  groups = {}
  
  #Read stage5 file paths into a list
  lines = args.infile.read().rstrip().split('\n') 
 
  #Loop through file and execute for each run
  for run in lines:
    runID = run[-17:-12]
    print "Querying",runID, "..."
  
    #Do mySQL queries through command line, using subprocess module 
    execCMD_TCM = "select tel_cut_mask from tblRun_Analysis_Comments where run_id='%s'" %(runID)
    
    execCMD_all = "select MONTH(data_start_time),DAY(data_start_time),DATEDIFF(data_start_time,'%s'),DATEDIFF(data_start_time,'%s'),config_mask from tblRun_Info where run_id='%s'" %(runsobj.NA_date,runsobj.UA_date,runID)
    
    #Retrieve query results
    q_tcutmask = runsobj.runSQL(execCMD_TCM,'VOFFLINE')
    q_all = runsobj.runSQL(execCMD_all,'VERITAS')
    
    #use query results to determine parameters required for grouping runs
    tcutmask = runsobj.get_tel_cut_mask(q_tcutmask)
    ac = runsobj.get_array_config(q_all)
    atm = runsobj.get_atm(q_all)
    tconfigmask = runsobj.get_tel_config_mask(q_all)
  
    #Choose telescope combination
    if tcutmask == "NULL":
      #print "No DQM info exists, using observer reported tel-config"
      telcombo = runsobj.get_tel_combo(tconfigmask)
    #if TEL_CUT_MASK does exist, crosschecking with CONFIG_MASK
    else:      
      #print "DQM info available, cross-checking with observer-reported tel config"
      telcombo = runsobj.reconcile_tel_masks(tcutmask, tconfigmask)
    
    #combined configuration code for identifying runs with groups
    fullConfig = ac + atm + telcombo 
    
    #check to see if a group already exists for a given config and add run to group
    #otherwise, create a new group and add run to group
    if fullConfig in groups:
      groups[fullConfig].append(run)
    else:
      groups[fullConfig] = [run]
  
  #Switching auto EA filename generation on if requested
  runsobj.matchEA = args.EAmatch
  print runsobj.matchEA
  
  #Setting EA file location specified by user. Default is ./
  runsobj.EA_file_dir = args.EAdir 

  #passing arguments specifiable by users for producing correct EA filenames
  user_configs=[args.cuts, args.SimModel, args.SimSource, args.Offset, args.TelMulti, args.LZA]
  user_configs=["_" + user_config for user_config in user_configs]

  #prints the runlist
  runsobj.print_runlist(groups,args.outfile,*user_configs)
  
if __name__ == '__main__':
  main()
