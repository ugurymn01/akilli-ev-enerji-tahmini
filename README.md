# akilli-ev-enerji-tahmini
Bu projenin amacı, bir akıllı eve ait zaman ve hava durumu verilerini kullanarak evin anlık toplam elektrik tüketimini (kW) tahmin etmektir. Projede, tüketimi sınıflandırmak yerine gerçek tüketim değerini tahmin eden regresyon tabanlı bir yaklaşım benimsenmiştir.

# Verinin içeriği

# Amaç Ve Tahmin edilen değişken
- Modelin tahmin etmeye çalıştığı hedef değişken House overall [kW] değişkenidir. Bu değişken evin belirli bir andaki toplam elektrik tüketimini (kW cinsinden) temsil etmektedir. Bu problem bir regresyon problemi olarak ele alınmış ve modelden sürekli (sayısal) bir çıktı üretilmesi hedeflenmiştir.
- Regresyon alma sebebimiz ise biz tüketimin yüksek mi düşük mü gibi basitleştirilmiş bir sınıflandırma yapmak yerine gerçek tüketimi tahmin etmek istedik. 

# Kullanılan değişkenler
Modelde 3 ana değişken gubu kullandık:

## 1-Zaman tabalı değişkenler
Zaman bilgisi, ev içi enerji tüketiminin günlük ve haftalık alışkanlıklara bağlı olarak değişmesi nedeniyle modelimizde çok önemlidir. Bu nedenle zaman değişkeni (time) kullanılarak aşağıdaki türetilmiş değişkenler elde edilmiştir:
•	hour: saat
•	dayofweek: gün
•	month: Ay 
Bu değişkenler, ev halkının günlük rutinlerini ve mevsimsel davranışlarını modele yansıtmak amacıyla kullanılmıştır.
Başta direk time olarak kullandığımız zaman bu değişken bize direk anlık olarak net bir tarih ve saat değeri döndürdüğünden dolayı analiz sürecinde sıkıntı çıkartacaktı.

## 2-Hava durumu değişkenleri
Ev enerji tüketimi, özellikle ısıtma ve soğutma sistemleri nedeniyle hava koşullarından etkilenmektedir. Bu nedenle aşağıdaki hava durumu değişkenleri modele dahil edilmiştir:
•	temperature (sıcaklık)
•	humidity (nem oranı)
•	windSpeed (rüzgar hızı)
•	cloudCover (bulut oranı)
•	icon (kategorik hava durumu etiketi, sayısal olarak encode edilmiştir) 
Bu değişkenler, evin enerji ihtiyacını dolaylı olarak etkileyen çevresel faktörleri temsil etmektedir.

## 3-Pivot (Baseline) Değişkenleri
Amaç, evin farklı koşullar altında sahip olduğu normal enerji tüketimini sayısal bir referans noktası olarak modele öğretmektir.
Bu kapsamda iki farklı pivot tablo oluşturulmuştur:
•	Saat + Hava Durumu (icon) bazlı pivot
→ baseline_consumption
•	Saat + Sıcaklık Seviyesi (temperature bin) bazlı pivot
→ baseline_temp
Bu pivot tablolar, belirli saatlerde ve belirli hava koşullarında evin ortalama tüketimini temsil etmektedir. Daha sonra bu ortalama değerler ana veri setine eklenerek, modelin normal tüketimden sapmaları öğrenmesi sağlanmıştır.

# Kullanılmayan Değişkenler
Veri setinde yer alan bazı değişkenler bilinçli olarak modele dahil edilmemiştir. Bizim analizini yapmak istediğimiz konumuz hava durumu ve sıcaklık-soğukluk etkilerinin evdeki toplam enerji tüketimine etkileri olduğundan bazı verilerin sadece kalabalıklaştırdığını ve karmaşıklığı arttırdığını fark ettik.
- Dishwasher, Fridge, Microwave, Furnace, Kitchen, Living room gibi cihaz bazlı güç tüketimi değişkenleri, evin toplam tüketiminin genel bileşenleridir. Bu değişkenlerin modele dahil edilmesi, hedef değişkenin zaten parçalarını modele vermek anlamına geleceği için veri sızıntısı oluşturacaktır.
- Bizim ana hedefimiz zaten house overall[kW] bulmak olduğundan bunları ayrı ayrı almak mantıksızdı çünkü toplamı tahmin ederken parçaları kullanmadık işimiz toplamlaydı.
- apparentTemperature (hissedilen sıcaklık), dewPoint (çiğ noktası) , pressure (atmosfer basıncı), windBearing (rüzgar yönü), visibility (görüş mesafesi), precipIntensity (yağış şiddeti) , precipProbability  (yağış olasılığı) ve summary(hava durumu özeti) gibi değişkenler ya sıcaklık ve nem ile yüksek korelasyona sahip olmaları ya da ev içi enerji tüketimi üzerinde doğrudan etkiye sahip olmamaları nedeniyle modele dahil edilmemiştir. Bu değişkenlerin kullanılması, model karmaşıklığını artırırken tahmin başarısını artırmamaktadır.

# Pivot nedir ve neden kullandık ?
Pivot, çok sayıda veriyi daha anlaşılır hale getirmek için kullanılan bir özetleme yöntemidir. Ham veriler genellikle satır satır ve dağınık halde bulunur. Pivot işlemi, bu verileri belirli kurallara göre gruplayarak ortalama, toplam veya sayım gibi özet değerler üretir.
Kısaca pivot, çok fazla bilgiyi tek bir tablo halinde özetleme yöntemidir. Sadeleştirme diyebilirz.

Enerji tüketimi gibi insan davranışına bağlı verilerde, anlık değişimler sıkça görülür. Pivot tablolar, bu anlık değişimleri azaltarak verinin genel yapısını ortaya çıkarmaya yardımcı olur.
Yani pivot sayesinde tek tek ölçümlere bakmak yerine, verinin ortalama davranışı anlaşılır hale gelir.




