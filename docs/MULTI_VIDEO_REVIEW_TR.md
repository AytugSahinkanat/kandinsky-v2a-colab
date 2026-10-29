# Kandinsky çoklu video dinleme değerlendirmesi

## Amaç

Kandinsky'nin mevcut video + kısa metin istemi üretimini birkaç oyun sahnesinde, tekrar üretilebilir biçimde dinleyiciye değerlendirtmek. Bu bir eğitim işi değildir. Her video için aynı istem ve aynı model ayarları korunur; yalnızca iki seed değiştirilir. İlk pilot böylece hem sahneler arasındaki farkı hem seed'in aday seçimine katkısını görür.

## İlk deney kapsamı

- 2–5 kısa video sahnesi; pratik başlangıç önerisi 3 sahne.
- Her sahne için tek, beş saniyelik pencere. Olay daha sonra oluyorsa `start_seconds` o ana göre ayarlanır.
- Kandinsky 6.0 Lite Distill ve aynı kısa, ses odaklı istem.
- Her sahne için seed 42 ve 123; toplam 6 aday (3 sahne seçilirse).
- Değerlendirme boyutları: sahne/olay uyumu, video-ses zamanlaması, ses kalitesi, artefakt/gürültü, istenmeyen müzik/konuşma ve adayı üründe tutma kararı.

İki seed arasında aday farkı görmek, seed'lerden birinin her zaman daha iyi olduğunu kanıtlamaz. Üç sahne küçük ve yön gösterici bir pilot sağlar; genel başarı oranı çıkarmaz. Bu aşama Kandinsky'yi kendi içinde puanlar, ElevenLabs veya mevcut Orfeo akışıyla henüz karşılaştırmaz.

## Colab kullanımı

1. `Kandinsky_V2A_MultiVideo_Review.ipynb` dosyasını Colab'de A100 runtime ile aç.
2. İki-beş MP4/MOV/M4V video yükle.
3. Notebook'un yazdırdığı tam dosya adlarını `SCENE_CONFIG` içine gir. Her dosya için kısa olay prompt'u ve olayı içeren `start_seconds` ayarla.
4. Hücreleri sırayla çalıştır. Her sahne iki seed ile üretilir; CLI her adayda modeli yeniden yükleyebileceğinden üretimler ardışık ilerler.
5. `Kandinsky_Review_Researcher_Artifacts.zip` dosyasını indir. Çıkardığında araştırmacı anahtarını ve tüm çıktıları koru. Katılımcıya **yalnızca** içindeki `Participant_Package.zip` dosyasını ver.

### Katılımcı akışı

Katılımcı ZIP'i çıkarır ve `Review.html` dosyasını Chrome, Edge veya Firefox'ta açar. İnternet veya hesap gerekmez. Video sessiz oynatılır; aday sesler ayrıca çalınır. Sahne ve aday sırası katılımcı başına karıştırılır. Puanlar tarayıcıda tutulur; kişi tamamlayınca JSON yanıtını indirip araştırmacıya iletir. Sunucuya otomatik yükleme yoktur.

Katılımcı paketi kaynak video kesitlerini ve üretilmiş sesleri içerir. Dışarı paylaşılmasına uygun olmayan müşteri/özel görüntüleri bu şekilde dağıtma. Herkese açık web sayfasına yüklemek ayrıca erişim kararıdır; bu notebook kendiliğinden yayımlama yapmaz.

## Yanıtları birleştirme

Katılımcılardan gelen `kandinsky_answers_*.json` dosyalarını ayrı bir klasörde topla. Araştırmacı anahtarını katılımcılara gönderme.

```powershell
python tools/aggregate_kandinsky_review.py "review/researcher_key.json" "review/responses" "review/summary.json"
```

Özet; her seed adayı için puan ortalamalarını, istenmeyen ses sayısını, üründe tutma kararlarını ve sahne başına tercih sayılarını verir. Ortalama puanlar başarı yüzdesi değildir. Katılımcı sayısı azsa bunlar yalnızca yön gösterici insan geri bildirimidir.

Artefakt/gürültü puanında **düşük değer daha iyidir** (1 = yok, 5 = şiddetli). Diğer üç puanda yüksek değer daha iyidir.

## Eşleştirme ve mahremiyet

- Katılımcı sayfası seed, model revizyonu ve istem metnini göstermez. Bunların eşlemesi yalnızca `researcher_key.json` içinde saklanır.
- `Participant_Package.zip` araştırmacı anahtarını içermez; indirilen üst araştırmacı arşivini paylaşma.
- İsim/e-posta istenmez. Katılımcı JSON'u kullanıcı takma adını yalnızca kendisi girerse içerir.
- Puanlamalar ağ üzerinden gönderilmez. Bu yüzden yanıt JSON'unu indirme ve geri iletme katılımcının sorumluluğundadır.
- Video ve ses dosyaları katılımcı paketinden çıkarılabilir; bu format erişim kısıtlaması sağlamaz.

## Çıktı / iddia sınırları

Bu çalışma şu anki Kandinsky modelinin video destekli ses üretimini ve seed adayları arasından seçim yapılabilirliğini değerlendirir. Bu, prompt'suz üretim, doğrudan fiziksel parametre kontrolü, ses katmanlarını one-shot olarak ayırma, ürün API'si veya ticari lisans onayı anlamına gelmez. Bunlar ayrı iş kalemleridir.

Model kodu ve ağırlıklar için ticari kullanım ve bağımlılık/lisans denetimi ayrıca sürmelidir. Bu dinleme aracı model ya da medya lisansına yeni bir izin eklemez.

