# =========================================================
# GÜNCELLENMİŞ: engelliler_sarayi/__init__.py DOSYASI
# =========================================================

# Görünürlük modülünden fonksiyonumuzu alıyoruz
from .gorunurluk import check_contrast_ratio

# Seslendirme modülünden YENİ fonksiyonlarımızı alıyoruz
from .seslendirme import metni_seslendir, listele_sesleri

# Okunabilirlik modülünden YEPYENİ fonksiyonumuzu alıyoruz
from .okunabilirlik import analiz_et_okunabilirlik
