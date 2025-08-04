import React from 'react';
import { motion } from 'framer-motion';
import { useAI } from '../context/AIContext';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const AIAnalysis = () => {
  const { state: aiState, helpers } = useAI();

  // Mock data for charts (in real app, this would come from API)
  const performanceData = [
    { model: 'Ultimate AI', roi: 51, winRate: 52, grade: 'A+' },
    { model: 'Enhanced Adaptive', roi: 48, winRate: 51, grade: 'A' },
    { model: 'Adaptive Simple', roi: 51, winRate: 52, grade: 'A' },
    { model: 'Practical Hybrid', roi: 45, winRate: 50, grade: 'B+' },
    { model: 'Multi-Player', roi: 42, winRate: 49, grade: 'B' },
    { model: 'Enhanced Simple', roi: 40, winRate: 49, grade: 'B' },
    { model: 'Optimized Adaptive', roi: 35, winRate: 47, grade: 'C' }
  ];

  const recentPredictions = [
    { time: '14:30', model: 'Ultimate AI', action: 'Hit', confidence: 95, result: 'Win' },
    { time: '14:28', model: 'Enhanced Adaptive', action: 'Stand', confidence: 88, result: 'Win' },
    { time: '14:25', model: 'Adaptive Simple', action: 'Hit', confidence: 92, result: 'Lose' },
    { time: '14:22', model: 'Ultimate AI', action: 'Double', confidence: 97, result: 'Win' },
    { time: '14:20', model: 'Practical Hybrid', action: 'Stand', confidence: 85, result: 'Push' }
  ];

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-4">
            AI Performans Analizi
          </h1>
          <p className="text-xl text-gray-300">
            Detaylı AI model performans analizi ve istatistikler
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Performance Overview */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2"
          >
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                <ChartBarIcon className="w-8 h-8 mr-3 text-green-400" />
                Model Performans Karşılaştırması
              </h2>

              <div className="space-y-6">
                {/* ROI Comparison */}
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">ROI Karşılaştırması</h3>
                  <div className="space-y-3">
                    {performanceData.map((item, index) => (
                      <div key={index} className="bg-gray-700 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-white font-semibold">{item.model}</span>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            item.grade === 'A+' ? 'bg-yellow-600 text-white' :
                            item.grade === 'A' ? 'bg-green-600 text-white' :
                            item.grade === 'B+' ? 'bg-blue-600 text-white' :
                            item.grade === 'B' ? 'bg-purple-600 text-white' :
                            'bg-gray-600 text-white'
                          }`}>
                            {item.grade}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-300">ROI: {item.roi}%</span>
                          <span className="text-gray-300">Win Rate: {item.winRate}%</span>
                        </div>
                        <div className="mt-2 bg-gray-600 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${(item.roi / 60) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-400 mb-1">
                      {aiState.totalPredictions}
                    </div>
                    <div className="text-gray-300 text-sm">Toplam Tahmin</div>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-400 mb-1">
                      {aiState.successfulPredictions}
                    </div>
                    <div className="text-gray-300 text-sm">Başarılı Tahmin</div>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-400 mb-1">
                      {(aiState.averageConfidence * 100).toFixed(1)}%
                    </div>
                    <div className="text-gray-300 text-sm">Ortalama Güven</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            {/* System Status */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <CheckCircleIcon className="w-6 h-6 mr-2 text-green-400" />
                Sistem Durumu
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">API Bağlantısı:</span>
                  <span className={`font-semibold ${aiState.apiConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {aiState.apiConnected ? 'Aktif' : 'Bağlantı Yok'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Yüklenen Modeller:</span>
                  <span className="text-white font-semibold">{aiState.availableModels.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Seçili Model:</span>
                  <span className="text-blue-400 font-semibold">
                    {helpers.getModelDisplayName(aiState.selectedModel)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Son Güncelleme:</span>
                  <span className="text-gray-400 text-sm">Şimdi</span>
                </div>
              </div>
            </div>

            {/* Recent Predictions */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <ClockIcon className="w-6 h-6 mr-2 text-blue-400" />
                Son Tahminler
              </h3>
              
              <div className="space-y-3">
                {recentPredictions.map((prediction, index) => (
                  <div key={index} className="bg-gray-700 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-white font-semibold text-sm">{prediction.model}</span>
                      <span className="text-gray-400 text-xs">{prediction.time}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300 text-sm">
                        {prediction.action} ({prediction.confidence}%)
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        prediction.result === 'Win' ? 'bg-green-600 text-white' :
                        prediction.result === 'Lose' ? 'bg-red-600 text-white' :
                        'bg-yellow-600 text-white'
                      }`}>
                        {prediction.result}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <ArrowTrendingUpIcon className="w-6 h-6 mr-2 text-purple-400" />
                Hızlı İşlemler
              </h3>
              
              <div className="space-y-3">
                <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition-colors">
                  Yeni Analiz Başlat
                </button>
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors">
                  Rapor İndir
                </button>
                <button className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg transition-colors">
                  Model Karşılaştır
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AIAnalysis; 