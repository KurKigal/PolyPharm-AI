# User Stories — Kabul Kriterleri

Bu doküman, `docs/product_backlog.md` içindeki Sprint 1–3 user story'lerinin
kabul kriterlerini ve güncel kapsam kararlarını içerir.

---

## US-01 — Demo hasta seçimi

**Doktor olarak** demo hasta seçebilmek istiyorum; **böylece** ürünü hızlıca test edebilirim.

**Kabul Kriterleri:**
- Streamlit arayüzünde önceden tanımlı demo hastalar (`data/sample_patients.json`) listeden seçilebilir.
- Demo hasta seçildiğinde yaş, cinsiyet, mevcut ilaç listesi ve laboratuvar değerleri (eGFR, kreatinin, AST, ALT) otomatik doldurulur.
- Kullanıcı ek bir veri girişi yapmadan doğrudan analiz akışına geçebilir.

---

## US-02 — Manuel hasta girişi

**Doktor olarak** manuel hasta bilgisi girebilmek istiyorum; **böylece** farklı klinik senaryoları deneyebilirim.

**Kabul Kriterleri:**
- Yaş (0–120), cinsiyet, mevcut ilaç listesi alanları manuel olarak doldurulabilir.
- Girilen ilaç isimleri normalize edilir (baş/son boşluk temizlenir, büyük/küçük harfe duyarsız tekrarlar tekilleştirilir).
- Zorunlu alanlar boş bırakıldığında (`Patient`/`PrescriptionRequest` validasyonu) kullanıcıya uyarı gösterilir.

---

## US-03 — Yeni ilaç analizi

**Doktor olarak** mevcut ilaçları ve yeni ilacı analiz ettirmek istiyorum.

**Kabul Kriterleri:**
- Yeni yazılmak istenen ilaç adı girilebilir ve boş bırakılamaz (`min_length=1`).
- "Analiz Et" tetiklendiğinde `Orchestrator.analyze()` çağrılır ve tüm agent'lar (Interaction, LabRisk, Scoring, Report) sırayla çalışır.
- Analiz sonucu ekranda güvenlik skoru, risk seviyesi ve bulgu listesi olarak gösterilir.

---

## US-04 — İlaç-ilaç etkileşim kontrolü

**Sistem olarak** ilaç-ilaç etkileşimlerini demo veri tabanından kontrol etmek istiyorum.

**Kabul Kriterleri:**
- `InteractionAgent`, yeni ilacı hastanın mevcut ilaç listesindeki her bir ilaçla `data/demo_interactions.json` üzerinden karşılaştırır.
- Eşleşen bir etkileşim bulunursa `RiskFinding` (başlık, önem derecesi, açıklama, öneri) üretilir.
- Etkileşim bulunmazsa ilgili agent'tan boş bulgu listesi döner; sistem hatasız devam eder.

---

## US-05 — Laboratuvar temelli risk sinyalleri

**Sistem olarak** laboratuvar değerlerine göre risk sinyali üretmek istiyorum.

**Kabul Kriterleri:**
- `LabRiskAgent`, eGFR ve kreatinin değerlerine göre böbrek fonksiyonu riskini değerlendirir.
- `LabRiskAgent`, AST ve ALT değerlerine göre karaciğer fonksiyonu riskini değerlendirir.
- Hastanın yaşı ve mevcut ilaç sayısına göre polifarmasi riski ayrıca değerlendirilir.
- Tüm laboratuvar değerleri tanımlı aralıklar içinde olmalıdır (örn. eGFR 0–150, kreatinin 0–20); aralık dışı girişte validasyon hatası verilir.

---

## US-06 — Güvenlik skoru ve risk seviyesi

**Doktor olarak** güvenlik skoru ve risk seviyesi görmek istiyorum.

**Kabul Kriterleri:**
- `ScoringAgent`, `InteractionAgent` ve `LabRiskAgent`'tan gelen tüm bulguları önem derecesine göre (critical > high > medium > low) sıralar.
- Bulgulara göre 0–100 arası bir `safety_score` ve buna karşılık gelen bir `risk_level` (örn. düşük/orta/yüksek) hesaplanır.
- Sonuç, kullanıcı arayüzünde net ve tek bakışta anlaşılır şekilde gösterilir.

---

## US-07 — Raporu dışa aktarma

**Doktor olarak** analiz raporunu indirebilmek istiyorum.

**Kabul Kriterleri:**
- `ReportAgent`, bulgular ve güvenlik skorunu okunabilir bir özet (`recommendation_summary`) haline getirir.
- Tam analiz, Markdown formatında (`markdown_report`) indirilebilir.
- Ham analiz çıktısı JSON formatında da arayüzde görüntülenebilir.

---

## US-08 — Temel testler

**Geliştirici olarak** temel testleri çalıştırmak istiyorum; **böylece** analiz mantığının doğru çalıştığını doğrulayabilirim.

**Kabul Kriterleri:**
- `pip install -r requirements.txt` sonrası `pytest` kurulu olur.
- `python -m pytest -q` komutu proje kök dizininde hatasız/anlamlı sonuç döner.
- En az MVP akışının uçtan uca (hasta girişi → analiz → sonuç) doğru çalıştığını doğrulayan bir test seti bulunur.

> **Not:** Bu kriter Sprint 1 sonunda backlog'da "Devam Ediyor" olarak işaretlenmiştir; `tests/` klasörünün eklenmesi Sprint 2'ye taşınmıştır.

---

## US-09 — Sprint 1 dokümantasyonu

**Ürün ekibi olarak** Sprint 1 çıktılarını GitHub üzerinde belgelemek istiyorum.

**Kabul Kriterleri:**
- `README.md` içinde takım, ürün, mimari ve kurulum bilgileri eksiksiz yer alır.
- `docs/sprint1/` altında Sprint Backlog, Daily Scrum notları, Sprint Review ve Retrospective belgeleri bulunur.
- Ürünün çalıştığını gösteren en az iki ekran görüntüsü (`docs/sprint1/screenshots/`) eklenir.
- Tüm dokümanlar GitHub reposunda public olarak erişilebilir durumdadır.

---

## US-10 — Harici ilaç veri kaynakları

**Geliştirici olarak** harici ilaç kaynaklarına bağlanmak istiyorum; **böylece** demo
veri sınırının ötesinde resmi kaynak bilgisi kullanabilirim.

**Kabul Kriterleri:**

- RxNorm yerel veritabanı ilaç adı ve marka-etken madde çözümlemesi sağlar.
- openFDA istemcisi prospektüs uyarılarını zaman aşımı ve önbellekle getirir.
- Harici kaynak hataları kural tabanlı analizi durdurmaz.

---

## US-11 — Provider katmanı

**Geliştirici olarak** veri kaynaklarını tek servis arkasında toplamak istiyorum;
**böylece** agent'lar kaynak ayrıntılarına bağımlı kalmaz.

**Kabul Kriterleri:**

- `DrugDataService`, RxNorm, openFDA ve yerel kural sağlayıcısını ortak akışta kullanır.
- Harici kaynaklar bağımsız olarak açılıp kapatılabilir.
- Agent testlerinde sahte sağlayıcılar kullanılabilir.

---

## US-12 — RAG araştırması

**Geliştirici olarak** resmi kaynaklar için RAG yaklaşımını değerlendirmek istiyorum.

**Kabul Kriterleri:**

- Mevcut RxNorm/openFDA yaklaşımıyla RAG yaklaşımının kapsam farkı belgelenir.
- Implementasyon kararı ve gerekçesi kayıt altına alınır.
- Araştırma sonucu `docs/sprint2/RAG_RESEARCH.md` içinde bulunur.

---

## US-13 — Ayrıntılı rapor

**Doktor olarak** daha okunabilir bir analiz raporu almak istiyorum.

**Kabul Kriterleri:**

- Markdown raporu risk skoru, sıralı bulgular ve kaynak bilgisini içerir.
- RxNorm/openFDA bilgileri mevcut olduğunda rapora eklenir.
- AI özeti üretildiğinde ayrı ve açıkça işaretlenmiş bölümde gösterilir.

---

## US-14 — Akıcı arayüz

**Kullanıcı olarak** analiz sonucunu düzenli bir arayüzde incelemek istiyorum.

**Kabul Kriterleri:**

- Sonuçlar özet, risk bulguları, ilaç bilgisi ve ham çıktı sekmelerine ayrılır.
- Risk seviyeleri tutarlı renk ve etiketlerle gösterilir.
- RxNorm eşleşmesi ve veri kaynağı durumu kullanıcıya görünürdür.

---

## US-15 — Genişletilmiş test kapsamı

**Geliştirici olarak** regresyonları otomatik testlerle yakalamak istiyorum.

**Kabul Kriterleri:**

- Agent, provider, orchestrator ve rapor katmanlarının birim testleri bulunur.
- Harici API çağrıları testlerde mock'lanır veya kapatılır.
- Testler API anahtarı ve internet gerektirmeden tamamlanır.

---

## US-16 — Tekrar üretilebilir kalite doğrulaması

**Ürün ekibi olarak** projenin kurulumunu ve kalite kontrollerini tekrar üretilebilir
hale getirmek istiyorum.

**Kabul Kriterleri:**

- Doğrudan bağımlılıklar doğrulanmış sürümlere sabitlenir.
- Streamlit açılışı ve çevrimdışı analiz smoke testlerle doğrulanır.
- GitHub Actions, pull request'lerde tüm test setini çalıştırır.
- Beklenmeyen analiz hataları kullanıcı dostu mesajla gösterilir ve loglanır.

---

## US-17 — Final demo ve video

Bu story ürün kararıyla **Not Planned** durumundadır. Final demo senaryosu, sunum
videosu ve yeni ekran görüntüleri Sprint 3 kapsamına dahil edilmemiştir.

---

## US-18 — Final dokümantasyonu

**Ürün ekibi olarak** README ve sprint belgelerini final teslimine hazır hale getirmek
istiyorum.

**Kabul Kriterleri:**

- Product backlog tamamlanan Sprint 2 ve Sprint 3 durumlarını doğru gösterir.
- `docs/sprint3/` altında backlog, daily scrum, review ve retrospective bulunur.
- README güncel kurulum, test sonucu, kapsam kararı ve belge bağlantılarını içerir.
- Canlı deployment yapılmadığı ve production URL bulunmadığı açıkça belirtilir.

---

## Referanslar

- Product Backlog: `docs/product_backlog.md`
- Sprint 1 Backlog: `docs/sprint1/SPRINT_BACKLOG.md`
- Sprint 1 Review: `docs/sprint1/SPRINT1_REVIEW.md`
- Sprint 1 Retrospective: `docs/sprint1/RETROSPECTIVE.md`
- Sprint 2 Backlog: `docs/sprint2/SPRINT_BACKLOG.md`
- Sprint 2 RAG Araştırması: `docs/sprint2/RAG_RESEARCH.md`
- Sprint 3 Backlog: `docs/sprint3/SPRINT_BACKLOG.md`
