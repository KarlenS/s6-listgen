#!/usr/bin/python

# Script to convert list of stage 5 files to the format required by stage6 in vegas 2.5
# The first argument is the stage 5 run list file.
# The second argument is the reformatted output file.
#
# The script only identifies the number of tels, na/oa, and summer/winter.
# The user must still match up EA tags with the real
# EA files. The script doesn't know where you keep your set of EAs.
# The script also doesn't know about things like soft/med/hard or H vs HFit.  
#
# Contents of CONFIG blocks of each group are left blank. The user should add the desired
# cuts or configs (e.g., S6A_RingSize 0.17)
#
# Format assumed for stage 5 files is /path/to/file/<RUN ID>.stage5.root
#
# Winter atmosphere (ATM21) is from November through March
# Summer atmosphere (ATM22) is from April to October

import subprocess 
import argparse
import sys

class ListGen(object):
    
  #Dates for array configs
  NA_date = "2009-09-01"
  UA_date = "2012-09-01"

  #Database information
  hostName = "lucifer1.spa.umn.edu"
  portNum = 33060

  def __init__(self):
    
    #define months for ATM21/ATM22 distinction
    self.spring_cutoff = 3  #ATM21 goes through this month 
    self.fall_cutoff = 11   #ATM22 goes up to this month (not including)
    self.matchEA = True
    self.EA_file_dir = "/data/lucifer1.1/veritas/lookups/vegas/v2_5_0/ea/"  

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
    config_mask_ref={0 : "_xxxx",
                     1 : "_T1",
                     2 : "_T2",
                     3 : "_T1T2",
                     4 : "_T3",
                     5 : "_T1T3",
                     6 : "_T2T3",
                     7 : "_T1T2T3",
                     8 : "_T4",
                     9 : "_T1T4",
                     10 : "_T2T4",
                     11 : "_T1T2T4",
                     12 : "_T3T4",
                     13 : "_T1T3T4",
                     14 : "_T2T3T4",
                     15 : "",
    }

    return config_mask_ref[tel_config_mask]

  def reconcile_tel_masks(self, tel_cut_mask, tel_config_mask):
    #when tel_cut_mask is present, checks it against tel_config_mask
    #and returns the result
    #!!! the case where the two do not match is not handled !!!
    tel_cut_ref_T1 = ["1","2","3","4","5","6","7","NULL","0"]
    tel_cut_ref_T2 = ["1","2","3","8","9","10","11","NULL","0"]
    tel_cut_ref_T3 = ["1","4","5","8","9","12","13","NULL","0"]
    tel_cut_ref_T4 = ["2","4","6","8","10","12","14","NULL","0"]
  
    config_ref_T1 = [1,3,5,7,9,11,13,15]
    config_ref_T2 = [2,3,6,7,10,11,14,15]
    config_ref_T3 = [4,5,6,7,12,13,14,15]
    config_ref_T4 = [8,9,10,11,12,13,14,15]
      
    tel_config = "_"
    T1 = ""
    T2 = ""
    T3 = ""
    T4 = ""

    if str(tel_cut_mask) in tel_cut_ref_T1 and tel_config_mask in config_ref_T1:
      T1="T1"
      tel_config = str(T1)+str(T2)+str(T3)+str(T4)
      
    if str(tel_cut_mask) in tel_cut_ref_T2 and tel_config_mask in config_ref_T2:
      T2="T2"
      tel_config=str(T1)+str(T2)+str(T3)+str(T4)
      
    if str(tel_cut_mask) in tel_cut_ref_T3 and tel_config_mask in config_ref_T3:
      T3="T3"
      tel_config=str(T1)+str(T2)+str(T3)+str(T4)
      
    if str(tel_cut_mask) in tel_cut_ref_T4 and tel_config_mask in config_ref_T4:
      T4="T4"
      tel_config=str(T1)+str(T2)+str(T3)+str(T4)

    if (tel_config == "_T1T2T3T4"):
      tel_config = ""

    return tel_config


  def get_atm(self, query):
    #parses query result for month (day) and returns appropriate ATM (21 or 22)
    month = int(query.split("\t")[0])
    day = int(query.split("\t")[1]) #can define division for a specific day of month

    if month <= self.spring_cutoff or month >= self.fall_cutoff:
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
      return "ua"
    elif date_diff_NA >= 0:
      return "na"
    elif date_diff_NA < 0:
      return "oa"

  def get_EA_file(self, EA_config, cuts):
    
    simType = "ea"
    simDate = "_Oct2012"
    simPars = "_7sam_Alloff"
    cuts = "_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01"
    
    #config = "_" + EA_config[0:8]
    #tel = EA_config[9:]
    vegasv = "vegasv250rc5_"

    EA_choices = { "ua_ATM22" : "ea_Oct2012_ua_ATM22_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM22_T2T3T4" : "ea_Oct2012_ua_ATM22_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM22_T1T3T4" : "ea_Oct2012_ua_ATM22_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM22_T1T2T4" : "ea_Oct2012_ua_ATM22_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM22_T1T2T3" : "ea_Oct2012_ua_ATM22_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM21" : "ea_Oct2012_ua_ATM21_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM21_T2T3T4" : "ea_Oct2012_ua_ATM21_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM21_T1T3T4" : "ea_Oct2012_ua_ATM21_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM21_T1T2T4" : "ea_Oct2012_ua_ATM21_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "ua_ATM21_T1T2T3" : "ea_Oct2012_ua_ATM21_vegasv250rc5_7sam_Alloff_s700t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM22" : "ea_Oct2012_na_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM22_T2T3T4" : "ea_Oct2012_na_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM22_T1T3T4" : "ea_Oct2012_na_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM22_T1T2T4" : "ea_Oct2012_na_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM22_T1T2T3" : "ea_Oct2012_na_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM21" : "ea_Oct2012_na_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM21_T2T3T4" : "ea_Oct2012_na_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM21_T1T3T4" : "ea_Oct2012_na_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM21_T1T2T4" : "ea_Oct2012_na_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "na_ATM21_T1T2T3" : "ea_Oct2012_na_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM22" : "ea_Oct2012_oa_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01.root_LZA",
                   "oa_ATM22_T2T3T4" : "ea_Oct2012_oa_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root", 
                   "oa_ATM22_T1T3T4" : "ea_Oct2012_oa_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM22_T1T2T4" : "ea_Oct2012_oa_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM22_T1T2T3" : "ea_Oct2012_oa_ATM22_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM21" : "ea_Oct2012_oa_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM21_T2T3T4" : "ea_Oct2012_oa_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM21_T1T3T4" : "ea_Oct2012_oa_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM21_T1T2T4" : "ea_Oct2012_oa_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   "oa_ATM21_T1T2T3" : "ea_Oct2012_oa_ATM21_vegasv250rc5_7sam_Alloff_s400t2_std_MSW1p1_MSL1p3_MH7_ThetaSq0p01_LZA.root",
                   }

    return EA_choices[EA_config]

  def print_runlist(self,groups,outfile):
    #takes dictionary of run groups and output file and
    #prints them according to the format required by v2.5.1+
    GROUPID = 0
    for EA_config, group_runs in groups.iteritems():
      #handles first group that requires special formatting(not printing config)
      if GROUPID == 0:
        for l in group_runs:
          outfile.write( l+"\n" )
        outfile.write( "[EA ID: %s]\n" % (GROUPID) )
        if self.matchEA: EA_config = self.EA_file_dir + self.get_EA_file(EA_config,'med')
        outfile.write( EA_config + "\n" )
        outfile.write( "[/EA ID: %s]\n" % (GROUPID) )
        GROUPID += 1
      #for all other groups
      else:
        outfile.write( "[RUNLIST ID: %s]\n" % (GROUPID) )
        for l in group_runs:
          outfile.write( l +"\n")
        outfile.write( "[/RUNLIST ID: %s]\n" % (GROUPID) )
        #prints out Effective Area blocks for each group
        #currently, it writes codes for EA file, which then
        #need to be replaced by the full EA paths
        #ADD AUTOMATCHING FUNCTIONALITY
        if self.matchEA: EA_config = self.EA_file_dir + self.get_EA_file(EA_config,'med')
        outfile.write( "[EA ID: %s]\n" % (GROUPID) )
        outfile.write( EA_config +"\n")
        outfile.write( "[/EA ID: %s]\n" % (GROUPID) )
        outfile.write( "[CONFIG ID: %s]\n" % (GROUPID) )
        outfile.write( "[/CONFIG ID: %s]\n" % (GROUPID) )
        GROUPID += 1

def main():

  #parsing arguments
  parser = argparse.ArgumentParser(description='Takes an input file with paths to stage5 files and generates a runlist for stage6. Note: the runlist still needs to be manually edited to input the proper paths to EA files and fill out the Config blocks with desired cuts/configs.')
  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Input file name with list of stage5 root files, containing paths to the files")
  parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="Output file name written out with the properly formatted runlist") 
  parser.add_argument('--cuts', nargs='?', default='med', help="Takes either 'med' or 'soft' for medium or soft analysis") 
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
      print "No DQM info exists, using observer reported tel-config"
      telcombo = runsobj.get_tel_combo(tconfigmask)
    #if TEL_CUT_MASK does exist, crosschecking with CONFIG_MASK
    else:      
      print "DQM info available, cross-checking with observer-reported tel config"
      telcombo = runsobj.reconcile_tel_masks(tcutmask, tconfigmask)
    
    
    #combined configuration code for identifying runs with groups
    fullConfig = ac + atm + telcombo 
    
    #check to see if a group already exists for a given config and add run to group
    #otherwise, create a new group and add run to group
    if fullConfig in groups:
      groups[fullConfig].append(run)
    else:
      groups[fullConfig] = [run]

  #prints the runlist
  runsobj.print_runlist(groups,args.outfile)
  
if __name__ == '__main__':
  main()
