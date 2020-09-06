import os
import tweepy as tw
import re
import datetime


def Connection():
    consumer_key= '******'
    consumer_secret= '******'
    access_token= '******'
    access_token_secret= '******'
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    return api

def GettingTweetsOfParties(start_date, end_date, db_connection):
    parties_accounts = ["@pisorgpl", "@Platforma_org", "@__Lewica", "@wiosnabiedronia", "@partiarazem", "@nowePSL","@KONFEDERACJA_",
                        "@AndrzejDuda", "@krzysztofbosak", "@trzaskowski_", "@RobertBiedron", "@szymon_holownia", "@KosiniakKamysz"]
    timeStart = start_date
    timeStop = end_date
    api = Connection()
    for i in parties_accounts:
        for t in tw.Cursor(api.user_timeline, screen_name=i).items(5000):
            c = db_connection.cursor()
            tmpQ = c.execute("select id from Partie_polityczne where tweeter_account = ?", [i])
            tmpList = [q for q in tmpQ.fetchone()]
            tmpID = int(tmpList[0])
            tmpDate = t.created_at
            tmpText = t.text
            tmpText = tmpText.lower()
            c.close()
            # getting tweets only from given time period
            if tmpDate < timeStop and tmpDate >= timeStart:
                c = db_connection.cursor()
                c.execute("insert into tweets_partie values (?,?,?)", [tmpID, tmpDate, tmpText])
                c.commit()
        print("Searching for " + i + "has been finished")




