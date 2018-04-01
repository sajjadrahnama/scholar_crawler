# In The Name Of God
# ========================================
# [] File Name : conf
#
# [] Creation Date : 31/02/18
#
# [] Created By : Sajjad Rahnama (sajjad.rahnama7@gmail.com)
# =======================================
####################
# configuration part
####################
from pymongo import MongoClient

dbHost = "localhost"
dbPort = 27017
dbUser = ''
dbPass = ''
maxArticle = 10
maxCArtcile = 20
torControlPassword = ''
productionMode = False


def db_client():
    if dbPass and dbUser:
        return MongoClient(dbHost, dbPort, username=dbUser, password=dbPass)
    else:
        return MongoClient(dbHost, dbPort)
