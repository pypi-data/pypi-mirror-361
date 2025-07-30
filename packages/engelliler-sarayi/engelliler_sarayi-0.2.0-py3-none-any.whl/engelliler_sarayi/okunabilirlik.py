# ========================================================
# YENİ DOSYA: engelliler_sarayi/okunabilirlik.py
# ========================================================

import re

def _say_heceleri(metin: str) -> int:
    """Türkçe bir metindeki toplam hece sayısını yaklaşık olarak hesaplar."""
    # Türkçe'de her ünlü bir hece oluşturur kuralını temel alıyoruz.
    # Bu %100 doğru olmasa da çok güçlü bir yaklaşımdır.
    unluler = "aeıioöuü"
    # Küçük harfe çevirerek sayım yapalım
    metin = metin.lower()
    hece_sayisi = 0
    for harf in metin:
        if harf in unluler:
            hece_sayisi += 1
    return hece_sayisi

def _say_kelimeleri(metin: str) -> int:
    """Metindeki toplam kelime sayısını hesaplar."""
    # Noktalama işaretlerini boşlukla değiştir ve kelimeleri ayır
    kelimeler = re.findall(r'\b\w+\b', metin)
    return len(kelimeler)

def _say_cumleleri(metin: str) -> int:
    """Metindeki toplam cümle sayısını hesaplar."""
    # Cümle sonu işaretlerine göre ayır (. ! ?)
    cumleler = re.split(r'[.!?]+', metin)
    # Boş elemanları listeden çıkar (örn: metin sonunda . olunca)
    cumleler = [c for c in cumleler if c.strip()]
    # Eğer hiç cümle sonu işareti yoksa, en az 1 cümle kabul edelim
    return len(cumleler) if len(cumleler) > 0 else 1

def analiz_et_okunabilirlik(metin: str, dil: str = 'tr'):
    """
    Verilen metnin Flesch-Kincaid Okuma Kolaylığı skorunu hesaplar.
    Türkçe ('tr') için özel bir formül kullanır.

    Args:
      metin (str): Analiz edilecek metin.
      dil (str, optional): Metnin dili. Şu an için sadece 'tr' desteklenmektedir.

    Returns:
      dict: Analiz sonuçlarını içeren bir sözlük.
    """
    if dil.lower() != 'tr':
        return {"hata": "Şu anda sadece Türkçe ('tr') dil desteği bulunmaktadır."}

    kelime_sayisi = _say_kelimeleri(metin)
    cumle_sayisi = _say_cumleleri(metin)
    hece_sayisi = _say_heceleri(metin)

    # Kelime veya cümle sayısı sıfırsa, anlamsız sonuçları engelle
    if kelime_sayisi == 0 or cumle_sayisi == 0:
        return {
            "skor": 0,
            "yorum": "Analiz için yetersiz metin.",
            "detaylar": {
                "kelime_sayisi": 0,
                "cumle_sayisi": 0,
                "hece_sayisi": 0
            }
        }

    # Türkçe Flesch-Kincaid Formülü (Atesman, 1997)
    # Skor = 198.825 - (40.175 * (toplam_hece / toplam_kelime)) - (2.610 * (toplam_kelime / toplam_cümle))
    skor = 198.825 - (40.175 * (hece_sayisi / kelime_sayisi)) - (2.610 * (kelime_sayisi / cumle_sayisi))

    # Skora göre yorumlama
    if skor >= 90:
        yorum = "Çok Kolay (İlkokul 5. sınıf seviyesi)"
    elif 70 <= skor < 90:
        yorum = "Kolay (Ortaokul seviyesi)"
    elif 50 <= skor < 70:
        yorum = "Standart (Lise seviyesi)"
    elif 30 <= skor < 50:
        yorum = "Zor (Üniversite seviyesi)"
    else:
        yorum = "Çok Zor (Akademik seviye)"

    return {
        "skor": skor,
        "yorum": yorum,
        "detaylar": {
            "kelime_sayisi": kelime_sayisi,
            "cumle_sayisi": cumle_sayisi,
            "hece_sayisi": hece_sayisi
        }
    }
