#!/usr/bin/env python
"""
Created on @ 2020
@author:
"""
# imports
from flask import Flask, render_template, json, request, session, redirect, url_for, send_file, send_from_directory, \
    safe_join, abort, flash, Response
import os
import sys
import time
from flaskext.mysql import MySQL
from csv import reader
import io
import csv
import pymysql
import re

# initialize the flask and SQL Objects
app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'your secret key'

# configure MYSQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Guavus@123'
app.config['MYSQL_DATABASE_DB'] = 'op_dashboard_new'
app.config['MYSQL_DATABASE_HOST'] = '192.168.133.196'
# app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

# Config Parameters
app.config["CLIENT_CSV"] = "/Users/mohitsharma/Desktop/operaton-dashboard/scripts/"

# define methods for routes (what to do and display)
# error = None

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


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "uname" and "psw" POST requests exist (user submitted form)
    if request.method == 'POST' and 'uname' in request.form and 'psw' in request.form:
        # Create variables for easy access
        username = request.form['uname']
        password = request.form['psw']
        # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        print(account)
        print(account[1])
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            return redirect(url_for('clusters'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        username=request.form['uname']
        password=request.form['psw']
        email=request.form['email']
        print(username)
        # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            conn = mysql.get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            conn.commit()
            conn.close()
            msg = 'You have successfully registered!'
            return render_template("login.html", msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/')
def clusters():
    if 'loggedin' in session:
        try:
            print("Showing Clusters!!")
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT A.cluster_name,A.cluster_desc,A.cluster_owner,(SELECT TABLE_ROWS from information_schema.tables where TABLE_NAME like QUOTE(A.cluster_name)),cluster_creation_date FROM cluster_info A;")
            data = cursor.fetchall()
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT firstname,lastname FROM accounts where username like %s", (session['username']))
            user = cursor.fetchall()
            return render_template("clusters.html", value=data, user=user, username=session['username'])
        except Exception as e:
            return render_template("clusters_fresh.html", error = str(e))
    return redirect(url_for('login'))

@app.route('/<cluster_name>/home')
def home(cluster_name):
    if 'loggedin' in session:
        print("Showing Homepage")
        return render_template("homepage.html", name=cluster_name)
    return redirect(url_for('login'))

@app.route('/inprogress')
def inprogress():
    return render_template("inprogress.html")


@app.route('/profile')
def profile():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username,firstname,lastname,email FROM accounts where username like %s",(session['username']))
    data = cursor.fetchall()
    return render_template("profile.html", value=data)

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
    cursor.execute("SELECT A.cluster_name,A.cluster_desc,A.cluster_owner,(SELECT TABLE_ROWS from information_schema.tables where TABLE_NAME like QUOTE(A.cluster_name)),cluster_creation_date FROM cluster_info A;")
    data = cursor.fetchall()
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT firstname,lastname FROM accounts where username like %s", (session['username']))
    user = cursor.fetchall()
#    error = 'Cluster Successfully Deleted!!'
    #   return redirect(url_for('clusters', error = error))
    flash("Cluster Deleted!", "success")
    return render_template("clusters.html", user=user, value=data, clusterName=clusterName)


@app.route('/search', methods=['POST'])
def search():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT firstname,lastname FROM accounts where username like %s", (session['username']))
    user = cursor.fetchall()
    error = None
    if request.method == "POST":
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT count(cluster_name) FROM cluster_info WHERE cluster_name like %s", request.form['search'])
        if cursor.fetchone()[0] == 1:
            print("Cluster found!!")
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT A.cluster_name,A.cluster_desc,A.cluster_owner,(SELECT TABLE_ROWS from information_schema.tables where TABLE_NAME like QUOTE(A.cluster_name)),cluster_creation_date FROM cluster_info A where A.cluster_name = %s",
                request.form['search'])
            data = cursor.fetchall()
            return render_template("clusters.html", value=data, user=user, username=session['username'])
        else:
            flash("Cluster not found!", "danger")
            return redirect(url_for("clusters"))


@app.route('/add_cluster', methods=['GET', 'POST'])
def add_cluster():
    if request.method == 'POST':
        print(session['username'])
        check_cluster_name = request.form['email']
        conn3 = mysql.connect()
        cursor3 = conn3.cursor()
        cursor3.execute("SELECT cluster_name FROM cluster_info WHERE cluster_name = %s", (check_cluster_name))
        data3 = cursor3.fetchone()
        if data3:
            flash("Cluster already exists!", "danger")
            return redirect(url_for("clusters"))
        else:
            new_cluster_name = request.form['email']
            cluster_description = request.form['description']
            cluster_date = time.strftime('%Y-%m-%d %H:%M:%S')
            conn = mysql.get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO cluster_info(cluster_name, cluster_desc, cluster_creation_date, cluster_owner) VALUES (%s,%s,%s,%s)",
                        (new_cluster_name, cluster_description, cluster_date, session['username']))
            conn.commit()
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT cluster_name FROM cluster_info WHERE cluster_name = %s LIMIT 1", (new_cluster_name))
            data1 = cursor.fetchone()
            data2 = data1[0]
            if data2 == request.form['email']:
                new_cluster_name = request.form['email']
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT cluster_id FROM cluster_info where cluster_name = %s LIMIT 1",
                               (new_cluster_name))
                clust_id_temp = cursor.fetchone()
                clust_id = clust_id_temp[0]
                conn1 = mysql.get_db()
                cur = conn1.cursor()
                cur.execute(
                    "CREATE TABLE `%s`(cluster_id INT NOT NULL, cluster_name VARCHAR(20) NOT NULL, host_id INT NOT NULL AUTO_INCREMENT, hostgroup VARCHAR(20) NOT NULL, host_IP VARCHAR(20) NOT NULL,host_fqdn VARCHAR(200) NOT NULL,host_live VARCHAR(20), PRIMARY KEY (host_id))",
                    (new_cluster_name))
                if request.form['hg1']:
                    host_group1 = request.form['hg1']
                    ip_address1 = request.form['ip1']
                    fqdn1 = request.form['fq1']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group1, ip_address1, fqdn1))
                if request.form['hg2']:
                    host_group2 = request.form['hg2']
                    ip_address2 = request.form['ip2']
                    fqdn2 = request.form['fq2']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group2, ip_address2, fqdn2))
                if request.form['hg3']:
                    host_group3 = request.form['hg3']
                    ip_address3 = request.form['ip3']
                    fqdn3 = request.form['fq3']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group3, ip_address3, fqdn3))
                if request.form['hg4']:
                    host_group4 = request.form['hg4']
                    ip_address4 = request.form['ip4']
                    fqdn4 = request.form['fq4']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group4, ip_address4, fqdn4))
                if request.form['hg5']:
                    host_group5 = request.form['hg5']
                    ip_address5 = request.form['ip5']
                    fqdn5 = request.form['fq5']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group5, ip_address5, fqdn5))
                if request.form['hg6']:
                    host_group6 = request.form['hg6']
                    ip_address6 = request.form['ip6']
                    fqdn6 = request.form['fq6']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group6, ip_address6, fqdn6))
                if request.form['hg7']:
                    host_group7 = request.form['hg7']
                    ip_address7 = request.form['ip7']
                    fqdn7 = request.form['fq7']
                    cur.execute(
                        "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                        (new_cluster_name, clust_id, new_cluster_name, host_group7, ip_address7, fqdn7))
                conn1.commit()
                conn1.close()
                #              flash('Cluster Successfully Added!!')
                flash("Cluster Added!", "success")
                return redirect(url_for('clusters'))
            else:
                return ('Cluster with that name not exist!!')
    return render_template('addcluster.html')


@app.route('/<cluster_name>/hosts')
def hosts(cluster_name):
    print("Showing Host List!!")
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT hostgroup, host_IP, host_fqdn, host_live FROM `%s` ", (cluster_name))
    data = cursor.fetchall()
    return render_template("page2.html", value=data, name=cluster_name)


@app.route('/<cluster_name>/hosts/checklist')
def selectChecklist(cluster_name):
    print("Showing Host List!!")
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT hostgroup, host_IP, host_fqdn, host_live FROM `%s` ", (cluster_name))
    data = cursor.fetchall()
    return render_template("selectChecklist.html", value=data, name=cluster_name)


@app.route('/<clusterName>/<hostName>/delete_host')
def delete_host(clusterName, hostName):
    print("Deleting Host!!")
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `%s` WHERE host_IP = %s ", (clusterName, hostName))
    conn.commit()
    conn.close()
    #    flash('Host Successfully Deleted!!')
    flash("Host Deleted!", "success")
    return redirect(url_for('hosts', cluster_name=clusterName))


@app.route('/<clusterName>/add_host', methods=['GET', 'POST'])
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
            host_group1 = request.form['hg1']
            ip_address1 = request.form['ip1']
            fqdn1 = request.form['fq1']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group1, ip_address1, fqdn1))
        if request.form['hg2']:
            host_group2 = request.form['hg2']
            ip_address2 = request.form['ip2']
            fqdn2 = request.form['fq2']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group2, ip_address2, fqdn2))
        if request.form['hg3']:
            host_group3 = request.form['hg3']
            ip_address3 = request.form['ip3']
            fqdn3 = request.form['fq3']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group3, ip_address3, fqdn3))
        if request.form['hg4']:
            host_group4 = request.form['hg4']
            ip_address4 = request.form['ip4']
            fqdn4 = request.form['fq4']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group4, ip_address4, fqdn4))
        if request.form['hg5']:
            host_group5 = request.form['hg5']
            ip_address5 = request.form['ip5']
            fqdn5 = request.form['fq5']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group5, ip_address5, fqdn5))
        if request.form['hg6']:
            host_group6 = request.form['hg6']
            ip_address6 = request.form['ip6']
            fqdn6 = request.form['fq6']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group6, ip_address6, fqdn6))
        if request.form['hg7']:
            host_group7 = request.form['hg7']
            ip_address7 = request.form['ip7']
            fqdn7 = request.form['fq7']
            cur.execute(
                "INSERT INTO `%s`(cluster_id, cluster_name, hostgroup, host_IP, host_fqdn) VALUES (%s, %s, %s, %s, %s)",
                (new_cluster_name, clust_id, new_cluster_name, host_group7, ip_address7, fqdn7))
        conn1.commit()
        conn1.close()
        #       flash('Host Successfully Deleted!!')
        flash("Host is added", "success")
        return redirect(url_for('hosts', cluster_name=clusterName))
    return render_template('addhost.html', name=clusterName)


@app.route('/<clusterName>/checklist', methods=['GET', 'POST'])
def checklist(clusterName):
        if request.method == 'POST':
#            conn = mysql.connect()
#            cursor = conn.cursor()
#            cursor.execute("SELECT host_fqdn FROM `%s`", (clusterName))
#            data = cursor.fetchall()
            data_host = request.form.getlist('host')
            print(data_host)
            with open('scripts/hosts', 'w') as f:
                for item in data_host:
                    f.write("%s\n" % item)
            CHECK = request.form['check']
            print(CHECK)
            os.system("sh scripts/run.sh %d" %int(CHECK))
            with open('scripts/reports/tabular_report.csv', 'r') as read_obj:
                csv_reader = reader(read_obj)
                list_of_lists = list(map(list, csv_reader))
                print(list_of_lists)
    # Now put tuple value to the Tables
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT  cluster_id, host_id FROM `%s`", (clusterName))
            data = cursor.fetchall()
            data1 = list(data)
   #         cursor.execute("SELECT count(cluster_id) FROM `%s`", (clusterName))
   #         host_count = cursor.fetchone()[0]
            host_count = len(data_host)
            print(host_count)
    #        int_host_count = int(host_count[0])
#           print(data1)
            check_table_name = clusterName + "_checklist"
            print(check_table_name)
            for i in range(host_count):
                list_of_lists[i].insert(0, check_table_name)
            print(list_of_lists)
            list_of_tuples = [tuple(l) for l in list_of_lists]
            print(list_of_tuples)

            tuple_check_table_name = (check_table_name)
            list_check_table_name = [tuple_check_table_name, ] * host_count
            print(list_check_table_name)

            conn1 = mysql.get_db()
            cur = conn1.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS `%s`(cluster_id int(11), host_id int(11), host_fqdn VARCHAR(200) NOT NULL, timestamp VARCHAR(200) NOT NULL, ping_status VARCHAR(200), ssh_status VARCHAR(200),  system_manufacturer VARCHAR(200), system_product_name VARCHAR(200), system_uuid VARCHAR(200), system_version VARCHAR(200), kernel_version VARCHAR(200), hardware_platform VARCHAR(200), bios_version VARCHAR(200), total_cpu VARCHAR(200), processor_frequency VARCHAR(200), total_memory VARCHAR(200), number_of_disks VARCHAR(200), sum_of_disks_space VARCHAR(200), os_version VARCHAR(200), hostname VARCHAR(200), host_timezone VARCHAR(200), ntp_sync_status VARCHAR(200), cidr VARCHAR(200), selinux_status VARCHAR(200) , dhcp_status VARCHAR(200) , network_manager_status VARCHAR(200) , interface_speed VARCHAR(200), mtu_speed VARCHAR(200) , log_fs_size VARCHAR(200), root_fs_size VARCHAR(200) , ip_forward_status VARCHAR(200), dmesg_status VARCHAR(200) , transparent_huge_pages_status VARCHAR(200), hdp_status VARCHAR(200), hadoop_version VARCHAR(200), hadoop_status VARCHAR(200), kerberos_status VARCHAR(200), ambari_server_status VARCHAR(200), ambari_client_status VARCHAR(200), zookeeper_status VARCHAR(200), kafka_status VARCHAR(200), kubernetes_status VARCHAR(200))",(check_table_name))
    #        cur.executemany("INSERT INTO `%s`( host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", list_of_tuples)
            check_int = int(CHECK)
            print(check_int)
            print("Run condition if elif loop")
            if check_int == 1:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    print(j)
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(j))
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space FROM `%s` ORDER BY timestamp DESC LIMIT %s",(check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            elif check_int == 2:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    print(j)
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(j))
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status FROM `%s` ORDER BY timestamp DESC LIMIT %s", (check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            elif check_int == 3:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",j)
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status FROM `%s` ORDER BY timestamp DESC LIMIT %s",(check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            elif check_int == 4:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",j)
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status FROM `%s` ORDER BY timestamp DESC LIMIT %s",(check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            elif check_int == 5:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",j)
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status FROM `%s` ORDER BY timestamp DESC LIMIT %s",(check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            elif check_int == 6:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",j)
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status FROM `%s` ORDER BY timestamp DESC LIMIT %s",(check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            elif check_int == 7:
                for i in range(host_count):
                    j = list_of_tuples[i]
                    cur.execute("INSERT INTO `%s`(host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",j)
                conn1.commit()
                conn1.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status FROM `%s` ORDER BY timestamp DESC LIMIT %s",(check_table_name, host_count))
                data = cursor.fetchall()
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            else:
                print("Enter Incorrect value Check List!!")
                return render_template("checklist.html", value=data, name=clusterName, view=CHECK)
            print("Running Check List!!")
    # Now get the data and put in table



@app.route("/<clusterName>/checklist/reports")
def show_reports(clusterName):
    print("Showing reports!")
    conn = mysql.connect()
    cursor = conn.cursor()
    tableName = clusterName + '_checklist'
    cursor.execute("SELECT DISTINCT timestamp FROM `%s` ORDER BY timestamp DESC limit 10", (tableName))
    data = cursor.fetchall()
    return render_template("checklist_reports.html", value=data, name=clusterName)


@app.route("/<clusterName>/return-file")
def download_report(clusterName):
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        check_table_name = clusterName + "_checklist"
        cursor.execute("SELECT timestamp FROM `%s` ORDER BY timestamp DESC LIMIT 1", (check_table_name))
        timestamp = cursor.fetchall()
        cursor.execute("SELECT IFNULL(cluster_id, 'None'), IFNULL(host_id, 'None'), IFNULL(host_fqdn, 'None'), IFNULL(timestamp, 'None'), IFNULL(ping_status, 'None'), IFNULL(ssh_status, 'None'), IFNULL(system_manufacturer, 'None'), IFNULL(system_product_name, 'None'), IFNULL(system_uuid, 'None'), IFNULL(system_version, 'None'), IFNULL(kernel_version, 'None'), IFNULL(hardware_platform, 'None'), IFNULL(bios_version, 'None'), IFNULL(total_cpu, 'None'), IFNULL(processor_frequency, 'None'), IFNULL(total_memory, 'None'), IFNULL(number_of_disks, 'None'), IFNULL(sum_of_disks_space, 'None'), IFNULL(os_version, 'None'), IFNULL(hostname, 'None'), IFNULL(host_timezone, 'None'), IFNULL(ntp_sync_status, 'None'), IFNULL(cidr, 'None'), IFNULL(selinux_status, 'None'), IFNULL(dhcp_status, 'None'), IFNULL(network_manager_status, 'None'), IFNULL(interface_speed, 'None'), IFNULL(mtu_speed, 'None'), IFNULL(log_fs_size, 'None'), IFNULL(root_fs_size, 'None'), IFNULL(ip_forward_status, 'None'), IFNULL(dmesg_status, 'None'), IFNULL(transparent_huge_pages_status, 'None'), IFNULL(hdp_status, 'None'), IFNULL(hadoop_version, 'None'), IFNULL(hadoop_status, 'None'), IFNULL(kerberos_status, 'None'), IFNULL(ambari_server_status, 'None'), IFNULL(ambari_client_status, 'None'), IFNULL(zookeeper_status, 'None'), IFNULL(kafka_status, 'None'), IFNULL(kubernetes_status, 'None') FROM `%s` where timestamp=%s", (check_table_name,timestamp))
        result = cursor.fetchall()
        print("Result is : ",result)
        output = io.StringIO()
        writer = csv.writer(output)

#        line = ['host_fqdn, timestamp, uptime, os_version, kernel_version, disk_util_opt, disk_util_var, disk_util_root, core, memory, mtu, swap, selinux, firewall, ntpd, IP_forwarding']
        line = ['cluster_id, host_id, host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status']

        writer.writerow(line)


        for row in result:
            line = [row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3] + ',' + row[4] + ',' + row[5] + ',' + row[6] + ',' + row[7] + ',' + row[8] + ',' + row[9] + ',' + row[10] + ',' + row[11] + ',' + row[12] + ',' + row[13] + ',' + row[14] + ',' + row[15] + ',' + row[16] + ',' + row[17] + ',' + row[18] + ',' + row[19] + ',' + row[20] + ',' + row[21] + ',' + row[22] + ',' + row[23] + ',' + row[24] + ',' + row[25] + ',' + row[26] + ',' + row[27] + ',' + row[28] + ',' + row[29] + ',' + row[30] + ',' + row[31] + ',' + row[32] + ',' + row[33] + ',' + row[34] + ',' + row[35] + ',' + row[36] + ',' + row[37] + ',' + row[38] + ',' + row[39] + ',' + row[40] + ',' + row[41]]
            print("Line is :",line)
            writer.writerow(line)

        output.seek(0)

        return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=checklist_report.csv"})
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route("/<clusterName>/<timestamp>/return-file")
def download_past_report(clusterName, timestamp):
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        check_table_name = clusterName + "_checklist"
        cursor.execute("SELECT IFNULL(cluster_id, 'None'), IFNULL(host_id, 'None'), IFNULL(host_fqdn, 'None'), IFNULL(timestamp, 'None'), IFNULL(ping_status, 'None'), IFNULL(ssh_status, 'None'), IFNULL(system_manufacturer, 'None'), IFNULL(system_product_name, 'None'), IFNULL(system_uuid, 'None'), IFNULL(system_version, 'None'), IFNULL(kernel_version, 'None'), IFNULL(hardware_platform, 'None'), IFNULL(bios_version, 'None'), IFNULL(total_cpu, 'None'), IFNULL(processor_frequency, 'None'), IFNULL(total_memory, 'None'), IFNULL(number_of_disks, 'None'), IFNULL(sum_of_disks_space, 'None'), IFNULL(os_version, 'None'), IFNULL(hostname, 'None'), IFNULL(host_timezone, 'None'), IFNULL(ntp_sync_status, 'None'), IFNULL(cidr, 'None'), IFNULL(selinux_status, 'None'), IFNULL(dhcp_status, 'None'), IFNULL(network_manager_status, 'None'), IFNULL(interface_speed, 'None'), IFNULL(mtu_speed, 'None'), IFNULL(log_fs_size, 'None'), IFNULL(root_fs_size, 'None'), IFNULL(ip_forward_status, 'None'), IFNULL(dmesg_status, 'None'), IFNULL(transparent_huge_pages_status, 'None'), IFNULL(hdp_status, 'None'), IFNULL(hadoop_version, 'None'), IFNULL(hadoop_status, 'None'), IFNULL(kerberos_status, 'None'), IFNULL(ambari_server_status, 'None'), IFNULL(ambari_client_status, 'None'), IFNULL(zookeeper_status, 'None'), IFNULL(kafka_status, 'None'), IFNULL(kubernetes_status, 'None') FROM `%s` where timestamp=%s",(check_table_name, timestamp))
        result = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        line = ['cluster_id, host_id, host_fqdn, timestamp, ping_status, ssh_status, system_manufacturer, system_product_name, system_uuid, system_version, kernel_version, hardware_platform, bios_version, total_cpu, processor_frequency, total_memory, number_of_disks, sum_of_disks_space, os_version, hostname, host_timezone, ntp_sync_status, cidr, selinux_status, dhcp_status, network_manager_status, interface_speed, mtu_speed, log_fs_size, root_fs_size, ip_forward_status, dmesg_status, transparent_huge_pages_status, hdp_status, hadoop_version, hadoop_status, kerberos_status, ambari_server_status, ambari_client_status, zookeeper_status, kafka_status, kubernetes_status']
        writer.writerow(line)

        for row in result:
            line = [
                row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3] + ',' + row[4] + ',' + row[5] + ',' + row[6] + ',' +
                row[7] + ',' + row[8] + ',' + row[9] + ',' + row[10] + ',' + row[11] + ',' + row[12] + ',' + row[
                    13] + ',' + row[14] + ',' + row[15] + ',' + row[16] + ',' + row[17] + ',' + row[18] + ',' + row[
                    19] + ',' + row[20] + ',' + row[21] + ',' + row[22] + ',' + row[23] + ',' + row[24] + ',' + row[
                    25] + ',' + row[26] + ',' + row[27] + ',' + row[28] + ',' + row[29] + ',' + row[30] + ',' + row[
                    31] + ',' + row[32] + ',' + row[33] + ',' + row[34] + ',' + row[35] + ',' + row[36] + ',' + row[
                    37] + ',' + row[38] + ',' + row[39] + ',' + row[40] + ',' + row[41]]
            print("Line is :", line)
            writer.writerow(line)

        output.seek(0)

        return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=checklist_report.csv"})
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run()