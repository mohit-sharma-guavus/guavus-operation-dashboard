#!/usr/bin/env python
"""
Created on @ 2020
@author: 
"""
#imports
from flask import Flask, render_template, json, request, session, redirect, url_for, send_file, send_from_directory, safe_join, abort, flash
import os
import sys
import time
from flaskext.mysql import MySQL
from csv import reader


#initialize the flask and SQL Objects
app = Flask(__name__)
mysql = MySQL()

#configure MYSQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Guavus@123'
app.config['MYSQL_DATABASE_DB'] = 'op_dashboard_new'
app.config['MYSQL_DATABASE_HOST'] = '192.168.133.196'
#app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

#Config Parameters
app.config["CLIENT_CSV"] = "/Users/mohitsharma/Desktop/operaton-dashboard/scripts/"

#define methods for routes (what to do and display)
#error = None

"""
@app.route('/')
def home():
    try:
        print("Showing Clusters!!")
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT cluster_name, cluster_desc, cluster_creation_date FROM cluster_info")
        data = cursor.fetchall()
        return render_template("homepage.html", value=data)
    except Exception as e:
        return render_template("homepage.html")
"""
@app.route('/')
def clusters():
    try:
        print("Showing Clusters!!")
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT cluster_name,cluster_desc,cluster_creation_date FROM cluster_info")
        data = cursor.fetchall()
        return render_template("clusters.html", value=data)
    except Exception as e:
        return render_template("clusters_fresh.html", error = str(e))

@app.route('/<cluster_name>/home')
def home(cluster_name):
    print("Showing Homepage")
    return render_template("homepage.html", name=cluster_name)

@app.route('/inprogress')
def inprogress():
    return render_template("inprogress.html")


@app.route('/<clusterName>/delete_cluster')
def delete_cluster(clusterName):
    error = None
    print("Deleting Cluster Clusters!!")
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cluster_info WHERE cluster_name = %s ", (clusterName))
    cursor.execute("DROP TABLE `%s`", (clusterName))
    conn.commit()
    conn.close()
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT cluster_name,cluster_desc,cluster_creation_date FROM cluster_info")
    data = cursor.fetchall()
    error = 'Cluster Successfully Deleted!!'
 #   return redirect(url_for('clusters', error = error))
    return render_template("clusters.html", error = error, value=data)


@app.route('/search', methods=['POST'])
def search():
    error = None
    if request.method == "POST":
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT count(cluster_name) FROM cluster_info WHERE cluster_name = %s", request.form['search'])
        if cursor.fetchone()[0] == 1 :
            print("Clueter found!!")
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT cluster_name,cluster_desc,cluster_creation_date FROM cluster_info where cluster_name = %s", request.form['search'])
            data = cursor.fetchall()
            return render_template("clusters.html", value=data)
        else:
            error = 'No such cluster Found!!'
            return render_template("clusters.html", error = error)
        
@app.route('/add_cluster', methods = ['GET', 'POST'])
def add_cluster():
    if request.method == 'POST':
        check_cluster_name = request.form['email']
        conn3 = mysql.connect()
        cursor3 = conn3.cursor()
        cursor3.execute("SELECT cluster_name FROM cluster_info WHERE cluster_name = %s", (check_cluster_name))
        data3 = cursor3.fetchone()
        if data3:
            error = 'Oops! Cluster with this name already exists! Try again with new name.'
            return render_template("clusters.html", error=error)
        else:
            new_cluster_name=request.form['email']
            cluster_description=request.form['description']
            cluster_date=time.strftime('%Y-%m-%d %H:%M:%S')
            conn = mysql.get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO cluster_info(cluster_name, cluster_desc, cluster_creation_date) VALUES (%s,%s,%s)", (new_cluster_name,cluster_description,cluster_date))
            conn.commit()
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT cluster_name FROM cluster_info WHERE cluster_name = %s LIMIT 1", (new_cluster_name))
            data1 = cursor.fetchone()
            data2 = data1[0]
            if data2 == request.form['email']:
                new_cluster_name=request.form['email']
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT cluster_id FROM cluster_info where cluster_name = %s LIMIT 1", (new_cluster_name))
                clust_id_temp = cursor.fetchone()
                clust_id = clust_id_temp[0]
                conn1 = mysql.get_db()
                cur = conn1.cursor()
                cur.execute("CREATE TABLE `%s`(cluster_id INT NOT NULL, cluster_name VARCHAR(20) NOT NULL, host_id INT NOT NULL AUTO_INCREMENT, hostgroup VARCHAR(20) NOT NULL, host_IP VARCHAR(20) NOT NULL,host_fqdn VARCHAR(200) NOT NULL,host_live VARCHAR(20), PRIMARY KEY (host_id))",(new_cluster_name))
                if request.form['hg1']:
                    host_group1=request.form['hg1']
                    ip_address1=request.form['ip1']
                    fqdn1=request.form['fq1']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group1, ip_address1, fqdn1))
                if request.form['hg2']:
                    host_group2=request.form['hg2']
                    ip_address2=request.form['ip2']
                    fqdn2=request.form['fq2']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group2, ip_address2, fqdn2))
                if request.form['hg3']:
                    host_group3=request.form['hg3']
                    ip_address3=request.form['ip3']
                    fqdn3=request.form['fq3']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group3, ip_address3, fqdn3))
                if request.form['hg4']:
                    host_group4=request.form['hg4']
                    ip_address4=request.form['ip4']
                    fqdn4=request.form['fq4']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group4, ip_address4, fqdn4))
                if request.form['hg5']:
                    host_group5=request.form['hg5']
                    ip_address5=request.form['ip5']
                    fqdn5=request.form['fq5']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group5, ip_address5, fqdn5))
                if request.form['hg6']:
                    host_group6=request.form['hg6']
                    ip_address6=request.form['ip6']
                    fqdn6=request.form['fq6']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group6, ip_address6, fqdn6))
                if request.form['hg7']:
                    host_group7=request.form['hg7']
                    ip_address7=request.form['ip7']
                    fqdn7=request.form['fq7']
                    cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group7, ip_address7, fqdn7))
                conn1.commit()
                conn1.close()
#              flash('Cluster Successfully Added!!')
                return redirect(url_for('clusters'))
            else:
                return('Cluster with that name not exist!!')
    return render_template('addcluster.html')


@app.route('/<cluster_name>/hosts')
def hosts(cluster_name):
    print("Showing Host List!!")
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT hostgroup, host_IP, host_fqdn, host_live FROM `%s` ", (cluster_name))
    data = cursor.fetchall()
    return render_template("page2.html", value=data, name=cluster_name)

@app.route('/<clusterName>/<hostName>/delete_host')
def delete_host(clusterName , hostName):
    print("Deleting Host!!")
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `%s` WHERE host_IP = %s ", (clusterName, hostName))
    conn.commit()
    conn.close()
#    flash('Host Successfully Deleted!!')
    return redirect(url_for('hosts', cluster_name=clusterName))


@app.route('/<clusterName>/add_host', methods = ['GET', 'POST'])
def add_host(clusterName):
    if request.method == 'POST':
        print("Deleting Host!!")
        new_cluster_name = clusterName
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT cluster_id FROM cluster_info where cluster_name = %s LIMIT 1", (new_cluster_name))
        clust_id_temp = cursor.fetchone()
        clust_id = clust_id_temp[0]
        conn1 = mysql.get_db()
        cur = conn1.cursor()
        if request.form['hg1']:
            host_group1=request.form['hg1']
            ip_address1=request.form['ip1']
            fqdn1=request.form['fq1']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group1, ip_address1, fqdn1))
        if request.form['hg2']:
            host_group2=request.form['hg2']
            ip_address2=request.form['ip2']
            fqdn2=request.form['fq2']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group2, ip_address2, fqdn2))
        if request.form['hg3']:
            host_group3=request.form['hg3']
            ip_address3=request.form['ip3']
            fqdn3=request.form['fq3']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group3, ip_address3, fqdn3))
        if request.form['hg4']:
            host_group4=request.form['hg4']
            ip_address4=request.form['ip4']
            fqdn4=request.form['fq4']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group4, ip_address4, fqdn4))
        if request.form['hg5']:
            host_group5=request.form['hg5']
            ip_address5=request.form['ip5']
            fqdn5=request.form['fq5']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group5, ip_address5, fqdn5))
        if request.form['hg6']:
            host_group6=request.form['hg6']
            ip_address6=request.form['ip6']
            fqdn6=request.form['fq6']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group6, ip_address6, fqdn6))
        if request.form['hg7']:
            host_group7=request.form['hg7']
            ip_address7=request.form['ip7']
            fqdn7=request.form['fq7']
            cur.execute("INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",(new_cluster_name, clust_id, new_cluster_name, host_group7, ip_address7, fqdn7))
        conn1.commit()
        conn1.close()
#       flash('Host Successfully Deleted!!')
        return redirect(url_for('hosts', cluster_name=clusterName))
    return render_template('addhost.html', name=clusterName )

@app.route('/<clusterName>/checklist')
def checklist(clusterName):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT host_fqdn FROM `%s`", (clusterName))
        data = cursor.fetchall()
        with open('scripts/hosts', 'w') as f:
            for item in data:
                f.write("%s\n" % item)
        os.system("sh scripts/run.sh")
        #Adding scripts output table in list of tuples
        with open('scripts/reports/tabular_report.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            list_of_lists = list(map(list, csv_reader))
#            print(list_of_lists)
        #Now put tuple value to the Tables
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT  cluster_id, host_id FROM `%s`", (clusterName))
        data = cursor.fetchall()
        data1 = list(data)
        cursor.execute("SELECT count(cluster_id) FROM `%s`", (clusterName))
        host_count = cursor.fetchone()[0]
        print(host_count)
#        int_host_count = int(host_count[0])
        print(data1)
        check_table_name = clusterName + "_checklist" 
        for i in range(6):
            list_of_lists[i].insert(0, check_table_name)
        print(list_of_lists)
        list_of_tuples = [tuple(l) for l in list_of_lists]
        print(list_of_tuples)
        t1 = list_of_tuples[0]
        t2 = list_of_tuples[1]
        t3 = list_of_tuples[2]
        t4 = list_of_tuples[3]
        t5 = list_of_tuples[4]
        t6 = list_of_tuples[5]
        print(t1)
        tuple_check_table_name = ( check_table_name )
        list_check_table_name = [tuple_check_table_name,]*host_count
        print(list_check_table_name)
        conn1 = mysql.get_db()
        cur = conn1.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS `%s`(cluster_id VARCHAR(200), host_id VARCHAR(200), host_fqdn VARCHAR(200) NOT NULL, timestamp VARCHAR(200) NOT NULL, uptime VARCHAR(200), os_version VARCHAR(200), kernel_version VARCHAR(200), disk_util_opt VARCHAR(200), disk_util_var VARCHAR(200), disk_util_root VARCHAR(200), core VARCHAR(200), memory VARCHAR(200), mtu VARCHAR(200), swap VARCHAR(200), selinux VARCHAR(200) , firewall VARCHAR(200) , ntpd VARCHAR(200) , IP_forwarding VARCHAR(200))", (check_table_name))
#        cur.executemany("INSERT INTO `%s`( host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", list_of_tuples)
        cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", t1)
        cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", t2)
        cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", t3)
        cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", t4)
        cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", t5)
        cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", t6)
        conn1.commit()
        conn1.close()
        print("Running Check List!!")
        # Now get the data and put in table
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding FROM `%s` ORDER BY timestamp DESC LIMIT 6", (check_table_name))
        data = cursor.fetchall()
        return render_template("checklist.html", value=data, name=clusterName)

@app.route("/return-file")
def get_csv():
    try:
        return send_from_directory(
            app.config["CLIENT_CSV"], filename="Checklist_All_Host.txt", as_attachment=True
            )
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":
    app.run()