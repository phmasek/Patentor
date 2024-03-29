#!/usr/bin/python
# Written by Philip Masek
# More info found at https://www.github.com/pletron

import sys, getopt
import xml.etree.ElementTree as xml
from datetime import datetime

def main(argv):
	inputfile = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print 'patents_to_sql.py -i <inputfile> -o <outputfile>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'patents_to_sql.py -i <inputfile> -o <outputfile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg

	
	if outputfile == '' or inputfile == '':
		print 'patents_to_sql.py -i <inputfile> -o <outputfile>'
		sys.exit(2)	

	
	e = xml.parse(inputfile).getroot()
	f = open(outputfile, 'w')


	PUB_TITLE = 0
	PUB_ID = 1
	GRANTED = 2
	PUB_DATE = 3
	PUB_OWNERS = 5
	PUB_IPC = 4
	NR_CITED = 7
	NR_CITINGS = 6
	ABSTRACT = 8


	pCounter = 1
	iCounter = 0

	ipclist = []

	ipc_relation_queries = []
	ipc_queries = []
	patent_queries = []



	f.write('# Generated SQL DB from the %s file regarding patents\n# Generated by script written by Philip Masek\n# More info at https://www.github.com/pletron\n\n' % inputfile)
	f.write('DROP TABLE IF EXISTS `patents`;\n' +
	'CREATE TABLE `patents` (\n' +
	  '\t`pid` int(11) DEFAULT NULL,\n' +
	  '\t`pub_title` varchar(255) DEFAULT NULL,\n' +
	  '\t`pub_nr` varchar(50) DEFAULT NULL,\n' +
	  '\t`granted` varchar(3) DEFAULT NULL,\n' +
	  '\t`pub_date` datetime DEFAULT NULL,\n' +
	  '\t`current_owner` varchar(150) DEFAULT NULL,\n' +
	  '\t`nr_citings` int(11) DEFAULT NULL,\n' +
	  '\t`nr_cited` int(11) DEFAULT NULL,\n' +
	  '\t`abstract` varchar(256) DEFAULT NULL\n' +
	') ENGINE=InnoDB DEFAULT CHARSET=latin1;\n')

	f.write('DROP TABLE IF EXISTS `ipc`;\n' +
	'CREATE TABLE `ipc` (\n' +
	  '\t`iid` int(11) unsigned NOT NULL AUTO_INCREMENT,\n' +
	  '\t`name` varchar(100) DEFAULT NULL,\n' +
	  '\tPRIMARY KEY (`iid`)\n' +
	') ENGINE=InnoDB DEFAULT CHARSET=latin1;\n')

	f.write('DROP TABLE IF EXISTS `ipc_relation`;\n' +
	'CREATE TABLE `ipc_relation` (\n' +
	  '\t`rid` int(11) unsigned NOT NULL AUTO_INCREMENT,\n' +
	  '\t`pid` int(11) DEFAULT NULL,\n' +
	  '\t`iid` int(11) DEFAULT NULL,\n' +
	  '\tPRIMARY KEY (`rid`)\n' +
	') ENGINE=InnoDB DEFAULT CHARSET=latin1;\n')



	# IPC unique extraction for all IPC's in xml
	for child in e:
		for ipc in child[PUB_IPC]:
			if ipc.text.encode('utf-8') not in ipclist:
				ipclist.append(ipc.text.encode('utf-8'))
				ipc_queries.append('INSERT INTO `ipc` (`name`) VALUES (\'%s\');' % ipc.text.encode('utf-8'))
				iCounter += 1


	print "Finished: IPC extraction done with %d IPC queries" % len(ipc_queries)


	# Patent extractions and relation with IPC
	for child in e:


		# Extract owners to one single string
		owners = ''
		for owner in child[PUB_OWNERS]:
			if owner.text is not None:
				owners += '%s, ' % owner.text.encode('utf-8').replace('\'','\\\'')

		# Check all IPC for one Patent and relate to [ipclist]
		for ipc in child[PUB_IPC]:
			ipc_relation_queries.append('INSERT INTO `ipc_relation` (`pid`, `iid`) VALUES (%d, %d);' % (pCounter, int(ipclist.index(ipc.text.encode('utf-8'))+1)))


		if child[ABSTRACT].text is not None:
			abstract = child[ABSTRACT].text.encode('utf-8').replace('\\','\\\\').replace('\'','\\\'')
		else:
			abstract = ''

		patent_queries.append('INSERT INTO `patents` (`pid`, `pub_title`, `pub_nr`, `granted`, `pub_date`, `current_owner`, `nr_citings`, `nr_cited`, `abstract`) VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d, %d, \'%s\');' % (pCounter, child[PUB_TITLE].text.encode('utf-8').replace('\'','\\\''), child[PUB_ID].text.encode('utf-8'), child[GRANTED].text.encode('utf-8'), datetime.strptime(child[PUB_DATE].text.encode('utf-8'), "%Y/%m/%d"), owners, int(child[NR_CITINGS].text.encode('utf-8').replace('n.a.','0')), int(child[NR_CITED].text.encode('utf-8').replace('n.a.','0')), abstract))

		pCounter+=1


	print "Finished: patent extrations with %d IPC_relation queries and %d patent queries" % (len(ipc_relation_queries), len(patent_queries))


	f.write("\n".join(patent_queries))
	f.write("\n".join(ipc_queries))
	f.write("\n".join(ipc_relation_queries))



	f.close()

if __name__ == "__main__":
	main(sys.argv[1:])