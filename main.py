from twitter_connection import Connection, GettingTweetsOfParties
from db_connection import DBConnection, tmpTable
from plots import Dataframes, Plots
import matplotlib.pyplot as plt
import datetime

api = Connection()
db = DBConnection()
d = Dataframes()
p = Plots()

#users definitions
Partie = {1:'PiS', 2:'PO', 3:'Lewica', 4:'Wiosna',5:'Razem',6:'PSL', 7:'Konfederacja', 8:'Duda',9:'Bosak',10:'Trzaskowki',
          11:'Biedroń', 12:'Hołownia', 13:'Kosiniak-Kamysz'}
###saving tweets from Twitter into DB_table from 6th of June to 19th of July 2020
"""timeStart = datetime.datetime(2020,6,1,0,0,0)
timeStop = datetime.datetime(2020,7,19,0,0,0)
GettingTweetsOfParties(timeStart, timeStop,db)"""

###getting most frequently used words for each account
"""c = db.cursor()
tmpQ = c.execute('select id from Partie_polityczne')
tmpQ = tmpQ.fetchall()
t =tmpTable()
for i in tmpQ:
    t.CreatingTmpTable(i[0])"""

###dictionary for collecting all plots
tmpPlots = {}

###getting sum of tweets per day for users:
PartieProcessed, KandydaciProcessed = d.TweetsPerDay(db, Partie)
#line plot of tweets per users
tmpPlots['LinePlot1'] = d.DFs2LinePlot(PartieProcessed, 'Partie')
tmpPlots['LinePlot2'] = d.DFs2LinePlot(KandydaciProcessed, 'Kandydaci na prezydenta')


###average stats of tweets
tweetsStats = d.AvgTweetsPerDay(db,Partie)
tmpPlots['Stats'] = p.Table(tweetsStats)

###bar plot of most frequently used words
tmpWords = d.TopWordsOverall(db)
tmpPlots['Bar'] = p.Bar(tmpWords)


###top 5 words by party
tmpDFs = d.Top5WordsPerUser(db, Partie)
#mapping DFs to Dicts for WordCloud format
tmpDicts ={}
for key, value in tmpDFs.items():
    tmpDicts[key] = d.DFtoDict(value)
#generating wc plots and saving into dictionary of wc plots
tmpWC = {}
for key, value in tmpDicts.items():
    #tmpWC[key] = p.wc(value,key)
    tmpPlots[key]= p.wc(value,key)


###creating PDF RAPORT
d.saving(tmpPlots)
