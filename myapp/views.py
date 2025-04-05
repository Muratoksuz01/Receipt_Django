from .serializers import UploadedImageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import ImageToTextPipeline  
import google.generativeai as genai
from .models import Snippet
from google.cloud import vision
import json
import os


@api_view(["POST"])
def upload_and_process_image(request):
    print("burada")
    print("Gelen dosya:", request.FILES)  # Gelen dosyayı yazdır
    if "image" not in request.FILES:
        return Response({"error": "Dosya seçilmedi"}, status=400)

    # Serializer ile dosya verisini almak
    serializer = UploadedImageSerializer(data=request.data)

    if serializer.is_valid():
        # Görseli kaydetme
        image_instance = serializer.save()
        image_path = image_instance.image.path

        # OCR ve NLP Pipeline - örnek
        print("ilk")
        res = extract_text(image_path)  # OCR işleminden gelen metin
        print("ikinci")
        processed_text = gemini_api(os.getenv("GEMINI_API_KEY"), res)  # API çağrısı
      
        print("üçüncü")

        try:
           
            start = processed_text.index("{") 
            end = processed_text.index("}") + 1 
            json_data = processed_text[start:end]
            print(json_data)
            processed_text = json.loads(json_data) 
            if os.path.exists(image_path):
                os.remove(image_path)

        except json.JSONDecodeError as e:
            print(f"JSON decode hatası: {e}")
            return Response({"error": "Metin işleme hatası"}, status=500)

        except ValueError as e:
            print(f"Değer hatası: {e}")
            return Response({"error": "Geçersiz format, JSON verisi alınamadı"}, status=500)

        return Response({"extracted_text": processed_text}, status=201)

    return Response(serializer.errors, status=400)
@api_view(["POST"])
def save_data(request):
   # print("Gelen ham veri:", request.body.decode('utf-8'))  # Ham veriyi yazdır
    parsed_data = json.loads( request.body.decode('utf-8'))  # Gelen veriyi al
    data = parsed_data.get("data", [])
  #  print("Data:", data)  
    # print(len(data))
    # print(data[0]["saat"])
    # print(data[0].get("saat"))
    try:
        # Gelen her bir siparişi veritabanına kaydet
        for order in data:
            saat = order.get("saat")
            tarih = order.get("tarih")
            adres = order.get("adres")
            urunler = order.get("urunler")
            toplam = order.get("toplam")

            # Modeli kullanarak veritabanına kaydet
            new_order = Snippet(
                time=saat,
                date=tarih,
                address=adres,
                items=urunler,
                total=toplam
            )
            new_order.save()  # V
        return Response({"message": "Veriler başarıyla kaydedildi"}, status=201)
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return Response({"error": str(e)}, status=500)

def gemini_api(api_key, text):
    genai.configure(api_key=api_key)  # API anahtarını burada ayarla
    model = genai.GenerativeModel("gemini-1.5-flash")  # Modeli burada oluştur
    prompt = f"""
Verilen metni analiz et ve JSON formatında aşağıdaki anahtarlarla birlikte yalnızca gerekli bilgileri döndür.
Eğer herhangi bir bilgi eksikse, 'bilgi yok' olarak döndür. JSON çıktısında anahtarlar şu şekilde olmalı:
- "saat": Fişte geçen saat bilgisi
- "tarih": Fişte geçen tarih bilgisi
- "adres": İşletmenin açık adresi, şirketin adı ile beraber
- "urunler": Satın alınan ürünlerin isimleri, fiyatları ve adetleri. Ürünleri ';' ile ayır, detayları ',' ile ayır.
- "toplam": Satın alınan ürünlerin toplam tutarı.

Eğer bu bilgileri bulursan, değerlerini yaz. Bulamazsan, 'bilgi yok' olarak döndür.

Örnek format şu şekilde olmalı:

    "saat": "bilgi yok",
    "tarih": "bilgi yok",
    "adres": "bilgi yok",
    "urunler": "bilgi yok",
    "toplam": "bilgi yok"


Metin:
{text}
"""
    response = model.generate_content(prompt)
    return response.text


def extract_text(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description
    else:
        return "Metin bulunamadı."


"""
[
    {
        "saat": "11:58",
        "tarih": "18.05.2023",
        "adres": "Darıcı Mh. Salim Uğurlu Sokak No: 11/ B-C OSKODAR/9480423762",
        "urunler": "BOZBEYİGURME3TAT,117,00,1;BOZBEYIGURME3TAT,117,00,1;TARABYA250G TULUM PE,54,90,1",
        "toplam": "756,37"
    },
    {
        "saat": "11:58",
        "tarih": "18.05.2023",
        "adres": "Darıcı Mh. Salim Uğurlu Sokak No: 11/ B-C OSKODAR/9480423762",
        "urunler": "BOZBEYİGURME3TAT,117,00,1;BOZBEYIGURME3TAT,117,00,1;TARABYA250G TULUM PE,54,90,1",
        "toplam": "756,37"
    }
]
"""