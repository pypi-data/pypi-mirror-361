# Engelliler Sarayı Kütüphanesi

**Engelliler Sarayı**, Python geliştiricilerinin daha erişilebilir uygulamalar yapmalarına yardımcı olmak için tasarlanmış bir kütüphanedir.

Bu proje, özellikle görme ve işitme engelleri olan kullanıcılar için yazılım geliştirme sürecini kolaylaştıran araçlar sunmayı hedefler.

## Özellikler

- **Renk Kontrastı Kontrolü:** Yazı ve arka plan renklerinin WCAG standartlarına göre okunabilir olup olmadığını kontrol eder.
- **Metni Sese Çevirme:** Verilen metinleri, ayarlanabilir hızda ve sesle bilgisayarın hoparlöründen okur.

## Kurulum

Kütüphaneyi `pip` kullanarak kolayca kurabilirsiniz:

bash
pip install engelliler-sarayi


## Hızlı Başlangıç

İşte kütüphaneyi kullanmanın ne kadar kolay olduğuna dair birkaç örnek:

```python
import engelliler_sarayi

# 1. Renklerin kontrastını kontrol etme (HEX veya RGB ile)
yeterli_mi, oran = engelliler_sarayi.check_contrast_ratio("#FFFFFF", "#000000")
if yeterli_mi:
    print(f"Renkler erişilebilir! Kontrast oranı: {oran:.2f}")

# 2. Bir metni seslendirme (hızını ayarlayarak)
engelliler_sarayi.metni_seslendir(
    "Merhaba, bu kütüphane harika çalışıyor.",
    hiz=200
)

