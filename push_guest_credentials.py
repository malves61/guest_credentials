#!/usr/local/bin/push_guest_wifi/bin/python3
from requests.auth import HTTPBasicAuth
import requests
import json
import urllib3
import random
import string
import segno
import paramiko
from datetime import datetime
from time import sleep

 
def generate_random_string(length):
    val_chars = string.ascii_letters + string.digits + "_-"
    random_string = ''.join(random.choice(val_chars) for i in range(length))
    return random_string

def update_mikrotik_ap(credentials):
    urllib3.disable_warnings()
    apiURL = 'http://192.168.X.X/rest' # Please enter URL 
    apiUsername = 'XXXX' # Input username here 
    apiPassword = 'XXXXX' # Input password here 
    apiHeaders={'Content-type':'application/json','Accept':'application/json'} # Headers for json content
    set2_4 = requests.patch(apiURL+'/interface/wifi/configuration/Config_guest2.4GHz', json={"ssid":credentials["guest_ssid"]}, auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False, headers=apiHeaders)
    set5 = requests.patch(apiURL+'/interface/wifi/configuration/Config_guest5GHz', json={"ssid":credentials["guest_ssid"]}, auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False, headers=apiHeaders)
    set_sec_guest = requests.patch(apiURL+'/interface/wifi/security/sec_guest', json={"passphrase":credentials["guest_password"]}, auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False, headers=apiHeaders)

def update_openwrt_ap(credentials):
    host = "192.168.X.X" # Please enter IP address
    user = "XXXX" # Input username here
    password = "XXXX" # Input password here
    client = paramiko.SSHClient()    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host,username=user,password=password,look_for_keys=False,allow_agent=False)

    for i in ['0', '1', '2', '3']:
        stdin, stdout, stderr = client.exec_command('uci get wireless.@wifi-iface['+i+'].network')
        sleep(0.25)
        for line in stdout:
             if line=="GUEST\n":
                 client.exec_command('uci set wireless.@wifi-iface['+i+'].ssid='+credentials['guest_ssid'])
                 sleep(0.25)
                 client.exec_command('uci set wireless.@wifi-iface['+i+'].key='+credentials['guest_password'])
                 sleep(0.25)
    client.exec_command('uci commit wireless', timeout=4)
    sleep(0.25)
    client.exec_command('wifi', timeout=4)
    sleep(0.25)
    client.close()

guest_credentials={"guest_ssid":generate_random_string(7),
                   "guest_password":generate_random_string(10),
                   "creation_date":datetime.now().strftime('%d-%m-%Y %H:%M:%S')} # create credentials
guest_credentials_file = '/etc/openhab/html/guest_credentials.json' # save credentials to json file

qrcode = segno.make_qr("WIFI:T:WPA;S:"+guest_credentials["guest_ssid"]+";P:"+guest_credentials["guest_password"]+";;")
qrcode.save("/etc/openhab/html/wifi.png", scale=4, border=1)

with open(guest_credentials_file, 'w', encoding ='utf8') as json_file: 
    json.dump(guest_credentials, json_file) 

update_mikrotik_ap(guest_credentials)
update_openwrt_ap(guest_credentials)