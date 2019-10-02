import requests
import json
import time
import urllib
import uuid
import os
import random
import getpass
import sys

class notion_api():
    def __init__(self,token = ''):
        self.USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        self.session  = requests.Session()
        self.session.cookies['token_v2'] = token
    def to_notion_uid(self,s):
        s = s[:8] + '-' + s[8:12] + '-' + s[12:16] + '-' + s[16:20] + '-' + s[20:]
        return s
    def getRecordValues(self,request_content):
        API_URL = 'https://www.notion.so/api/v3/getRecordValues'
        #form_data = json.loads('{"collectionId":"6566fb1f-6df1-4bb3-b5d4-17dc7736dc15","collectionViewId":"906231bd-65dd-4044-8f99-886fc8de465d","query":{"sort":[{"id":"2185123c-d38b-4f85-9f3d-3c0136d7b593","type":"date","property":"]=/L","direction":"ascending"}],"filter_operator":"and","filter":[],"aggregate":[]},"loader":{"type":"table","limit":70,"userTimeZone":"Asia/Taipei","userLocale":"en","loadContentCover":true}}')
        self.session.headers = {'user-agent' : self.USER_AGENT,'Content-type': 'application/json'}
        req = self.session.post(API_URL,json=request_content)
        return json.loads(req.text)
    def loadPageChunk(self,request_content):
        API_URL = 'https://www.notion.so/api/v3/loadPageChunk'
        #form_data = json.loads('{"collectionId":"6566fb1f-6df1-4bb3-b5d4-17dc7736dc15","collectionViewId":"906231bd-65dd-4044-8f99-886fc8de465d","query":{"sort":[{"id":"2185123c-d38b-4f85-9f3d-3c0136d7b593","type":"date","property":"]=/L","direction":"ascending"}],"filter_operator":"and","filter":[],"aggregate":[]},"loader":{"type":"table","limit":70,"userTimeZone":"Asia/Taipei","userLocale":"en","loadContentCover":true}}')
        self.session.headers = {'user-agent' : self.USER_AGENT,'Content-type': 'application/json'}
        req = self.session.post(API_URL,json=request_content)
        return json.loads(req.text)
    def get_page_collection_ID(self,pageID):
        form_data = json.loads('{"requests": [{"table": "block","id": "'+ pageID + '"}]}')
        r = self.getRecordValues(form_data)
        return r['results'][0]['value']['collection_id']

    def get_event(self,page_url,max_limit=70):
        #page_url_s = page_url.split('/')[-1]
        page_uid = page_url.split('/')[-1].split('?v=')[0]
        view_uid = page_url.split('/')[-1].split('?v=')[1]
        page_uid = self.to_notion_uid(page_uid)
        view_uid = self.to_notion_uid(view_uid)
        collection_uid = self.get_page_collection_ID(page_uid)

        print('page_uid = ',page_uid)
        print('view_uid = ',view_uid)
        print('collection_uid = ',collection_uid)
        
        API_URL = 'https://www.notion.so/api/v3/queryCollection'
        form_data = json.loads('{"collectionId":"' + collection_uid + '","collectionViewId":"' +  view_uid +'","query":{"sort":[{"id":"2185123c-d38b-4f85-9f3d-3c0136d7b593","type":"date","property":"]=/L","direction":"ascending"}],"filter_operator":"and","filter":[],"aggregate":[]},"loader":{"type":"table","limit":' + str(max_limit) + ',"userTimeZone":"Asia/Taipei","userLocale":"en","loadContentCover":true}}')
        self.session.headers = {'user-agent' : self.USER_AGENT,'Content-type': 'application/json'}
        req = self.session.post(API_URL,json=form_data)
        json_req = json.loads(req.text)

        #page_uid = 'da322135-7f35-4b12-8534-fe408f7fdefb'
        #view_uid = '906231bd-65dd-4044-8f99-886fc8de465d'
        #collection_uid = '6566fb1f-6df1-4bb3-b5d4-17dc7736dc15'

        return_data_package = {"properties" :[],"events" : []}

        properties_tag = json_req['recordMap']['collection_view'][view_uid]['value']['format']['list_properties']

        for p in properties_tag:
            #print(p)
            if p['visible']== True:
                _properties={"name":"","uid_tag":""}
                _properties["name"] = json_req['recordMap']['collection'][collection_uid]['value']['schema'][p['property']]['name']
                _properties["uid_tag"] = p['property']
                _properties["type"] = json_req['recordMap']['collection'][collection_uid]['value']['schema'][p['property']]['type']
                return_data_package['properties'].append(_properties)
                #print("get p = ",_properties["name"])
            
        #print(return_data_package['properties'])
        for item in json_req['result']['blockIds']:
            event_data = {"title":"","date":"","content":"","notion_content_id":"","google_cal_event_id":""}
            properties = json_req['recordMap']['block'][item]['value']['properties']
            _event={}
            for required_tag in return_data_package['properties']:
                _event['_name'] = properties['title'][0][0]
                if required_tag['uid_tag'] in properties.keys():
                    if required_tag['type'] == 'text':
                        _event[required_tag['name']] = properties[required_tag['uid_tag']][0][0]
                    elif required_tag['type'] == 'date':
                        _event[required_tag['name']] = properties[required_tag['uid_tag']][0][1][0][1]['start_date']
                    elif required_tag['type'] == 'select':
                        _event[required_tag['name']] = properties[required_tag['uid_tag']][0][0]
                _event['_link'] = page_url + '&p=' + item.replace('-','')
                return_data_package["events"].append(_event)
                
            
        return return_data_package
     

    def get_event_list(self):
        
        API_URL = 'https://www.notion.so/api/v3/queryCollection'
        form_data = json.loads('{"collectionId":"6566fb1f-6df1-4bb3-b5d4-17dc7736dc15","collectionViewId":"906231bd-65dd-4044-8f99-886fc8de465d","query":{"sort":[{"id":"2185123c-d38b-4f85-9f3d-3c0136d7b593","type":"date","property":"]=/L","direction":"ascending"}],"filter_operator":"and","filter":[],"aggregate":[]},"loader":{"type":"table","limit":70,"userTimeZone":"Asia/Taipei","userLocale":"en","loadContentCover":true}}')
        self.session.headers = {'user-agent' : self.USER_AGENT,'Content-type': 'application/json'}
        req = self.session.post(API_URL,json=form_data)
        json_req = json.loads(req.text)

        page_uid = 'da322135-7f35-4b12-8534-fe408f7fdefb'
        view_uid = '906231bd-65dd-4044-8f99-886fc8de465d'
        collection_uid = '6566fb1f-6df1-4bb3-b5d4-17dc7736dc15'

        data_tag_information={'date_property':{'name':'due day','uid_tag':''},
        'category_property':{'name':'Course Name','uid_tag':''},
        'content_property':{'name':'Task Content','uid_tag':''}}

        properties_tag = json_req['recordMap']['collection_view'][view_uid]['value']['format']['list_properties']

        for p in properties_tag:
            tag_name = json_req['recordMap']['collection'][collection_uid]['value']['schema'][p['property']]['name']
            if tag_name == data_tag_information['date_property']['name']:
                data_tag_information['date_property']['uid_tag'] = p['property']
            elif tag_name == data_tag_information['category_property']['name']:
                data_tag_information['category_property']['uid_tag'] = p['property']
            elif tag_name == data_tag_information['content_property']['name']:
                data_tag_information['content_property']['uid_tag'] = p['property']

        events_to_add={"events":[]}
        for item in json_req['result']['blockIds']:
            event_data = {"title":"","date":"","content":"","notion_content_id":"","google_cal_event_id":""}
            properties = json_req['recordMap']['block'][item]['value']['properties']
            #print(properties['title'][0][0])
            event_data['title'] = properties['title'][0][0]
            if data_tag_information['date_property']['uid_tag'] in properties:
                event_data['date'] = properties[data_tag_information['date_property']['uid_tag']][0][1][0][1]['start_date']
                if data_tag_information['category_property']['uid_tag'] in properties:
                    event_data['title'] = '[' + properties[data_tag_information['category_property']['uid_tag']][0][0]  + '] ' + event_data['title']
                if data_tag_information['content_property']['uid_tag'] in properties:
                    event_data['content'] = properties[data_tag_information['content_property']['uid_tag']][0][0] 
                
                event_data['content'] = event_data['content'] + '\n' + 'Link: https://www.notion.so/da3221357f354b128534fe408f7fdefb?v=2115b96ea09941658fedd1095843e652&p=' + item.replace('-','')
                event_data['notion_content_id'] = item
                
                events_to_add['events'].append(event_data)
                print(event_data['title'])
            else:
                continue
        return events_to_add
     
