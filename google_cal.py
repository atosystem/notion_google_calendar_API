from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import pickle
import json
import os.path

class google_cal_api():
    def __init__(self,need_generate=False,myCalid=""):
        if need_generate or (not os.path.exists("token.pkl")):
            self.get_credentials()
        self.load_credentials()
        self.current_cal_id = myCalid
    def get_credentials(self):
        scopes = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
        credentials = flow.run_console()
        pickle.dump(credentials, open("token.pkl", "wb"))

    def load_credentials(self):
        self.credentials = pickle.load(open("token.pkl", "rb"))
        self.service = build("calendar", "v3", credentials=self.credentials)
    def insert_calendar(self,summary,return_json=False):
        calendar = {
            'summary': summary
        }
        created_calendar = self.service.calendars().insert(body=calendar).execute()
        #print created_calendar['id']
        self.current_cal_id = created_calendar['id']
        if return_json:
            return created_calendar
    def delete_calendar(self):
        if self.current_cal_id =="":
            return False
        self.service.calendars().delete(calendarId=self.current_cal_id ).execute()
        self.current_cal_id =""
        return True
    def insert_event(self,calendar_event_entry=-1):
        if self.current_cal_id =="":
            return False
        if(calendar_event_entry==-1):
            return False
            '''
            calendar_event_entry = {
                "end": {
                    "date": str("")
                },
                "start": {
                    "date": str("")
                },
                "summary": str(""),
                "description": str("")
            }
            '''
        calendar_event_entry = self.service.events().insert(calendarId=self.current_cal_id , body=calendar_event_entry).execute()
        return calendar_event_entry.get('id')
    def update_event(self,event_Id,calendar_event_entry):
        if self.current_cal_id =="":
            return False
        updated_event = self.service.events().update(calendarId=self.current_cal_id , eventId=event_Id, body=calendar_event_entry).execute()
    def get_event(self,event_Id):
        if self.current_cal_id =="":
            return False
        event = self.service.events().get(calendarId=self.current_cal_id, eventId=event_Id).execute()
        return event
