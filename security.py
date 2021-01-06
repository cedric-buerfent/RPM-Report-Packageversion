#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from glob import glob
import __builtin__
import string
import re
import time      #zeitbibliothek
from time import strftime

from glob import glob   #dir

import traceback #for debug
import sys

import shutil  #file copy

import codecs #utf-8
import io


# --------------------------- NEW csv rpm versionscript 02 12 2020 CB -------------------- 
# -------------- EXAMPLES 

# for installed packages:
# rpm -qa --queryformat "%{NAME}.%{ARCH}|%{VERSION}-%{RELEASE}\n"|sort > /tmp/rpmquery_dev.txt
#gpgme.x86_64|1.3.2-5.el7
#gpg-pubkey.(none)|00f97f56-467e318a
#gpg-pubkey.(none)|352c64e5-52ae6884
#gpg-pubkey.(none)|61e8806c-5581df56
#gpg-pubkey.(none)|621e9f35-58adea78
#gpg-pubkey.(none)|f4a80eb5-53a7ff4b
#libgpg-error-devel.x86_64|1.12-3.el7
#libgpg-error.i686|1.12-3.el7
#libgpg-error.x86_64|1.12-3.el7
#pygpgme.x86_64|0.3-9.el7
#-> none ist gut!


# for what new updates:
#yum check-update|tr "\n" "#" | sed -e 's/# / /g' | tr "#" "\n"|awk '{print $1"|"$2}'|grep -v "^*"|grep -v "^Loaded"| \
#         grep -v "^Loading"|grep -v "^Obsoleting"|grep -v "^Last"|grep -v "^|"|sort|uniq  > /tmp/checkupdate_yumdev.txt
#java-1.8.0-openjdk.x86_64|1:1.8.0.272.b10-1.el7_9
#java-1.8.0-openjdk-devel.x86_64|1:1.8.0.272.b10-1.el7_9
#java-1.8.0-openjdk-headless.x86_64|1:1.8.0.272.b10-1.el7_9
#tzdata-java.noarch|2020d-2.el7




# lazy - put anything we want global as variable
class cVariables:
	debug = False #see below
	develop = False #see below
	filename_rpm_txt = ""  #text list rpm qa like
	filename_yum_txt = ""  #text list yum check-update like
	rpm_raw = []
	yum_raw = []
	rpm_ordered = []  #syntax [0] => {package,version}   ordered because same order as input txt file
	yum_ordered = []  #syntax [0] => {package,version}
	yum_oldver_newver  = []   #syntax [0] => package, oldver, newver           #aka Update  here unordered because first match new then install then installed
	                          #       [1] => package,   -   , newver           #aka Install
							  #       [2] => package, oldver,   -              #aka Remove
	filename_out_report_txt = ""  #output filename for update report
	 
	
	 
	

v = cVariables()

# --- Takes temorary test files
v.develop = True
		
# --- debugmodus verbose on/off
v.debug = True

	
	
# ----------- takes a filename and a array ------
def read_file(aFile,aArray):
	try:
		f = open(aFile,'r')
		lines = f.readlines()
		f.close()
		for l in lines:
			if l == None or l == "" or l == "\n":
				#nop
				pass
			else:
				aArray.append(l.rstrip())
	except:
		print "No file %s"%aFile
		#traceback.print_exc(file=sys.stdout)
		
# ----------- takes a filename and a array ------	
def write_file(aFile,aArray):
	try:
		f = open(aFile,'w')
		for line in aArray:
			line.rstrip()
			f.write(line+"\n")
		f.close()
	except:
		print "nono. Cannot write to file %s"%aFile
		

def check_params(): 
	if len(sys.argv) < 3:
		print "please provide params."
		print "    syntax :  security.py <ip> <eventstring>"
		print "    e.g.   :  security.py 172.24.10.24 laser"
		sys.exit(0)		

# ------- loading rpm txt file into memory array ------------------------------
def create_array_rpm(rpm_raw,rpm_ordered):
	print "[STEP] create_array_rpm"

	for i,r in enumerate(rpm_raw):
		#print str(i)+"->"+r #0->abattis-cantarell-fonts.noarch|0.0.25-1.el7
		r2 = r.strip().split("|")[0]
		#print r2
		ver = ""
		valid = True
		try:
			ver = r.strip().split("|")[1]
		except:
			print "ERRHANDLER CATCH: Cannot get version!"
			print "Bad String is:->"+r.strip()+"<-"
			print "    should be: package|version"
			#traceback.print_exc(file=sys.stdout)
			valid = False
		#print ver			
		#break
		# -- we store rpm tupel if it has a version string else thats strange
		if valid:
			rpm_ver = {}
			rpm_ver[r2] = ver
			rpm_ordered.append(rpm_ver)

#slightlely different that rpm for example:
# yum: autocorr-en.noarch|1:5.3.6.1-24.el7   container-selinux.noarch|2:2.119.2-1.911c772.el7_8
# rpm: autocorr-en.noarch|5.3.6.1-19.el7     container-selinux.noarch|2.107-3.el7
def create_array_yum(yum_raw,yum_ordered):
	print "[STEP] create_array_yum"
	
	for i,r in enumerate(yum_raw):
		r2 = r.strip().split("|")[0]
		ver = ""
		valid = True
		try:
			ver = r.strip().split("|")[1]
			# handle case 1:5.3.6.1-24.el7 --> 5.3.6.1-24.el7 
			if ":" in ver:
				ver = ver.split(":")[1]
		except:
			print "ERRHANDLER CATCH: Cannot get version!"
			print "Bad String is:->"+r.strip()+"<-"
			print "    should be: package|version"
			#traceback.print_exc(file=sys.stdout)
			valid = False
		# -- we store rpm tupel if it has a version string else thats strange
		if valid:
			yum_ver = {}
			yum_ver[r2] = ver
			yum_ordered.append(yum_ver)	

# ------- two arrays, rpm and yum will be merged into report  ------------------------------
def compare_yumupdates_installedyum(newrpm,oldrpm,res):
	print "[STEP] Merge"
	#res.append("test")
	# -- iterate over yum so all new packages found
	for n in newrpm:
		newpackage = n.keys()[0]
		newversion = n.values()[0]
		#print apackage
		#print aversion
		#break
		#look for the package name if inside oldrpm
		match=False
		oldversion="-"
		for o in oldrpm:
			oldpackage = o.keys()[0]
			oldversion_tmp = o.values()[0]
			if newpackage == oldpackage:				
				match=True
				oldversion=oldversion_tmp
				break
		if match == False:
			#print "new install of package "+newpackage
			pass
		# --- write all package names with status: Update (ver) or Install (-)
		package_verpre_vernew=[]
		package_verpre_vernew.append(newpackage)
		package_verpre_vernew.append(oldversion)
		package_verpre_vernew.append(newversion)
		res.append(package_verpre_vernew)
		
	# -- jetzt die alten rpm Pakete matchen: Rest = ohne Update
	# -- iterate over actually installed rpm package and check for an update
	for o in oldrpm:
		oldpackage = o.keys()[0]
		oldversion = o.values()[0]
		match=False
		newversion="-"
		for n in newrpm:
			newpackage = n.keys()[0]
			newversion_tmp = n.values()[0]
			if oldpackage == newpackage:
				match=True
				newversion=newversion_tmp
				break
		# -- only when we have no update we mark it into our list.
		if match == False:
			#print "no update for package "+oldpackage
			# -- here we can add it to the result list but only those without an update
			package_verpre_vernew=[]
			package_verpre_vernew.append(oldpackage)
			package_verpre_vernew.append(oldversion)
			package_verpre_vernew.append(newversion)  #only strich normalerweise
			res.append(package_verpre_vernew)
			
	# -- arrived here we have an unordered list. Use |sort for a sorted list.
	# -- this is wanted. Better for debug in case of errors.
				
				
# -- write report to a text file but removing some stuff like obvious architecture			
def output_result_file(outarray,outFilename):
	print "[Step] Write output file "+outFilename
	output_string_array = []
	#we create a output string array in form  package,oldver,newver
	#                                         package,-,newver
	#                                         package,oldver,-
	for o in outarray:
		s = ""
		packagename = o[0]
		#we remove .x64_64 from packagename
		if packagename.endswith(".x86_64"):
			packagename =packagename[:-7]
		oldver = o[1]
		newver = o[2]
		s = packagename+","+oldver+","+newver
		output_string_array.append(s)
		
		 		
	for s in output_string_array:
		#print s
		pass		
	#print output_string_array
	
	write_file(outFilename,output_string_array)		
		
def check_params(Variables):
	if len(sys.argv) < 4:
		print "please provide params."	
		print "    syntax :  security.py <rpm.txt> <yum.txt> <outreport.txt>"
		print "    e.g.   :  security.py rpmquery_dev.txt checkupdate_yumdev.txt outreport.txt"  
		sys.exit(0)

	v.filename_rpm_txt = sys.argv[1]
	v.filename_yum_txt = sys.argv[2]	
	v.filename_out_report_txt = sys.argv[3]
	print "Parameters are:"
	print "RPM    :"+v.filename_rpm_txt 
	print "YUM    :"+v.filename_yum_txt
	print "Report :"+v.filename_out_report_txt

		
		
# --------------- MAIN ----------------------------------------

#v.filename_rpm_txt = "rpmquery_dev.txt"
#v.filename_yum_txt = "checkupdate_yumdev.txt"	
#v.filename_out_report_txt = "outreport.txt"
check_params(v)

#sys.exit(0)
# -- read files in memory
read_file(v.filename_rpm_txt,v.rpm_raw)
read_file(v.filename_yum_txt,v.yum_raw)
if v.debug:
	pass
	#print v.rpm_raw
	#print v.yum_raw

#sys.exit(0)	
# -- create rpm array (not associative) with cleaned values
create_array_rpm(v.rpm_raw,v.rpm_ordered)
if v.debug:
	pass
	#print "\n".join(v.rpm_ordered[0])
	#print v.rpm_ordered[1]
	for l in v.rpm_ordered:
		pass
		#print l
		
create_array_yum(v.yum_raw,v.yum_ordered)
if v.debug:
	for l in v.yum_ordered:
		pass
		#print l
		
#print v.yum_ordered
		
# -- merging the two lists: we take the yum updates and check for match in installed rpm packages
# package,oldver,newver  = Update
# package,  -   ,newver  = New
# package,oldver, -      = Removed
compare_yumupdates_installedyum(v.yum_ordered,v.rpm_ordered,v.yum_oldver_newver)
		 
if v.debug:
	pass
	for r in v.yum_oldver_newver:
		#print r
		pass
	#print v.yum_oldver_newver

#write file
output_result_file(v.yum_oldver_newver,v.filename_out_report_txt)
