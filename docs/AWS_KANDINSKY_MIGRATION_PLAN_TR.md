# Kandinsky AWS Geçiş Hazırlığı

**Durum:** Plan ve doğrulama ölçütleri hazırlandı. AWS hesabında kaynak başlatılmadı; harcama yapılmadı.

## Amaç

Colab’de çalışan Kandinsky 6.0 **video-to-audio** akışını, AWS üzerinde tekrarlanabilir ve maliyeti izlenebilir tek GPU denemesine taşımak. İlk AWS adımı ürün servisi kurmak veya eğitim yapmak değil; aynı 5 saniyelik örneği AWS’de üretip kalite, süre ve bellek farkını ölçmektir.

## Şu an bildiklerimiz

- Bu akış video ve metin prompt’unu birlikte alıyor; prompt şu an zorunlu. Çıktı, videonun görüntülerini koruyan MP4 içine yazılmış tek ses akışı. Ayrı semantik stem/one-shot üretimi mevcut değil.
- Kandinsky’nin resmî hızlı başlangıç belgesi Python 3.13/3.14 ve NVIDIA GPU istiyor. just setup, GPU’nun compute capability değerini okuyup uygun PyTorch/attention bağımlılıklarını kuruyor.
- Mevcut kullanıcı denemelerinde 5 saniyelik üretim yaklaşık **120 saniye Lite Distill**, **686 saniye tam Lite** sürmüş. Bunlar tekil Colab gözlemleridir; AWS süresi tahmini değildir.
- Kandinsky’nin resmî hız tablosu **text-to-audio-video** ölçüyor. Bizim görevimiz **video-to-audio** olduğu için tablodaki süreleri AWS maliyet tahminine taşımayacağız.
- Geçişten önce Colab’de başarılı olan model, checkpoint, prompt, seed, config ve kaynak video penceresini sabitleyeceğiz. GitHub notebook’larının hareketli bir upstream kaynağı kullandığı yerlerde Kandinsky kaynak commit’ini ayrıca kaydedeceğiz.

## İlk GPU adayı

| Aday | Donanım | Kullanım |
|---|---|---|
| **EC2 p5.4xlarge** | 1 × NVIDIA H100, 80 GiB GPU belleği; 16 vCPU ve 256 GiB sistem belleği | İlk AWS eşdeğerlik ve hız deneyi için önerilen aday |
| EC2 g6e, tek L40S GPU | 48 GiB GPU belleği | Daha düşük maliyetli alternatif; ancak önce Lite/Distill’in gerekli offload ayarlarıyla sığdığı ve hızının yeterli olduğu doğrulanmalı |
| EC2 p4de.24xlarge | 8 × A100 80 GiB | Tek GPU’lu çıkarım deneyi için gereksiz büyük; bu aşamada önerilmiyor |

P5.4xlarge, Colab’de kullandığımız A100 80 GB’a göre aynı GPU belleği sınıfında, ayrıca H100 ve 256 GiB sistem belleği sağlar. Tek kart kullanmak, çoklu GPU dağıtımı ve paralel model yükleme karmaşıklığını şimdilik önler. Kaynaklar: [AWS EC2 instance types](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-types.pdf), [P5 single-GPU duyurusu ve bölge seçenekleri](https://aws.amazon.com/about-aws/whats-new/2025/08/amazon-p5-single-gpu-instances-now-available/).

**İlk seçim önerisi:** Hesapta bölge, kapasite ve kota uygunsa p5.4xlarge On-Demand. AWS duyurusuna göre bu boyut On-Demand olarak Londra, Mumbai, Jakarta, Tokyo ve São Paulo bölgelerinde satın alınabiliyor; bölge/kapasite durumu ve güncel fiyat başlatmadan önce hesapta teyit edilmeli. İstanbul’dan en yakın aday Londra olsa da veri konumu ve şirket politikası kararı etkileyebilir.

## Maliyet yaklaşımı

- AWS fiyatı bölgeye, satın alma türüne ve anlık kapasiteye bağlı. **AWS Pricing Calculator** ile seçilen bölgede On-Demand saatlik fiyatı, EBS diskini ve S3 kullanımını başlatmadan önce hesaplayacağız.
- AWS’nin güncel Capacity Blocks fiyat sayfasında p5.4xlarge için **5,97 ABD doları/saat eşdeğeri** listeleniyor. Ancak bu kısa testler için otomatik olarak uygun değil: Capacity Block süreleri 1 günlük artışlarla satın alınıyor, bedel rezervasyon sırasında peşin alınıyor ve satın alınmış block iptal edilemiyor. Sadece bu fiyatı görüp Capacity Block satın almayacağız.
- İlk kısa deney için bölge/hesap izin veriyorsa On-Demand tercih edilecek; çalışmayan GPU boşta açık bırakılmayacak. Tam maliyet hesabına instance çalışma süresi, EBS, S3, veri aktarımı ve varsa işletim sistemi ücreti girecek.
- P5 ailesi için EC2 Service Quotas’ta On-Demand vCPU kotası gerekebilir. p5.4xlarge 16 vCPU olduğundan, başlatmadan önce ilgili kota ve instance erişimini kontrol edeceğiz.

Kaynaklar: [AWS On-Demand fiyatlandırma](https://aws.amazon.com/ec2/pricing/on-demand/), [Capacity Blocks fiyatları](https://aws.amazon.com/ec2/capacityblocks/pricing/), [Capacity Block süre ve satın alma kuralları](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-blocks-purchase.html), [Capacity Block faturalaması](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-blocks-pricing-billing.html).

## Deney planı

### Aşama 1 — Çalıştırma paketini sabitle

- [ ] Colab’de gerçekten iyi sonuç veren tek 5 saniyelik video kesitini seç.
- [ ] Aynı kısa prompt, seed, checkpoint (Lite Distill veya tam Lite), örnekleme adımı, çözünürlük, attention, offload ve beautifier ayarlarını kaydet.
- [ ] Kaynak video ve prompt dosyasının SHA-256 değerini kaydet; videoyu GitHub’a koyma.
- [ ] Kandinsky upstream commit’ini, notebook commit’ini, model/checkpoint kimliğini ve launch.json/üretim loglarını kaydet.
- [ ] Çalışan Colab ortamından Python, PyTorch, CUDA/driver, just setup çıktısı ve kurulu paket sürümlerini dışa aktar.

### Aşama 2 — AWS tek GPU smoke run

- [ ] AWS bölgesi, P5 quota, kapasite, bütçe alarmı ve EBS boyutunu kontrol et.
- [ ] Instance’ı özel ağda başlat; geniş internete açık SSH/Jupyter portu bırakma. Yönetim erişimi için Systems Manager Session Manager kullan.
- [ ] Model ağırlıklarını Git’e değil, şifreli EBS cache’e indir. Kaynak/çıktı dosyalarını özel S3 bucket’ında tut.
- [ ] İlk koşuda Colab’deki **aynı bilinen config** ile tek üretim yap. Bu koşu donanım değişikliğinin sonucu nasıl etkilediğini gösterir.
- [ ] Model yükleme süresi ile çıkarım süresini ayrı ölç. Tepe GPU belleği, sistem RAM’i, disk, üretim süresi, çıktı SHA-256’sı ve gözlenen kaliteyi JSON raporuna yaz.
- [ ] Üretim ve S3’ye yükleme doğrulandıktan sonra instance’ı durdur/sonlandır; geçici cache’i kalıcı bırakma.

### Aşama 3 — Hız ayarlarını ayrı ölç

İlk eşdeğerlik koşusundan sonra, bir seferde tek değişkeni oynat:

1. Aynı modeli ve aynı girişi, önce Colab’deki SDPA ayarıyla ölç.
2. Sonra H100 için resmî attention/compile önerisini ayrı bir koşuda dene.
3. Aynı video/prompt/seed/checkpoint ile kalite ve süreyi karşılaştır.
4. Sadece süre iyileşiyor ve dinleme kalitesi korunuyorsa optimizasyonu kabul et.

Bu ayrım önemli: resmî H100 benchmark’ı farklı T2AV görevidir; mevcut V2A kalitemize/süremize garanti vermez.

## AWS üzerinde ilk mimari

İlk prototip için Kubernetes/EKS, çok GPU, fine-tuning veya sürekli açık API sunucusu kurmuyoruz.

Orfeo / test script → S3 private input → tek EC2 GPU worker (p5.4xlarge, Kandinsky V2A) → S3 private output (MP4/WAV + metadata JSON) → Orfeo adayları dinler, seçer ve timeline’a taşır.

İlk koşuda iş isteği SSM ile çalıştırılabilir. Tekrarlanabilir sonuç alındıktan sonra aynı Python adapter’ı arka plan worker/job sözleşmesine alırız. Uzun çıkarım süreleri nedeniyle üretimi HTTP isteği açık bekletmek yerine iş kimliği ve durum takibiyle yürütmek daha uygun olur.

## Güvenlik ve veri

- Model token’ı, AWS access key veya kullanıcı sırrı notebook’a ya da GitHub’a yazılmaz.
- AWS worker’a IAM instance role verilir; S3 erişimi yalnızca ilgili özel input/output prefix’leriyle sınırlandırılır.
- S3 public access kapalı, EBS şifreli, çıktı saklama süresi belirli olur.
- Gerçek müşteri videosuyla başlamayız; önce zaten kullanılan test klibiyle teknik smoke test yaparız.
- Model kodu, ağırlık/checkpoint, bağımlılıklar ve eğitim verisinin lisans/provenance incelemesi birbirinden ayrıdır. AWS’ye taşımak ticari lisans onayı anlamına gelmez.

## Başarı ölçütleri ve karar kapısı

AWS smoke test “geçti” sayılacaksa:

1. Bilinen 5 saniyelik input aynı Kandinsky V2A akışıyla tamamlanır.
2. Çıktı video ve ses olarak açılır; üretim logları/ayarları saklanır.
3. Tepe VRAM ve RAM mevcut AWS profiline güvenli payla sığar.
4. Colab ile süre farkı gerçek V2A örneğinde ölçülür; T2AV benchmark’ından tahmin edilmez.
5. Dinleme notunda sahne uyumu, senkronizasyon, ses kalitesi ve artefaktlar ayrı karşılaştırılır.
6. Her koşunun gerçek AWS maliyeti ölçülür ve kullanım başına maliyet formülüne girer.

Bu kapıdan sonra karar: **(a)** H100 üzerinde çıkarım prototipine devam et, **(b)** daha ucuz G6e profiliyle tekrar ölç, veya **(c)** birden çok paralel istek gerekirse worker havuzunu tasarla. Fine-tuning ve oyun event encoder’ı, ayrı lisanslı/aligned veri ve ölçülebilir bir hata hedefi oluşana kadar sonraki aşamada kalır.

## Kaynaklar

- [Kandinsky 6.0 resmî depo ve performans tablosu](https://github.com/kandinskylab/kandinsky-6)
- [Kandinsky hızlı başlangıç: Python/GPU setup](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/quickstart/quick_start.md)
- [Kandinsky video-to-audio modu ve giriş sınırları](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/generation_modes.md)
- [AWS EC2 P5 instance specifications](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-types.pdf)
- [AWS P5.4xlarge availability](https://aws.amazon.com/about-aws/whats-new/2025/08/amazon-p5-single-gpu-instances-now-available/)
- [AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/)
