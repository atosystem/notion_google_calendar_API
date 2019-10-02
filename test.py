import notion_api as nta;
import google_cal as gc

obj_nta = nta.notion_api()


#return a dict
event_get = obj_nta.get_event('https://www.notion.so/da3221357f354b128534fe408f7fdefb?v=906231bd65dd40448f99886fc8de465d')

obj_gc = gc.google_cal_api()

#create a calendar
obj_gc.insert_calendar('Notion')

calendar_event_entry = {
        "end": {
            "date": "2019-10-1"
        },
        "start": {
            "date": "2019-10-1"
        },
        "summary": "the summary",
        "description": "the description..."
    }

#create event and return event id
obj_gc.insert_event(calendar_event_entry)