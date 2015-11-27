import virustotal
#https://github.com/joxeankoret/multiav

API_KEY = "52410f0f006ce4a4dd7abbfabd4fe566033d958d85cc7072984ad6ba71df9e9d"
v = virustotal.VirusTotal(API_KEY)

report = v.scan("/media/lannister/TOSHIBA EXT/storage/file/21367.bat")

report.join()
assert report.done == True

if report.done:
	print "Report"
	print "- Resource's UID:", report.id
	print "- Scan's UID:", report.scan_id
	print "- Permalink:", report.permalink
	print "- Resource's SHA1:", report.sha1
	print "- Resource's SHA256:", report.sha256
	print "- Resource's MD5:", report.md5
	print "- Resource's status:", report.status
	print "- Antivirus' total:", report.total
	print "- Antivirus's positives:", report.positives
	for antivirus, malware in report:
	    if malware is not None:
	        print
	        print "Antivirus:", antivirus[0]
	        print "Antivirus' version:", antivirus[1]
	        print "Antivirus' update:", antivirus[2]
	        print "Malware:", malware