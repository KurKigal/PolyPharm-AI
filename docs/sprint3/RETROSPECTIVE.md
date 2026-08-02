# Sprint 3 Retrospective

## İyi Gidenler

- Mevcut 51 test temiz ortamda çalıştırıldı ve iki UI smoke testiyle 53'e çıkarıldı.
- CI, bağımlılık sürümleri ve hata yönetimi aynı kalite turunda tamamlandı.
- Sprint 2 backlog durumları gerçekleşen ürün artışıyla uyumlu hale getirildi.
- RAG ile doğrudan API yaklaşımı arasındaki karar açıkça belgelendi.

## Zorlayan Noktalar

- Yerel sanal ortam, `requirements.txt` içindeki bazı paketleri içermiyordu.
- GitHub CLI oturumu yenilenmeden branch ve yayın akışı başlatılamadı.
- Eski belgelerde tamamlanmış Sprint 2 işleri hâlâ backlog olarak görünüyordu.

## Alınan Aksiyonlar

- Doğrudan bağımlılıklar test edilmiş sürümlere sabitlendi.
- Pull request tabanlı otomatik test eşiği eklendi.
- UI çalışma akışı smoke test kapsamına alındı.
- Backlog ve user story kabul kriterleri güncellendi.

## Sonraki Adımlar

- CI başarısız olursa pull request birleştirilmeden önce düzeltilmeli.
- Yeni özellikler ayrı user story ve kabul kriteriyle planlanmalı.
- Klinik kullanım düşünülürse veri kaynağı doğrulaması, güvenlik, gizlilik ve mevzuat
  çalışmaları ayrı bir ürün fazı olarak ele alınmalı.
