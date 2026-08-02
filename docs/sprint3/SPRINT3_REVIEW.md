# Sprint 3 Review

## Sprint Hedefi

PolyPharm AI projesini yerel çalıştırma, otomatik kalite doğrulaması, hata
dayanıklılığı ve dokümantasyon açısından final teslime hazır hale getirmek.

## Tamamlanan Ürün Artışı

1. Doğrudan bağımlılıklar test edilen sürümlere sabitlendi.
2. Pull request ve `main` güncellemelerinde testleri çalıştıran GitHub Actions CI eklendi.
3. Streamlit uygulama açılışı ve harici API kullanmayan analiz akışı smoke testlerle
   güvence altına alındı.
4. Bozuk/okunamayan yerel veri dosyaları uygulamayı durdurmadan loglanır hale getirildi.
5. Beklenmeyen analiz hataları ham traceback yerine kullanıcı dostu mesajla gösterilir.
6. Product backlog, kabul kriterleri ve sprint dokümantasyonu güncellendi.
7. RAG araştırmasının sonucu ve implementasyon yapılmama gerekçesi belgelendi.

## Doğrulama

- Yerel test sonucu: **53 passed**.
- Testlerde openFDA ve Gemini çağrıları çevrimdışı veya mock olarak çalışır.
- Smoke test, Streamlit uygulamasının açıldığını ve openFDA kapalıyken indirilebilir
  rapor ürettiğini doğrular.
- CI sonucu, Sprint 3 pull request'i açıldıktan sonra GitHub Actions üzerinden izlenir.

## Kapsam Dışı

Ürün kararı gereği canlı deployment, production URL, final demo/video ve yeni ekran
görüntüleri hazırlanmamıştır.

## Sonuç

Sprint hedefi karşılanmıştır. Proje bir klinik ürün olarak değil, eğitim amaçlı yerel
karar destek prototipi olarak final teslimine hazırdır.
