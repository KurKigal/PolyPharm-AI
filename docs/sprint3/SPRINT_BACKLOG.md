# Sprint 3 Backlog

## Sprint Hedefi

PolyPharm AI projesini yerel çalıştırma, otomatik kalite doğrulaması, hata
dayanıklılığı ve dokümantasyon açısından final teslime hazır hale getirmek.

## Kapsam Kararı

Proje canlıya alınmayacaktır. Production URL, deployment, final demo senaryosu,
sunum videosu ve yeni ekran görüntüleri bu sprintin kapsamı dışındadır.

| No | User Story / Görev | Öncelik | Durum |
|---|---|---:|---|
| 1 | Doğrudan Python bağımlılıklarını doğrulanmış sürümlere sabitlemek | Yüksek | Tamamlandı |
| 2 | Testleri her pull request'te çalıştıran GitHub Actions CI eklemek | Yüksek | Tamamlandı |
| 3 | Streamlit uygulaması için açılış ve çevrimdışı analiz smoke testleri eklemek | Yüksek | Tamamlandı |
| 4 | Beklenmeyen veri ve analiz hatalarını kullanıcı dostu biçimde yönetmek | Yüksek | Tamamlandı |
| 5 | Product backlog ve user story durumlarını gerçekleşen işle uyumlu hale getirmek | Orta | Tamamlandı |
| 6 | Sprint 3 review, retrospective ve günlük kayıtlarını hazırlamak | Orta | Tamamlandı |
| 7 | README'yi final kapsam ve doğrulama bilgileriyle güncellemek | Orta | Tamamlandı |
| 8 | Uygulamayı canlıya almak ve production URL eklemek | — | Kapsam Dışı |
| 9 | Final demo/video ve yeni ekran görüntüleri hazırlamak | — | Kapsam Dışı |

## Definition of Done

- Temiz ortam kurulumu `requirements.txt` ile tekrar üretilebilir.
- `python -m pytest -q` komutu hatasız tamamlanır.
- Streamlit uygulaması harici API anahtarı olmadan açılır ve analiz üretir.
- GitHub Actions aynı test komutunu pull request'lerde çalıştırır.
- Kullanıcı beklenmeyen analiz hatasında ham traceback yerine anlaşılır mesaj görür.
- Backlog, kabul kriterleri, README ve Sprint 3 belgeleri günceldir.
