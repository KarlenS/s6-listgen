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
# Winter atmosphere (ATM21) is from November to March
# Summer atmosphere (ATM22) is from April to October

import subprocess 
import sys
import argparse
import os.path


class ListGen(object):

  def _init_(self, info, query):
    
    self.query = query

    #Dates for array configs
    self.NA_date = "2009-09-01"
    self.UA_date = "2012-09-01"

    #Database information
    self.hostName = "lucifer1.spa.umn.edu"
    self.portNum = 33060

  def runSQL(self, execCMD, database):
    #runs the mysql command provided and returns the output
    sqlOut = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly",\ 
                               "-D","%s" %(database), "--execute=%s" %(execCMD)], stdout=subprocess.PIPE)
    query, err = sqlOut.communicate()
    return query

  
  def get_tel_cut_mask(self, query):
    return query.rstrip().split("\n")[1]

  
  def get_tel_combo(self, query):
    
    config_mask_ref={0 : "xxxx",
                     1 : "1xxx",
                     2 : "x2xx",
                     3 : "12xx",
                     4 : "xx3x",
                     5 : "1x3x",
                     6 : "x23x",
                     7 : "123x",
                     8 : "xxx4",
                     9 : "1xx4",
                     10 : "x2x4",
                     11 : "12x4",
                     12 : "xx34",
                     13 : "1x34",
                     14 : "x234",
                     15 : "1234",
    }

    config_mask = int(query.rstrip().split("\n")[1])

    return ref_dict[config_mask]

  def reconcile_tels(self, tel_cut_mask, tel_config_mask):

    
  def get_atm(self, query):

    month = int(query.rstrip().split("\n")[1])

    if month <= 3 or month >= 11:
      return "ATM21"
    elif month >= 4 and month <= 10:
      return "ATM22"


  def get_array_config(self, query1,query2):

    date_diff = int(query1.rstrip().split("\n")[1])
    date_diff2 = int(query2.rstrip().split("\n")[1])
    
    #Choose upgrade, new, or old array
    if date_diff2 >= 0:
      return "UA"
    elif date_diff >= 0:
      return "NA"
    elif date_diff < 0:
      return "OA"

  def print_runlist(self,filename):
  #opening file for writing out the final runlist
  outfile = open(filename,"w")
  
  gROUPID = 0
  for key, value in groups.iteritems():
    if GROUPID == 0:
      for l in value:
        outfile.write( l+"\n" )
      outfile.write( "[EA ID: %s]\n" % (GROUPID) )
      outfile.write( key + "\n" )
      outfile.write( "[/EA ID: %s]\n" % (GROUPID) )
      GROUPID += 1
    else:
      outfile.write( "[RUNLIST ID: %s]\n" % (GROUPID) )
      for l in value:
        outfile.write( l +"\n")
      outfile.write( "[/RUNLIST ID: %s]\n" % (GROUPID) )
      outfile.write( "[EA ID: %s]\n" % (GROUPID) )
      outfile.write( key +"\n")
      outfile.write( "[/EA ID: %s]\n" % (GROUPID) )
      outfile.write( "[CONFIG ID: %s]\n" % (GROUPID) )
      outfile.write( "[/CONFIG ID: %s]\n" % (GROUPID) )
      GROUPID += 1
  
  outfile.close()

def main():
 # Check if an arg is passed and if file exists

  cmdargs = sys.argv
  nargs = len(sys.argv)

  if nargs <= 1 or not os.path.isfile(cmdargs[1]): # Check if an arg is passed and if file exists
    print "Pass valid file to parse as first argument"
    print "USAGE: python s6runlistGen.py stage5files.list (optional)outfileName.list"
    sys.exit()
  else:
    infile = open(cmdargs[1],"r")
  
  if nargs == 2: #if only one argument is given, use default filename for output file
    print"No output file specified.  (Over-)Writing 'runlist_temp.txt'"
    outname="runlist_temp.txt"
  else:
    outname=cmdargs[2]
  
  if os.path.isfile(outname):
    os.remove(outname)
  
  
  
  #Dictionary to keep track of groups
  groups = {}
  
  
  #mySQL queries
  
  lines = infile.read().rstrip().split('\n') #temporary - make this nicer too...
  infile.close()
  
  #Loop through file and execute for each run
  for run in lines:
    runID = run[-17:-12]
    print "Querying",runID, "..."
  
    #Do mySQL queries through command line, using subprocess module
    execCMD = "select tel_cut_mask from tblRun_Analysis_Comments where run_id='%s'" %(runID)
    sqlOut = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VOFFLINE", "--execute=%s" %(execCMD)], stdout=subprocess.PIPE)
    QUERY, err1 = sqlOut.communicate()
    
    execCMD2a = "select DATEDIFF(data_start_time,'%s') from tblRun_Info where run_id='%s'" %(NA_date, runID)
    sqlOut2a = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD2a)], stdout=subprocess.PIPE)
    QUERY2a, err2a = sqlOut2a.communicate()
  
    execCMD2b = "select DATEDIFF(data_start_time,'%s') from tblRun_Info where run_id='%s'" %(UA_date, runID)
    sqlOut2b = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD2b)], stdout=subprocess.PIPE)
    QUERY2b, err2b = sqlOut2b.communicate()
  
    
    execCMD3 = "select MONTH(data_start_time) from tblRun_Info where run_id='%s'" %(runID)
    sqlOut3 = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD3)], stdout=subprocess.PIPE)
    QUERY3, err = sqlOut3.communicate()
    
    execCMD4 = "select config_mask from tblRun_Info where run_id='%s'" %(runID)
    sqlOut4 = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD4)], stdout=subprocess.PIPE)
    QUERY4, err = sqlOut4.communicate()
  
    #parsing through sql results to get needed info
    #TEL_CUT_MASK = QUERY.rstrip().split("\n")[1]
    #DATE_DIFF = int(QUERY2a.rstrip().split("\n")[1])
    #DATE_DIFF2 = int(QUERY2b.rstrip().split("\n")[1])
    #MONTH = int(QUERY3.rstrip().split("\n")[1])
    #CONFIG_MASK = int(QUERY4.rstrip().split("\n")[1])
    
    #print TEL_CUT_MASK,DATE_DIFF,DATE_DIFF2,MONTH,CONFIG_MASK
  
    #Choose upgrade, new, or old array
    #if DATE_DIFF2 >= 0:
    #  ARRAY = "UA"
    #elif DATE_DIFF >= 0:
    #  ARRAY = "NA"
    #elif DATE_DIFF < 0:
    #  ARRAY = "OA"
    
  
    #Choose seasonal tables
    #if MONTH <= 3 or MONTH >= 11:
    #  SEASON = "ATM21"
    #elif MONTH >= 4 and MONTH <= 10:
    #  SEASON = "ATM22"
  
    
    #Choose telescope combination
    TELTOANA = ""
    T1 = "x"
    T2 = "x"
    T3 = "x"
    T4 = "x"
    if TEL_CUT_MASK == "NULL":
      print "No DQM info exists, using observer reported tel-config"
      #call run.get_tel_combo(query)
    
    #if TEL_CUT_MASK does exist, crosschecking with CONFIG_MASK
    else:
      print "DQM info available, cross-checking with observer-reported tel config"
      TEL_CUT_REF_T1 = ["1","2","3","4","5","6","7","NULL","0"]
      TEL_CUT_REF_T2 = ["1","2","3","8","9","10","11","NULL","0"]
      TEL_CUT_REF_T3 = ["1","4","5","8","9","12","13","NULL","0"]
      TEL_CUT_REF_T4 = ["2","4","6","8","10","12","14","NULL","0"]
  
      CONFIG_REF_T1 = [1,3,5,7,9,11,13,15]
      CONFIG_REF_T2 = [2,3,6,7,10,11,14,15]
      CONFIG_REF_T3 = [4,5,6,7,12,13,14,15]
      CONFIG_REF_T4 = [8,9,10,11,12,13,14,15]
  
      if str(TEL_CUT_MASK) in TEL_CUT_REF_T1 and CONFIG_MASK in CONFIG_REF_T1:
        T1=1
        TELTOANA = str(T1)+str(T2)+str(T3)+str(T4)
      
      if str(TEL_CUT_MASK) in TEL_CUT_REF_T2 and CONFIG_MASK in CONFIG_REF_T2:
        T2=2
        TELTOANA=str(T1)+str(T2)+str(T3)+str(T4)
      
      if str(TEL_CUT_MASK) in TEL_CUT_REF_T3 and CONFIG_MASK in CONFIG_REF_T3:
        T3=3
        TELTOANA=str(T1)+str(T2)+str(T3)+str(T4)
      
      if str(TEL_CUT_MASK) in TEL_CUT_REF_T4 and CONFIG_MASK in CONFIG_REF_T4:
        T4=4
        TELTOANA=str(T1)+str(T2)+str(T3)+str(T4)
      
    fullConfig = ARRAY + "_"+ SEASON +"_"+ "T" + TELTOANA 
    #check to see if the group already exists and add run to group
    if fullConfig in groups:
      groups[fullConfig].append(run)
    else:
      groups[fullConfig] = [run]
  
  
if __name__ = '__main__":
  main()
