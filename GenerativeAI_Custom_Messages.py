import pandas as pd
import openai


openai.api_key = 'your open ai key'

#Using OpenAi API to generate custom marketing messages for clients
def custom_message_creation(df):
    for index, row in df.iterrows():
        if row['message_processed'] == 0:
            name = row['Name']
            passed = row['Date Passed']
            response= ""
            stream = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                                    "role": "system",
                                    "content": "Send a custom marketing message for Safe 2 Drive Driving school tell the student hi and their name tell them when they passed their g2 and tell them to contact us to make their driving dreams come true! do not give any number or name of instructor Make sure to include verything within the tokens specifiied which are 120 do not leave your response unfinished i have maxtokens set to 120 in my program."
                },
                {
                                    "role": "user",
                                    "content": f"The name of the student is {name} and {passed} is the date they passed their G2"
                }
            ],
            stream=True,                    
            max_tokens=140)         
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
            df.at[index, 'message_creation'] = response
            df.at[index, 'message_processed'] = 1 

def main():
    df = pd.read_csv('/Users/affan/Documents/testing.csv', parse_dates=['Date Passed'])
    df.columns = df.columns.str.strip()

    #Setting the Processed column to an integer data type, filling missing values in message_processed column with 0, and setting the data type of the column to integer
    df['Processed'] = df['Processed'].astype('int')
    df['message_processed']= df['message_processed'].fillna(0)
    df['message_processed'] = df['message_processed'].astype('int')
    
    #Setting message_creation columns to an empty value
    df['message_creation'] = ""

    #Saving the updated DataFrame to a csv file
    df.to_csv('/Users/affan/Documents/testing.csv', index=False)
    print(df)

if __name__ == "__main__":
    main()