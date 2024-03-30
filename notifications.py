# tele bot Key: 6458077063:AAEnTeHpT5J2IDXlZk9v_4XJxXLhtrX5e-M
# https://app.nocodeapi.com/dashboard/api/telegram
    
# import requests
# import telegram

# def telegram_bot_sendtext(bot_message):
    
#     bot_token = '6458077063:AAEnTeHpT5J2IDXlZk9v_4XJxXLhtrX5e-M'
#     bot_chatID = '546662823'
#     bot_groupID = '-4107378534'
#     send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

#     response = requests.get(send_text)
#     return response.json()
    

# test = telegram_bot_sendtext("You're favourited car is available now!")
# print(test)



# Username: krystal.lim.2022@scis.smu.edu.sg
# Password: Gentlemengarage123@
# recovery code: G734ADUE1Q6V8VSJARHUCPX5
import twilio
from twilio.rest import Client

account_sid = 'AC1cb1d405e6378800190e5799b01df393'
auth_token = '6b78d430ef80f6ab20d7e7184f16b8f6'
client = Client(account_sid, auth_token)


def send_sms_notification(phone_number, message):
    try:
        message = client.messages.create(
            body=message,
            from_='+12153525406',
            to=phone_number
        )
        print(f"SMS sent successfully to {phone_number}: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
        
        
phone_number = '+6581382823'  # User's phone number
message = 'Hello from Vintage Car Bot! Your favorite car part is now available.'
send_sms_notification(phone_number, message)