import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score, mean_absolute_error

#dosyayı okuyoruz
df = pd.read_csv("Smart Home Dataset.csv")

#time sütununda sayısala çevrilemeyen satırları atıyoruz
df['time']= pd.to_numeric(df['time'], errors='coerce')
df.dropna(subset=['time'], inplace=True)

#cloudCover(Bulut oranı) sayısal değerlere çeviriyoruz
df['cloudCover']= pd.to_numeric(df['cloudCover'], errors='coerce')

#verimizde az sayıda Nan değeri olduğundan onları da direk temizliyoruz 
df.dropna(inplace=True)

#time sütunu çok geniş bir alan olduğundan time sütununa yeni özellikler veriyoruz
#time tarih olacağından dolayı 11-03-2025 gibi 16:00 gibi net tarihleri doğrudan anlayamaz
df['datetime']=pd.to_datetime(df['time'], unit='s')
#üstteki satırda saniye cinsinden olan verileri gerçek tarih ve zamana çeviriyoruz
df['hour']=  df['datetime'].dt.hour
#tarih bilgisinde net bilgiler olduğundan biz burada sadece saat bilgisini çıkarttık
#insan davranışı saatlerle dakikalarla belli olur.
df['dayofweek']= df['datetime'].dt.dayofweek
#hafta günleini sayısal olarak verir.(mesela pazartesi 0 pazar 6 gibi)
#günlere önem verdik çünkü insanlar haftasonu evde daha çok zaman geçirir ve bu da tüketimi arttırır
df['month']= df['datetime'].dt.month
#ay bilgisini sayısal olarak verir(1-12)
#kışın ısıtıcı yazın klima ama bahar da az tüketim mantığı olabilir

le=LabelEncoder()
df['icon_encoded']= le.fit_transform(df['icon'])
#her hava durumuna sayısal değerler veriyoruz
#bu hava durumunda tüketim artıyor azalıyor tespiti yapmak için kullandık


baseline_pivot= df.pivot_table(
    values= 'House overall [kW]', #ev toplam tüketimi
    index='hour', #saat bazlı
    columns='icon', #hava durumu bazlı
    aggfunc='mean' #ortalama (normal) tüketim
)

# o satırın saati, hava durumu, pivottan gelen normal tüketimi al yeni sütuna yaz
#artık her satırda gerçek tüketim ve normal tüketim yan yana duruyor (gerçek değer ile normal arasındaki sapma?)
df['baseline_consumption']=df.apply(
    lambda row: baseline_pivot.loc[row['hour'], row['icon']],
    axis=1
)

# 2.pivot Saat + Sıcaklık Seviyesi 

#sıcaklığı gruplara ayıralım ki sıcaklık etkisinin sonuçlarını görelim
df['temp_bin'] = pd.cut(
    df['temperature'],
    bins=[-30, 0, 10, 20, 30, 50],
    labels=['very_cold', 'cold', 'mild', 'warm', 'hot'],
    include_lowest=True 
)

#pivot üretiyoruz
# TEMP BIN İÇİN PIVOT (MERGE İLE)

temp_pivot = (
    df.pivot_table(
        values='House overall [kW]',
        index=['hour', 'temp_bin'],
        aggfunc='mean',
        observed=False
    )
    .reset_index()
)

df = df.merge(
    temp_pivot,
    on=['hour', 'temp_bin'],
    how='left',
    suffixes=('', '_temp')
)

df.rename(
    columns={'House overall [kW]_temp': 'baseline_temp'},
    inplace=True
)


#modelimiz artık normal tüketimi hava ve sıcaklık durumlarını inceliyor
df = df.dropna(subset=['hour', 'temp_bin']) #yeni oluşan pivotların nan değerlerini temizliyoruz

features = [
    'hour',
    'dayofweek',
    'month',
    'temperature',
    'humidity',
    'windSpeed',
    'cloudCover',
    'icon_encoded',
    'baseline_consumption',# bu saat ve bu hava koşullarında normalde ne kadar tüketiliyor(referans noktası)
    'baseline_temp'
]
# features e X değerlerini verdik ve ondan elektrik tüketimi(y) değerlerini isteyebilelim
# features=modelin bakmasına izin verdiğimiz bilgiler

X= df[features]
y= df['House overall [kW]']
#X modele verdiğimiz bilgiler iken y ise modelin tahmin etmesini istediğimiz şeylerdir

# model ezber mi yapıyor yoksa öğreniyor mu yani test verisinde değerlendirme yapıyoruz
X_train, X_test, y_train, y_test=train_test_split(
    X, y, test_size=0.2, random_state=42
)

#random forest
rf_model=RandomForestRegressor(n_estimators=100,random_state=42)
rf_model.fit(X_train,y_train)
rf_pred=rf_model.predict(X_test)
# saat+hava+baseline(türettik) arasındaki karmaşık ilişkileri yani lineer olmayan ilişkileri inceler
# normal tüketim yüksek ama bazı günler daha da yükseliyor

# scaling
scaler=StandardScaler()
X_train_scaled=scaler.fit_transform(X_train)
X_test_scaled= scaler.transform(X_test)

# KNN
knn_model=KNeighborsRegressor(n_neighbors=5)
knn_model.fit(X_train_scaled,y_train)
knn_pred= knn_model.predict(X_test_scaled)
# KNN mesafe ölçümü yapar yani yeni verim eski verilere ne kadar yakın ya da uzak
# öklid ile mesafe ölçümü yapar
# scaler ile ise özellikleri benzer özelliklere çekeriz çünkü KNN farklı ölçeklere sahiptir

# ÖRNEK TAHMİN TABLOSU

pred_df = pd.DataFrame({
    "Gerçek_kW": y_test.values[:10],
    "RF_Tahmin_kW": rf_pred[:10],
    "KNN_Tahmin_kW": knn_pred[:10]
})

print("\nÖrnek Tahminler (ilk 10 satır):")
print(pred_df.round(3))

print("Random forest")
print("R2= ", r2_score(y_test, rf_pred))
print("MAE", mean_absolute_error(y_test,rf_pred))

print("\nKNN")
print("R2= ", r2_score(y_test, knn_pred))
print("MAE", mean_absolute_error(y_test,knn_pred))

