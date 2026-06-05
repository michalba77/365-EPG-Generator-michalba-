# -*- coding: utf-8 -*-

#v3.01.2

import logging
logging.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
try:
    import sys
    import os
    import xmltv
    import epg_info
    import requests
    import xml.etree.ElementTree as ET
    import unicodedata
    import time
    from urllib.parse import quote
    from datetime import datetime, timedelta, date
    from ftplib import FTP
    import time
    import schedule
    from bs4 import BeautifulSoup
    from settings import*
    
except Exception as ex:
    print(ex)
    logging.error("365 EPG Generator - %s" % ex)
    input("Pro ukončení stiskněte libovolnou klávesu")
    sys.exit(0)


dn = os.path.dirname(os.path.realpath(__file__))
fn = os.path.join(dn,file_name)
custom_names_path = os.path.join(dn,"custom_names.txt")
now = datetime.now()
local_now = now.astimezone()
TS = " " + str(local_now)[-6:].replace(":", "")


def encode(string):
    string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'), "utf-8")
    return string


custom_names = []
try:
    f = open(custom_names_path, "r", encoding="utf-8").read().splitlines()
    for x in f:
        x = x.split("=")
        custom_names.append((x[0], x[1]))
except:
    pass


def replace_names(value):
    for v in custom_names:
        if v[0] == value:
            value = v[1]
    return value


def get_tm_programmes(tm_ids, d, d_b, lng):
    if d > 10:
        d = 10
    if lng == "cz":
        prfx = "tm-"
    else:
        prfx = "mag-"
        
    tm_ids_list = tm_ids.split(",")
    programmes2 = []
    
    params = {"dsid": "c75536831e9bdc93", "deviceName": "Xiaomi Mi 11", "deviceType": "OTT_STB", "osVersion": "13", "appVersion": "3.7.0", "language": lng.upper()}
    headers = {"Host": lng + "go.magio.tv", "authorization": "Bearer", "User-Agent": "okhttp/3.12.12", "content-type":  "application/json", "Connection": "Keep-Alive"}
    req = requests.post("https://" + lng + "go.magio.tv/v2/auth/init", params=params, headers=headers, verify=True).json()
    token = req["token"]["accessToken"]
    
    headers2 = {"Host": lng + "go.magio.tv", "authorization": "Bearer " + token, "User-Agent": "okhttp/5.3.2", "content-type":  "application/json"}
    
    req1 = requests.get("https://" + lng + "go.magio.tv/v2/television/channels?list=LIVE&queryScope=LIVE", headers=headers2).json()["items"]
    
    channels2 = []
    tvch = {}
    active_channel_ids = []
    
    for y in req1:
        id = str(y["channel"]["channelId"])
        if tm_ids_list == [""] or id in tm_ids_list:
            active_channel_ids.append(id)
            name = y["channel"]["name"]
            logo = str(y["channel"]["logoUrl"])
            
            chan_xml_id = prfx + id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-")
            tvch[name] = chan_xml_id
            
            if tm_ids_list == [""]:
                channels2.append(({"display-name": [(replace_names(name.replace(" HD", "")), u"cs")], "id": chan_xml_id, "icon": [{"src": logo}]}))
            else:
                channels2.append(({"display-name": [(name.replace(" HD", ""), u"cs")], "id": chan_xml_id, "icon": [{"src": logo}]}))

    now = datetime.now()
    for i in range(d_b * -1, d):
        next_day = now + timedelta(days = i)
        back_day = (now + timedelta(days = i)) - timedelta(days = 1)
        date_to = next_day.strftime("%Y-%m-%d")
        date_from = back_day.strftime("%Y-%m-%d")
        date_ = next_day.strftime("%d.%m.%Y")
        print(f"Stahuji program pro den: {date_}")
        
        for ch_id in active_channel_ids:
            try:
                url = "https://" + lng + "go.magio.tv/v2/television/epg?filter=channel.id=in=(" + ch_id + ");endTime=ge=" + date_from + "T23:00:00.000Z;startTime=le=" + date_to + "T23:59:59.999Z&limit=150&offset=0&lang=" + lng.upper()
                req_data = requests.get(url, headers=headers2).json().get("items", [])
                
                time.sleep(0.05)
                
                for x in range(0, len(req_data)):
                    for y in req_data[x]["programs"]:
                        channel = y["channel"]["name"]
                        start_time = y["startTime"].replace("-", "").replace("T", "").replace(":", "")
                        stop_time = y["endTime"].replace("-", "").replace("T", "").replace(":", "")
                        title = y["program"]["title"]
                        desc = y["program"]["description"]
                        epi = y["program"]["programValue"]["episodeId"]
                        if epi != None:
                            title = title + " (" + epi + ")"
                        year = y["program"]["programValue"]["creationYear"]
                        try:
                            subgenre = y["program"]["programCategory"]["subCategories"][0]["desc"]
                        except:
                            subgenre = ''
                        try:
                            genre = [(y["program"]["programCategory"]["desc"], u''), (subgenre, u'')]
                        except:
                            genre = None
                        try:
                            icon = y["program"]["images"][0]
                        except:
                            icon = None
                        try:
                            directors = []
                            for dr in y["program"]["programRole"]["directors"]:
                                directors.append(dr["fullName"])
                        except:
                            directors = []
                        try:
                            actors = []
                            for ac in y["program"]["programRole"]["actors"]:
                                actors.append(ac["fullName"])
                        except:
                            actors = []
                        try:
                            programm = {'channel': tvch[channel], 'start': start_time + TS, 'stop': stop_time + TS, 'title': [(title, u'')], 'desc': [(desc, u'')]}
                            if year != None:
                                programm['date'] = year
                            if genre != None:
                                programm['category'] = genre
                            if icon != None:
                                programm['icon'] = [{"src": icon}]
                            if directors != []:
                                programm['credits'] = {"director": directors}
                                if actors != []:
                                    programm['credits'] = {"director": directors, "actor": actors}
                            if actors != []:
                                programm['credits'] = {"actor": actors}
                                if directors != []:
                                    programm['credits'] = {"actor": actors, "director": directors}
                            if programm not in programmes2:
                                programmes2.append(programm)
                        except:
                            pass
            except Exception as e:
                continue
                
        print(date_ + "  OK")
    print("\n")
    return channels2, programmes2




class Get_channels_sms:

    def __init__(self):
        self.channels = []
        headers = {"user-agent": "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"}
        self.html = requests.get("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ", headers = headers).text
        self.ch = {}

    def all_channels(self):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                try:
                    icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                except:
                    icon = ""
                self.channels.append({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
            self.f.close()
        except:
            pass
        return self.ch, self.channels

    def cz_sk_channels(self):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                if i.find("p").text == "České" or i.find("p").text == "Slovenské":
                    self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                    try:
                        icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                    except:
                        icon = ""
                    self.channels.append({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch, self.channels

    def own_channels(self, cchc):
        try:
            root = ET.fromstring(self.html)
            cchc = cchc.split(",")
            for i in root.iter("a"):
                if i.attrib["id"] in cchc:
                    self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                    try:
                        icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                    except:
                        icon = ""
                    self.channels.append({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch, self.channels


class Get_programmes_sms:

    def __init__(self, days_back, days):
        self.programmes_sms = []
        self.days_back = days_back
        self.days = days

    def data_programmes(self, ch):
        if ch != {}:
            chl = ",".join(ch.keys())
            now = datetime.now()
            for i in range(self.days_back*-1, self.days):
                next_day = now + timedelta(days = i)
                date = next_day.strftime("%Y-%m-%d")
                date_ = next_day.strftime("%d.%m.%Y")
                print(f"Stahuji program pro den: {date_}")
                headers = {"user-agent": "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"}
                print(date_)
                html = requests.get("http://programandroid.365dni.cz/android/v6-program.php?datum=" + date + "&id_tv=" + chl, headers = headers).text
                root = ET.fromstring(html)
                root[:] = sorted(root, key=lambda child: (child.tag,child.get("o")))
                for i in root.iter("p"):
                    n = i.find("n").text
                    try:
                        k = i.find("k").text
                    except:
                        k = ""
                    if i.attrib["id_tv"] in ch:
                        self.programmes_sms.append({"channel": ch[i.attrib["id_tv"]].replace("804-ct-art", "805-ct-:d"), "start": i.attrib["o"].replace("-", "").replace(":", "").replace(" ", "") + TS, "stop": i.attrib["d"].replace("-", "").replace(":", "").replace(" ", "") + TS, "title": [(n, "")], "desc": [(k, "")]})
                sys.stdout.write('\x1b[1A')
                print(date_ + "  OK")
                time.sleep(0.5)
        print("\n")
        return self.programmes_sms


def main():
    os.system('cls||clear')
    channels = []
    programmes = []
    cchc = ""
    tm_id = ""
    print("365 EPG Generator(michalba) ver." + str(VERZE) + "\n")
    if TV_SMS_CZ == 1:
        try:
            print("TV.SMS.cz kanály")
            print("Stahuji data...")
            g = Get_channels_sms()
            if TV_SMS_CZ_IDS == "":
                ch, channels_sms = g.all_channels()
            else:
                ch, channels_sms = g.own_channels(TV_SMS_CZ_IDS)
            channels.extend(channels_sms)
            gg = Get_programmes_sms(days_back, days)
            programmes_sms = gg.data_programmes(ch)
            programmes.extend(programmes_sms)
        except Exception as ex:
            print("Chyba\n")
            logging.error("TV.SMS.cz kanály - %s" % ex)
    if T_MOBILE_TV_GO == 1:
        try:
            print("T-Mobile TV Go kanály")
            print("Stahuji data...")
            if T_MOBILE_TV_GO_IDS == "":
                tm_id = ""
            else:
                tm_id = T_MOBILE_TV_GO_IDS
            channels_tm, programmes_tm = get_tm_programmes(tm_id, days, days_back, "cz")
            channels.extend(channels_tm)
            programmes.extend(programmes_tm)
        except Exception as ex:
            print("Chyba\n")
            logging.error("T-Mobile TV Go kanály - %s" % ex)
    if MAGIO_GO == 1:
        try:
            print("Magio Go kanály")
            print("Stahuji data...")
            if MAGIO_GO_IDS == "":
                mag_id = ""
            else:
                mag_id = MAGIO_GO_IDS
            channels_mag, programmes_mag = get_tm_programmes(mag_id, days, days_back, "sk")
            channels.extend(channels_mag)
            programmes.extend(programmes_mag)
        except Exception as ex:
            print("Chyba\n")
            logging.error("Magio Go kanály - %s" % ex)
    if channels != []:
        print("Celkem kanálů: " + str(len(channels)))
        print("Generuji...")
        try:
            w = xmltv.Writer(encoding="utf-8", source_info_url="http://www.funktronics.ca/python-xmltv", source_info_name="Funktronics", generator_info_name="python-xmltv", generator_info_url="http://www.funktronics.ca/python-xmltv")
            for c in channels:
                w.addChannel(c)
            for p in programmes:
                w.addProgramme(p)
            w.write(fn, pretty_print=True)


            if EPG_INFO_GEN == 1:
                epg_info.generuj_prehled(channels, dn)
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')

            now = datetime.now()
            dt = now.strftime("%d.%m.%Y %H:%M")

            if ftp_upload == 1:
                try:
                    ftp = FTP()
                    ftp.set_debuglevel(2)
                    ftp.connect(ftp_server, ftp_port)
                    ftp.login(ftp_login, ftp_password)
                    ftp.cwd(ftp_folder)
                    file = open(fn, "rb")
                    ftp.storbinary('STOR ' + file_name, file)
                    file.close()
                    ftp.quit()
                except Exception as ex:
                    print("Chyba\n")
                    logging.error("FTP - %s" % ex)
            if update == 1:
                print("\n\nHotovo (" + dt + ")\n\n")
            else:
                print("Hotovo\n\n")
                input("Pro ukončení stiskněte libovolnou klávesu")
                sys.exit(0)
        except Exception as ex:
            sys.stdout.write('\x1b[1A')
            print("Chyba\n")
            logging.error("xmltv.Writer - %s" % ex)

    else:
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
        print("Žádné kanály\n\n")


if __name__ == "__main__":
    main()
    try:
        schedule.every(interval).hours.do(main)
        while update:
            schedule.run_pending()
            time.sleep(1)
    except Exception as ex:
        print(ex)
