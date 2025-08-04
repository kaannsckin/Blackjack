import React from 'react';
import { 
  HeartIcon, 
  CodeBracketIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

const Footer = () => {
  return (
    <footer className="bg-gray-900 bg-opacity-90 border-t border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Project Info */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <BeakerIcon className="w-6 h-6 text-green-400" />
              <h3 className="text-lg font-semibold text-white">
                Blackjack AI V4.0
              </h3>
            </div>
            <p className="text-gray-400 text-sm">
              Gelişmiş AI destekli blackjack sistemi. 8 farklı AI modeli ile 
              en iyi performansı elde edin.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Hızlı Linkler</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/game" className="text-gray-400 hover:text-green-400 transition-colors">
                  Oyun Masası
                </a>
              </li>
              <li>
                <a href="/analysis" className="text-gray-400 hover:text-green-400 transition-colors">
                  AI Analizi
                </a>
              </li>
              <li>
                <a href="/models" className="text-gray-400 hover:text-green-400 transition-colors">
                  Model Karşılaştırma
                </a>
              </li>
              <li>
                <a href="/settings" className="text-gray-400 hover:text-green-400 transition-colors">
                  Ayarlar
                </a>
              </li>
            </ul>
          </div>

          {/* Stats */}
          <div>
            <h3 className="text-white font-semibold mb-4">Sistem Durumu</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">AI Modelleri:</span>
                <span className="text-green-400 font-semibold">8</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">En İyi ROI:</span>
                <span className="text-green-400 font-semibold">51%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Test Edilen El:</span>
                <span className="text-green-400 font-semibold">100K+</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Sistem Durumu:</span>
                <span className="text-green-400 font-semibold">Aktif</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700 mt-8 pt-6 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 text-gray-400 text-sm">
            <CodeBracketIcon className="w-4 h-4" />
            <span>Geliştirildi</span>
            <HeartIcon className="w-4 h-4 text-red-500" />
            <span>AI ile</span>
          </div>
          
          <div className="text-gray-400 text-sm mt-2 md:mt-0">
            © 2024 Blackjack AI V4.0. Tüm hakları saklıdır.
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 