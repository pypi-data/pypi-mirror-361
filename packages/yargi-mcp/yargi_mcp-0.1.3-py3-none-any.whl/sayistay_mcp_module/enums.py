# sayistay_mcp_module/enums.py

from typing import Literal

# Chamber/Daire options for Temyiz Kurulu and Daire endpoints (1-8 + All)
DaireEnum = Literal[
    "ALL",           # All chambers/departments
    "1",             # 1. Daire
    "2",             # 2. Daire  
    "3",             # 3. Daire
    "4",             # 4. Daire
    "5",             # 5. Daire
    "6",             # 6. Daire
    "7",             # 7. Daire
    "8"              # 8. Daire
]

# Public Administration Types (Kamu İdaresi Türü)
KamuIdaresiTuruEnum = Literal[
    "ALL",                                      # All institutions
    "Genel Bütçe Kapsamındaki İdareler",       # General Budget Administrations
    "Yüksek Öğretim Kurumları",                # Higher Education Institutions
    "Diğer Özel Bütçeli İdareler",             # Other Special Budget Administrations
    "Düzenleyici ve Denetleyici Kurumlar",     # Regulatory and Supervisory Institutions
    "Sosyal Güvenlik Kurumları",               # Social Security Institutions
    "Özel İdareler",                           # Special Administrations
    "Belediyeler ve Bağlı İdareler",           # Municipalities and Affiliated Administrations
    "Diğer"                                    # Other
]

# Decision Subject Categories (Web Karar Konusu)
WebKararKonusuEnum = Literal[
    "ALL",                                                          # All subjects
    "Harcırah Mevzuatı ile İlgili Kararlar",                      # Travel Allowance Legislation Related Decisions
    "İhale Mevzuatı ile İlgili Kararlar",                         # Procurement Legislation Related Decisions
    "İş Mevzuatı ile İlgili Kararlar",                            # Labor Legislation Related Decisions
    "Personel Mevzuatı ile İlgili Kararlar",                      # Personnel Legislation Related Decisions
    "Sorumluluk ve Yargılama Usulleri ile İlgili Kararlar",       # Liability and Trial Procedures Related Decisions
    "Vergi Resmi Harç ve Diğer Gelirlerle İlgili Kararlar",       # Tax, Official Fee and Other Revenue Related Decisions
    "Çeşitli Konuları İlgilendiren Kararlar"                      # Decisions Concerning Various Topics
]

# Year ranges for different endpoints
GENEL_KURUL_YEARS = [str(year) for year in range(2006, 2025)]  # 2006-2024
TEMYIZ_KURULU_YEARS = [str(year) for year in range(1993, 2023)]  # 1993-2022
DAIRE_YEARS = [str(year) for year in range(2012, 2026)]  # 2012-2025

# Account years for Temyiz Kurulu and Daire endpoints
HESAP_YILLARI = [str(year) for year in range(1993, 2024)]  # 1993-2023