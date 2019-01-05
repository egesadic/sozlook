import sozlook
import sozlook_kadinlarkulubu
import time

def auto_fetch(baslik):
    sozlook.get_topic(baslik)
    plist = sozlook.parse_all_entries(baslik)
    sozlook.save_entries(plist)
    sozlook.to_excel(plist, baslik)
    print("Tamamlandı: " + baslik)
    del plist

def local_fetch(baslik):
    f = sozlook.load_entries(baslik+"-entrybase")
    return f
   
plist = sozlook_kadinlarkulubu.kadinlarkulubu_search("tampon")
sozlook.to_excel(plist, "tampon")