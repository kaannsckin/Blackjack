#!/usr/bin/env python3
"""
========================================================================
DOCKER CONTAINER QUICK TEST SCRIPT
========================================================================

🎯 Amaç: Docker container'ında hızlı testler için basit script
📋 Kapsam: F3.x entegrasyon testleri ve sistem kontrolü
🔧 Kullanım: python docker_test_quick.py

========================================================================
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(cmd, description=""):
    """Komut çalıştır ve sonucu döndür."""
    print(f"\n🔄 {description}")
    print(f"💻 Komut: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ BAŞARILI")
            if result.stdout.strip():
                print(f"📄 Çıktı:\n{result.stdout}")
        else:
            print(f"❌ HATA (kod: {result.returncode})")
            if result.stderr.strip():
                print(f"🚨 Hata: {result.stderr}")
                
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Komut 30 saniyede tamamlanamadı")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

def main():
    """Ana test fonksiyonu."""
    print("🚀 DOCKER CONTAINER QUICK TEST")
    print("=" * 60)
    
    tests = [
        ("python --version", "Python versiyonu kontrol"),
        ("pwd", "Mevcut dizin kontrol"),
        ("ls -la", "Dosya listesi kontrol"),
        ("python -c 'import sys; print(f\"Python path: {sys.path[0]}\")'", "Python path kontrol"),
        ("python -c 'import ray; print(f\"Ray version: {ray.__version__}\")'", "Ray import test"),
        ("python -c 'import optuna; print(f\"Optuna version: {optuna.__version__}\")'", "Optuna import test"),
        ("python -c 'import stable_baselines3; print(f\"SB3 version: {stable_baselines3.__version__}\")'", "Stable Baselines3 test"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for cmd, desc in tests:
        if run_command(cmd, desc):
            success_count += 1
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"📊 TEST SONUÇLARI")
    print(f"✅ Başarılı: {success_count}/{total_tests}")
    print(f"❌ Başarısız: {total_tests - success_count}/{total_tests}")
    print(f"📈 Başarı Oranı: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("\n🎯 Çalıştırabileceğiniz ana testler:")
        print("  python test_f3_integration.py")
        print("  python faz3_kritik_sorunlar_cozum_plani.py") 
        print("  python comprehensive_ai_analysis.py")
        print("  python scripts/train_play_agent.py")
    else:
        print("⚠️ Bazı testler başarısız oldu.")
    
    print("\n🐳 Docker container başarıyla çalışıyor!")
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 