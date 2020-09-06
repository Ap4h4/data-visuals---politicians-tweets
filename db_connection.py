import pyodbc
import re

def DBConnection():
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=******;'
                          'Database=******;'
                          'Trusted_Connection=yes;')
    return conn

class tmpTable:
    def CreatingTmpTable(self, checking_id):
        con = DBConnection()
        c = con.cursor()
        #getting all tweets for given id and converting to list of strings
        id = checking_id
        tmpQuery = c.execute('select tekst from tweets_partie where partia = (?)', [id])
        tmpTweets = tmpQuery.fetchall()
        listTweets = []
        for t in tmpTweets:
            listTweets.append(str(t))
        #creating global temporary table
        c.execute("exec p_creating_tmp_Table")

        pattern = "^[A-Za-zęóąśłżźćńĘÓĄŚŁŻŹĆŃ]*$"
        excluded = ['na', 'dlatego', 'dziś', 'dzisiaj', 'wczoraj', 'ponieważ', 'się', 'dla', 'jest','jak','przez','ale','oraz','nie','tak',\
                    'jutro','które','aby','trwa','pod', 'będzie', 'jutro','już','żeby','antenie', 'być','tylko','pan','tym' ,'czy','którzy',\
                    'jako','mamy','może','każdy','tej','która','kiedy','którzy','które','której','którego','jeśli','dzień','jestem'\
                    'przed','nad','był','mówi','kto','kogo','też','takie','tego','temu','było','liczba','jednym','coraz','przed','ten','także'\
                    'zobaczenia','jednak','tutaj','raz','trasy','live','części','trasie','internetowej','jeżeli','transmisje','porannego'\
                     'relację','ostatnich','oglądaj','gościem','widzimy','kolejne','plan','którym','konferencji','przy','właśnie','kilka'\
                    'spotkiania','podczas','godziny','zdjęć','jeszcze','spotkanie', 'nas', 'lat', 'bardzo','mam','gdzie', 'dzięki','mnie'\
                    'bez','nami', 'oglądajcie', 'konferencja','gdy','czerwca','niż','prasowa','wywiad','wielu']
        for s in listTweets:
            t = s.split()
            for word in t:
                # checking if it's a word or special char/number
                matched = re.match(pattern, word)
                check = bool(matched)
                if check == True and len(word) > 2 and word not in excluded:
                    c.execute("insert into ##tmpTable values (?)", [word])
        tmpQuery2 = c.execute('''select top 100 words, count(words) as [ilosc]
                                from ##tmpTable
                                group by words
                                order by count(words) desc''')
        tmpResult = tmpQuery2.fetchall()
        c.close()
        c = con.cursor()
        for i in tmpResult:
            #print(i[0])
            #print(i[1])
            c.execute('insert into tweety_slowa values (?,?,?)', [id, i[0],i[1]])
            c.commit()
        print('Zapisano wszystkie slowa dla partii/uzytkownika o id: ', id)




