# Sprint 2 Review

## Sprint Hedefi

Sprint 1'de oluşturulan MVP'nin veri kalitesini, analiz kapsamını ve kullanıcı deneyimini
harici veri kaynakları ve yapay zeka desteğiyle geliştirmek.

## Gösterilen Ürün Artışı (Increment)

1. **DrugDataProvider katmanı:** RxNorm (lokal) + openFDA (API) tek bir servis arkasında
   birleştirildi. Kaynaklardan biri erişilemez olduğunda uygulama kural tabanlı analizle
   çalışmaya devam ediyor.
2. **RxNorm entegrasyonu:** 23.401 ilaç adı ve 7.544 marka→etken madde ilişkisi içeren
   2,6 MB'lık lokal SQLite veritabanı. Marka adıyla girilen ilaçlar (Coumadin, Lipitor...)
   etken maddeye çözümlenerek etkileşim kurallarıyla eşleştiriliyor.
3. **openFDA entegrasyonu:** Yeni ilacın resmi FDA prospektüs verileri (kutulu uyarı,
   uyarılar, etkileşim metni, endikasyonlar) analize dahil ediliyor; kutulu uyarı varsa
   yüksek şiddetli bulgu olarak skora yansıyor.
4. **Gemini AI özeti:** Kural tabanlı bulgular + openFDA bağlamı, gemini-3.1-flash-lite ile
   Türkçe, hekim odaklı bir klinik özete dönüştürülüyor. API erişilemezse kural tabanlı
   özet devrede kalıyor.
5. **Genişletilmiş veri seti:** Demo etkileşim kuralları 9'dan 29'a çıkarıldı
   (kritik/yüksek/orta/düşük şiddet dağılımlı).
6. **Yenilenen arayüz:** Sekmeli sonuç görünümü (Özet / Risk Bulguları / İlaç Bilgisi /
   Ham Çıktı), RxNorm isim geri bildirimi, veri kaynağı aç-kapa anahtarları, marka→etken
   madde gösterimi.
7. **Gelişmiş rapor:** Markdown raporuna harici kaynak bilgisi ve AI değerlendirmesi eklendi.
8. **Test kapsamı:** 0 → 51 otomatik test (tüm agent'lar, provider'lar, orchestrator;
   openFDA ve Gemini mock'lu).

## Sprint Hedefine Ulaşma Durumu

Planlanan dokuz kalemden sekizi tamamlandı. "Canlıya alma" kalemi Sprint 3'e devredildi;
Streamlit Community Cloud önerilen seçenek olarak not edildi (gizli anahtarlar Streamlit
secrets ile yönetilecek).

## Paydaş Geri Bildirimi

Sprint review için ayrı bir paydaş yorum kaydı tutulmamıştır. Teknik review sonucunda
harici kaynakların hata durumunda kural tabanlı akışa dönmesi korunmuş; final kalite,
CI ve dokümantasyon işleri Sprint 3'e aktarılmıştır.
