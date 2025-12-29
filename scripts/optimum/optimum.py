import datetime
import uuid
from xml.dom import minidom
import getpass
import json
import requests
import os

from optimum.cable_box import Box
from optimum.content import Content, ScheduledContent, BestBet
from optimum.templates import base_url
from optimum import values
from optimum import utils
from optimum import errors


class API:
    def __init__(self,
                 optimum_ID=None,
                 password=None,
                 device_ID=None, # TODO get deviceID somehow, test
                 wifi_MAC=None,
                 device_type=None,
                 device_os=None,
                 user_agent=None):
        """


        :param optimum_ID: str
        :param password: str
        :param device_ID: str
        :param wifi_MAC: str
        :param device_type: str
        :param device_os: str
        :param user_agent: str
        """
        self.search_count = 1
        if not optimum_ID:
            raise errors.LoginError("No Optimum ID supplied")
        else:
            self.optimum_ID = optimum_ID
        if wifi_MAC:
            self.wifi_MAC = wifi_MAC
        else:
            self.wifi_MAC = str(uuid.uuid4())
        if device_type:
            self.device_type = device_type
        else:
            self.device_type = "mac"
        if device_os:
            self.device_os = device_os
        else:
            self.device_os = "10.9.5.0"
        if password:
            self.password = password
        else:
            self.password = getpass.getpass()
        if not device_ID:
            if os.path.exists("deviceID.txt"): # temp for easy testing w/o hardcoding my Device ID, sorry!
                with open("deviceID.txt", "r") as tmpfile:
                    self.device_ID = tmpfile.read()
            else:
                raise ValueError("No device_ID supplied")
        else:
            self.device_ID = device_ID
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko)"
        # send auth requests
        payload = {"request_type": "AUTHENTICATE",
                   "username": self.optimum_ID,
                   "password": self.password,
                   "deviceId": self.device_ID,
                   "version": "4.11",
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "WifiMAC": self.wifi_MAC,
                   "wifiRSSI": "NA"}
        auth_conn = requests.get(base_url.auth, params=payload)
        if auth_conn.status_code == 200:
            auth_xml = minidom.parseString(auth_conn.text)
            code = auth_xml.getElementsByTagName("Code")[0].childNodes[0].data
            if code != "0":
                message = auth_xml.getElementsByTagName("Message")[0].childNodes[0].data
                raise errors.LoginError(message)
            self.AuthToken = str(auth_xml.getElementsByTagName("AuthToken")[0].childNodes[0].data)
            self.device_ID = str(auth_xml.getElementsByTagName("DeviceId")[0].childNodes[0].data)
            self.home_ID = str(auth_xml.getElementsByTagName("HomeId")[0].childNodes[0].data)
            self.hub_ID = str(auth_xml.getElementsByTagName("HubId")[0].childNodes[0].data)
            self.enhanced_hub_ID = str(auth_xml.getElementsByTagName("EnhancedHubId")[0].childNodes[0].data)
            self.service_group_ID = str(auth_xml.getElementsByTagName("ServiceGroupId")[0].childNodes[0].data)
            self.corp = str(
                auth_xml.getElementsByTagName("Corp")[0].childNodes[0].data)  # first n digits of acct number!
            xml_boxes = auth_xml.getElementsByTagName("Boxes")[0].childNodes
            self.boxes = {}
            for box in xml_boxes:
                box_serial = str(box.childNodes[0].firstChild.data)
                box_name = str(box.childNodes[1].firstChild.data)
                box_resolution = str(box.childNodes[2].firstChild.data)
                box_type = str(box.childNodes[3].firstChild.data)
                box_space = self.getBoxFreeSpaceBySerial(box_serial)
                new_box = Box(box_name, box_serial, box_resolution, box_type, box_space)
                self.boxes[new_box.name] = new_box  # maybe these should be dict instead of objs
        elif auth_conn.status_code == 500:
            raise errors.LoginError("Couldn't Login!")

    def _genNetworkSettingsTimestamp(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f0-04:00")
        return timestamp

    def _validateKeypress(self, keys):
        """Validates a keypress list"""
        for key in keys:
            if key.upper() not in values.key_list:
                raise errors.ValidationError("Invalid Key: {}".format(key))
        return True

    def do_keypress(self, cable_box, keys, validate_keys=True):
        """Sends a series of keypresses [as a list] to a cable_box"""
        if validate_keys:
            self._validateKeypress(keys)
        keypress = ""
        for key in keys:
            keypress += key + ","
        keypress = keypress[:-1]  # strip last comma from string
        # print keypress
        payload = (("AuthToken", self.AuthToken),
                   ("optimum_id", self.optimum_ID),
                   ("deviceId", self.device_ID),
                   ("deviceType", self.device_type),
                   ("os", self.device_os),
                   ("homeId", self.home_ID),
                   ("hubId", self.hub_ID),
                   ("serialNumber", cable_box.serial),
                   ("keys", keypress),
                   ("wifiRSSI", "NA"),
                   ("TimeStamp", utils.genTimestamp()))
        conn = requests.get(base_url.keypress, params=payload)
        # print conn.url
        if conn.status_code == requests.codes.ok:
            return True
        else:
            return False

    def search(self,
               query=None,
               max_results=50,
               search_filter=None,
               stream_filter=False,
               return_xml=False):
        if not search_filter:
            final_filter = ""
        elif search_filter.upper() == "NOW":
            final_filter = "SynFilterNowNext"
        elif search_filter.upper() == "TV":
            final_filter = "SynFilterTV"
        elif search_filter.upper() == "HD":
            final_filter = "SyncFilterHD"
        else:
            final_filter = ""
        if stream_filter:
            if final_filter == "SynFilterTV" or final_filter == "":
                final_stream_filter = "stream"
            else:
                final_stream_filter = ""
        else:
            final_stream_filter = ""

        payload = {"XUN": self.device_ID,
                   "XUA": "cvpcmac",
                   "XPID": "pkg00@4.Cablevision",
                   "DS": "255",
                   "PN": "4",
                   "RPR": max_results,
                   "W": query,
                   "HID": self.home_ID,
                   "CC": self.search_count,
                   "os": "",
                   "FL": final_filter,
                   "PCL": final_stream_filter}
        conn = requests.get(base_url.search, params=payload)
        if conn.status_code == requests.codes.ok:
            self.search_count += 1
            test = conn.text.encode('ascii', 'xmlcharrefreplace')
            search_xml = minidom.parseString(test)
            channels = search_xml.getElementsByTagName("CI")
            content = []
            for channel in channels:
                name_string = ""
                name_tag = channel.getElementsByTagName("T")
                for tag in name_tag[0].childNodes:
                    if tag.childNodes:
                        name_string += tag.childNodes[0].data
                    else:
                        name_string += tag.data
                content_title = name_string
                content_type = channel.getElementsByTagName("TYP")[0].childNodes[0].data
                content_tags = []
                if channel.getElementsByTagName("EPT"):
                    name_string = ""
                    for element in channel.getElementsByTagName("EPT")[0].childNodes:
                        if element.childNodes:
                            name_string += element.childNodes[0].data
                        else:
                            name_string += element.data
                    episode_title = name_string
                else:
                    episode_title = None
                cast = []
                cast_node = channel.getElementsByTagName("C")
                for element in cast_node:
                    name_string = ""
                    name = element.getElementsByTagName("nm")
                    for child in name[0].childNodes:
                        if child.childNodes:
                            name_string += child.childNodes[0].data
                        else:
                            name_string += child.data
                    cast.append(name_string)
                for tag in channel.getElementsByTagName("GN"):
                    content_tags.append(str(tag.childNodes[0].data))
                attr_info = channel.getElementsByTagName("AI")[0]
                if channel.getElementsByTagName("ATTR"):
                    quals = channel.getElementsByTagName("ATTR")[0].childNodes[0].data
                else:
                    quals = None
                VOD_flag = attr_info.getElementsByTagName("ty")[0].childNodes[0].data
                if VOD_flag == "VOD":
                    continue
                channel_name = attr_info.getElementsByTagName("CS")[0].childNodes[0].data
                channel_number = attr_info.getElementsByTagName("VC")[0].childNodes[0].data
                tribune_ID = attr_info.getElementsByTagName("STID")[0].childNodes[0].data
                time_string_node = attr_info.getElementsByTagName("os")[0]
                if time_string_node.childNodes:
                    time_string = time_string_node.childNodes[0].data
                else:
                    time_string = None
                
                if channel.getElementsByTagName("L"):
                    language = channel.getElementsByTagName("L")[0].childNodes[0].data
                else:
                    language = None
                if channel.getElementsByTagName("RA"):
                    content_rating = channel.getElementsByTagName("RA")[0].childNodes[0].data
                else:
                    content_rating = None
                desc_string = ""
                if channel.getElementsByTagName("D"):
                    content_description = channel.getElementsByTagName("D")[0]
                    for desc in content_description.childNodes:
                        if desc.childNodes:
                            desc_string += desc.childNodes[0].data
                        else:
                            desc_string += desc.data

                else:
                    content_description = None
                new_content = Content(content_title,
                                      episode_title,
                                      content_type,
                                      desc_string,
                                      content_rating,
                                      content_tags,
                                      language,
                                      channel_name,
                                      channel_number,
                                      tribune_ID,
                                      time_string,
                                      cast,
                                      quals)
                content.append(new_content)
            return content

    def getDVRSettings(self):
        payload = {"request_type": "GET_DVR_SETTINGS",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "AuthToken": self.AuthToken,
                   "version":"4.11",
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "WifiMAC": self.wifi_MAC,
                   "wifiRSSI": "NA"}
        conn = requests.get(base_url.auth, params=payload)
        if conn.status_code == 200:
            dvr_xml = minidom.parseString(conn.text)
            code = dvr_xml.getElementsByTagName("Code")[0].childNodes[0].data
            if code != "0":
                message = dvr_xml.getElementsByTagName("Message")[0].childNodes[0].data
                raise ValueError("({}) {}".format(code, message))
            dvr_boxes = dvr_xml.getElementsByTagName("Box")
            self.boxes = {}
            for box in dvr_boxes:
                name = str(box.getElementsByTagName("Alias")[0].childNodes[0].data)
                serial = str(box.getElementsByTagName("SerialNumber")[0].childNodes[0].data)
                resolution = str(box.getElementsByTagName("BoxType")[0].childNodes[0].data)
                box_type = str(box.getElementsByTagName("DeviceType")[0].childNodes[0].data)
                new_box = Box(name, serial, resolution, box_type, "0") # Added dummy space
                self.boxes[name] = new_box
            return self.boxes

    def renameCableBox(self, cable_box, new_name):
        payload = {"request_type": "SET_ALIAS",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "wifiRSSI": "NA",
                   "box1": cable_box.serial + "|" + new_name}
        conn = requests.get(base_url.dvr_req, params=payload)
        if conn.status_code == requests.codes.ok and "SUCCESS" in conn.text:
            test = self.getDVRSettings()
            return self.boxes
        return False

    def getBoxFreeSpace(self, cable_box):
        payload = {"request_type": "GET_BOX_STORAGE",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "wifiRSSI": "NA",
                   "home_id": self.home_ID,
                   "serial_number": cable_box.serial,
                   "hubId": self.hub_ID}
        conn = requests.get(base_url.dvr_req, params=payload)
        if conn.status_code == 200:
            storage_xml = minidom.parseString(conn.text.strip())
            try:
                free_space = str(storage_xml.getElementsByTagName("FreeSpace")[0].childNodes[0].data)
                return free_space
            except IndexError:
                return False

    def getBoxFreeSpaceBySerial(self, serial_number):
        payload = {"request_type": "GET_BOX_STORAGE",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "wifiRSSI": "NA",
                   "home_id": self.home_ID,
                   "serial_number": serial_number,
                   "hubId": self.hub_ID}
        conn = requests.get(base_url.dvr_req, params=payload)
        if conn.status_code == 200:
            storage_xml = minidom.parseString(conn.text.strip())
            try:
                free_space = str(storage_xml.getElementsByTagName("FreeSpace")[0].childNodes[0].data)
                return free_space
            except IndexError:
                return False

    def getRecordedPrograms(self, cable_box):
        payload = {"request_type": "GET_RECORDED_PROGRAMS",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "home_id": self.home_ID,
                   "serial_number": cable_box.serial,
                   "hubId": self.hub_ID,
                   "wifiRSSI": "NA"}
        conn = requests.get(base_url.dvr_req, params=payload)
        if conn.status_code == 200:
            rec_data = json.loads(conn.text)
            code = rec_data['error'][0]['StatusCode']
            if code != 0:
                message = rec_data['error'][0]['StatusDescription']
                raise ValueError("({}) {}".format(code, message))
            return rec_data['result']['RecordedProgList']
        return False

    def getScheduledRecordings(self, cable_box):
        payload = {"request_type": "GET_SCHEDULED_RECORDINGS",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "home_id": self.home_ID,
                   "serial_number": cable_box.serial,
                   "hubId": self.hub_ID,
                   "wifiRSSI": "NA"}
        conn = requests.get(base_url.dvr_req, params=payload)
        if conn.status_code == 200:
            scheduled_data = json.loads(conn.text)
            code = scheduled_data['error'][0]['StatusCode']
            if code != 0:
                message = scheduled_data['error'][0]['StatusDescription']
                raise ValueError("({}) {}".format(code, message))
            content = []
            for program in scheduled_data['result']['SchProgMap']:
                elem = program['SchProgElement']
                prog = elem['Program']
                new_content = ScheduledContent(elem['Title'],
                                               elem['LongDescription'],
                                               prog['Genres'],
                                               prog['EndTime'],
                                               prog['TVRatings'],
                                               prog['TVSubRating'],
                                               prog['MPAARatings'],
                                               prog['CriticRating'],
                                               prog['ReleaseDate'],
                                               prog['callsign'],
                                               prog['ChannelNumber'],
                                               prog['StartTime'],
                                               prog['tribid'],
                                               prog.get('EpisodeTitle'),
                                               prog.get('EpisodeNumber'),
                                               prog.get('SeasonNumber'),
                                               prog['Qualifiers'],
                                               prog.get('Cast'))
                content.append(new_content)
            return content
        return False

    def requestSingleRecording(self,
                               cable_box,
                               content_obj,
                               stop_time,
                               save_days,
                               quality,
                               validate=True):
        start_time = utils.genRecordRequestTime(content_obj.start)
        show_end_time = utils.genRecordRequestTime(content_obj.end)
        end_time = utils.addSeconds(content_obj.end, stop_time)
        end_time = utils.genRecordRequestTime(end_time)
        payload = {"request_type": "REQUEST_RECORDING",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "wifiRSSI": "NA",
                   "home_id": self.home_ID,
                   "serial_number": cable_box.serial,
                   "hubId": self.hub_ID,
                   "rec_type": "0",
                   "channel_num": content_obj.channel_number,
                   "call_sign": content_obj.channel_name,
                   "start_time": start_time,
                   "end_time": end_time,
                   "showEndTime": show_end_time,
                   "saveDays": save_days,
                   "tribuneId": content_obj.tribune_ID,
                   "quality": quality}
        conn = requests.get(base_url.dvr_req, params=payload)
        return conn.status_code == 200

    def requestSeriesRecording(self,
                               cable_box,
                               content_obj,
                               stop_time,
                               save_days,
                               save_episodes,
                               all_episodes,
                               quality,
                               validate=True):
        start_time = utils.genRecordRequestTime(content_obj.start)
        show_end_time = utils.genRecordRequestTime(content_obj.end)
        end_time = utils.addSeconds(content_obj.end, stop_time)
        end_time = utils.genRecordRequestTime(end_time)
        payload = {"request_type": "REQUEST_RECORDING",
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "wifiRSSI": "NA",
                   "home_id": self.home_ID,
                   "serial_number": cable_box.serial,
                   "hubId": self.hub_ID,
                   "rec_type": "0",
                   "channel_num": content_obj.channel_number,
                   "call_sign": content_obj.channel_name,
                   "start_time": start_time,
                   "end_time": end_time,
                   "showEndTime": show_end_time,
                   "saveDays": save_days,
                   "tribuneId": content_obj.tribune_ID,
                   "save_episodes": save_episodes,
                   "all_episodes": all_episodes,
                   "quality": quality}
        conn = requests.get(base_url.dvr_req, params=payload)
        return conn.status_code == 200

    def eraseMultipleRecording(self,
                               cable_box,
                               content_obj,
                               is_recorded):
        callsign = content_obj.callsign
        channel_number = content_obj.channel_number
        start = utils.genRecordRequestTime(content_obj.start_time)
        end = utils.genRecordRequestTime(content_obj.end_time)
        payload = {"request_type": "ERASE_MULTIPLE_RECORDING",
                   "optimum_id": self.optimum_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "wifiRSSI": "NA",
                   "home_id": self.home_ID,
                   "serial_number": cable_box.serial,
                   "hubId": self.hub_ID,
                   "isRecorded": is_recorded,
                   "program1": callsign+"|"+channel_number+"|"+start+"|"+end}
        conn = requests.get(base_url.dvr_req, params=payload)
        if conn.status_code == 200:
            xml_dom = minidom.parseString(conn.text)
            code = xml_dom.getElementsByTagName("Code")[0].childNodes[0].data
            if code != "0":
                message = xml_dom.getElementsByTagName("Message")[0].childNodes[0].data
                raise ValueError("({}) {}".format(code, message))
            return True
        return False

    def setNetworkSettingsSeries(self,
                                 series_playback=None,
                                 series_stop=None,
                                 series_save_latest=None,
                                 series_option=None,
                                 DVRPLUS_series_save=None,
                                 validate=True):
        if validate:
            self._validateNetworkSettings(series_playback=series_playback,
                                          series_stop=series_stop,
                                          series_save_latest=series_save_latest,
                                          series_option=series_option,
                                          DVRPLUS_series_save=DVRPLUS_series_save)
        
        # Determine path to template
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, 'templates', 'network_settings_series.xml')
        
        with open(template_path, 'r') as tmp_file:
            base_xml = tmp_file.read()
        send_xml = base_xml.format(self.optimum_ID,
                                   self.home_ID,
                                   self.device_ID,
                                   self.AuthToken,
                                   self.hub_ID,
                                   self.device_type,
                                   utils.formatXMLValue(series_playback),
                                   utils.formatXMLValue(series_stop),
                                   utils.formatXMLValue(series_save_latest),
                                   utils.formatXMLValue(series_option),
                                   utils.formatXMLValue(DVRPLUS_series_save))
        payload = {"optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "AuthToken": self.AuthToken,
                   "hubId": self.hub_ID,
                   "deviceType": self.device_type,
                   "wifiRSSI": "NA"}
        headers = self._addNetworkSettingHeaders(len(send_xml))
        conn = requests.post(base_url.set_settings,
                             headers=headers,
                             data=send_xml,
                             params=payload)
        if conn.status_code == 200:
            xml_dom = minidom.parseString(conn.text)
            code = xml_dom.getElementsByTagName("Code")[0].childNodes[0].data
            if code != "1":
                message = xml_dom.getElementsByTagName("Message")[0].childNodes[0].data
                raise ValueError("({}) {}".format(code, message))
            return True
        return False

    def setNetworkSettingsEpisode(self,
                                  episode_playback=None,
                                  episode_stop=None,
                                  DVRPLUS_episode_save=None,
                                  validate=True):
        if validate:
            self._validateNetworkSettings(episode_playback=episode_playback,
                                          episode_stop=episode_stop,
                                          DVRPLUS_episode_save=DVRPLUS_episode_save)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, 'templates', 'network_settings_episode.xml')

        with open(template_path, 'r') as tmp_file:
            base_xml = tmp_file.read()
        send_xml = base_xml.format(self.optimum_ID,
                                   self.home_ID,
                                   self.device_ID,
                                   self.AuthToken,
                                   self.hub_ID,
                                   self.device_type,
                                   utils.formatXMLValue(episode_playback),
                                   utils.formatXMLValue(episode_stop),
                                   utils.formatXMLValue(DVRPLUS_episode_save))
        payload = {"optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "AuthToken": self.AuthToken,
                   "hubId": self.hub_ID,
                   "deviceType": self.device_type,
                   "wifiRSSI": "NA"}
        headers = self._addNetworkSettingHeaders(len(send_xml))
        conn = requests.post(base_url.set_settings,
                             headers=headers,
                             data=send_xml,
                             params=payload)
        if conn.status_code == 200:
            xml_dom = minidom.parseString(conn.text)
            code = xml_dom.getElementsByTagName("Code")[0].childNodes[0].data
            if code != "1":
                message = xml_dom.getElementsByTagName("Message")[0].childNodes[0].data
                raise ValueError("({}) {}".format(code, message))
            return True
        return False

    def getNetworkSettings(self):
        payload = {"AuthToken": self.AuthToken,
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "homeId": self.home_ID,
                   "hubId": self.hub_ID,
                   "wifiRSSI": "NA",
                   "datetime": self._genNetworkSettingsTimestamp()}
        conn = requests.get(base_url.get_settings, params=payload)
        if conn.status_code == 200:
            xml_data = minidom.parseString(conn.text)
            settings_dict = {}
            for settings in xml_data.getElementsByTagName("settings"):
                setting_type = settings.getAttribute("type")
                settings_dict[setting_type] = {}
                settings_dict[setting_type]["values"] = {}
                for setting in settings.getElementsByTagName("setting"):
                    name = setting.getAttribute("name")
                    settings_dict[setting_type]["group"] = setting.getAttribute("group")
                    settings_dict[setting_type]["updated"] = setting.getAttribute("last_updated")
                    for setting_value in setting.getElementsByTagName("value"):
                        if setting_value.childNodes:
                            settings_dict[setting_type]["values"][name] = setting_value.childNodes[0].data
            return settings_dict
        return False

    def getMostWatched(self):
        payload = {"hubId": self.hub_ID,
                   "AuthToken": self.AuthToken,
                   "optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "wifiRSSI": "NA",
                   "TimeStamp": utils.genTimestamp()}
        conn = requests.get(base_url.most_watched, params=payload)
        if conn.status_code == 200:
            json_data = json.loads(conn.text)
            code = json_data['error'][0]['StatusCode']
            if code != 0:
                message = json_data['error'][0]['StatusDescription']
                raise ValueError("({}) {}".format(code, message))
            return json_data['result']
        return False

    def getBestBets(self):
        # This needs values.getDate() which might be in utils or I missed it
        date = datetime.datetime.now()
        start = date.strftime("%m/%d/%Y+20:00:00")
        end = date.strftime("%m/%d/%Y+23:00:00")
        payload = {"optimum_id": self.optimum_ID,
                   "deviceId": self.device_ID,
                   "deviceType": self.device_type,
                   "os": self.device_os,
                   "AuthToken": self.AuthToken,
                   "hubId": self.hub_ID,
                   "startTime": start,
                   "endTime": end,
                   "wifiRSSI": "NA"}
        conn = requests.get(base_url.best_bets, params=payload)
        if conn.status_code == 200:
            xml_dom = minidom.parseString(conn.text)
            blocks = xml_dom.getElementsByTagName("block")
            best_bets = []
            best_bets_objs = []
            for block in blocks:
                this_block = {}
                if block.getAttribute("class") == "core":
                    attributes = block.getElementsByTagName("classifier")
                    for attribute in attributes:
                        if attribute.childNodes:
                            this_block[attribute.getAttribute("type")] = attribute.childNodes[0].data
                    best_bets.append(this_block)
            for best_bet in best_bets:
                new_best_bet_obj = BestBet(best_bet.get("PositiveContent"),
                                           best_bet.get("ProgramTitle"),
                                           best_bet.get("ProgramId"),
                                           best_bet.get("PrgSvcId"),
                                           best_bet.get("FullPrgSvcName"),
                                           best_bet.get("EventID"),
                                           best_bet.get("AirDateTime"),
                                           best_bet.get("Duration"),
                                           best_bet.get("Language"),
                                           best_bet.get("Channelnumber"),
                                           best_bet.get("ProgramType"),
                                           best_bet.get("tvrating"),
                                           best_bet.get("mpaa"),
                                           best_bet.get("Callsign"),
                                           None)
                best_bets_objs.append(new_best_bet_obj)
            return best_bets_objs
        return False

    def _addNetworkSettingHeaders(self, content_length):
        payload = {"Device-Id": self.device_ID,
                   "Referer": "http://optimumapp.iptv.optimum.net/Optimum.xap",
                   "Home-Id": self.home_ID,
                   "Corp": self.corp,
                   "Content-Type": "text/xml",
                   "Connection": "keep-alive",
                   "Request-Id": "1",
                   "Service-Group-Id": self.service_group_ID,
                   "Proxy-Connection": "keep-alive",
                   "Content-Length": str(content_length),
                   "Accept-Encoding": "identity"}
        return payload

    def _validateNetworkSettings(self,
                                 series_playback=None,
                                 series_stop=None,
                                 series_save_latest=None,
                                 series_option=None,
                                 DVRPLUS_series_save=None,
                                 episode_playback=None,
                                 episode_stop=None,
                                 episode_save=None,
                                 DVRPLUS_episode_save=None):
        if series_playback: assert series_playback in values.networkSettingValues["SERIES_PLAYBACK"]
        if series_stop: assert series_stop in values.networkSettingValues["SERIES_STOP"]
        if series_save_latest: assert series_save_latest in values.networkSettingValues["SERIES_SAVE_LATEST"]
        if series_option: assert series_option in values.networkSettingValues["SERIES_OPTION"]
        if DVRPLUS_series_save: assert DVRPLUS_series_save in values.networkSettingValues["DVRPLUS_SERIES_SAVE"]
        if episode_playback: assert episode_playback in values.networkSettingValues["EPISODE_PLAYBACK"]
        if episode_stop: assert episode_stop in values.networkSettingValues["EPISODE_STOP"]
        if DVRPLUS_episode_save: assert DVRPLUS_episode_save in values.networkSettingValues["DVRPLUS_EPISODE_SAVE"]
        return True
