import sys
import importlib.metadata
from packaging.version import parse as parse_version
    
# Kontrol edilecek kütüphaneler ve istenen minimum sürümleri
gereksinimler = {
    "numpy": "1.26",
    "pandas": "2.1",
    "gymnasium": "0.29.0",
    "pytest": "8.0",
    "flake8": "7.0",
    "tqdm": "4.66"
}

print(">>> Python ve Kütüphane Sürüm Kontrolü Başlatılıyor...\n")

# 1. Python Sürümünü Kontrol Et
print("--- Python Sürümü Kontrolü ---")
try:
    # Mevcut Python sürümünü al
    mevcut_python_surumu = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # İstenen sürümle karşılaştır
    if sys.version_info >= (3, 10):
        print(f"✅ Başarılı: Mevcut Python sürümü ({mevcut_python_surumu}) istenen 3.10+ ile uyumlu.\n")
    else:
        print(f"❌ Hata: Mevcut Python sürümü ({mevcut_python_surumu}) istenen 3.10+ sürümünden daha düşük!\n")
except Exception as e:
    print(f"❌ Hata: Python sürümü kontrol edilirken bir sorun oluştu: {e}\n")


# 2. Kütüphane Sürümlerini Kontrol Et
print("--- Kütüphane Sürümleri Kontrolü ---")
tum_gereksinimler_tamam = True

for kutuphane, min_surum in gereksinimler.items():
    try:
        # Kütüphanenin yüklü sürümünü al
        yuklu_surum_str = importlib.metadata.version(kutuphane)
        
        # Sürümleri karşılaştır
        if parse_version(yuklu_surum_str) >= parse_version(min_surum):
            print(f"✅ {kutuphane}: Yüklü sürüm ({yuklu_surum_str}) >= İstenen sürüm ({min_surum})")
        else:
            print(f"❌ {kutuphane}: Yükseltme Gerekli! Yüklü sürüm ({yuklu_surum_str}) < İstenen sürüm ({min_surum})")
            tum_gereksinimler_tamam = False
            
    except importlib.metadata.PackageNotFoundError:
        # Kütüphane bulunamadıysa hata ver
        print(f"❌ {kutuphane}: Yüklü değil! Lütfen yükleyin (minimum sürüm: {min_surum})")
        tum_gereksinimler_tamam = False
    except Exception as e:
        print(f"❌ {kutuphane}: Sürüm kontrol edilirken beklenmedik bir hata oluştu: {e}")
        tum_gereksinimler_tamam = False

# 3. Genel Sonuç
print("\n--- Kontrol Tamamlandı ---")
if tum_gereksinimler_tamam and sys.version_info >= (3, 10):
    print("🎉 Tüm gereksinimler başarıyla karşılanıyor. Sistem hazır!")
else:
    print("⚠️ Lütfen yukarıdaki hataları veya uyarıları düzelterek kurulumu tamamlayın.")


