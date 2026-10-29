# Kandinsky çoklu video dinleme değerlendirmesi

## Amaç

Altı farklı sahnede Kandinsky'nin video + kısa ses prompt'u ile ürettiği sesleri dinleyicilere puanlatmak. Bu bir eğitim işi değil; her video için tek üretim var ve farklı seed karşılaştırması yapılmıyor.

## Deney kapsamı

- Wikimedia Commons üzerinde CC0 1.0 olarak işaretlenmiş altı kaynak klip.
- Şehirde yürüyen insanlar, ledge üzerinde yürüyen küçük kuş, kameraya bakan kuş, akan dere, şömine ve açılan kapı.
- Her kaynaktan beş saniyelik sessiz video penceresi hazırlanır; kaynak videonun sesi atılır.
- Her sahne için kısa olay/ses prompt'u notebook içinde hazırdır. Promptlar Kandinsky'ye videoyla birlikte verilir.
- Aynı Kandinsky 6.0 Lite Distill ayarı ve seed 42 ile video başına bir üretim yapılır.
- Altı değerlendirme ölçüsü: sahne uyumu, video-ses zamanlaması, ses kalitesi, gürültü/artefakt şiddeti, istenmeyen müzik veya konuşma, sesi kullanma kararı.

Bu, küçük ve yön gösterici bir insan değerlendirmesidir. Genel başarı yüzdesi çıkarmaz; prompt etkisini videodan ayırmaz; yalnızca seed 42 ile üretilen örnekleri kapsar.

## Colab kullanımı

1. Kandinsky_V2A_MultiVideo_Review.ipynb dosyasını GitHub üzerinden Colab'de aç.
2. A100 runtime seçip hücreleri sırayla çalıştır.
3. Notebook videoları Wikimedia Commons'tan kendisi indirir. Video yükleme hücresi veya elle dosya adı kopyalama yoktur.
4. Her video için tek Kandinsky üretimi çalışır. Üretimler sırayla ilerler; model her üretim komutunda yeniden yüklenebilir.
5. Kandinsky_Six_Scene_Review_Artifacts.zip arşivini indir. Katılımcılara yalnızca içindeki Participant_Package.zip dosyasını gönder; researcher_key.json ve generation_bundle.zip araştırmacıda kalır.

## Katılımcı akışı

Katılımcı ZIP'i çıkarıp Review.html dosyasını Chrome, Edge veya Firefox'ta açar. İnternet veya hesap gerekmez. Video sessiz oynatılır, üretilen ses tek bir oynatıcıdan dinlenir. Sahne sırası katılımcı başına karıştırılır. Her kişi yanıt JSON'unu indirip araştırmacıya iletir; sunucuya otomatik yükleme yapılmaz.

Katılımcı paketi videoları ve sesleri içerir. Kaynak listesi ile CC0 sayfa bağlantıları VIDEO_SOURCES.txt dosyasındadır. Bu format erişim kısıtlaması sağlamaz; özel veya paylaşılmaması gereken görüntüler için kullanılmamalıdır.

## Yanıtları birleştirme

Katılımcı yanıt JSON'larını ayrı bir klasöre, araştırmacı anahtarını da paketin dışına koy. Ardından şu komutu çalıştır:

    python tools/aggregate_kandinsky_review.py "researcher_key.json" "responses" "summary.json"

Özet sahne başına puan ortalamalarını, istenmeyen ses bildirimlerini, kullanma kararlarını ve yazılı notları verir. Gürültü/artefakt puanında düşük değer daha iyidir; diğer sayısal puanlarda yüksek değer daha iyidir.

## Lisans ve iddia sınırları

Notebook içindeki her video bağlantısı, Commons sayfasında CC0 1.0 olarak işaretlenmiş bir dosyaya gider; kaynak adı, sayfa, çözümlenen indirme URL'si ve SHA-256 araştırma paketinde kaydedilir. Bu, bu videoların lisans bilgisini izlenebilir kılar. Kandinsky modelinin, ağırlıklarının ve bağımlılıklarının lisansı ayrı konudur; bu dinleme paketi model lisansına izin eklemez.

Bu deney prompt'suz üretim, fiziksel parametre kontrolü, ses katmanlarını ayırma, Orfeo/ElevenLabs ile kıyaslama veya ticari kullanıma hazır olma iddiası taşımaz.
