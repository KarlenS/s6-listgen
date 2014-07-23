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
import argparse
import sys

class ListGen(object):
    
  #Dates for array configs
  NA_date = "2009-09-01"
  UA_date = "2012-09-01"

  #Database information
  hostName = "lucifer1.spa.umn.edu"
  portNum = 33060

  def _init_(self, query):
    
    self.query = query


  def runSQL(self, execCMD, database):
    #runs the mysql command provided and returns the output
    sqlOut = subprocess.Popen(["mysql","-h","%s" %(self.hostName),"-P","%s" %(self.portNum),"-u", "readonly", 
                               "-D","%s" %(database), "--execute=%s" %(execCMD)], stdout=subprocess.PIPE)
    query, err = sqlOut.communicate()
    return query

  
  def get_tel_cut_mask(self, query):
    return query.rstrip().split("\n")[1]

  
  def get_tel_config_mask(self, query):
    return int(query.rstrip().split("\n")[1])

  def get_tel_combo(self, tel_config_mask):
    
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

    return config_mask_ref[tel_config_mask]

  def reconcile_tel_masks(self, tel_cut_mask, tel_config_mask):
    tel_cut_ref_T1 = ["1","2","3","4","5","6","7","NULL","0"]
    tel_cut_ref_T2 = ["1","2","3","8","9","10","11","NULL","0"]
    tel_cut_ref_T3 = ["1","4","5","8","9","12","13","NULL","0"]
    tel_cut_ref_T4 = ["2","4","6","8","10","12","14","NULL","0"]
  
    config_ref_T1 = [1,3,5,7,9,11,13,15]
    config_ref_T2 = [2,3,6,7,10,11,14,15]
    config_ref_T3 = [4,5,6,7,12,13,14,15]
    config_ref_T4 = [8,9,10,11,12,13,14,15]
      
    tel_config = ""
    T1 = "x"
    T2 = "x"
    T3 = "x"
    T4 = "x"

    if str(tel_cut_mask) in tel_cut_ref_T1 and tel_config_mask in config_ref_T1:
      T1=1
      tel_config = str(T1)+str(T2)+str(T3)+str(T4)
      
    if str(tel_cut_mask) in tel_cut_ref_T2 and tel_config_mask in config_ref_T2:
      T2=2
      tel_config=str(T1)+str(T2)+str(T3)+str(T4)
      
    if str(tel_cut_mask) in tel_cut_ref_T3 and tel_config_mask in config_ref_T3:
      T3=3
      tel_config=str(T1)+str(T2)+str(T3)+str(T4)
      
    if str(tel_cut_mask) in tel_cut_ref_T4 and tel_config_mask in config_ref_T4:
      T4=4
      tel_config=str(T1)+str(T2)+str(T3)+str(T4)

    return tel_config

  #def get_atm(self, query):
  #
  #  month = int(query.rstrip().split("\n")[1])
  #
  #  if month <= 3 or month >= 11:
  #    return "ATM21"
  #  elif month >= 4 and month <= 10:
  #    return "ATM22"
    
  def get_atm(self, query):

    month = int(query.rstrip().split("\n")[1])

    if month <= 3 or month >= 11:
      return "ATM21"
    elif month >= 4 and month <= 10:
      return "ATM22"


  def get_array_config(self, query1,query2):

    date_diff_NA = int(query1.rstrip().split("\n")[1])
    date_diff_UA = int(query2.rstrip().split("\n")[1])
    
    #Choose upgrade, new, or old array
    if date_diff_UA >= 0:
      return "UA"
    elif date_diff_NA >= 0:
      return "NA"
    elif date_diff_NA < 0:
      return "OA"

  #def organize_into_groups(self,code): #not sure yet how to best use this
    
    
  def print_runlist(self,groups,outfile):
  #opening file for writing out the final runlist
    #outfile = open(filename,"w")
  
    GROUPID = 0
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
  
    #outfile.close()

def main():
 # Check if an arg is passed and if file exists

  parser = argparse.ArgumentParser(description='Takes an input file with paths to stage5 files and generates a runlist for stage6. Note: the runlist still needs to be manually edited to input the proper paths to EA files and fill out the Config blocks with desired cuts/configs.')

  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
 
  args = parser.parse_args()
  #testing
  #for line in args.infile.read():
  #  print line

  #Dictionary to keep track of groups
  groups = {}
  
  
  #mySQL queries
  
  lines = args.infile.read().rstrip().split('\n') #temporary - make this nicer too...
  #print lines
  #infile.close()
 
  runsobj = ListGen() 

  #Loop through file and execute for each run
  for run in lines:
    runID = run[-17:-12]
    print "Querying",runID, "..."
  
    #Do mySQL queries through command line, using subprocess module
    execCMD_TCM = "select tel_cut_mask from tblRun_Analysis_Comments where run_id='%s'" %(runID)
    #sqlOut = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VOFFLINE", "--execute=%s" %(execCMD)], stdout=subprocess.PIPE)
    #QUERY, err1 = sqlOut.communicate()
    
    execCMD_NAdiff = "select DATEDIFF(data_start_time,'%s') from tblRun_Info where run_id='%s'" %(runsobj.NA_date, runID)
    #sqlOut2a = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD2a)], stdout=subprocess.PIPE)
    #QUERY2a, err2a = sqlOut2a.communicate()
  
    execCMD_UAdiff = "select DATEDIFF(data_start_time,'%s') from tblRun_Info where run_id='%s'" %(runsobj.UA_date, runID)
    #sqlOut2b = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD2b)], stdout=subprocess.PIPE)
    #QUERY2b, err2b = sqlOut2b.communicate()
  
    
    execCMD_month = "select MONTH(data_start_time) from tblRun_Info where run_id='%s'" %(runID)
    
    #execCMD_date = "select MONTH(data_start_time),DAY(data_start_time) from tblRun_Info where run_id='%s'" %(runID)
    
    #sqlOut3 = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD3)], stdout=subprocess.PIPE)
    #QUERY3, err = sqlOut3.communicate()
    
    execCMD4 = "select config_mask from tblRun_Info where run_id='%s'" %(runID)


    q_tcutmask = runsobj.runSQL(execCMD_TCM,'VOFFLINE')
    #print q
    tcutmask = runsobj.get_tel_cut_mask(q_tcutmask)
    #print tcutmask

    q_ddiffNA = runsobj.runSQL(execCMD_NAdiff,'VERITAS')
    q_ddiffUA = runsobj.runSQL(execCMD_UAdiff,'VERITAS')
    ac = runsobj.get_array_config(q_ddiffNA,q_ddiffUA)
    #print ac
    q_month = runsobj.runSQL(execCMD_month,'VERITAS')

    atm = runsobj.get_atm(q_month)
    #print atm
    q_cmask = runsobj.runSQL(execCMD4,'VERITAS')
    #print q_cmask
    tconfigmask = runsobj.get_tel_config_mask(q_cmask)
    #sqlOut4 = subprocess.Popen(["mysql","-h","%s" %(hostName),"-P","%s" %(portNum),"-u", "readonly", "-D","VERITAS", "--execute=%s" %(execCMD4)], stdout=subprocess.PIPE)
    #QUERY4, err = sqlOut4.communicate()
  
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
    if tcutmask == "NULL":
      print "No DQM info exists, using observer reported tel-config"
      telcombo = runsobj.get_tel_combo(tconfigmask)
      
    #if TEL_CUT_MASK does exist, crosschecking with CONFIG_MASK
    else:      
      print "DQM info available, cross-checking with observer-reported tel config"
      telcombo = runsobj.reconcile_tel_masks(tcutmask, tconfigmask)
      #TEL_CUT_REF_T1 = ["1","2","3","4","5","6","7","NULL","0"]
      #TEL_CUT_REF_T2 = ["1","2","3","8","9","10","11","NULL","0"]
      #TEL_CUT_REF_T3 = ["1","4","5","8","9","12","13","NULL","0"]
      #TEL_CUT_REF_T4 = ["2","4","6","8","10","12","14","NULL","0"]
  
      #CONFIG_REF_T1 = [1,3,5,7,9,11,13,15]
      #CONFIG_REF_T2 = [2,3,6,7,10,11,14,15]
      #CONFIG_REF_T3 = [4,5,6,7,12,13,14,15]
      #CONFIG_REF_T4 = [8,9,10,11,12,13,14,15]
  
      #if str(TEL_CUT_MASK) in TEL_CUT_REF_T1 and CONFIG_MASK in CONFIG_REF_T1:
      #  T1=1
      #  TELTOANA = str(T1)+str(T2)+str(T3)+str(T4)
      
      #if str(TEL_CUT_MASK) in TEL_CUT_REF_T2 and CONFIG_MASK in CONFIG_REF_T2:
      #  T2=2
      #  TELTOANA=str(T1)+str(T2)+str(T3)+str(T4)
      
      #if str(TEL_CUT_MASK) in TEL_CUT_REF_T3 and CONFIG_MASK in CONFIG_REF_T3:
      #  T3=3
      #  TELTOANA=str(T1)+str(T2)+str(T3)+str(T4)
      
      #if str(TEL_CUT_MASK) in TEL_CUT_REF_T4 and CONFIG_MASK in CONFIG_REF_T4:
      #  T4=4
      #  TELTOANA=str(T1)+str(T2)+str(T3)+str(T4)
      
    fullConfig = ac + "_"+ atm +"_"+ "T" + telcombo 
    #print fullConfig
    #check to see if the group already exists and add run to group
    if fullConfig in groups:
      groups[fullConfig].append(run)
    else:
      groups[fullConfig] = [run]

  runsobj.print_runlist(groups,args.outfile)
  
if __name__ == '__main__':
  main()
