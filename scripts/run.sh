#!/bin/bash

day=`date +%d%m%y`
SSH_USERNAME=guavus
PASSWORD="guavus@123"  # Put Root Password Here
REPORTS="./scripts/reports"
RUN_VALUE=$1
echo $RUN_VALUE
#There must be entry of all fqdn in knowhost file.

which sshpass
if [ $? -eq 0 ]
then
     echo "sshpass is configured!!"
else
     echo "sshpass is not configured, Kindly install SSHPASS FIRST !!"
     exit
fi

rm -rf ./scripts/reports/Ch*

for i in `cat ./scripts/hosts`
do
echo $i
/usr/local/bin/sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no ./scripts/checklist_new.sh "$SSH_USERNAME"@"$i":/tmp/.
/usr/local/bin/sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USERNAME"@"$i" "echo "guavus@123" | sudo -S chmod +x /tmp/checklist_new.sh"
/usr/local/bin/sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USERNAME"@"$i" "echo 'guavus@123' | sudo -S su -c '/tmp/checklist_new.sh '\\\"$RUN_VALUE\\\"'';"
#sshpass -p "password" ssh username@74.11.11.11 'su -lc "cp -r '\\\"$location2\\\"' '\\\"$location1\\\"'";'
/usr/local/bin/sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$SSH_USERNAME"@"$i":/tmp/Checklist_"$i"_"$day".txt ./scripts/reports/.
done

#rm ./scripts/Checklist_All_Host.txt

for j in `cat ./scripts/hosts`
do
ping -q -c3 $j > /dev/null
if [ $? -eq 0 ]
then
  gsed -i '3s/^/PING_STATUS : PING SUCEESS[P]\n/' ./scripts/reports/Checklist_"$j"_"$day".txt
else
  gsed -i '3s/^/PING_STATUS : PING FAILED[P]\n/' ./scripts/reports/Checklist_"$j"_"$day".txt
fi

sshpass -p guavus@123 ssh -o StrictHostKeyChecking=no guavus@$j "echo 2>&1"
if [ $? -eq 0 ]
then
  gsed -i '4s/^/SSH_STATUS : SSH SUCEESS[P]\n/' ./scripts/reports/Checklist_"$j"_"$day".txt
else
  gsed -i '4s/^/SSH_STATUS : SSH FAILED[P]\n/' ./scripts/reports/Checklist_"$j"_"$day".txt
fi
done

rm ./scripts/reports/tabular_report.csv


for h in `ls -l "$REPORTS" | awk '{ print $NF }'`
do
case "$RUN_VALUE" in 
  "1") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%16?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;

  "2") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%19?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;

  "3") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%13?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;

  "4") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%31?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;

  "5") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%25?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;

  "6") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%28?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;

  "7") 
    cut -d: -f2 "$REPORTS"/"$h" | awk 'ORS=NR%40?",":"\n"'  >> "$REPORTS"/tabular_report.csv
    ;;
esac 
done
