#!/bin/bash

day=`date +%d%m%y`
SSH_USERNAME=guavus
PASSWORD="guavus@123"  # Put Root Password Here

#There must be entry of all fqdn in knowhost file.

which sshpass
if [ $? -eq 0 ]
then
     echo "sshpass is configured!!"
else
     echo "sshpass is not configured, Kindly install SSHPASS FIRST !!"
     exit
fi

rm -rf /Users/mohitsharma/Desktop/operaton-dashboard/scripts/reports/Ch*

for i in `cat /Users/mohitsharma/Desktop/operaton-dashboard/scripts/hosts`
do
echo $i
/usr/local/bin/sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no /Users/mohitsharma/Desktop/operaton-dashboard/scripts/checklist.sh "$SSH_USERNAME"@"$i":/tmp/.
/usr/local/bin/sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USERNAME"@"$i" "chmod +x /tmp/checklist.sh"
/usr/local/bin/sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USERNAME"@"$i" "sh /tmp/checklist.sh"
/usr/local/bin/sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$SSH_USERNAME"@"$i":/tmp/Checklist_"$i"_"$day".txt /Users/mohitsharma/Desktop/operaton-dashboard/scripts/reports/.
done

>/Users/mohitsharma/Desktop/operaton-dashboard/scripts/Checklist_All_Host.txt

for j in `cat /Users/mohitsharma/Desktop/operaton-dashboard/scripts/hosts`
do
cat /Users/mohitsharma/Desktop/operaton-dashboard/scripts/reports/Checklist_"$j"_"$day".txt >> /Users/mohitsharma/Desktop/operaton-dashboard/scripts/Checklist_All_Host.txt
done
