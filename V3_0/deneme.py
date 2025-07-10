import gymnasium as gym

# CartPole ortamını oluştur
env = gym.make("CartPole-v1", render_mode="human")

# Ortamı sıfırla ve ilk gözlemi al
observation, info = env.reset(seed=42)

for _ in range(1000):
    # Rastgele bir eylem seç (0: sola it, 1: sağa it)
    action = env.action_space.sample()

    # Eylemi gerçekleştir ve geri bildirimleri al
    observation, reward, terminated, truncated, info = env.step(action)

    # Eğer bölüm bittiyse (direk çok eğildi veya araba sınırdan çıktı)
    if terminated or truncated:
        print("Bölüm sona erdi.")
        observation, info = env.reset()

# Ortamı kapat
env.close()