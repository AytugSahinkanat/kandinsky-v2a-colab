# Orfeo Ses Üretim Modülü — Ürünleştirme Planı v0.1

## Amaç

Orfeo'nun mevcut API tabanlı ses üretiminin yanına video ve oyun olay verisiyle yönlendirilen bir üretim sağlayıcısı eklemek. Kullanıcı prompt yazmak zorunda kalmamalı; sistem sahne/olay bilgisini kısa bir ses niyetine çevirmeli. Kullanıcı adayları dinleyebilmeli, bir parçayı yeniden üretebilmeli ve miks özelliklerini değiştirebilmelidir.

İlk sürüm tek bir modeli her işe zorlamaz. Ortak bir sağlayıcı arayüzü kurar; router'ı en az iki model aynı veri ve ölçütlerle karşılaştırıldıktan sonra ekler.

## Mevcut durum — doğrulanmış ve doğrulanmamış

**Şu ana kadar görülenler**
- Kandinsky V2A video ve metin prompt'unu birlikte alıyor.
- Doğrulanmış temel üretim 5 saniyelik pencere ve tek sürekli ses akışı.
- Seed değişince aynı pencerenin ses adayları değişiyor.
- Kullanıcı örneklerinde senkronizasyon güçlü bulundu; henüz geniş bir sahne kümesinde ölçülmedi.

**Henüz sunulmayanlar**
- Prompt'suz model çağrısı: prompt şu an gerekli; sistem sonradan otomatik yazabilir.
- Ayrı semantik one-shot dosyaları: mevcut çıktı tek sürekli akış.
- Motor sayılarını modelin latent alanına doğrudan bağlama: yapılmadı.
- Genel ticari kalite, uzun kliplerde tutarlılık veya gerçek zamanlı üretim: kanıtlanmadı.

## Kullanıcı akışı

1. Video veya motor bağımsız olay metadata'sı Orfeo'dan alınır.
2. Intent compiler metadata'yı kısa ses niyetine çevirir. Metadata yoksa video analizi kısa bir ses açıklaması önerir.
3. Prompt compiler bu niyetten tek cümlelik, ses odaklı prompt üretir; kamera/ışık/hikâye ayrıntılarını eklemez.
4. Window planner klibi 5 saniyelik işlere böler.
5. Kandinsky provider her pencere için bir veya daha fazla aday üretir.
6. Candidate manager sadece zayıf pencerenin yeniden üretilmesini, önceki iyi adayların korunmasını sağlar.
7. Kullanıcı miks parametrelerini değiştirir ve seçilmiş parçaları timeline'a aktarır.

**İlk ürün sınırı:** 5 saniyelik pencereleri taşıma/değiştirme hedeflenebilir. Bir pencerenin içindeki tek tek darbeleri ayrı one-shot olarak yönetmek sonraki doğrulama aşamasıdır.

## Modüller ve sorumluluklar

- **Orfeo adapter:** video asset ID'si, zaman aralığı ve olay verisini alır; motor bağımsız kalır.
- **Intent/prompt compiler:** metadata şablonunu önce kullanır; metadata yoksa kısıtlı video açıklamasına geçer. Otomatik prompt kısa tutulur. Üretim modeline video da verilmeye devam eder.
- **Window planner:** 5 saniyelik kesitleri ve zaman damgalarını yönetir; örtüşme/birleştirme henüz deneysel.
- **Provider adapter:** ortak generate isteği ve aday cevabı tanımlar. İlk sağlayıcı Kandinsky V2A'dır.
- **Candidate manager:** girdi penceresi, prompt kaynağı/sürümü, checkpoint, seed, süre ve kalite notlarını saklar.
- **Post-processing:** ham üretimi saklar; gain, distance, pan ve reverb'i geri alınabilir ayrı miks adımları olarak uygular.
- **Timeline exporter:** seçilmiş asset'leri başlangıç zamanlarıyla Orfeo'ya verir.

Taslak istek şeması: schemas/sound_job_request.schema.json.

## Sayısal kontrollerin doğru yeri

Material/action/size/intensity ilk adımda intent ve prompt derleyicisine bilgi verir; bunlar Kandinsky'ye doğrudan sayısal latent koşul olarak bağlanmış değildir. Miks aşamasındaki gain yalnızca sinyal seviyesini değiştirir; fiziksel darbe kuvvetiyle eşdeğer değildir. Distance, pan ve reverb üretim sonrasında uygulanabilir. Bunlar ürün kontrolü sağlar ama yeniden üretim koşullandırmasıyla aynı şey değildir. Doğrudan fiziksel koşullandırma için ayrı model/adapter eğitimi ve deney gerekir.

## API taslağı

- POST /v1/sound-jobs — video, pencere, niyet, prompt politikası, checkpoint, seed ve miks ayarıyla iş oluşturur.
- GET /v1/sound-jobs/{job_id} — durum, adaylar ve kaynak bilgilerini döndürür.
- POST /v1/sound-jobs/{job_id}/windows/{window_id}/regenerate — yalnızca seçilen pencereyi yeniler.
- PATCH /v1/sound-assets/{asset_id}/mix — ham dosyayı değiştirmeden miks ayarlarını değiştirir.
- POST /v1/sound-jobs/{job_id}/export — seçilmiş adayları zaman çizelgesine aktarır.

İlk aşamada HTTP servisi şart değil; notebook/Python adapter aynı alanları kullanarak prototiplenebilir.

## Yol haritası ve karar kapıları

### 0. Çoklu video dinleyici pilotu
2–5 farklı beş saniyelik oyun sahnesinde aynı Kandinsky Lite Distill ayarlarıyla ikişer seed adayı üret. Katılımcılar sahne/olay uyumu, zamanlama, kalite, artefakt ve üründe tutma kararını değerlendirir. Bu adım model kıyaslaması veya genel başarı oranı iddiası değildir; hangi sahnelerde aday seçimi işe yarıyor sorusuna küçük bir insan değerlendirmesi sağlar.

### A. Prompt otomasyonu
Aynı 5 saniyelik sahnede aynı checkpoint ve seed ile elle kısa prompt, motor metadata şablonu ve video açıklaması yollarını karşılaştır. Olay uyumu, doğallık, artefakt ve istenmeyen müzik/konuşmayı ayrı puanla. Sonuç, prompt'u otomatikleştirmenin kalite etkisini gösterecek.

### B. Pencere yenileme
Mevcut seed sweep'ten en iyi adayı seç; 15 saniyelik örnekte zayıf pencereyi yenilerken diğer adayları koru. Her pencerenin üretim bilgisini sakla.

### C. Timeline ve geçiş
Üç 5 saniyelik parçayı sırala; senkronizasyonu, tekrarları ve ek yerlerini dinle. Örtüşme/crossfade'i ancak ayrı A/B ile seç.

### D. Miks kontrolleri
Aynı ham sesin kopyalarında gain, distance filtresi, pan ve reverb'i ayrı ayrı dene. Kaynak wav her zaman saklansın ve işlemler geri alınabilsin.

### E. Orfeo bağlantısı ve router
Sözleşmeyi Orfeo arayüzüne bağla. Router'ı iki veya daha fazla sağlayıcı aynı örneklerde kalite, gecikme, maliyet ve lisans karşılaştırmasından sonra ekle.

## Ölçülecekler

Olay uyumu, doğallık, artefakt/gürültü, istenmeyen sesler, video-ses zamanlaması, pencereler arası devamlılık, yeniden üretimde aday seçme başarısı, süre/bellek ve lisans/checkpoint izlenebilirliği. Tek klip genel başarı kanıtı sayılmaz.

## Lisans ve izlenebilirlik

Her sağlayıcının kodu, kesin ağırlık checkpoint'i, bağımlılıkları ve veri kökeni ayrı kaydedilir. Kandinsky model kartındaki MIT etiketi, bağımlılıkların veya eğitim verisinin ticari temizliğini tek başına kanıtlamaz. Ticari dağıtımdan önce bunlar ayrıca incelenir. API anahtarları ve token'lar notebook'a/repoya yazılmaz.

