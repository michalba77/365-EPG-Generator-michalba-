# -*- coding: utf-8 -*-
import os
import logging

def generuj_prehled(channels, dn):
    try:
        print("Generuji přehledový soubor epg_info.txt...")
        info_path = os.path.join(dn, "epg_info.txt")
        
        sms_channels = []
        magenta_channels = []
        magio_channels = []
        
        for ch in channels:
            xmltv_id = ch.get("id", "")
            if xmltv_id.startswith("tm-"):
                magenta_channels.append(ch)
            elif xmltv_id.startswith("mag-"):
                magio_channels.append(ch)
            else:
                sms_channels.append(ch)
        
        def get_clean_name(ch_obj):
            try:
                raw_name = ch_obj.get("display-name", [("", "")])
                if isinstance(raw_name, list) and len(raw_name) > 0:
                    return str(raw_name[0][0])
                return str(raw_name)
            except:
                return "Neznamy"

        sms_channels = sorted(sms_channels, key=lambda x: get_clean_name(x).lower())
        magenta_channels = sorted(magenta_channels, key=lambda x: get_clean_name(x).lower())
        magio_channels = sorted(magio_channels, key=lambda x: get_clean_name(x).lower())

        with open(info_path, "w", encoding="utf-8") as f_info:
            
            # --- SMS.CZ ---
            if sms_channels:
                f_info.write("=== SMS.cz ===\n\n")
                for ch in sms_channels:
                    clean_n = get_clean_name(ch)
                    xmltv_id = ch.get("id", "")
                    parts = xmltv_id.split("-")
                    raw_id = parts[0] if len(parts) > 0 else xmltv_id
                    
                    f_info.write(f'     tvg-name="{clean_n}",{clean_n}\n')
                    f_info.write(f'     tvg-id="{xmltv_id}"\n')
                    f_info.write(f'     IDS : "{raw_id}"\n\n')
                    
            # --- MAGENTA ---
            if magenta_channels:
                f_info.write("=== Magenta TV ===\n\n")
                for ch in magenta_channels:
                    clean_n = get_clean_name(ch)
                    xmltv_id = ch.get("id", "")
                    parts = xmltv_id.split("-")
                    raw_id = parts[1] if len(parts) > 1 else xmltv_id
                    
                    f_info.write(f'     tvg-name="{clean_n}",{clean_n}\n')
                    f_info.write(f'     tvg-id="{xmltv_id}"\n')
                    f_info.write(f'     IDS : "{raw_id}"\n\n')

            # --- MAGIO ---
            if magio_channels:
                f_info.write("=== Magio TV ===\n\n")
                for ch in magio_channels:
                    clean_n = get_clean_name(ch)
                    xmltv_id = ch.get("id", "")
                    parts = xmltv_id.split("-")
                    raw_id = parts[1] if len(parts) > 1 else xmltv_id
                    
                    f_info.write(f'     tvg-name="{clean_n}",{clean_n}\n')
                    f_info.write(f'     tvg-id="{xmltv_id}"\n')
                    f_info.write(f'     IDS : "{raw_id}"\n\n')
            f_info.close()        
        print("Soubor epg_info.txt byl úspěšně vytvořen.")
    except Exception as info_ex:
        print("Chyba při tvorbě epg_info.txt")
        logging.error("epg_info.txt - %s" % info_ex)
