# RAG Araştırma Notu

## Amaç

Resmi ilaç kaynaklarının Retrieval-Augmented Generation (RAG) yaklaşımıyla
sorgulanmasının PolyPharm AI prototipine sağlayacağı katkıyı değerlendirmek.

## Değerlendirme

- RxNorm isim normalizasyonu için yerel ve deterministik bir SQLite kaynağı sağlar.
- openFDA, resmi prospektüs bölümlerini API üzerinden doğrudan döndürür.
- `FdaLabelInteractionAgent`, prospektüs metninde ilaç eşleşmesini kaynak metniyle
  birlikte raporlar.
- Gemini yalnızca mevcut bulguları özetler; yeni klinik bilgi kaynağı olarak kullanılmaz.

Mevcut prototip kapsamı sınırlı ve veri kaynakları yapılandırılmış olduğu için ayrıca
bir vektör veritabanı ve retrieval hattı eklemek operasyonel karmaşıklığı artıracaktır.
Kaynak güncelliği, chunk seçimi ve klinik alıntı izlenebilirliği için ek doğrulama da
gerektirir.

## Karar

Sprint 2'de RAG implementasyonu yapılmamasına karar verilmiştir. Resmi kaynak erişimi
RxNorm ve openFDA üzerinden sürdürülür; yapay zeka katmanı yalnızca elde edilen
bulguları özetler. Serbest biçimli, çok dokümanlı resmi kaynak koleksiyonu eklendiğinde
RAG ayrı bir ürün artışı olarak yeniden değerlendirilebilir.
