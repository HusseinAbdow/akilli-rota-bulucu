.. code:: ipython3

    !pip install networkx
    !python -m pip install --upgrade pip
    


.. parsed-literal::

    Defaulting to user installation because normal site-packages is not writeable
    Requirement already satisfied: networkx in c:\programdata\anaconda3\lib\site-packages (3.3)
    Defaulting to user installation because normal site-packages is not writeable
    Requirement already satisfied: pip in c:\users\elifg\appdata\roaming\python\python312\site-packages (25.3)
    

.. code:: ipython3

    def yolu_Sadelestir(path):
        """
        Verilen yol içerisindeki gereksiz döngüleri (cycle) tespit eder ve temizler.
        Liste yerine Sözlük (Dictionary) kullanarak işlemi hızlandırır.
        Örn: [0, 5, 7, 9, 7, 10] -> [0, 5, 7, 10]
        """
        cleaned = []
        seen = {}  #Sözlük (Dictionary) Sözlük (Dictionary): Anahtar ve Değer (Key : Value) eşleşmesi vardır.
    
        # 'seen' sözlüğü hafıza görevi görür. 
        # Hangi düğümün, temizlenmiş listenin kaçıncı sırasında olduğunu tutar.
        # Yapısı: {Düğüm_No: İndeks_No} örn: {0:0, 5:1, 7:2}
    
        for node in path:
            # DÖNGÜ TESPİTİ
            # Eğer şu anki düğüm (node) zaten hafızada (seen) varsa,
            # demek ki buraya daha önce uğramışız ve bir daire çizip geri gelmişiz.
            if node in seen:
                
                # daha önceki indexe kadar kes
                idx = seen[node]
                cleaned = cleaned[:idx+1]
               # hafizanin temizligi icin
                # Listeyi kestigimiz icin, silinen dugumlerin hafızadan da (seen) silinmesi gerekir.
                # Sadece 'cleaned' icinde kalan dugumler icin sozlugu yeniden olusturuyoruz.
                seen = {n: i for i, n in enumerate(cleaned)}  #Python'da bir listeyi numaralandırmaya yarayan  bir komut.
            else:
                cleaned.append(node) #Listeye ekle
                seen[node] = len(cleaned) - 1 # Hafızaya kaydet (Düğüm: İndeks)
    
        return cleaned
    

.. code:: ipython3

    test_path =  [
        0, 3, 7, 12, 18, 21, 33, 40, 7, 12, 45, 50, 33, 21, 
        77, 88, 99, 77, 12, 3, 150, 160, 170, 12, 18, 200]
    
    print("Orijinal path:", test_path)
    print("Sadeleştirme sonrası:", yolu_Sadelestir(test_path))
    
    test_path2 = [
        5, 9, 14, 22, 30, 41, 55, 60, 14, 22, 30, 90, 95, 
        100, 55, 120, 130, 140, 22, 200, 210, 220, 230, 140, 
        250, 260, 270, 22, 300, 310, 320, 330, 340, 350, 5, 400
    ]
    print("\nOrijinal path2:", test_path2)
    print("Sadeleştirme sonrası:", yolu_Sadelestir(test_path2))
    


.. parsed-literal::

    Orijinal path: [0, 3, 7, 12, 18, 21, 33, 40, 7, 12, 45, 50, 33, 21, 77, 88, 99, 77, 12, 3, 150, 160, 170, 12, 18, 200]
    Sadeleştirme sonrası: [0, 3, 150, 160, 170, 12, 18, 200]
    
    Orijinal path2: [5, 9, 14, 22, 30, 41, 55, 60, 14, 22, 30, 90, 95, 100, 55, 120, 130, 140, 22, 200, 210, 220, 230, 140, 250, 260, 270, 22, 300, 310, 320, 330, 340, 350, 5, 400]
    Sadeleştirme sonrası: [5, 400]
    

.. code:: ipython3

    
    def  yol_gecerli_mi(G, path, S, D):
        """
        Verilen yolun (path) kurallara uygun olup olmadığını denetler.
        1. Yol boş olmamalı.
        2. İstenen kaynaktan (S) başlayıp hedefe (D) varmalı.
        3. Yol üzerindeki tüm adımlar grafikte fiziksel olarak bağlı olmalı.
        """
        # Boş ya da çok kısa path'ler geçersiz
        if not path or len(path) < 2:
            return False
        
        # Başlangıç ve bitiş kontrolü
        if path[0] != S:
            return False
        if path[-1] != D:
            return False
        
        # Her adım graf içinde var mı?
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            if not G.has_edge(u, v): #Hafızadaki Graf veri yapısında u ve v düğümleri arasında tanımlı bir kenar olup olmadığını sorgular.
                return False
        
        return True
    

.. code:: ipython3

    def generate_random_path(G, source, destination, max_steps=300):
        """
        Kaynak (source) düğümünden hedef (destination) düğümüne 
        rastgele ama geçerli bir yol üretir.
        """
        for _ in range(500):  # çok fazla deneme yapabilir
            path = [source]
            current = source
            visited = {source}
    
            while current != destination and len(path) < max_steps:
                neighbors = list(G.neighbors(current))
    
                if not neighbors:
                    break
                
                # Komşuları karıştır (randomness için)
                random.shuffle(neighbors)
    
                # Ziyaret edilmemiş komşular
                unvisited = [n for n in neighbors if n not in visited]
    
                # %80 ziyaret edilmemiş komşulara git
                if unvisited and random.random() < 0.8:
                    next_node = random.choice(unvisited)
                else:
                    # %20 random komşulardan biri
                    next_node = random.choice(neighbors)
    
                path.append(next_node)
                visited.add(next_node)
                current = next_node
    
            if current == destination:
                return yolu_Sadelestir(path)
    
        return None
    

.. code:: ipython3

    import random
    
    def tamamla_path(G, path, D, max_steps=300): #→ GA / SA aşamasında ÖNEMLİ OLACAK.Değiştirilebilir.
        """
        Mutasyon sonrası bozulmuş veya yarım kalmış path'i
        D'ye ulaşacak şekilde tamamlar.
        """
    
        if not path:
            return None
    
        current = path[-1]
        steps = 0
    
        while current != D and steps < max_steps:
            neighbors = list(G.neighbors(current))
    
            if not neighbors:
                return None  
    
            nxt = random.choice(neighbors)
            path.append(nxt)
            current = nxt
            steps += 1
    
        return yolu_Sadelestir(path) 
    

.. code:: ipython3

    #→ Simulated Annealing (SA) kodunda kullanılacak.Değiştirilebilir.
    
    
    def generate_neighbor_path(G, path, S, D): 
        """
        Var olan path üzerinde küçük bir değişiklik yaparak
        SA için komşu yol üretir.
        """
    
        if len(path) < 3:
            return path[:]  
    
        idx = random.randint(1, len(path) - 2)
    
        new_path = path[:idx]
    
        completed = tamamla_path(G, new_path, D)
    
        if completed is None:
            return path[:]
    
        return completed
    

.. code:: ipython3

    #  KODUN TESTİ 
    
    # 1. Rastgele Kaynak (S) ve Hedef (D) seç
    # Path'ler farklı çıksın diye random generator'ı serbest bırak
    #random.seed(None)
    
    # 1. Rastgele Kaynak (S) ve Hedef (D) seç
    nodes_list = list(G.nodes())
    S = random.choice(nodes_list)
    D = random.choice(nodes_list)
    
    
    nodes_list = list(G.nodes())
    S = random.choice(nodes_list)
    D = random.choice(nodes_list)
    
    # S ve D aynı olmasın
    while S == D:
        D = random.choice(nodes_list)
    
    print(f"\n--- Rota Aranıyor: {S} -> {D} ---")
    
    # 2. Fonksiyonunu çağır (Sonucu 'random_path' değişkenine ata)
    random_path = generate_random_path(G, S, D)
    
    if random_path:
        print("Yol Bulundu.")
        
        print(f"path= {random_path}")
        print(f"Adım Sayısı: {len(random_path)}")
        
        # 3. Geçerlilik kontrolü
        is_valid = yol_gecerli_mi(G, random_path, S, D)
        print(f"Yol Geçerli mi? {is_valid}")
    
        
        # Listenin uzunluğu ile Kümenin (eşsiz elemanların) uzunluğu aynı mı?
        if len(random_path) == len(set(random_path)):
            
            print("Hiçbir düğüm tekrar etmiyor.")
        else:
            print("HATA: Tekrar eden düğümler var")
    
    else:
        # 500 deneme sonunda yol çıkmadıysa
        print("Yol bulunamadı. Tekrar deneyin.")


.. parsed-literal::

    
    --- Rota Aranıyor: 171 -> 219 ---
    Yol Bulundu.
    path= [171, 145, 125, 73, 105, 210, 184, 182, 108, 157, 133, 220, 115, 39, 140, 87, 121, 161, 135, 188, 227, 169, 198, 97, 103, 109, 118, 50, 74, 167, 247, 21, 78, 233, 132, 219]
    Adım Sayısı: 36
    Yol Geçerli mi? True
    Hiçbir düğüm tekrar etmiyor.
    
