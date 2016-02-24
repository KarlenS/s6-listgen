s6-listgen
==========

TODO:
---
improve EA name handling and config info parsing
---

formats VEGAS stage6 runlist to be compatable with v2.5.1+

author: Karlen Shahinyan
email: shahin@astro.umn.edu
last updated: 02/24/16

This is a script to convert list of stage 5 files to the format required by stage6 in vegas 2.5
The first argument is the stage 5 run list file.
The second argument is the reformatted output file.

For info & listing of all arguments/options use:
python s6RunlistGen.py --help 

The script only identifies the number of tels, na/oa, and summer/winter.

There is now an automated EA path/filename generation option --EAmatch (based on standard convention).
When enabled, the script will take user specifiable command-line values (default if not specified)
for all other parameters required for generating EA filenames.

Contents of CONFIG blocks of each group are left blank. The user should add the desired
cuts or configs (e.g., S6A_RingSize 0.17)

Format assumed for stage 5 files is /path/to/file/<RUN ID>.stage5.root

Winter/Summer atmosphere dates are taken from Henrike's spreadsheet
------------------------------------------------------------------------------
 -------------------------------help printout--------------------------------
------------------------------------------------------------------------------
Takes an input file with paths to stage5 files and generates a runlist for
stage6. Note: the runlist still needs to be manually edited to fill out the
Config blocks with desired cuts/configs and plug in EA paths. Use options
--EAmatch and --EAdir /path/to/EAfiles/ if you want to automatically generate
and plug in EA paths/names based on standard naming convention.

positional arguments:
  infile                Input file name with list of stage5 root files,
                        containing paths to the files.
  outfile               Output file for writing formatted runlist. If skipped,
                        will print to screen.

optional arguments:
  -h, --help            show this help message and exit
  --EAmatch             Set option to enable automatic EA filename generation.
  --EAdir [EADIR]       Path to directory containing EA files
  --cuts [{soft,med,hard,loose}]
                        Cuts used for the analysis.
  --SimModel [SIMMODEL]
                        'Oct2012' (GrISU) or 'MDL10UA' or 'MDL15NA' etc
                        (KASCADE)
  --SimSource [SIMSOURCE]
                        Simulation type ('GrISU' or 'KASCADE' or 'CARE') used
                        to generate EAs
  --Offset [{Alloff,050off}]
                        Specifies Offsets covered by EA ('Alloff' or '050off')
  --TelMulti [TELMULTI]
                        Telescope Multiplicity (t2, t3, or t4)
  --LZA [{LZA,}]        'LZA' or '' if not LZA
