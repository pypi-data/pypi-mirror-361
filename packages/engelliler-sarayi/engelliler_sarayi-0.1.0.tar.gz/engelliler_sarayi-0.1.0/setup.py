from setuptools import setup, find_packages

# README dosyasının içeriğini uzun açıklama olarak oku
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="engelliler-sarayi",  # PyPI'da görünecek isim (benzersiz olmalı!)
    version="0.1.0",          # Projenin ilk versiyonu
    author="Sizin Adınız",
    author_email="mail@adresiniz.com",
    description="Yazılımlar için erişilebilirlik araçları sunan bir kütüphane.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kullanici-adiniz/engelliler-sarayi-projesi", # Projenin GitHub adresi (varsa)
    packages=find_packages(), # Projedeki tüm paketleri (içinde __init__.py olan klasörleri) otomatik bulur
    
    # Projenin çalışması için gereken diğer kütüphaneler
    install_requires=[
        "pyttsx3",
    ],
    
    # Projeyi sınıflandıran etiketler (PyPI'da aramayı kolaylaştırır)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6", # Gerekli en düşük Python versiyonu
)
