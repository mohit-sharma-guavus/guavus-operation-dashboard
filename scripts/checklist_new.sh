#!/bin/bash

# Date 
# Copyright @GUAVUS CS TEAM
# Shell script to checks on server


#### User provided ####

CASE_VALUE=$1

#### GLOBAL VARIABLES ###
day=`date +%d%m%y`
HNAME=`hostname -f`
date_time=`date "+%Y-%m-%d_%H-%M"`

####### Customer Provided check value to compare
OS_VERSION="7.6.1810"
SELINUX_STATUS=None
DHCP_STATUS_CUST=None
FIREWALL_STATUS=None
SWAP_STATUS=None
DHCP_STATUS=None
VIP_IP=None
NetworkManager_STATUS=None
NTPD_STATUS=None
IP_FORWARD_STATUS=None
KAFKA_FS=None



#########################################

> /tmp/Checklist_"$HNAME"_"$day".txt
echo "HOST_FQDN: $HNAME " >> /tmp/Checklist_"$HNAME"_"$day".txt
echo "DATE_TIME: $date_time" >> /tmp/Checklist_"$HNAME"_"$day".txt

######## Fuctaions Section ########

function hardware_check() {

  # ---- hadware_check function local variable ---
  KERNEL_VERSION="$(uname -r)"
  SYSTEM_MANUFACTURER=`dmidecode -s system-manufacturer`
  SYATEM_PRODUCT_NAME=`dmidecode -s system-product-name`
  SYSTEM_VERSION=`dmidecode -s system-version|sed 's/,//'`
  SYSTEM_UUID=`dmidecode -s system-uuid`
  PROCESSOR_FREQUENCY=`dmidecode -s processor-frequency | head -1`
  BIOS_VERSION=`dmidecode -s bios-version`
  HARDWARE_PLATFORM=`uname -i`
  NUMBER_OF_DISK=`lsblk | grep disk | wc -l`
  SUM_OF_DISK_SPACE=`lsblk | grep disk | awk 'BEGIN {FS = " "} ; {sum+=$4} END {print sum}'`
  CPU=`nproc --all`
  MEM=`free -g | grep -i Mem | awk '{ print $2 }'`

  # ---hadware_check function Output Section ---
  
  
  echo "SYSTEM_MANUFACTURER : ${SYSTEM_MANUFACTURER} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "SYATEM_PRODUCT_NAME : ${SYATEM_PRODUCT_NAME} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "SYSTEM_UUID : ${SYSTEM_UUID} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "SYSTEM_VERSION : ${SYSTEM_VERSION} " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "KERNEL_VERSION : ${KERNEL_VERSION} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "HARDWARE_PLATFORM : ${HARDWARE_PLATFORM} " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "BIOS_VERSION : ${BIOS_VERSION} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "TOTAL_CPU : ${CPU} " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "PROCESSOR_FREQUENCY : ${PROCESSOR_FREQUENCY} "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "TOTAL_MEMORY : ${MEM} " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "NUMBER_OF_DISK : ${NUMBER_OF_DISK} " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "SUM_OF_DISK_SPACE : ${SUM_OF_DISK_SPACE} " >> /tmp/Checklist_"$HNAME"_"$day".txt
}

function os_check() {

  # ---- OS_check function local variable ---
  OS_VERSION_CENTOS=`cat /etc/redhat-release | awk '{print $4}'`
  UPTIME=`uptime -p`
  HOSTNAME=`hostname`
  TIMEZONE=`date | awk '{print $5}'`
  NTP_SYNC_STATUS=`timedatectl  | grep "NTP synchronized" | cut -d: -f2`
  CIDR=`ip a | grep brd | grep inet| awk '{ print $2 }'`
  SE_STATUS=`getenforce`
  SWAP=`free -g | grep -i Swap | awk '{print $2}'`
  INTERFACE=`ip -4 route get 8.8.8.8 | awk {'print $5'} | tr -d '\n'`
  NET_FILE=`echo "/etc/sysconfig/network-scripts/ifcfg-"$INTERFACE`
  DHCP_STAT=`cat $NET_FILE | grep BOOTPROTO | cut -d= -f2`
  NM_STAT=`systemctl status NetworkManager | grep Active | awk '{print $2}'`
  INTERFACE_SPEED=`ethtool $INTERFACE | grep -i Speed | awk '{ print $2}'`
  MTU=`ifconfig | grep -i $INTERFACE | awk '{print $4}'`
#  OPT_SIZE="$(df -h | grep /opt/repos | awk '{ print $2 }' | sed 's/[^0-9]*//g')"
  VAR_SIZE="$(df -h | grep /var/log | awk '{ print $2 }' | sed 's/[^0-9]*//g')"
  ROOT_SIZE="$(df -h | grep / | awk '{ print $2 }' | sed 's/[^0-9]*//g' | head -1)"
  IP_FORWARD_VALUE=`cat /proc/sys/net/ipv4/ip_forward`
  DMESG_STATUS=`dmesg | grep -i "error\|failed" | wc -l`
  NODE_TYPE=`hostname| cut -d- -f2` ##temp
  date_time=`date "+%Y-%m-%d_%H:%M"`
  PYTHON_VERSION=`python --version`
  TRANSPARENT_HUGE_PAGES_STATUS=`cat /sys/kernel/mm/transparent_hugepage/enabled`

  # ---OS_check function Output Section ---

  
  echo "OS_VERSION : ${OS_VERSION_CENTOS}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "HOSTNAME : ${HOSTNAME}[P] "  >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "HOST_TIMEZONE : ${TIMEZONE}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "NTP_SYNC_STATUS : ${NTP_SYNC_STATUS}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "CIDR : ${CIDR}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt

  if [[ $SELINUX_STATUS == None ]]; then
    echo "SELINUX_STATUS : ${SE_STATUS}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $SELINUX_STATUS != $SE_STATUS ]]; then
    echo "SELINUX_STATUS : ${SE_STATUS}[F] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $SELINUX_STATUS == $SE_STATUS ]]; then
    echo "SELINUX_STATUS : ${SE_STATUS}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi

  if [[ $DHCP_STATUS_CUST == None ]]; then
    echo "DHCP_STATUS : ${DHCP_STAT}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $DHCP_STATUS_CUST != $DHCP_STAT ]]; then
    echo "DHCP_STATUS : ${DHCP_STAT}[F] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $DHCP_STATUS_CUST == $DHCP_STAT ]]; then
    echo "DHCP_STATUS : ${DHCP_STAT}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
  
  systemctl status NetworkManager
  if [[ $? -eq 4 ]]; then
    echo "NETWORK_MANAGER_STATUS : Not_Running[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $NetworkManager_STATUS == None ]]; then
    echo "NETWORK_MANAGER_STATUS : ${NM_STAT}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $NetworkManager_STATUS != $NM_STAT ]]; then
    echo "NETWORK_MANAGER_STATUS : ${NM_STAT}[F] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $NetworkManager_STATUS == $NM_STAT ]]; then
    echo "NETWORK_MANAGER_STATUS : ${NM_STAT}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
  
  echo "INTERFACE_SPEED : ${INTERFACE_SPEED}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "MTU_SPEED : ${MTU}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "LOG_FS_SIZE : ${VAR_SIZE}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  echo "ROOT_FS_SIZE : ${ROOT_SIZE}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt

  if [[ $IP_FORWARD_STATUS == $IP_FORWARD_VALUE ]]; then
    echo "IP_FORWARD_STATUS : ${IP_FORWARD_VALUE}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $IP_FORWARD_STATUS != $NM_STAT ]]; then
    echo "IP_FORWARD_STATUS : ${IP_FORWARD_VALUE}[F] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  elif [[ $IP_FORWARD_STATUS == None ]]; then
    echo "IP_FORWARD_STATUS : ${IP_FORWARD_VALUE}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
  
  if [[ $DMESG_STATUS -eq 0 ]]; then
    echo "ROOT_FS_SPEED : No Failure in DMESG[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "DMESG_STATUS : DMESG_FAIL_COUNT=${DMESG_STATUS}[F] " >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi 

  echo "TRANSPARENT_HUGE_PAGES_STATUS : ${TRANSPARENT_HUGE_PAGES_STATUS}[P] " >> /tmp/Checklist_"$HNAME"_"$day".txt 
}

function platform_check() {

  
  # hdp status
  which hdp-select > /dev/null 2>&1
  if [ $? -eq 0 ]
  then
    HDP_VERSION=`hdp-select versions`
    echo "HDP_STATUS : Installed-${HDP_VERSION}[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "HDP_STATUS : Not Installed [F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
   
  # Hadoop Install Status
  which hadoop > /dev/null 2>&1
  if [ $? -eq 0 ]
  then
    HADOOP_VERSION=`hadoop version | grep "Hadoop" | cut -d" " -f2`
    echo "HADOOP_VERSION_STATUS : Installed-${HDP_VERSION}[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "HADOOP_VERSION_STATUS : Not Installed [F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi

  # Hadoop status
  HADOOP_STATUS=`timeout 4s hadoop dfsadmin -report | grep "Decommission Status" | head -1 | cut -d: -f2`
  if [ $HADOOP_STATUS == " Normal" ]
  then
    echo "HADOOP_VERSION_STATUS : ${HADOOP_STATUS}[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "HADOOP_VERSION_STATUS : ${HADOOP_STATUS}[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi

  # ---- Check Kinit  ---
 
  which kinit > /dev/null 2>&1
  if [ $? -eq 0  ]
  then
    echo "KERBEROS_STATUS : Installed[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "KERBEROS_STATUS : Not-Installed[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
  
  # Ambari server status
  AMBARI_SERVER_STATUS=`for service in /etc/init.d/ambari-server; do $service status; done | grep "Server" |head -1 | cut -d" " -f3`
  if [ $AMBARI_SERVER_STATUS == "running"  ]
  then
    echo "AMBARI_SERVER_STATUS : ${AMBARI_SERVER_STATUS}[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "AMBARI_SERVER_STATUS : ${AMBARI_SERVER_STATUS}[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi

  # Ambari client status
  AMBARI_CLIENT_STATUS=`/etc/init.d/ambari-agent status | head -2 | grep -v Found | cut -d" " -f2`
  if [ $AMBARI_CLIENT_STATUS == "running."  ]
  then
    echo "AMBARI_CLIENT_STATUS : ${AMBARI_CLIENT_STATUS}[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "AMBARI_CLIENT_STATUS : ${AMBARI_CLIENT_STATUS}[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
  
  # Zookeeper status
  hdp_version=`hdp-select versions`
  /usr/hdp/${hdp_version}/zookeeper/bin/zkServer.sh status
  if [ $? -eq 0  ]
  then
    echo "ZOOKEEPER_STATUS : Running[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "ZOOKEEPER_STATUS : Not-Running[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi

  # Kafka Status
  KAFKA_STATUS=`/usr/hdp/${hdp_version}/kafka/bin/kafka status | cut -d' ' -f3`
  if [ $KAFKA_STATUS == "running" ]
  then
    echo "KAFKA_STATUS : Running[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "KAFKA_STATUS : Not-Running[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
  
  # Kubernetes Status
  which kubectl
  if [ $? -eq 0 ]
  then
    echo "KUBERNETES_STATUS : Running[P]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  else
    echo "KUBERNETES_STATUS : Not-Running[F]" >> /tmp/Checklist_"$HNAME"_"$day".txt
  fi
}


###### Final Run CASE Statement #########

case "$CASE_VALUE" in 
  "1") 
    hardware_check
    ;;

  "2") 
    os_check
    ;;

  "3") 
    platform_check
    ;;

  "4") 
    hardware_check
    os_check
    ;;

  "5") 
    hardware_check
    platform_check
    ;;

  "6") 
    os_check
    platform_check
    ;;

  "7") 
    hardware_check
    os_check
    platform_check
    ;;
esac 




