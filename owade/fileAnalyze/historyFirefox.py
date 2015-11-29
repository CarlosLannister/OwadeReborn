import sqlite3
import datetime
import re
from owade.constants import *

class GetFirefoxHistory:

    def getHistory(self, db):
        print "--", "Getting firefox history"
        dic = {}
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        listhistory = []
        cursor.execute("SELECT url, visit_count, last_visit_date "
                            "FROM moz_places")

        all_rows = cursor.fetchall()
        for row in all_rows:
            # If the is not last_visit_day
            if row[2] is not None:
                # TO DO: Darle formato molon a la fecha
                last_visit_date = datetime.datetime.fromtimestamp(row[2] / 1000000.0)
            else:
                last_visit_date = row[2]
            dic['url'] = row[0]
            dic['visit_count'] = row[1]
            dic['last_visit_date'] = str(last_visit_date)

            listhistory.append(dic)
            dic = {}
        return listhistory

    def getDownloads(self, db):
        print "--", "Getting firefox downloads"
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        listnumbersid = []  # All the ids from the different programms.
        rowdownloads = []
        listdownloads = []
        dic = {}
        cursor.execute("SELECT place_id FROM moz_annos")
        all_rows = cursor.fetchall()

        for row in all_rows:
            listnumbersid.append(row[0])
        listnumbersid = set(listnumbersid)
        for number in listnumbersid:
            cursor.execute("SELECT content from moz_annos WHERE place_id =" + str(number))
            all_rows = cursor.fetchall()
            # Size of the files
            size = re.findall("\d+", all_rows[2][0].split(",")[2])[0]
            # Date when the file was downloaded
            date = datetime.datetime.fromtimestamp(int(re.findall("\d+", all_rows[2][0].split(",")[1])[0]) / 1000.0)
            # Pathfile of the file
            pathfile = re.sub("file:///", '', all_rows[0][0])
            # Name of the file
            namefile = all_rows[1][0]
            dic['size'] = size
            dic['date'] = str(date)
            dic['pathfile'] = pathfile
            dic['namefile'] = namefile

            listdownloads.append(dic)
            dic = {}

        return listdownloads

    # TIME

    def main(self, myPath):
        myFirefoxPath = myPath + "/firefox/"
        profiles = os.listdir(myFirefoxPath)
        history = {}
        downloads = {}
        for profile in profiles:
            myFirefoxHistoryPath = myFirefoxPath + profile + "/" + firefoxHistoryFile
            history[profile] = self.getHistory(myFirefoxHistoryPath)
            downloads[profile] = self.getDownloads(myFirefoxHistoryPath)

        dic = {"GetFirefoxHistory" : history, "GetFirefoxDownloads" : downloads}

        return dic