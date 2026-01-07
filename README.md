# Akıllı Rota Bulucu (Smart Route Finder)

Bu proje, ağ (graph) yapıları üzerinde **akıllı rota bulma** problemini çözmek için geliştirilmiştir. Farklı algoritmalar (Genetic Algorithm, ACO, Q-Learning vb.) kullanılarak en uygun rotanın bulunması ve sonuçların **grafik arayüz (UI)** üzerinden görselleştirilmesi amaçlanmaktadır.

Proje; algoritma katmanı, veri üretimi/işleme katmanı ve kullanıcı arayüzü olacak şekilde yeniden düzenlenmiştir.

---

## 📁 Proje Klasör Yapısı

```
akilli-rota-bulucu/
│
├── Arayuz/                 # Grafik kullanıcı arayüzü (UI)
│   ├── main.py             # Uygulamanın çalıştırıldığı ana dosya
│   ├── ui/                 # UI bileşenleri
│   └── resources/          # Görseller ve statik dosyalar
│
├── ACO_Algorithm.py        # Ant Colony Optimization algoritması
├── GeneticAlgorithm.py     # Genetic Algorithm algoritması
├── QLearning.py            # Q-Learning algoritması
├── Metrics.py              # Performans metrikleri
├── generate_graf.py        # Grafik (graph) üretimi
├── path_utilities.py       # Yol / rota yardımcı fonksiyonları
│
├── data/                   # Veri dosyaları (CSV vb.)
├── requirements.txt        # Python bağımlılıkları
└── README.md               # Proje dokümantasyonu
```

> ⚠️ Not: Önceki sürümlerde bulunan yinelenmiş klasör yapısı kaldırılmıştır. Projenin **tek geçerli yapısı** yukarıdaki gibidir.

---

## ⚙️ Gereksinimler

* Python **3.9+** (önerilen)
* Gerekli Python kütüphaneleri (requirements.txt içinde listelenmiştir)

---

## 📦 Kurulum

1️⃣ Repoyu klonlayın:

```bash
git clone https://github.com/HusseinAbdow/akilli-rota-bulucu.git
cd akilli-rota-bulucu
```

2️⃣ (Önerilen) Sanal ortam oluşturun:

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3️⃣ Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

---

## ▶️ Uygulamayı Çalıştırma

Uygulamanın **ana giriş noktası (main)** aşağıdaki dosyadadır:

```
Arayuz/main.py
```

Çalıştırmak için:

```bash
python Arayuz/main.py
```

Bu komut grafik arayüzü başlatır ve rota bulma algoritmalarını UI üzerinden kullanmanızı sağlar.

---

## 🧠 Kullanılan Algoritmalar

* **Genetic Algorithm** – Evrimsel optimizasyon
* **Ant Colony Optimization (ACO)** – Karınca koloni tabanlı rota bulma
* **Q-Learning** – Takviyeli öğrenme yaklaşımı

Algoritmalar kök dizinde yer almakta ve UI tarafından çağrılmaktadır.

---

## 🧪 Geliştirme Notları

* `__pycache__/` klasörleri GitHub’a dahil edilmemelidir
* Yeni algoritma eklerken kök dizin yapısı korunmalıdır
* Büyük yapısal değişikliklerden sonra `git reset --hard origin/main` gerekebilir

---

## 👥 Katkı

Bu proje akademik bir çalışma kapsamında geliştirilmiştir. Katkı sağlamak için:

1. Fork alın
2. Yeni bir branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull Request gönderin

---

## 📄 Lisans

Bu proje eğitim amaçlıdır. Lisans bilgisi daha sonra eklenecektir.

---

## ✍️ Not

Bu README, proje yapısının sadeleştirilmesi ve UI merkezli kullanım amacıyla hazırlanmıştır. Eski klasör yapıları artık geçerli değildir.
