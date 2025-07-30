# Yargı MCP: Türk Hukuk Kaynakları için MCP Sunucusu

[![Star History Chart](https://api.star-history.com/svg?repos=saidsurucu/yargi-mcp&type=Date)](https://www.star-history.com/#saidsurucu/yargi-mcp&Date)

Bu proje, çeşitli Türk hukuk kaynaklarına (Yargıtay, Danıştay, Emsal Kararlar, Uyuşmazlık Mahkemesi, Anayasa Mahkemesi - Norm Denetimi ile Bireysel Başvuru Kararları, Kamu İhale Kurulu Kararları, Rekabet Kurumu Kararları ve Sayıştay Kararları) erişimi kolaylaştıran bir [FastMCP](https://gofastmcp.com/) sunucusu oluşturur. Bu sayede, bu kaynaklardan veri arama ve belge getirme işlemleri, Model Context Protocol (MCP) destekleyen LLM (Büyük Dil Modeli) uygulamaları (örneğin Claude Desktop veya [5ire](https://5ire.app)) ve diğer istemciler tarafından araç (tool) olarak kullanılabilir hale gelir.

![örnek](./ornek.png)

🎯 **Temel Özellikler**

* Çeşitli Türk hukuk veritabanlarına programatik erişim için standart bir MCP arayüzü.
* **Kapsamlı Mahkeme Daire/Kurul Filtreleme:** 79 farklı daire/kurul filtreleme seçeneği
* **Dual/Triple API Desteği:** Her mahkeme için birden fazla API kaynağı ile maksimum kapsama
* **Kapsamlı Tarih Filtreleme:** Tüm Bedesten API araçlarında ISO 8601 formatında tarih aralığı filtreleme
* **Kesin Cümle Arama:** Tüm Bedesten API araçlarında çift tırnak ile tam cümle arama desteği
* Aşağıdaki kurumların kararlarını arama ve getirme yeteneği:
    * **Yargıtay:** Detaylı kriterlerle karar arama ve karar metinlerini Markdown formatında getirme. **Dual API** (Ana + Bedesten) + **52 Daire/Kurul Filtreleme** + **Tarih & Kesin Cümle Arama** (Hukuk/Ceza Daireleri, Genel Kurullar)
    * **Danıştay:** Anahtar kelime bazlı ve detaylı kriterlerle karar arama; karar metinlerini Markdown formatında getirme. **Triple API** (Keyword + Detailed + Bedesten) + **27 Daire/Kurul Filtreleme** + **Tarih & Kesin Cümle Arama** (İdari Daireler, Vergi/İdare Kurulları, Askeri Yüksek İdare Mahkemesi)
    * **Yerel Hukuk Mahkemeleri:** Bedesten API ile yerel hukuk mahkemesi kararlarına erişim + **Tarih & Kesin Cümle Arama**
    * **İstinaf Hukuk Mahkemeleri:** Bedesten API ile istinaf mahkemesi kararlarına erişim + **Tarih & Kesin Cümle Arama**
    * **Kanun Yararına Bozma (KYB):** Bedesten API ile olağanüstü kanun yoluna erişim + **Tarih & Kesin Cümle Arama**
    * **Emsal (UYAP):** Detaylı kriterlerle emsal karar arama ve karar metinlerini Markdown formatında getirme.
    * **Uyuşmazlık Mahkemesi:** Form tabanlı kriterlerle karar arama ve karar metinlerini (URL ile erişilen) Markdown formatında getirme.
    * **Anayasa Mahkemesi (Norm Denetimi):** Kapsamlı kriterlerle norm denetimi kararlarını arama; uzun karar metinlerini (5.000 karakterlik) sayfalanmış Markdown formatında getirme.
    * **Anayasa Mahkemesi (Bireysel Başvuru):** Kapsamlı kriterlerle bireysel başvuru "Karar Arama Raporu" oluşturma ve listedeki kararların metinlerini (5.000 karakterlik) sayfalanmış Markdown formatında getirme.
    * **KİK (Kamu İhale Kurulu):** Çeşitli kriterlerle Kurul kararlarını arama; uzun karar metinlerini (varsayılan 5.000 karakterlik) sayfalanmış Markdown formatında getirme.
    * **Rekabet Kurumu:** Çeşitli kriterlerle Kurul kararlarını arama; karar metinlerini Markdown formatında getirme.
    * **Sayıştay:** 3 karar türü ile kapsamlı denetim kararlarına erişim + **8 Daire Filtreleme** + **Tarih Aralığı & İçerik Arama** (Genel Kurul yorumlayıcı kararları, Temyiz Kurulu itiraz kararları, Daire ilk derece denetim kararları)
    * **KVKK (Kişisel Verilerin Korunması Kurulu):** Brave Search API ile veri koruma kararlarını arama; uzun karar metinlerini (5.000 karakterlik) sayfalanmış Markdown formatında getirme + **Türkçe Arama** + **Site Hedeflemeli Arama** (kvkk.gov.tr kararları)

* Karar metinlerinin daha kolay işlenebilmesi için Markdown formatına çevrilmesi.
* Claude Desktop uygulaması ile `fastmcp install` komutu kullanılarak kolay entegrasyon.
* Yargı MCP artık [5ire](https://5ire.app) gibi Claude Desktop haricindeki MCP istemcilerini de destekliyor!
---
🚀 **Claude Haricindeki Modellerle Kullanmak İçin Çok Kolay Kurulum (Örnek: 5ire için)**

Bu bölüm, Yargı MCP aracını 5ire gibi Claude Desktop dışındaki MCP istemcileriyle kullanmak isteyenler içindir.

* **Python Kurulumu:** Sisteminizde Python 3.11 veya üzeri kurulu olmalıdır. Kurulum sırasında "**Add Python to PATH**" (Python'ı PATH'e ekle) seçeneğini işaretlemeyi unutmayın. [Buradan](https://www.python.org/downloads/) indirebilirsiniz.
* **Git Kurulumu (Windows):** Bilgisayarınıza [git](https://git-scm.com/downloads/win) yazılımını indirip kurun. "Git for Windows/x64 Setup" seçeneğini indirmelisiniz.
* **`uv` Kurulumu:**
    * **Windows Kullanıcıları (PowerShell):** Bir CMD ekranı açın ve bu kodu çalıştırın: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
    * **Mac/Linux Kullanıcıları (Terminal):** Bir Terminal ekranı açın ve bu kodu çalıştırın: `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Microsoft Visual C++ Redistributable (Windows):** Bazı Python paketlerinin doğru çalışması için gereklidir. [Buradan](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) indirip kurun.
* İşletim sisteminize uygun [5ire](https://5ire.app) MCP istemcisini indirip kurun.
* 5ire'ı açın. **Workspace -> Providers** menüsünden kullanmak istediğiniz LLM servisinin API anahtarını girin.
* **Tools** menüsüne girin. **+Local** veya **New** yazan butona basın.
    * **Tool Key:** `yargimcp`
    * **Name:** `Yargı MCP`
    * **Command:**
        ```
        uvx yargi-mcp
        ```
    * **Save** butonuna basarak kaydedin.
![5ire ayarları](./5ire-settings.png)
* Şimdi **Tools** altında **Yargı MCP**'yi görüyor olmalısınız. Üstüne geldiğinizde sağda çıkan butona tıklayıp etkinleştirin (yeşil ışık yanmalı).
* Artık Yargı MCP ile konuşabilirsiniz.

---
⚙️ **Claude Desktop Manuel Kurulumu**


1.  **Ön Gereksinimler:** Python, `uv`, (Windows için) Microsoft Visual C++ Redistributable'ın sisteminizde kurulu olduğundan emin olun. Detaylı bilgi için yukarıdaki "5ire için Kurulum" bölümündeki ilgili adımlara bakabilirsiniz.
2.  Claude Desktop **Settings -> Developer -> Edit Config**.
3.  Açılan `claude_desktop_config.json` dosyasına `mcpServers` altına ekleyin:

    ```json
    {
      "mcpServers": {
        // ... (varsa diğer sunucularınız) ...
        "Yargı MCP": {
          "command": "uvx",
          "args": [
            "yargi-mcp"
          ]
        }
      }
    }
    ```
4.  Claude Desktop'ı kapatıp yeniden başlatın.

---
🌟 **Gemini CLI ile Kullanım**

Yargı MCP'yi Gemini CLI ile kullanmak için:

1. **Ön Gereksinimler:** Python, `uv`, (Windows için) Microsoft Visual C++ Redistributable'ın sisteminizde kurulu olduğundan emin olun. Detaylı bilgi için yukarıdaki "5ire için Kurulum" bölümündeki ilgili adımlara bakabilirsiniz.

2. **Gemini CLI ayarlarını yapılandırın:**
   
   Gemini CLI'ın ayar dosyasını düzenleyin:
   - **macOS/Linux:** `~/.gemini/settings.json`
   - **Windows:** `%USERPROFILE%\.gemini\settings.json`
   
   Aşağıdaki `mcpServers` bloğunu ekleyin:
   ```json
   {
     "theme": "Default",
     "selectedAuthType": "###",
     "mcpServers": {
       "yargi_mcp": {
         "command": "uvx",
         "args": [
           "yargi-mcp"
         ]
       }
     }
   }
   ```
   
   **Yapılandırma açıklamaları:**
   - `"yargi_mcp"`: Sunucunuz için yerel bir isim
   - `"command"`: `uvx` komutu (uv'nin paket çalıştırma aracı)
   - `"args"`: GitHub'dan doğrudan Yargı MCP'yi çalıştırmak için gerekli argümanlar

3. **Kullanım:**
   - Gemini CLI'ı başlatın
   - Yargı MCP araçları otomatik olarak kullanılabilir olacaktır
   - Örnek komutlar:
     - "Yargıtay'ın mülkiyet hakkı ile ilgili son kararlarını ara"
     - "Danıştay'ın imar planı iptaline ilişkin kararlarını bul"
     - "Anayasa Mahkemesi'nin ifade özgürlüğü kararlarını getir"

🛠️ **Kullanılabilir Araçlar (MCP Tools)**

Bu FastMCP sunucusu **30 MCP aracı** sunar:

### **Yargıtay Araçları (Ana API + 52 Daire Filtreleme)**
1. `search_yargitay_detailed(arananKelime, birimYrgKurulDaire, ...)`: Yargıtay kararlarını detaylı kriterlerle arar. **52 daire/kurul seçeneği** (Hukuk/Ceza Daireleri 1-23, Genel Kurullar, Başkanlar Kurulu)
2. `get_yargitay_document_markdown(id: str)`: Belirli bir Yargıtay kararının metnini Markdown formatında getirir.

### **Danıştay Araçları (Dual API + 27 Daire Filtreleme)**
3. `search_danistay_by_keyword(andKelimeler, orKelimeler, ...)`: Danıştay kararlarını anahtar kelimelerle arar.
4. `search_danistay_detailed(daire, esasYil, ...)`: Danıştay kararlarını detaylı kriterlerle arar.
5. `get_danistay_document_markdown(id: str)`: Belirli bir Danıştay kararının metnini Markdown formatında getirir.

### **Birleşik Bedesten API Araçları (5 Mahkeme)**
6. `search_bedesten_unified(phrase, court_types, birimAdi, kararTarihiStart, kararTarihiEnd, ...)`: **5 mahkeme türünü** birleşik arama (Yargıtay, Danıştay, Yerel Hukuk, İstinaf Hukuk, KYB) + **79 daire filtreleme** + **Tarih & Kesin Cümle Arama**
7. `get_bedesten_document_markdown(documentId: str)`: Bedesten API'den herhangi bir belgeyi Markdown formatında getirir (HTML/PDF → Markdown)

### **Emsal Karar Araçları (UYAP)**
8. `search_emsal_detailed_decisions(keyword, ...)`: Emsal (UYAP) kararlarını detaylı kriterlerle arar.
9. `get_emsal_document_markdown(id: str)`: Belirli bir Emsal kararının metnini Markdown formatında getirir.

### **Uyuşmazlık Mahkemesi Araçları**
10. `search_uyusmazlik_decisions(icerik, ...)`: Uyuşmazlık Mahkemesi kararlarını çeşitli form kriterleriyle arar.
11. `get_uyusmazlik_document_markdown_from_url(document_url)`: Bir Uyuşmazlık kararını tam URL'sinden alıp Markdown formatında getirir.

### **Anayasa Mahkemesi Araçları (Norm Denetimi)**
12. `search_anayasa_norm_denetimi_decisions(keywords_all, ...)`: AYM Norm Denetimi kararlarını kapsamlı kriterlerle arar.
13. `get_anayasa_norm_denetimi_document_markdown(document_url, page_number)`: Belirli bir AYM Norm Denetimi kararını URL'sinden alır ve **sayfalanmış Markdown** içeriğini getirir.

### **Anayasa Mahkemesi Araçları (Bireysel Başvuru)**
14. `search_anayasa_bireysel_basvuru_report(keywords, ...)`: AYM Bireysel Başvuru "Karar Arama Raporu" oluşturur.
15. `get_anayasa_bireysel_basvuru_document_markdown(document_url_path, page_number)`: Belirli bir AYM Bireysel Başvuru kararını URL path'inden alır ve **sayfalanmış Markdown** içeriğini getirir.

### **KİK (Kamu İhale Kurulu) Araçları**
16. `search_kik_decisions(karar_tipi, ...)`: KİK (Kamu İhale Kurulu) kararlarını arar. 
17. `get_kik_document_markdown(karar_id, page_number)`: Belirli bir KİK kararını, Base64 ile encode edilmiş `karar_id`'sini kullanarak alır ve **sayfalanmış Markdown** içeriğini getirir.
### **Rekabet Kurumu Araçları**
    * `search_rekabet_kurumu_decisions(KararTuru: Literal[...], ...) -> RekabetSearchResult`: Rekabet Kurumu kararlarını arar. `KararTuru` için kullanıcı dostu isimler kullanılır (örn: "Birleşme ve Devralma").
    * `get_rekabet_kurumu_document(karar_id: str, page_number: Optional[int] = 1) -> RekabetDocument`: Belirli bir Rekabet Kurumu kararını `karar_id` ile alır. Kararın PDF formatındaki orijinalinden istenen sayfayı ayıklar ve Markdown formatında döndürür.


---

* **Sayıştay Araçları (3 Karar Türü + 8 Daire Filtreleme):**
    * `search_sayistay_genel_kurul(karar_no, karar_tarih_baslangic, karar_tamami, ...)`: Sayıştay Genel Kurul (yorumlayıcı) kararlarını arar. **Tarih aralığı** (2006-2024) + **İçerik arama** (400 karakter)
    * `search_sayistay_temyiz_kurulu(ilam_dairesi, kamu_idaresi_turu, temyiz_karar, ...)`: Temyiz Kurulu (itiraz) kararlarını arar. **8 Daire filtreleme** + **Kurum türü** + **Konu sınıflandırması**
    * `search_sayistay_daire(yargilama_dairesi, web_karar_metni, hesap_yili, ...)`: Daire (ilk derece denetim) kararlarını arar. **8 Daire filtreleme** + **Hesap yılı** + **İçerik arama**
    * `get_sayistay_genel_kurul_document_markdown(decision_id: str)`: Genel Kurul kararının tam metnini Markdown formatında getirir
    * `get_sayistay_temyiz_kurulu_document_markdown(decision_id: str)`: Temyiz Kurulu kararının tam metnini Markdown formatında getirir  
    * `get_sayistay_daire_document_markdown(decision_id: str)`: Daire kararının tam metnini Markdown formatında getirir

* **KVKK Araçları (Brave Search API + Türkçe Arama):**
    * `search_kvkk_decisions(keywords, page, pageSize, ...)`: KVKK (Kişisel Verilerin Korunması Kurulu) kararlarını Brave Search API ile arar. **Türkçe arama** + **Site hedeflemeli** (`site:kvkk.gov.tr "karar özeti"`) + **Sayfalama desteği**
    * `get_kvkk_document_markdown(decision_url: str, page_number: Optional[int] = 1)`: KVKK kararının tam metnini **sayfalanmış Markdown** formatında getirir (5.000 karakterlik sayfa)


---

### **📊 Kapsamlı İstatistikler**
- **Toplam Mahkeme/Kurum:** 13 farklı hukuki kurum (KVKK dahil)
- **Toplam MCP Tool:** 30 arama ve belge getirme aracı  
- **Daire/Kurul Filtreleme:** 87 farklı seçenek (52 Yargıtay + 27 Danıştay + 8 Sayıştay)
- **Tarih Filtreleme:** Birleşik Bedesten API aracında ISO 8601 formatında tam tarih aralığı desteği
- **Kesin Cümle Arama:** Birleşik Bedesten API aracında çift tırnak ile tam cümle arama (`"\"mülkiyet kararı\""` formatı)
- **Birleşik API:** 10 ayrı Bedesten aracı → 2 birleşik araç (search_bedesten_unified + get_bedesten_document_markdown)
- **API Kaynağı:** Dual/Triple API desteği ile maksimum kapsama
- **Tam Türk Adalet Sistemi:** Yerel mahkemelerden en yüksek mahkemelere kadar

**🏛️ Desteklenen Mahkeme Hiyerarşisi:**
```
Yerel Mahkemeler → İstinaf → Yargıtay/Danıştay → Anayasa Mahkemesi
     ↓              ↓            ↓                    ↓
Bedesten API   Bedesten API   Dual/Triple API   Norm+Bireysel API
+ Tarih + Kesin + Tarih + Kesin + Daire + Tarih   + Gelişmiş
  Cümle Arama    Cümle Arama   + Kesin Cümle     Arama
```

**⚖️ Kapsamlı Filtreleme Özellikleri:**
- **Daire Filtreleme:** 79 seçenek (52 Yargıtay + 27 Danıştay)
  - **Yargıtay:** 52 seçenek (1-23 Hukuk, 1-23 Ceza, Genel Kurullar, Başkanlar Kurulu)
  - **Danıştay:** 27 seçenek (1-17 Daireler, İdare/Vergi Kurulları, Askeri Mahkemeler)
- **Tarih Filtreleme:** 5 Bedesten API aracında ISO 8601 formatı (YYYY-MM-DDTHH:MM:SS.000Z)
  - Tek tarih, tarih aralığı, tek taraflı filtreleme desteği
  - Yargıtay, Danıştay, Yerel Hukuk, İstinaf Hukuk, KYB kararları
- **Kesin Cümle Arama:** 5 Bedesten API aracında çift tırnak formatı
  - Normal arama: `"mülkiyet kararı"` (kelimeler ayrı ayrı)
  - Kesin arama: `"\"mülkiyet kararı\""` (tam cümle olarak)
  - Daha kesin sonuçlar için hukuki terimler ve kavramlar

---

🌐 **Web Service / ASGI Deployment**

Yargı MCP artık web servisi olarak da çalıştırılabilir! ASGI desteği sayesinde:

- **Web API olarak erişim**: HTTP endpoint'leri üzerinden MCP araçlarına erişim
- **Cloud deployment**: Heroku, Railway, Google Cloud Run, AWS Lambda desteği
- **Docker desteği**: Production-ready Docker container
- **FastAPI entegrasyonu**: REST API ve interaktif dokümantasyon

**Hızlı başlangıç:**
```bash
# ASGI dependencies yükle
pip install yargi-mcp[asgi]

# Web servisi olarak başlat
python run_asgi.py
# veya
uvicorn asgi_app:app --host 0.0.0.0 --port 8000
```

Detaylı deployment rehberi için: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

📜 **Lisans**

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.
