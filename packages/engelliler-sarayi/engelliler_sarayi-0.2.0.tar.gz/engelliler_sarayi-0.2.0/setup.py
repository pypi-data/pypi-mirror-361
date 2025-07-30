# ==========================================================
# GÜNCELLENMİŞ VE SON HALİ: setup.py DOSYASI (v2.0 için)
# ==========================================================

from setuptools import setup, find_packages

# README dosyasının içeriğini uzun açıklama olarak oku
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="engelliler-sarayi",
    version="0.2.0",          # Versiyonumuz doğru.
    author="Miraç Birben",
    author_email="miracbirben@gmail.com",
    
    # <<<--- DEĞİŞİKLİK 1: Açıklamayı daha kapsayıcı hale getirdik.
    description="Görsel, işitsel ve bilişsel erişilebilirlik için Python araçları.",
    
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kullanici-adiniz/engelliler-sarayi-projesi",
    packages=find_packages(),
    
    install_requires=[
        "pyttsx3", # Yeni bir bağımlılık eklemedik, bu yüzden liste aynı.
    ],
    
    # <<<--- DEĞİŞİKLİK 2: Yeni özelliğimizi yansıtan bir sınıflandırıcı ekledik.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Text Processing", # Okunabilirlik analizi için eklendi.
    ],
    python_requires=">=3.6",
)