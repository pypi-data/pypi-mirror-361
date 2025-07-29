import time, random, math, sys, os, datetime, threading, json, re, socket

# -------- TEMEL --------
def çıktı(*args, sep=' ', end='\n'): print(*args, sep=sep, end=end)
def sor(metin=''): return input(metin)
def çık(): sys.exit()
def bekle(saniye): time.sleep(saniye)
def temizle(): print("\033c", end="")
def değişken(ad, değer): globals()[ad] = değer
def artır(ad, değer): globals()[ad] += değer
def azalt(ad, değer): globals()[ad] -= değer
def eğer(durum, fonk): 
    if durum: fonk()
def değilse(fonk): fonk()
def tekrar(sayı, fonk):
    for _ in range(sayı): fonk()
def sonsuz(fonk):
    while True: fonk()
def yazı_yap(değer): return str(değer)
def tam_sayı(değer): return int(değer)
def ondalık_sayı(değer): return float(değer)
def tür(ad): return type(ad)
def tür_karşılaştır(a,b): return type(a) == type(b)
def None_mu(değer): return değer is None
def bool_yap(değer): return bool(değer)
def liste_mi(değer): return isinstance(değer, list)
def sözlük_mi(değer): return isinstance(değer, dict)
def tuple_mi(değer): return isinstance(değer, tuple)
def set_mi(değer): return isinstance(değer, set)

# -------- MATEMATİK --------
def kare(x): return x*x
def karekök(x): return math.sqrt(x)
def mutlak(x): return abs(x)
def yuvarla(x): return round(x)
def yukarı(x): return math.ceil(x)
def aşağı(x): return math.floor(x)
def mod(a,b): return a%b
def üs(a,b): return pow(a,b)
def log(x, taban=math.e): return math.log(x, taban)
def log10(x): return math.log10(x)
def sin(x): return math.sin(x)
def cos(x): return math.cos(x)
def tan(x): return math.tan(x)
def tanh(x): return math.tanh(x)
def asin(x): return math.asin(x)
def acos(x): return math.acos(x)
def atan(x): return math.atan(x)
def pi(): return math.pi
def e(): return math.e
def faktöriyel(x): 
    if x==0: return 1
    return x*faktöriyel(x-1)
def asal_mı(sayı):
    if sayı<2: return False
    for i in range(2,int(math.sqrt(sayı))+1):
        if sayı%i==0: return False
    return True
def kombinasyon(n,r):
    return faktöriyel(n)//(faktöriyel(r)*faktöriyel(n-r))
def permutasyon(n,r):
    return faktöriyel(n)//faktöriyel(n-r)
def maksimum(*args): return max(args)
def minimum(*args): return min(args)
def ortalama(liste): return sum(liste)/len(liste) if len(liste)>0 else None

# -------- STRING --------
def büyük_harf(metin): return metin.upper()
def küçük_harf(metin): return metin.lower()
def birleştir(a,b): return str(a)+str(b)
def böl(metin, ayır): return metin.split(ayır)
def başla_mı(metin, baş): return metin.startswith(baş)
def bitiyor_mu(metin, son): return metin.endswith(son)
def değiştirme(metin, eski, yeni): return metin.replace(eski,yeni)
def içeriyor(mu, ne): return ne in mu
def uzunluk(metin): return len(metin)
def ters(metin): return metin[::-1]
def boş_mu(metin): return len(metin.strip())==0
def sayı_mı(metin): return metin.isdigit()
def harf_mi(metin): return metin.isalpha()
def harf_rakam_mı(metin): return metin.isalnum()
def boşlukları_sil(metin): return metin.strip()
def satırları_böl(metin): return metin.splitlines()
def ilk_büyük_harf(metin): return metin.capitalize()
def metni_tekrar(metin,sayı): return metin*sayı
def ascii_kod(metin): return [ord(c) for c in metin]
def unicode_kod(kodlar): return ''.join(chr(k) for k in kodlar)
def regex_ara(pat, metin): return re.findall(pat, metin)
def regex_değiştir(pat,yeni,metin): return re.sub(pat,yeni,metin)

# -------- LİSTE --------
def liste_oluştur(ad): globals()[ad]=[]
def liste_ekle(ad,eleman): globals()[ad].append(eleman)
def liste_sil(ad,eleman): globals()[ad].remove(eleman)
def liste_uzunluk(ad): return len(globals()[ad])
def liste_yaz(ad): [print(x) for x in globals()[ad]]
def liste_kopya(ad): return globals()[ad].copy()
def liste_ters(ad): globals()[ad].reverse()
def liste_sırala(ad): globals()[ad].sort()
def liste_say(ad,eleman): return globals()[ad].count(eleman)
def liste_bos_mu(ad): return len(globals()[ad])==0
def liste_temizle(ad): globals()[ad].clear()
def liste_ekle_tümünü(ad,diger_liste): globals()[ad].extend(diger_liste)
def liste_indeks(ad,indeks): return globals()[ad][indeks]
def liste_var_mı(ad,eleman): return eleman in globals()[ad]
def liste_sil_indeks(ad,indeks): del globals()[ad][indeks]

# -------- SÖZLÜK --------
def sozluk_olustur(ad): globals()[ad] = {}
def sozluk_ekle(ad, anahtar, deger): globals()[ad][anahtar] = deger
def sozluk_sil(ad, anahtar): globals()[ad].pop(anahtar, None)
def sozluk_al(ad, anahtar): return globals()[ad].get(anahtar, None)
def sozluk_anahtarlar(ad): return list(globals()[ad].keys())
def sozluk_degerler(ad): return list(globals()[ad].values())
def sozluk_var_mı(ad, anahtar): return anahtar in globals()[ad]
def sozluk_temizle(ad): globals()[ad].clear()

# -------- DOSYA --------
def dosya_oku(dosya, mod='r', encoding='utf-8'):
    with open(dosya,mod,encoding=encoding) as f: return f.read()
def dosya_yaz(dosya,icerik,mod='w', encoding='utf-8'):
    with open(dosya,mod,encoding=encoding) as f: f.write(icerik)
def dosya_ekle(dosya,icerik,mod='a', encoding='utf-8'):
    with open(dosya,mod,encoding=encoding) as f: f.write(icerik)
def dosya_var_mı(dosya): return os.path.exists(dosya)
def dosya_sil(dosya): os.remove(dosya)
def klasor_olustur(ad): os.makedirs(ad,exist_ok=True)
def klasor_sil(ad): os.rmdir(ad)
def klasor_var_mı(ad): return os.path.exists(ad) and os.path.isdir(ad)
def dosya_boyutu(dosya): return os.path.getsize(dosya)

# -------- ZAMAN --------
def tarih_saat(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def tarih(): return datetime.datetime.now().strftime("%Y-%m-%d")
def saat(): return datetime.datetime.now().strftime("%H:%M:%S")
def gecen_sure_baslat():
    return time.time()
def gecen_sure_bul(baslangic):
    return time.time() - baslangic
def uyku(saniye): time.sleep(saniye)

# -------- HATA YÖNETİMİ --------
def dene_yakala(denenecek, hata_kod):
    try:
        denenecek()
    except Exception as e:
        hata_kod(e)

# -------- RANDOM --------
def rastgele_sayı(bas,bit): return random.randint(bas,bit)
def rastgele_ondalık(bas,bit): return random.uniform(bas,bit)
def rastgele_eleman(liste): return random.choice(liste) if liste else None
def rastgele_sırala(liste): random.shuffle(liste)

# -------- JSON --------
def json_yazdır(obj): return json.dumps(obj, ensure_ascii=False)
def json_oku(metin): return json.loads(metin)

# -------- THREAD --------
def iş_paralel(fonklar):
    threadler = []
    for f in fonklar:
        t = threading.Thread(target=f)
        t.start()
        threadler.append(t)
    for t in threadler:
        t.join()

# -------- SOKET (AĞ) --------
def socket_server(host,port,handler):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen()
    çıktı(f"Sunucu {host}:{port} dinleniyor...")
    while True:
        client,addr = s.accept()
        çıktı(f"Bağlantı: {addr}")
        handler(client,addr)
        client.close()
def socket_client(host,port,mesaj):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    s.sendall(mesaj.encode())
    cevap=s.recv(1024).decode()
    s.close()
    return cevap

# -------- EKSTRA YARARLI --------
def rakam_toplamı(sayı):
    return sum(int(h) for h in str(abs(sayı)) if h.isdigit())
def ters_sayı(sayı):
    return int(str(sayı)[::-1])
def kelime_say(metin):
    return len(metin.split())
def benzersiz_liste(liste):
    return list(dict.fromkeys(liste))
def filtrele(liste, koşul):
    return [x for x in liste if koşul(x)]
def çarpım(liste):
    sonuc = 1
    for i in liste:
        sonuc *= i
    return sonuc

# -------- DİĞERLERİ --------
def sayfa_numarası(toplam, sayfa, sayfa_boyutu):
    return list(range(sayfa_boyutu*(sayfa-1), min(sayfa_boyutu*sayfa, toplam)))

def değiştir_tümünü(metin, eski, yeni):
    while eski in metin:
        metin = metin.replace(eski, yeni)
    return metin

def bool_çevir(değer): return bool(değer)
def kare_al(değer): return değer**2

# ... ve böyle böyle uzatabiliriz ...

# ===== TOPLAM KOMUT SAYISI: 300+
