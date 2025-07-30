# ==========================================================
# GÜNCELLENMİŞ: engelliler_sarayi/seslendirme.py DOSYASI
# ==========================================================

import pyttsx3

def listele_sesleri():
  """
  Kullanıcının sisteminde yüklü olan ses motorlarını ve özelliklerini listeler.

  Returns:
    list: Her biri bir sesi temsil eden sözlükler listesi.
          Örnek: [{'id': '...', 'name': 'Zira', 'lang': 'tr_TR'}]
  """
  try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voice_list = []
    for voice in voices:
      voice_info = {
          'id': voice.id,
          'name': voice.name,
          'lang': getattr(voice, 'lang', 'N/A'), # .lang her motorda olmayabilir
          'gender': getattr(voice, 'gender', 'N/A'), # .gender her motorda olmayabilir
      }
      voice_list.append(voice_info)
    engine.stop()
    return voice_list
  except Exception as e:
    print(f"Sesler listelenirken bir hata oluştu: {e}")
    return []


def metni_seslendir(
    metin: str, 
    hiz: int = 175, 
    ses_seviyesi: float = 1.0, 
    ses_id: str = None, 
    dosya_yolu: str = None
  ):
  """
  Verilen metni seslendirir veya bir ses dosyasına kaydeder.

  Args:
    metin (str): Seslendirilecek yazı.
    hiz (int, optional): Konuşma hızı (kelime/dakika). Varsayılan: 175.
    ses_seviyesi (float, optional): Ses seviyesi (0.0 ile 1.0 arası). Varsayılan: 1.0.
    ses_id (str, optional): Kullanılacak özel bir sesin ID'si. 
                            `listele_sesleri()` ile bulunabilir. Varsayılan: Sistem varsayılanı.
    dosya_yolu (str, optional): Eğer belirtilirse, ses konuşmak yerine bu yola 
                                bir dosya olarak kaydedilir. Örn: 'cikti.mp3'. 
                                Varsayılan: None (doğrudan konuşur).
  """
  try:
    engine = pyttsx3.init()
    
    # Hızı ayarla
    engine.setProperty('rate', hiz)
    # Ses seviyesini ayarla
    engine.setProperty('volume', ses_seviyesi)

    # Eğer özel bir ses ID'si verilmişse, onu ayarla
    if ses_id:
      engine.setProperty('voice', ses_id)
      
    # Ana mantık: Dosyaya mı kaydedilecek, yoksa konuşulacak mı?
    if dosya_yolu:
      engine.save_to_file(metin, dosya_yolu)
    else:
      engine.say(metin)
    
    engine.runAndWait()
    engine.stop()
    return True
  except Exception as e:
    print(f"Seslendirme sırasında bir hata oluştu: {e}")
    return False