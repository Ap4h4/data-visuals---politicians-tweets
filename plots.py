import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.plotting import table
from datetime import date, timedelta
from wordcloud import WordCloud
from matplotlib.backends.backend_pdf import PdfPages


class Plots:
    def LinePlot(self,df,axis):
        tmpLabel = df.head(1)['Uzytkownik']
        label = tmpLabel[0]
        return df.plot(kind='line', x='Dzien', y='ile', ax=axis, label=label)

    def Table(self, df):
        fig = plt.figure()
        ax = plt.subplot(111, frame_on=False)  # no visible frame
        ax.xaxis.set_visible(False)  # hide the x axis
        ax.yaxis.set_visible(False)  # hide the y axis
        ax.set_title("Statystyki badanych użytkowników według średniej ilości tweetów na dzień", fontsize=10)
        tab = table(ax, df, loc='upper center',colWidths=[0.3, 0.1, 0.2, 0.2, 0.2, 0.2])
        tab.auto_set_font_size(False)
        tab.set_fontsize(6.5)
        return fig

    def wc(self, df, title):
        wc = WordCloud(background_color="white")
        tmpDict = {}
        for key, values in df.items():
            tmpDict[key] = values
        wc.generate_from_frequencies(frequencies=tmpDict)
        fig = plt.figure()
        fig.suptitle(title, fontsize=16)
        ax = fig.add_subplot()
        ax.imshow(wc, interpolation="bilinear")
        ax.axis('off')
        return fig

    def Bar(self, df):
        fig = plt.figure()
        ax = plt.subplot(111)  # no visible frame
        df.plot(ax=ax, kind='bar', x='slowo', y='ilosc', legend=False, rot=30,
                      title='Najczesciej uzywane slowa przez wszystkich badanych uzytkownikow')
        plt.ylabel = 'Ilość wystąpień'
        plt.xlabel = 'Słowo'
        return fig


class Dataframes:
    def Sql2DF(self, sqlQuery,conenction):
        tmpDF = pd.read_sql_query(sqlQuery, conenction)
        #converting str to datetime
        dzien_in_df = 'Dzien' in tmpDF
        if dzien_in_df:
           tmpDF['Dzien'] = pd.to_datetime(tmpDF['Dzien'], format='%Y-%m-%d')
        return tmpDF

    def ConcatDFs(self, listOfDFs):
        tmpDF = pd.concat(listOfDFs)
        return tmpDF

    def DFtoDict(self, df):
        #removing column
        df.drop(columns='partia', inplace=True)
        #creating dictionary based on df
        tmpDict = {}
        for i in range(df.index.stop):
            tmpDict[df.loc[i].values[0]] = df.loc[i].values[1]
        return tmpDict


    def DateValues(self, d1,d2):
        delta = d2 - d1
        result = []
        for i in range(delta.days + 1):
            result.append(d1 + timedelta(days=i))
        return result

    def DFs2LinePlot(self, dict, title):
        fig = plt.figure()
        # tmpX = Plots.DateValues(self, date(2020, 6, 1), date(2020, 7, 11))
        ax = plt.gca()
        # plt.xticks(tmpX)
        for k, v in dict.items():
            Plots.LinePlot(self, v, ax)
        #marking dates of elections with the vertical lines
        plt.axvline(date(2020,6,22)) # 1st round
        plt.text(date(2020,6,22),-0.5,'I tura',color='#FF0000', weight = 'bold', va='center')
        plt.axvline(date(2020,7,12)) # 2nd round
        plt.text(date(2020,7,12), -0.5 , 'II tura',color='#FF0000', weight = 'bold', va='center')
        fig.suptitle(title)
        plt.ylabel('Ilosc tweetow')
        return fig

    def TweetsPerDay(self, connection, dict):
        PartieDF = {}
        KandydaciDF = {}
        for keys, values in dict.items():
            id_uzytkownika = int(keys)
            sqlQuery1 = f'''
            select p.partia as [Uzytkownik],
            CAST(t.data_dodania as date) as Dzien, 
            count(tekst) as ile
            from tweets_partie as t with (nolock)
            inner join Partie_polityczne  as p  with (nolock) on t.Partia=p.id
            where p.id = {id_uzytkownika}
            group by p.partia, CAST(t.data_dodania as date)
            order by CAST(t.data_dodania as date)
            '''
            # dictionary of df of parties
            if keys < 8:
                PartieDF[values] = self.Sql2DF(sqlQuery1, connection)
            else:
                # dictionary of df of president's candidates
                KandydaciDF[values] = self.Sql2DF(sqlQuery1, connection)
        return PartieDF, KandydaciDF

    def AvgTweetsPerDay(self, connection, dict):
        tweetsStats = {}
        for keys, values in dict.items():
            id_uzytkownika = int(keys)
            sqlQuery1 = f'''
            select p.partia as [Uzytkownik],
            COUNT(distinct(CAST(t.data_dodania as date))) as [Dni],
			MIN(CAST(t.data_dodania as date)) as [Dzien 0],
			MAX(CAST(t.data_dodania as date)) as [Ostatni dzien],
			COUNT(t.tekst) as [Suma tweetow],
			(COUNT(t.tekst) / COUNT(distinct(CAST(t.data_dodania as date)))) as [Tweety/dzien]			
            from tweets_partie as t with (nolock)
            inner join Partie_polityczne  as p  with (nolock) on t.Partia=p.id
			where p.id = {id_uzytkownika}
            group by p.partia
            order by (COUNT(t.tekst) / COUNT(distinct(CAST(t.data_dodania as date)))) DESC
            '''
            tweetsStats[values] = self.Sql2DF(sqlQuery1, connection)
        #concatinating dataframes to one
        listStats = []
        for key, value in tweetsStats.items():
            listStats.append(value)
        tmpDF = self.ConcatDFs(listStats)
        #sorting by average numbers of tweets per day
        tmpDF.sort_values('Tweety/dzien', ascending=False, inplace=True)
        #reseting index and starting from 1
        tmpDF = tmpDF.reset_index(drop='True')
        tmpDF.index = tmpDF.index + 1
        return tmpDF

    def Top5WordsPerUser(self, connection, dict):
        top5WordsPerUserDFs = {}
        for keys, values in dict.items():
            id_uzytkownika = int(keys)
            sqlQuery = f'''select p.partia, t.slowo, t.ilosc
            from tweety_slowa as t
            inner join Partie_polityczne  as p  with (nolock) on t.id_uzytkownika=p.id
            where
            t.id_uzytkownika = {id_uzytkownika}
            and
            t.id in (select top 5 t2.id from tweety_slowa as t2 
            where t2.slowo not in ('który', 'jestem','będę', 'zapraszam', 'wam', 'mnie','kandydat', 'was',
            'kampanii', 'słowa', 'mój')
             and
            t2.id_uzytkownika = t.id_uzytkownika
            --group by t2.id_uzytkownika, t2.ilosc
            order by t2.ilosc desc
                )
            order by t.id_uzytkownika, t.ilosc desc'''
            top5WordsPerUserDFs[values] = self.Sql2DF(sqlQuery, connection)
        return top5WordsPerUserDFs

    def TopWordsOverall(self, connection):
        sqlQuery = '''select top 15 t1.slowo, sum(t1.ilosc) as ilosc
            from tweety_slowa as t1 
            where
            t1.slowo not in
            ('który', 'jestem','będę', 'zapraszam', 'wam', 'mnie','kandydat', 'was',
            'kampanii', 'słowa', 'mój', 'bez')
            group by t1.slowo
            order by SUM(t1.ilosc) desc
            '''
        topWords = self.Sql2DF(sqlQuery,connection)
        return topWords

    def saving(self, dict):
            fileName = input("Podaj nazwe pliku: ")
            fileName = fileName + '.pdf'
            with PdfPages(fileName) as pdf:
                for values in dict.values():
                    pdf.savefig(values)
                    plt.close()