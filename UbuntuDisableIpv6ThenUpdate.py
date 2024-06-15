import os
os.system("sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1")
os.system("sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1")
os.system("sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
os.system("sudo apt-get update")
os.system("sudo apt-get upgrade")