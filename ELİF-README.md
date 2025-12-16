Elif'in Kodu için README:

GÜNCELLEME: 1. nin yaptığı değişiklikler üstüne kodlar üzerinde güncelleme yapılmıştır

3) Elif → Random Path & Path Utilities
📌 Elif’in görevi nedir?
 GA ve SA çalışabilmek için başlangıç yollarına ihtiyaç duyar. 
Elif bu yolları rastgele ama geçerli şekilde üreten kişi olacak. 
📌 Elif ne yapacak?
 random_path(S, D) fonksiyonu S’den başlar Komşular arasından random seçim yaparak ilerler D’ye ulaşınca path döndürür
Adım sayısı çok artarsa durdurur simplify_path Döngüleri (cycle) bulur Aynı node ikinci kez geçildiyse aradaki kısmı siler Path’i temiz hale getirir
Path doğrulama Path S’den D’ye gidiyor mu?
 Tüm edge’ler graf içinde geçerli mi? GA ve SA’ya yardımcı fonksiyonlar 
 Mutasyon sonrası path tamamlama SA’da komşu (neighbor) üretimine destek 
⚡ Sonuç: Elif’in random path fonksiyonu → Hüseyin (graph), Hüseyin (GA), Ammar (SA) tarafından kullanılacak yapı taşlarını üretir.

Yazdığım random path fonksiyonlarını, Hussein'in oluşturduğu graf üzerinde test ettim.

generate_random_path(G, S, D)
→ S’den D’ye rastgele ama geçerli bir yol üretir.

yolu_Sadelestir(path)
→ Path içindeki döngüleri temizler, gereksiz tekrarları siler.

yol_gecerli_mi(G, path, S, D)
→ Yolun gerçekten S’den başlayıp D’ye gidip gitmediğini ve tüm adımların graf içinde geçerli olup olmadığını kontrol eder.

tamamla_path(G, path, D)
→ Mutasyon sonrası bozulmuş ya da yarım kalmış path’i D’ye kadar tamamlar.

generate_neighbor_path(G, path, S, D)
→ SA için mevcut path’e küçük bir değişiklik yaparak yeni bir komşu yol üretir.


