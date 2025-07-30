# engelliler_sarayi/seslendirme.py dosyasının GÜNCEL içeriği

import pyttsx3

def metni_seslendir(metin: str, hiz: int = 175, cinsiyet: str = 'default'):
  """
  Verilen metni seslendirir. Ses hızı ve cinsiyeti ayarlanabilir.

  Args:
    metin (str): Seslendirilecek yazı.
    hiz (int, optional): Konuşma hızı (kelime/dakika). Varsayılan: 175.
    cinsiyet (str, optional): 'erkek', 'kadin' veya 'default'. 
                             Sistemde uygun ses varsa ayarlar. Varsayılan: 'default'.
  """
  try:
    engine = pyttsx3.init()
    
    # Hızı ayarla
    engine.setProperty('rate', hiz)

    # Cinsiyeti ayarla (eğer istenmişse ve uygun ses varsa)
    if cinsiyet != 'default':
      voices = engine.getProperty('voices')
      # pyttsx3'te cinsiyet standardı yok, bu yüzden isim veya ID'den arama yapıyoruz
      # Bu kısım işletim sistemine göre farklı çalışabilir
      gender_map = {'kadin': 'female', 'erkek': 'male'}
      target_gender = gender_map.get(cinsiyet.lower())

      for voice in voices:
        # voice.gender özelliği her zaman mevcut olmayabilir, bu yüzden name'e bakmak daha güvenli
        if target_gender and target_gender in voice.name.lower():
          engine.setProperty('voice', voice.id)
          break

    engine.say(metin)
    engine.runAndWait()
    engine.stop()
    return True
  except Exception as e:
    print(f"Seslendirme sırasında bir hata oluştu: {e}")
    return False