# RPM-Report-Packageversion

Small documentation. Start 6/1/2020 CB

Returns a csv list we can import into Excel to create a RPM report.
The list has 3 columns:
- Packagename,  Current-Version,   New-Available-Version
- With dashs if info not available:
-                                           [-]  (means no new version. Keep current)            
-                   [-] (means new install. Nothing to replace)                                     



#/usr/bin/python2 security.py rpminstalled.srv-tixdmz-02.strg.arte.txt checkupdate.srv-tixdmz-02.strg.arte.txt  out.txt
/usr/bin/python2 security.py $1 $2 $3

With:
"Give me a list of all actually installed (old) packages":
rpminstalled.srv-tixdmz-02.strg.arte.txt
#rpm -qa --queryformat "%{NAME}.%{ARCH}|%{VERSION}-%{RELEASE}\n"|sort > /tmp/rpmquery_dev.txt
- abattis-cantarell-fonts.noarch|0.0.25-1.el7
- abrt-addon-ccpp.x86_64|2.1.11-50.el7.centos


And:
checkupdate.srv-tixdmz-02.strg.arte.txt
\#yum check-update|tr "\n" "#" | sed -e 's/# / /g' | tr "#" "\n"|awk '{print $1"|"$2}'|grep -v "^*"|grep -v "^Loaded"| \
\#         grep -v "^Loading"|grep -v "^Obsoleting"|grep -v "^Last"|grep -v "^|"|sort|uniq  > /tmp/checkupdate_yumdev.txt

- abrt-addon-ccpp.x86_64|2.1.11-60.el7.centos
- abrt-addon-kerneloops.x86_64|2.1.11-60.el7.centos
- abrt-addon-pstoreoops.x86_64|2.1.11-60.el7.centos

Result:
out.txt
- abrt-addon-ccpp,2.1.11-50.el7.centos,2.1.11-60.el7.centos
- abrt-addon-kerneloops,2.1.11-50.el7.centos,2.1.11-60.el7.centos
- abrt-addon-pstoreoops,2.1.11-50.el7.centos,2.1.11-60.el7.centos
- ..libwayland-egl,-,1.15.0-1.el7
- ...
- xterm,295-3.el7,-
- xvattr,1.3-27.el7,-



unsorted! That is wanted to better trace errors inside script.
To sort:

```bash
vi merge.sh
cd /home/buerfent/ansible3/PROJ4_RPM_QA
#python lpb.py rpminstalled.127.0.0.1.txt checkupdate.127.0.0.1.txt out_checkupdate.127.0.0.1.txt
#python lpb.py $1 $2 $3
#cat $3|sort|grep -v "^$" > resultat_sorted_$3
#cat resultat_1.csv|sort|grep -v "^$"  > $1_sorted.txt
#/usr/bin/python2 security.py rpminstalled.srv-tixdmz-02.strg.arte.txt checkupdate.srv-tixdmz-02.strg.arte.txt  out.txt
/usr/bin/python2 security.py $1 $2 $3
cat $3|sort > resultat_sorted_$3
```
