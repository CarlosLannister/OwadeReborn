import sqlite3
from owade.constants import *


class GetChromeHistory:

    def getChromeHistoryData(self, myPath):
        """
            From https://github.com/OsandaMalith/ChromeFreak/blob/master/ChromeFreak.py CC license
        """

        historyValues = {}
        try:
            sqlitePath = myPath + "/chrome/" + chromeHistoryFile
            connexion = sqlite3.connect(sqlitePath)
            c = connexion.cursor()
            c.execute("SELECT urls.url, urls.title, urls.visit_count,urls.typed_count, \
			    datetime((urls.last_visit_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			    datetime((visits.visit_time/1000000)-11644473600,'unixepoch', 'localtime'), \
			    CASE (visits.transition & 255)\
			    WHEN 0 THEN 'User clicked a link'\
			    WHEN 1 THEN 'User typed the URL in the URL bar'\
			    WHEN 2 THEN 'Got through a suggestion in the UI'\
			    WHEN 3 THEN 'Content automatically loaded in a non-toplevel frame - user may not realize'\
			    WHEN 4 THEN 'Subframe explicitly requested by the user'\
			    WHEN 5 THEN 'User typed in the URL bar and selected an entry from the list - such as a search bar'\
			    WHEN 6 THEN 'The start page of the browser'\
			    WHEN 7 THEN 'A form the user has submitted values to'\
			    WHEN 8 THEN 'The user reloaded the page, eg by hitting the reload button or restored a session'\
			    WHEN 9 THEN 'URL what was generated from a replacable keyword other than the default search provider'\
			    WHEN 10 THEN 'Corresponds to a visit generated from a KEYWORD'\
			    END AS Description\
			    FROM urls, visits WHERE urls.id = visits.url")

            for row in c:
                try:
                    historyValues['URL %s' % row[0]] = {'title':row[1].encode("utf-8"), 'visitNumber':str(row[2]),
                    'lastVisit':str(row[4]), 'firstVisit':str(row[5])}
                except Exception, e:
                    print e
                    continue
            return historyValues
        except sqlite3.OperationalError, e:
            e = str(e)
            if e == 'database is locked':
                print '[!] Make sure Google Chrome is not running in the background'
            elif e == 'no such table: downloads':
                print '[!] Something wrong with the database name'
            elif e == 'unable to open database file':
                print '[!] Something wrong with the database path'
            else:
                print e
            return None

    def getChromeDowloadData(self, myPath):
        """
            From https://github.com/OsandaMalith/ChromeFreak/blob/master/ChromeFreak.py CC license
        """
        downloadValues = {}
        try:
            sqlitePath = myPath + "/chrome/" + chromeHistoryFile
            connexion = sqlite3.connect(sqlitePath)
            c = connexion.cursor()
            c.execute("SELECT url, current_path, target_path,datetime((end_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			 datetime((start_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			 received_bytes, total_bytes FROM downloads,\
			 downloads_url_chains WHERE downloads.id = downloads_url_chains.id")

            for row in c:
                receivedBytes = ''
                try:
                    #"%.2f" % receivedBytes
                    receivedBytes = "%.2f Bytes" % float(row[5])
                    #if receivedBytes < 1024:
                    #downloads += 'Received Bytes = %.2f Bytes\n' % (float(row[5]))
                    if float(row[5]) > 1024 and float(row[5]) < 1048576:
                        receivedBytes = "%.2f KB" % (float(row[5]) / 1024)
                    elif (float(row[5]) > 1048576 and float(row[5]) < 1073741824):
                        receivedBytes = "%.2f MB" % (float(row[5]) / 1048576)
                    else:
                        receivedBytes = "%.2f GB" % (float(row[5]) / 1073741824)

                    downloadValues['URL %s' % row[0]] = {'currentPath':str(row[1]), 'targetPath':str(row[2]),
                    'endTime':str(row[4]), 'startTime':str(row[5]), 'receivedBytes':str(receivedBytes)}

                except UnicodeError:
                    continue

            return downloadValues

        except sqlite3.OperationalError, e:
            e = str(e)
            if e == 'database is locked':
                print '[!] Make sure Google Chrome is not running in the background'
            elif e == 'no such table: downloads':
                print '[!] Something wrong with the database name'
            elif e == 'unable to open database file':
                print '[!] Something wrong with the database path'
            else:
                print e
            return None

    def main(self, myPath):
        placesValues = self.getChromeHistoryData(myPath)
        if placesValues == None:
            return None
        downloadValues = self.getChromeDowloadData(myPath)
        return {self.__class__.__name__:{'history':placesValues, 'download':downloadValues}}