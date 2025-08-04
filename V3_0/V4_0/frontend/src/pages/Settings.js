import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useGame } from '../context/GameContext';
import { useAI } from '../context/AIContext';
import { 
  CogIcon, 
  UserIcon,
  BellIcon,
  ShieldCheckIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';

const Settings = () => {
  const { state: gameState, actions: gameActions } = useGame();
  const { state: aiState, actions: aiActions } = useAI();
  
  const [settings, setSettings] = useState({
    // Game settings
    defaultBankroll: gameState.bankroll,
    minBet: gameState.minBet,
    maxBet: gameState.maxBet,
    
    // AI settings
    defaultModel: aiState.selectedModel,
    autoLoadModels: true,
    showPredictions: true,
    
    // UI settings
    theme: 'dark',
    animations: true,
    soundEffects: false,
    
    // Notification settings
    emailNotifications: false,
    pushNotifications: true,
    predictionAlerts: true
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = () => {
    // Save settings to localStorage
    localStorage.setItem('blackjackSettings', JSON.stringify(settings));
    
    // Update game state
    gameActions.updateBankroll(settings.defaultBankroll);
    
    // Update AI state
    aiActions.setSelectedModel(settings.defaultModel);
    
    alert('Ayarlar kaydedildi!');
  };

  const handleResetSettings = () => {
    const defaultSettings = {
      defaultBankroll: 10000,
      minBet: 10,
      maxBet: 1000,
      defaultModel: 'ultimate_ai',
      autoLoadModels: true,
      showPredictions: true,
      theme: 'dark',
      animations: true,
      soundEffects: false,
      emailNotifications: false,
      pushNotifications: true,
      predictionAlerts: true
    };
    
    setSettings(defaultSettings);
    localStorage.setItem('blackjackSettings', JSON.stringify(defaultSettings));
    alert('Ayarlar varsayılana sıfırlandı!');
  };

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-4">
            Ayarlar
          </h1>
          <p className="text-xl text-gray-300">
            Sistem ayarlarını ve tercihlerinizi yönetin
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Game Settings */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <UserIcon className="w-6 h-6 mr-2 text-green-400" />
                Oyun Ayarları
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Varsayılan Bankroll
                  </label>
                  <input
                    type="number"
                    value={settings.defaultBankroll}
                    onChange={(e) => handleSettingChange('defaultBankroll', parseInt(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-green-500"
                    min="1000"
                    max="100000"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Minimum Bahis
                  </label>
                  <input
                    type="number"
                    value={settings.minBet}
                    onChange={(e) => handleSettingChange('minBet', parseInt(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-green-500"
                    min="1"
                    max="100"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Maksimum Bahis
                  </label>
                  <input
                    type="number"
                    value={settings.maxBet}
                    onChange={(e) => handleSettingChange('maxBet', parseInt(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-green-500"
                    min="100"
                    max="10000"
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* AI Settings */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <ComputerDesktopIcon className="w-6 h-6 mr-2 text-blue-400" />
                AI Ayarları
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Varsayılan AI Modeli
                  </label>
                  <select
                    value={settings.defaultModel}
                    onChange={(e) => handleSettingChange('defaultModel', e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  >
                    {aiState.availableModels.map((model) => (
                      <option key={model} value={model}>
                        {model.replace('_', ' ').toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    Modelleri Otomatik Yükle
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.autoLoadModels}
                    onChange={(e) => handleSettingChange('autoLoadModels', e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    Tahminleri Göster
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.showPredictions}
                    onChange={(e) => handleSettingChange('showPredictions', e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* UI Settings */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
          >
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <CogIcon className="w-6 h-6 mr-2 text-purple-400" />
                Arayüz Ayarları
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Tema
                  </label>
                  <select
                    value={settings.theme}
                    onChange={(e) => handleSettingChange('theme', e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="dark">Koyu Tema</option>
                    <option value="light">Açık Tema</option>
                    <option value="auto">Otomatik</option>
                  </select>
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    Animasyonlar
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.animations}
                    onChange={(e) => handleSettingChange('animations', e.target.checked)}
                    className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    Ses Efektleri
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.soundEffects}
                    onChange={(e) => handleSettingChange('soundEffects', e.target.checked)}
                    className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Notification Settings */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <BellIcon className="w-6 h-6 mr-2 text-yellow-400" />
                Bildirim Ayarları
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    E-posta Bildirimleri
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                    className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    Push Bildirimleri
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.pushNotifications}
                    onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                    className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-gray-300 text-sm font-medium">
                    Tahmin Uyarıları
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.predictionAlerts}
                    onChange={(e) => handleSettingChange('predictionAlerts', e.target.checked)}
                    className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="mt-8 flex justify-center space-x-4"
        >
          <button
            onClick={handleSaveSettings}
            className="flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
          >
            <ShieldCheckIcon className="w-5 h-5 mr-2" />
            Ayarları Kaydet
          </button>
          
          <button
            onClick={handleResetSettings}
            className="flex items-center px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
          >
            <CogIcon className="w-5 h-5 mr-2" />
            Varsayılana Sıfırla
          </button>
        </motion.div>

        {/* Current System Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          className="mt-8"
        >
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Sistem Bilgileri</h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-400">API Durumu:</span>
                <span className={`ml-2 font-semibold ${aiState.apiConnected ? 'text-green-400' : 'text-red-400'}`}>
                  {aiState.apiConnected ? 'Bağlı' : 'Bağlantı Yok'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Yüklenen Modeller:</span>
                <span className="ml-2 font-semibold text-white">{aiState.availableModels.length}</span>
              </div>
              <div>
                <span className="text-gray-400">Toplam Tahmin:</span>
                <span className="ml-2 font-semibold text-white">{aiState.totalPredictions}</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Settings; 