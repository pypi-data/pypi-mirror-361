# =========================================================
# GÜNCELLENMİŞ: engelliler_sarayi/gorunurluk.py DOSYASI
# =========================================================

def _hex_to_rgb(hex_color: str):
  """#RRGGBB formatındaki bir hex renk kodunu (R, G, B) tuple'ına çevirir."""
  hex_color = hex_color.lstrip('#')
  # 3 karakterli hex kodlarını da destekleyelim (örn: #FFF)
  if len(hex_color) == 3:
      hex_color = "".join([c*2 for c in hex_color])
  return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def _get_luminance(rgb_color: tuple):
  """Bir rengin göreceli parlaklığını (luminance) hesaplar."""
  srgb = [val / 255.0 for val in rgb_color]
  luminance_values = []
  for val in srgb:
    if val <= 0.03928:
      luminance_values.append(val / 12.92)
    else:
      luminance_values.append(((val + 0.055) / 1.055) ** 2.4)
  
  L = 0.2126 * luminance_values[0] + 0.7152 * luminance_values[1] + 0.0722 * luminance_values[2]
  return L

def check_contrast_ratio(text_color, background_color, level: str = 'AA'):
  """
  İki renk arasındaki kontrast oranını WCAG standartlarına göre kontrol eder.
  Renkler (R,G,B) tuple'ı veya '#RRGGBB' hex string'i olarak verilebilir.

  Args:
    text_color (tuple | str): Metin rengi.
    background_color (tuple | str): Arka plan rengi.
    level (str, optional): Kontrol edilecek erişilebilirlik seviyesi. 
                           'AA' (oran >= 4.5) veya 'AAA' (oran >= 7.0). 
                           Varsayılan: 'AA'.

  Returns:
    dict: Kontrast oranı ve erişilebilirlik durumu hakkında bilgi içeren bir sözlük.
          Örnek: {'ratio': 15.3, 'is_accessible': True, 'level_checked': 'AA'}
  """
  # Renk formatını kontrol et ve gerekirse dönüştür
  if isinstance(text_color, str):
    text_color = _hex_to_rgb(text_color)
  if isinstance(background_color, str):
    background_color = _hex_to_rgb(background_color)

  L1 = _get_luminance(text_color)
  L2 = _get_luminance(background_color)

  if L1 > L2:
    ratio = (L1 + 0.05) / (L2 + 0.05)
  else:
    ratio = (L2 + 0.05) / (L1 + 0.05)
  
  # Seviyeye göre eşik değerini belirle
  threshold = 7.0 if level.upper() == 'AAA' else 4.5
  is_accessible = ratio >= threshold
  
  # Sonuçları daha açıklayıcı bir sözlük olarak döndür
  return {
      "ratio": ratio,
      "is_accessible": is_accessible,
      "level_checked": level.upper(),
      "threshold": threshold
  }