import pandas as pd
from datetime import datetime
import cloudscraper
import json
import time
import openai
import logging
from custommessage import custom_message_creation

openai.api_key = 'your openai key'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#This class manages the initialization and configuration of a TextNow bot, utilizing session ID and CSRF token for secure interactions
class TextNowBot:
    def __init__(self, sid, csrf):
        self.cookies = {
            'connect.sid': sid,
            '_csrf': csrf
        }
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'darwin', 'mobile': False}
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.3',
            'x-csrf-token': self.get_initial_csrf_token()
        }

#Storing and using cookies for authentication 
    def get_initial_csrf_token(self):
        try:
            req = cloudscraper.create_scraper().get('https://www.textnow.com/messaging', cookies=self.cookies)
            if req.status_code == 200:
                resp = req.text
                needle = 'csrf-token" content="'
                needle_index = resp.find(needle)
                token_start = needle_index + len(needle)
                token_end = resp.find('"', token_start)
                csrf_token = resp[token_start:token_end]
                return csrf_token
        except Exception as e:
            logging.error(f"Failed to get CSRF token: {e}")
            raise

#Setting up data values & posting message requests using a cloudscraper
    def send_sms(self, phone_number, text):
        try:
            data = {
                'json': json.dumps({
                    'contact_value': phone_number,
                    'contact_type': 2,
                    'message': text,
                    'read': 1,
                    'message_direction': 2,
                    'message_type': 1,
                    'from_name': 'TextNowUser',
                    'has_video': False,
                    'new': True,
                    'date': datetime.now().isoformat()          
                })
            }
            response = cloudscraper.create_scraper().post(f'https://www.textnow.com/api/users/affannaushad500/messages',
                                headers=self.headers, cookies=self.cookies, data=data)
            print(f"Request data: {data}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            response.raise_for_status()        
            return response
        except Exception as e:
            logging.error(f"Error in send_sms: {e}")

#Prompting for authentication cookies  
def login():
    print("Go to https://www.textnow.com/messaging and open developer tools")
    print("\n")
    print("Open application tab and copy connect.sid cookie and paste it here.")
    sid = input("connect.sid: ")
    print("Open application tab and copy _csrf cookie and paste it here.")
    csrf = input("_csrf: ")
    return sid, csrf

#Sending texts to clients when 10 months have passed since their driving test
def process_customers(df, bot, today):
    try:
        for index, row in df.iterrows():
            if row['Processed'] == 0:
                passed = row['Date Passed']
                days_diff = (today - passed).days
                print(days_diff)
                if days_diff >= 304:
                    message = row['message_creation']                            
                    bot.send_sms(row['Number'], message)
                    time.sleep(30)
                    df.at[index, 'Processed'] = 1               
                else:
                    df.at[index, 'Processed'] = 0
    except Exception as e:
        logging.error(f"Error in process_customers: {e}")

    finally:                
        print(df['Processed'])

def main():
    try:
        df = pd.read_csv('/Users/affan/Documents/testing.csv', parse_dates=['Date Passed'])
        df.columns = df.columns.str.strip()
        # Setting the processed column value to 0 when no value is defined in the dataset
        if 'Processed' not in df.columns:
            df['Processed'] = 0
        else:
            df['Processed'].fillna(0, inplace=True)
        #Filling Missing Values with 0, Setting the Data Type to Integer & Setting the message_creation column to an empty value
        df['message_processed']= df['message_processed'].fillna(0)
        df['message_processed'] = df['message_processed'].astype('int')
        df['message_creation'] = ""
           
        custom_message_creation(df)
        sid, csrf = login()
        bot = TextNowBot(sid, csrf)
        today = datetime.now()
        process_customers(df, bot, today)
        df.to_csv('/Users/affan/Documents/testing.csv', index=False)
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
