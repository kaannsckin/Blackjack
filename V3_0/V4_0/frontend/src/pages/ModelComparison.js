import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAI } from '../context/AIContext';
import { 
  BeakerIcon, 
  StarIcon,
  ChartBarIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';

const ModelComparison = () => {
  const { helpers } = useAI();
  const [selectedModels, setSelectedModels] = useState(['ultimate_ai', 'enhanced_adaptive', 'adaptive_simple']);

  const allModels = [
    { id: 'ultimate_ai', name: 'Ultimate AI System', grade: 'A+', roi: 51, winRate: 52, description: '4-Level Hierarchical Architecture' },
    { id: 'enhanced_adaptive', name: 'Enhanced Adaptive AI', grade: 'A', roi: 48, winRate: 51, description: 'Sophisticated crisis management' },
    { id: 'adaptive_simple', name: 'Adaptive Simple AI', grade: 'A', roi: 51, winRate: 52, description: 'Proven Simple AI + crisis management' },
    { id: 'practical_hybrid', name: 'Practical Hybrid AI', grade: 'B+', roi: 45, winRate: 50, description: 'Hybrid approach combining strategies' },
    { id: 'multi_player', name: 'Multi-Player AI', grade: 'B', roi: 42, winRate: 49, description: 'Multi-player environment support' },
    { id: 'enhanced_simple', name: 'Enhanced Simple AI', grade: 'B', roi: 40, winRate: 49, description: 'Enhanced version with card tracking' },
    { id: 'optimized_adaptive', name: 'Optimized Adaptive AI', grade: 'C', roi: 35, winRate: 47, description: 'Optimized version of adaptive AI' }
  ];

  const handleModelToggle = (modelId) => {
    setSelectedModels(prev => 
      prev.includes(modelId) 
        ? prev.filter(id => id !== modelId)
        : [...prev, modelId]
    );
  };

  const selectedModelData = allModels.filter(model => selectedModels.includes(model.id));

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
            AI Model Karşılaştırması
          </h1>
          <p className="text-xl text-gray-300">
            Farklı AI modellerinin detaylı karşılaştırması ve performans analizi
          </p>
        </motion.div>

        {/* Model Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <BeakerIcon className="w-6 h-6 mr-2 text-blue-400" />
              Karşılaştırılacak Modelleri Seçin
            </h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {allModels.map((model) => (
                <div
                  key={model.id}
                  className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border-2 ${
                    selectedModels.includes(model.id)
                      ? 'bg-green-600 border-green-500 text-white'
                      : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                  }`}
                  onClick={() => handleModelToggle(model.id)}
                >
                  <div className="text-center">
                    <div className="text-sm font-semibold mb-1">{model.name.split(' ')[0]}</div>
                    <div className="text-xs opacity-75">{model.grade}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
              <ChartBarIcon className="w-6 h-6 mr-2 text-green-400" />
              Detaylı Karşılaştırma
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-600">
                    <th className="text-left p-3 text-white font-semibold">Model</th>
                    <th className="text-center p-3 text-white font-semibold">Grade</th>
                    <th className="text-center p-3 text-white font-semibold">ROI (%)</th>
                    <th className="text-center p-3 text-white font-semibold">Win Rate (%)</th>
                    <th className="text-center p-3 text-white font-semibold">Açıklama</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedModelData.map((model, index) => (
                    <motion.tr
                      key={model.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 * index }}
                      className="border-b border-gray-700 hover:bg-gray-700 transition-colors"
                    >
                      <td className="p-3">
                        <div className="flex items-center">
                          <span className="text-white font-semibold">{model.name}</span>
                          {model.grade === 'A+' && (
                            <StarIcon className="w-4 h-4 text-yellow-400 ml-2" />
                          )}
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          model.grade === 'A+' ? 'bg-yellow-600 text-white' :
                          model.grade === 'A' ? 'bg-green-600 text-white' :
                          model.grade === 'B+' ? 'bg-blue-600 text-white' :
                          model.grade === 'B' ? 'bg-purple-600 text-white' :
                          'bg-gray-600 text-white'
                        }`}>
                          {model.grade}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        <span className="text-green-400 font-semibold">{model.roi}%</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className="text-blue-400 font-semibold">{model.winRate}%</span>
                      </td>
                      <td className="p-3 text-center">
                        <span className="text-gray-300 text-sm">{model.description}</span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>

        {/* Performance Charts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid lg:grid-cols-2 gap-8"
        >
          {/* ROI Comparison Chart */}
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">ROI Karşılaştırması</h3>
            <div className="space-y-4">
              {selectedModelData.map((model, index) => (
                <div key={model.id} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300">{model.name}</span>
                    <span className="text-green-400 font-semibold">{model.roi}%</span>
                  </div>
                  <div className="bg-gray-700 rounded-full h-3">
                    <div 
                      className="bg-green-500 h-3 rounded-full transition-all duration-1000"
                      style={{ width: `${(model.roi / 60) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Win Rate Comparison Chart */}
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Win Rate Karşılaştırması</h3>
            <div className="space-y-4">
              {selectedModelData.map((model, index) => (
                <div key={model.id} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300">{model.name}</span>
                    <span className="text-blue-400 font-semibold">{model.winRate}%</span>
                  </div>
                  <div className="bg-gray-700 rounded-full h-3">
                    <div 
                      className="bg-blue-500 h-3 rounded-full transition-all duration-1000"
                      style={{ width: `${(model.winRate / 60) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Recommendations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-8"
        >
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <TrophyIcon className="w-6 h-6 mr-2 text-yellow-400" />
              Öneriler
            </h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2">🏆 En İyi Performans</h3>
                <p className="text-gray-300 text-sm">
                  Ultimate AI System en yüksek ROI (%51) ve win rate (%52) ile 
                  en iyi performansı gösteriyor.
                </p>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2">⚡ Hızlı Başlangıç</h3>
                <p className="text-gray-300 text-sm">
                  Adaptive Simple AI, basit ama etkili yaklaşımı ile 
                  yeni başlayanlar için ideal.
                </p>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2">🔄 Gelişmiş Özellikler</h3>
                <p className="text-gray-300 text-sm">
                  Enhanced Adaptive AI, kriz yönetimi ve adaptif öğrenme 
                  özellikleri ile gelişmiş deneyim sunuyor.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ModelComparison; 