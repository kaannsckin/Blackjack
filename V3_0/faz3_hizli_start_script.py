#!/usr/bin/env python3
"""
========================================================================
FAZ3.X HIZLI BAŞLANGIÇ SCRIPT'İ
========================================================================

🎯 Amaç: Docker container'da hızlı optimizasyon ve test
📋 Kapsam: AI model optimization, multi-player test, analytics
🔧 Kullanım: python faz3_hizli_start_script.py

========================================================================
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class Faz3QuickStarter:
    """Faz3.x hızlı başlangıç sınıfı."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        
    def run_command(self, cmd, description="", timeout=300):
        """Komut çalıştır ve sonucu döndür."""
        print(f"\n🔄 {description}")
        print(f"💻 Komut: {cmd}")
        print("-" * 60)
        
        try:
            start = time.time()
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            duration = time.time() - start
            
            if result.returncode == 0:
                print(f"✅ BAŞARILI ({duration:.1f}s)")
                if result.stdout.strip():
                    print(f"📄 Çıktı:\n{result.stdout[:500]}...")
                return True, result.stdout, duration
            else:
                print(f"❌ HATA (kod: {result.returncode}, {duration:.1f}s)")
                if result.stderr.strip():
                    print(f"🚨 Hata: {result.stderr[:200]}...")
                return False, result.stderr, duration
                
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT - {timeout}s'de tamamlanamadı")
            return False, "TIMEOUT", timeout
        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
            return False, str(e), 0

    def test_system_ready(self):
        """Sistem hazırlığını test et."""
        print("🚀 SİSTEM HAZIRLIK TESTİ")
        print("=" * 60)
        
        tests = [
            ("python --version", "Python version"),
            ("python -c 'import ray; print(f\"Ray: {ray.__version__}\")'", "Ray import"),
            ("python -c 'import stable_baselines3; print(f\"SB3: {stable_baselines3.__version__}\")'", "SB3 import"),
            ("ls -la runs/", "Runs directory check"),
            ("ls -la models/", "Models directory check"),
        ]
        
        success_count = 0
        for cmd, desc in tests:
            success, output, duration = self.run_command(cmd, desc, 30)
            if success:
                success_count += 1
        
        ready = success_count >= 4
        self.results['system_ready'] = {
            'success': ready,
            'tests_passed': f"{success_count}/{len(tests)}",
            'ready_percentage': (success_count / len(tests)) * 100
        }
        
        return ready

    def quick_model_optimization(self):
        """Hızlı model optimizasyonu."""
        print("\n🧠 HIZLI MODEL OPTİMİZASYONU")
        print("=" * 60)
        
        # Kısa süreli hyperparameter tuning
        success, output, duration = self.run_command(
            "python scripts/optimize_hyperparameters.py --n-trials 10 --total-steps 50000",
            "Hızlı Hyperparameter Tuning (10 trials)",
            180  # 3 dakika timeout
        )
        
        self.results['model_optimization'] = {
            'success': success,
            'duration': duration,
            'trials': 10,
            'output_snippet': output[:300] if output else "No output"
        }
        
        return success

    def multi_player_demo(self):
        """Multi-player demo çalıştır."""
        print("\n🎮 MULTI-PLAYER DEMO")
        print("=" * 60)
        
        success, output, duration = self.run_command(
            "python faz4_multi_player_training.py --players=4 --episodes=1000 --quick-demo",
            "4 Oyunculu Hızlı Demo",
            120  # 2 dakika timeout
        )
        
        self.results['multi_player_demo'] = {
            'success': success,
            'duration': duration,
            'players': 4,
            'episodes': 1000,
            'output_snippet': output[:300] if output else "No output"
        }
        
        return success

    def performance_benchmark(self):
        """Performance benchmark çalıştır."""
        print("\n📊 PERFORMANCE BENCHMARK")
        print("=" * 60)
        
        success, output, duration = self.run_command(
            "python comprehensive_ai_analysis.py --quick-benchmark",
            "Hızlı Performance Analizi",
            90  # 1.5 dakika timeout
        )
        
        self.results['performance_benchmark'] = {
            'success': success,
            'duration': duration,
            'output_snippet': output[:300] if output else "No output"
        }
        
        return success

    def integration_test(self):
        """F3.x entegrasyon testi."""
        print("\n🔧 F3.X ENTEGRASYON TESTİ")
        print("=" * 60)
        
        success, output, duration = self.run_command(
            "python test_f3_integration.py",
            "F3.x Entegrasyon Testi",
            120  # 2 dakika timeout
        )
        
        self.results['integration_test'] = {
            'success': success,
            'duration': duration,
            'output_snippet': output[:300] if output else "No output"
        }
        
        return success

    def generate_report(self):
        """Sonuç raporu oluştur."""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 FAZ3.X HIZLI BAŞLANGIÇ RAPORU")
        print("=" * 80)
        
        successful_tests = sum(1 for test in self.results.values() if test.get('success', False))
        total_tests = len(self.results)
        
        print(f"🕐 Toplam Süre: {total_duration:.1f} saniye")
        print(f"✅ Başarılı Testler: {successful_tests}/{total_tests}")
        print(f"📈 Başarı Oranı: {(successful_tests/total_tests)*100:.1f}%")
        print()
        
        for test_name, result in self.results.items():
            status = "✅" if result.get('success', False) else "❌"
            duration = result.get('duration', 0)
            print(f"{status} {test_name.replace('_', ' ').title()}: {duration:.1f}s")
        
        # JSON raporu kaydet
        report_data = {
            'timestamp': self.start_time.isoformat(),
            'total_duration': total_duration,
            'success_rate': (successful_tests/total_tests)*100,
            'results': self.results
        }
        
        report_file = f"runs/faz3_quick_start_report_{int(time.time())}.json"
        os.makedirs('runs', exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detaylı rapor kaydedildi: {report_file}")
        
        if successful_tests >= total_tests * 0.8:  # %80 başarı
            print("\n🎉 FAZ3.X HAZIR! Geliştirmelere devam edebilirsiniz!")
            print("\n🎯 Önerilen sonraki adımlar:")
            print("  1. python scripts/optimize_hyperparameters_advanced.py")
            print("  2. python faz4_multi_player_training.py --players=8")
            print("  3. jupyter lab --ip=0.0.0.0 --allow-root --no-browser")
        else:
            print("\n⚠️ Bazı testler başarısız. Lütfen logları kontrol edin.")
        
        return successful_tests >= total_tests * 0.8

    def run_all(self):
        """Tüm testleri çalıştır."""
        print("🚀 FAZ3.X HIZLI BAŞLANGIÇ BAŞLIYOR...")
        print("Bu işlem yaklaşık 5-10 dakika sürecek.")
        print("=" * 80)
        
        # Test sırası
        if not self.test_system_ready():
            print("❌ Sistem hazır değil. Çıkılıyor...")
            return False
        
        self.quick_model_optimization()
        self.multi_player_demo()
        self.performance_benchmark()
        self.integration_test()
        
        return self.generate_report()

def main():
    """Ana fonksiyon."""
    starter = Faz3QuickStarter()
    success = starter.run_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 