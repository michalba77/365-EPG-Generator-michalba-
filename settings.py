# Nastavení
VERZE = "v3.02.0"

# Počet dní (1-15)
days = 1

# Počet dní zpětně (0-7)
days_back = 0

# Výběr zdroje kanálů
# 1 = povolit
# 0 = zakázat
TV_SMS_CZ = 1
T_MOBILE_TV_GO = 1
MAGIO_GO = 1

# Generování přehledového textového souboru epg_info.txt
# 1 = povolit
# 0 = zakázat
EPG_INFO_GEN = 0


# Seznam vlastních kanálů
# Seznam id kanálů oddělené čárkou (např.: "2,3,32,94")
# Pro všechny kanály ponechte prázdné
TV_SMS_CZ_IDS = "1,2"
T_MOBILE_TV_GO_IDS = "4454"
MAGIO_GO_IDS = "4239,4507"




# název souboru
file_name = "epg.xml"

#Nahrát EPG na ftp server
#Ano = 1
#Ne = 0
ftp_upload = 0
ftp_server = ""
ftp_port = 21
ftp_login = ""
ftp_password = ""
ftp_folder = "/"

#Auto aktualizace
#Ano = 1
#Ne = 0
update = 0
#Každých x hodin
interval = 24