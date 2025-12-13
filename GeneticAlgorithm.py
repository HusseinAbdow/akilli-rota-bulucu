import FriendsRandomPath as rp
import Graph as gp
import Metrics as mr
import random

def population(G,source,target,size):
    #popülasyon oluşturma işlemi
    pop_list=[]
    tester=0
    while tester<(size*10):#Alacağımız kadarın 10 katı kadar deneme verdim.Her bir yol girmesi için 10 şans verdim.
        list1=rp.generate_random_path(G,source,target)#Elifin oluşturduğu rastgele yol oluşturma fonksiyonuyla rastgele yollar aldım
        if list1!=None and list1 not in pop_list and len(list1)>=2:#Eğer bu yol var olup olmadığını,popülasyonda var olup olmadığını ve en az 2 node olup olmadığına bakıyor
            pop_list.append(list1)

        if len(pop_list)==size:#Önceden popülasyon dolarsa döngüyü kırıyor.
            break
        tester+=1
    return pop_list


def fitness_calculation(G,pop_list,w1=0.33, w2=0.33,w3=0.34,max_delay=100):
    #fitness değeerini hesaplama fonsiyonu,burada aslında maliyet hesaplanıyor.Yani en az değeri olan daha iyi.
    pop_fit=[]
    #w1+w2+w3=1.Bu denklem şart.

    for pop in pop_list:#Burada tek tek popülasyonda olanların maliyetini hesaplıyor,yaptığım metrics sınıfında.
        TotalDelay=mr.Total_Delay(G,pop)
        TotalReliability=mr.Total_Reliability(G,pop)
        TotalBandwidth=mr.Total_Bandwidth(G,pop)

        if TotalDelay > max_delay:#Eğer toplam delay bizim belirlediğimiz max_delaydan yüksekse değerini çöp yapıyoruz.Maksat o yolu seçmesini engellemek.
            fitness = 999999
        else:
            fitness=((TotalDelay*w1)+(TotalReliability*w2)+(TotalBandwidth*w3))

        pop_fit.append((pop,fitness))#Burada hem yolu hem de onun maliyetini ekliyoruz tupple olarak.

    return pop_fit

def selection(pop_fit):
    #Anne baba seçimi.
    select=[]
    if len(pop_fit) < 4:#Bu if bloğunda gelen maliyeti hesaplanmış yolların sayısı 4 den az ise direkt anne baba seçimi yapıyor.
        pop_fit.sort(key=lambda x: x[1])
        if len(pop_fit) >= 2:
            return pop_fit[0][0], pop_fit[1][0]
        elif len(pop_fit) == 1:
            return pop_fit[0][0], pop_fit[0][0]
        else:
            return None, None
    count=0
    while len(select)<4 and count<50:#Burada  rastgele 4 tanesi seçilmeye çalışılıyor.Aynı değerler olmaması çallışılıyor.Çok zorlamasın diye sayaç koydum.
            temp=random.choice(pop_fit)
            if temp not in select:
                select.append(temp)
            count+=1
    while len(select)<4:#Eğer hala seçilmediyse seçilene kadar ekleme yapılıyor.
        tempeture=random.choice(pop_fit)
        select.append(tempeture)

    select.sort(key=lambda x:x[1])#Burada maliyet değerlerini sıraladım.En düşük olan başta olmak kaydıyla.

    father=select[0]#Sadece yolu alıyorum.Anne ve baba da.
    mother=select[1]

    return father[0],mother[0]

def crossover(father,mother):
    if father==None or mother==None:#Anne veya baba yoksa çocuk da yok.
        return None

    common_node=[node for node in father if node in mother]#ortak noktalarını aldım,crossover yapabilmek için.
    child=[]

    if len(common_node)<2:#ortak nokta 2 den az ise hiç ortak nokta yok.Zaten garanti source ile target olmak zorunda.
        return None

    for index in range(len(common_node)-1):
        u=common_node[index]#Sırasıyla ortak nokta aldığımız için burada ilk ile bir sonraki ortak noktayı alıyorum.
        v=common_node[index+1]

        indFaU=father.index(u)#Burada babnın ortak noktasının indeksini alıyorum.
        indFaV=father.index(v)
        listFa=father[indFaU:indFaV]#Aldığım indekslerin yardımıyla kesim yapıyorum.

        indMoU=mother.index(u)#Aynı senaryo annede de geçerli.
        indMoV=mother.index(v)
        listMo=mother[indMoU:indMoV]

        rand_cho=random.choice([listFa,listMo])#rastgele seçim yapıyorum aralarında.
        child.extend(rand_cho) #Listeye tek tek ekleme yapıyorum.

    child.append(common_node[-1])#En sonda target ı ekliyorum.
    return rp.yolu_Sadelestir(child)#Elifin yaptığı yolu sadeleştir fonksiyonuyla yolu sadeleştiriyorum.Sonra o değeri döndürüyorum.

def mutation(G,child,mutation_rate=0.1):

    if random.random() < mutation_rate and len(child)>2:#Zar atıyorum.Eğer zar tutarsa mutasyon yapılacak.Ayrıyeten çocuğun uzunlu 2 den büyük olması lazım.(S,T)
        choice=random.randint(1,len(child)-2)#Rastgele indeks sayısı aldım.Source ile target ı dahil etmedim.
        temp=child[:choice+1]#Seçilen yerde dahil,oraya kadarını aldım.
        temp=rp.tamamla_path(G,temp,child[-1])#Elifin yaptığı yolu tamamla fonskiyonuyla yolu tamamlattırdım.
        if temp==None:#Boş gelirse mutasyon yaptırmadım.Eğer tam yol geldiyse Elifin yolu sadeleştir fonksiyonuyla yolu sadeleştirip değeri dönderdim.
            return child
        else:
            return rp.yolu_Sadelestir(temp)
    else:
        return child

def genetic_algorithm(G,source,target,pop_size=50,generations=100,mutation_rate=0.1,w1=0.33,w2=0.33,w3=0.34,max_delay=100):
    #Main kısmı
    population_group=population(G,source,target,pop_size)#Popülasyon oluşturdum.
    global_best_value=99999#En iyi değeri şimdilik 999999 verdim.İleride en iyi değer değişmezse geçiçi olarak mutasyon oranını arttıracağım.
    mutation_value_count=0#Buda bir üstteki kodun sayacı.
    current_mutation_rate=mutation_rate#Mutation rate kaybolmasın diye geçici bir mutation rate yaptım.Maksat eski oranı kullanmak için.Bunla iş yapacağız.
    for i in range(generations):#Kaç nesil gitsin maksadıyla oluşturuldu.
        fitness_group = fitness_calculation(G, population_group, w1, w2, w3,max_delay)#fitness değerleri hesaplandı.
        best_generetion=[]#çocuklar için oluşturuldu.
        fitness_group.sort(key=lambda x: x[1])#Sıraladım başta.Çünkü bir aşağıda yıldızlarla işaretledğim yerde en iyi iki kişiyi kaybetmemek için onları gruba ekledim.

        if fitness_group[0][1] < global_best_value:#Burada mutasyon oranını yükesltmek amacıyla yapıldı.En iyi değer bulunduysa sayacı sıfırladım.
            global_best_value=fitness_group[0][1]
            mutation_value_count=0
            current_mutation_rate=mutation_rate
        else:#Eğer en iyi değer hala dönmediyse sayacı arttırıyorum.
            mutation_value_count+=1

        if mutation_value_count==10:#Belli bir 10 nesildir hala en iyi değer gelmediyse mutasyon aranını  arttırıyorum.
            current_mutation_rate=0.3

        if mutation_value_count==20:#20 nesıl olunca da mutasyon oranını eski haline getiriyorum.
            current_mutation_rate = mutation_rate

        if rp.yol_gecerli_mi(G,fitness_group[0][0],source,target):#*****Yol geçerli olup olmadığına da baktım.Değerde bozulma ihtimaline karşın kopyaladım.Referrans almadım.
            best_generetion.append(fitness_group[0][0][:])#Referans almadım,kopyaladım.

        if rp.yol_gecerli_mi(G,fitness_group[1][0],source,target):#*****Yol geçerli olup olmadığına da baktım.Değerde bozulma ihtimaline karşın kopyaladım.Referrans almadım.
            best_generetion.append(fitness_group[1][0][:])#Referans almadım,kopyaladım.

        child_count=0#Çocuk while döngüsünde kaç kere eklenmediyse diye sayaç oluşturdum.
        generation_count=0#Eğer best_generation dolmazsa çok zorlamaması açısından sayaç koydum.Her nesil için 1000 kere hak var.
        while len(best_generetion)<pop_size and generation_count<1000:

            father, mother = selection(fitness_group)#Anne baba seçiliyor.
            child = crossover(father, mother)#Crossoveryapılıyor.
            if child is None: continue#Çocuk yoksa devam.
            child = mutation(G, child, current_mutation_rate)#Mutasyon yapılıyor,yapılacaksa tabi.

            if rp.yol_gecerli_mi(G,child, source,target):#Elifin yazdığı yol geçerli mi fonksiyonunda yolun olup olmadığına bakılıyor.True yada false döndürüyor.
                if child not in best_generetion or child_count>15:#Çocuk best_generetion da yoksa veya sayaç 15 i geçtiyse çocuğu ekliyor.
                    best_generetion.append(child)
                    child_count=0
                else:
                    child_count+=1
            generation_count+=1

        population_group=best_generetion#En sonda oluşan çocuklar bir diğer nesili oluşturmak için çocuk yapacak.Yani bunlar anne,baba seçimi olacak.


    fitness_group = fitness_calculation(G, population_group, w1, w2, w3,max_delay)#En sonda oluşan best yolların fitness ını(maliyetini) hesapladım.
    fitness_group.sort(key=lambda x:x[1])#Sıraladım.En düşük maliyet en başta.
    return fitness_group[0][0]#En iyisi döndürdüm.


import FriendGraph as gg
import Metrics as mr
import GeneticAlgorithm as ga  # Senin yazdığın son dosyayı buraya import ediyoruz
import networkx as nx


def main():
    print("--- GENETİK ALGORİTMA BAŞLATILIYOR ---")

    # 1. Grafı Oluştur (Hocanın ayarlarıyla)
    print("1. Graf oluşturuluyor...")
    G = gg.graf_uret()
    print(f"   -> {len(G.nodes)} düğüm ve {len(G.edges)} kenar oluşturuldu.")

    # 2. Kaynak ve Hedef Belirle
    # Test için rastgele uzak iki nokta seçelim
    nodes = list(G.nodes())
    source = nodes[0]
    target = nodes[-1]  # Genelde son düğüm uzaktır

    # Eğer bu iki düğüm arasında hiç yol yoksa (Graph bağlı değilse) hata almamak için:
    if not nx.has_path(G, source, target):
        print("   -> Uyarı: Seçilen düğümler arasında yol yok. Rastgele yenisi seçiliyor.")
        while True:
            import random
            source = random.choice(nodes)
            target = random.choice(nodes)
            if source != target and nx.has_path(G, source, target):
                break

    print(f"2. Rota Hesaplanacak: Düğüm {source} -> Düğüm {target}")
    print("   -> Algoritma çalışıyor... (Lütfen bekleyin)")

    # 3. SENİN YAZDIĞIN FONKSİYONU ÇAĞIR
    # Parametreleri değiştirebilirsin: pop_size=100, generations=200 gibi.
    best_path = ga.genetic_algorithm(
        G,
        source,
        target,
        pop_size=50,
        generations=100,
        mutation_rate=0.1,
        max_delay=150  # Gecikme sınırı
    )

    # 4. Sonuçları Ekrana Bas
    print("\n--- SONUÇLAR ---")

    if best_path is None:
        print("❌ Üzgünüm, geçerli bir yol bulunamadı.")
    else:
        print("✅ EN İYİ YOL BULUNDU!")
        print(f"   -> Yol: {best_path}")
        print(f"   -> Adım Sayısı (Hop): {len(best_path) - 1}")

        # Metrikleri Hesapla
        delay = mr.Total_Delay(G, best_path)
        reliability = mr.Total_Reliability(G, best_path)
        bandwidth = mr.Total_Bandwidth(G, best_path)

        # Fitness Skoru (Senin formülünle: w1, w2, w3 varsayılan)
        # w1=0.33, w2=0.33, w3=0.34
        fitness = (delay * 0.33) + (reliability * 0.33) + (bandwidth * 0.34)

        print("-" * 30)
        print(f"   ⏱️  Toplam Gecikme: {delay} ms")
        print(f"   🛡️  Güvenilirlik Maliyeti: {reliability:.4f}")
        print(f"   📡  Bant Genişliği Maliyeti: {bandwidth:.4f}")
        print("-" * 30)
        print(f"   🏆  TOPLAM FITNESS SKORU: {fitness:.4f}")
        print("-" * 30)


if __name__ == "__main__":
    main()