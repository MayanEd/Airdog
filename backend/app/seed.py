from datetime import datetime

from sqlalchemy.orm import Session

from .auth import hash_password
from .models import (
    Category,
    CategoryTranslation,
    News,
    NewsTranslation,
    Page,
    Product,
    ProductImage,
    ProductTranslation,
    User,
)

LOCALES = ("en", "zh-CN", "zh-HK")


def t3(en: str, cn: str, hk: str) -> dict[str, str]:
    return {"en": en, "zh-CN": cn, "zh-HK": hk}


def add_cat(db: Session, slug: str, image: str, order: int, names: dict, descs: dict, nav=True) -> Category:
    cat = Category(slug=slug, image=image, sort_order=order, show_in_nav=nav)
    db.add(cat)
    db.flush()
    for loc in LOCALES:
        db.add(
            CategoryTranslation(
                category_id=cat.id, locale=loc, name=names[loc], description=descs[loc]
            )
        )
    return cat


def add_product(db: Session, data: dict, cat_id: int | None) -> Product:
    p = Product(
        sku=data["sku"],
        slug=data["slug"],
        category_id=cat_id,
        price_yen=data["price"],
        stock_status=data.get("stock", "in_stock"),
        color=data.get("color", ""),
        size=data.get("size", ""),
        is_service=data.get("service", False),
        featured=data.get("featured", False),
        sort_order=data.get("order", 0),
        image=data["image"],
    )
    db.add(p)
    db.flush()
    for loc in LOCALES:
        tr = data["tr"][loc]
        db.add(
            ProductTranslation(
                product_id=p.id,
                locale=loc,
                name=tr["name"],
                subtitle=tr.get("subtitle", ""),
                description=tr["description"],
                included=tr.get("included", ""),
                specs_json=tr.get("specs", "[]"),
                disclaimers=tr.get("disclaimers", ""),
            )
        )
    db.add(ProductImage(product_id=p.id, url=data["image"], alt=data["sku"], sort_order=0))
    return p


def seed_if_empty(db: Session, admin_email: str, admin_password: str) -> None:
    if db.query(User).first():
        return

    db.add(
        User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            name="Administrator",
            is_admin=True,
        )
    )

    x = add_cat(
        db,
        "x-series",
        "/assets/img/category/1/Airdog-Type-01.jpg",
        10,
        t3(
            "High-performance air purifier — Airdog X Series (floor-standing)",
            "高性能空气净化器 — Airdog X系列（落地式）",
            "高性能空氣清新機 — Airdog X系列（座地式）",
        ),
        t3(
            "Airdog’s signature floor-standing models. Every unit includes the TPA filter. Choose the model that fits your space.",
            "Airdog经典落地机型。全机种均搭载标志性TPA滤网，可根据使用环境选择合适型号。",
            "Airdog經典座地型號。全線均搭載標誌性TPA濾網，可按使用環境選擇合適型號。",
        ),
    )
    mini = add_cat(
        db,
        "mini",
        "/assets/img/category/1/Airdog-Type-02.jpg",
        20,
        t3(
            "High-performance air purifier — Airdog mini Series",
            "高性能空气净化器 — Airdog mini系列",
            "高性能空氣清新機 — Airdog mini系列",
        ),
        t3(
            "Airdog’s smallest portable purifiers. A compact TPA filter keeps personal space clean. Choose corded or rechargeable.",
            "Airdog最小的便携空气净化器。高性能小型TPA滤网随时净化个人空间。可按用途选择电源式或充电式。",
            "Airdog最小的便攜空氣清新機。高性能小型TPA濾網隨時淨化個人空間。可按用途選擇有線或充電式。",
        ),
    )
    moi = add_cat(
        db,
        "moi",
        "/assets/img/category/1/Airdog-Type-03.jpg",
        30,
        t3(
            "Evaporative humidifier — Airdog moi",
            "气化器加湿器 — Airdog moi",
            "氣化式加濕器 — Airdog moi",
        ),
        t3(
            "An evaporative humidifier that sanitizes tank water so you humidify with clean water. Auto mode senses room humidity. 3.2 L tank with easy top-fill.",
            "对水箱内的水进行除菌，始终以洁净水源加湿。配备感应室内湿度并保持舒适状态的自动模式。3.2升水箱可从上部轻松补水。",
            "對水箱內的水進行除菌，時刻以潔淨水源加濕。配備感應室內濕度並保持舒適狀態的自動模式。3.2升水箱可從上部輕鬆加水。",
        ),
    )
    options = add_cat(
        db,
        "options",
        "/assets/img/category/1/Airdog-Type-05.jpg",
        70,
        t3(
            "Options, maintenance goods, and parts",
            "选配件、保养用品及零件",
            "選配件、保養用品及零件",
        ),
        t3(
            "Optional accessories, care items, and replacement parts for Airdog products. Parts and seasonal items are limited to 5 per SKU per order.",
            "Airdog使用时的便利选配、保养用品及损坏零件。零件与季节限定品单次下单每SKU以5件为限。",
            "Airdog使用時的便利選配、保養用品及損壞零件。零件與季節限定品每次訂單每SKU以5件為限。",
        ),
    )
    add_cat(
        db,
        "filter-service",
        "/assets/img/category/1/Airdog-Type-06.jpg",
        80,
        t3("Filter replacement service", "滤网更换服务", "濾網更換服務"),
        t3(
            "The dedicated filter exchange portal is operated for Japan. International customers may inquire about maintenance parts through this site.",
            "专用滤网更换门户面向日本运营。海外客户可通过本站咨询保养零件。",
            "專用濾網更換門戶面向日本營運。海外客戶可透過本站查詢保養零件。",
        ),
        nav=True,
    )
    add_cat(
        db,
        "care-plus",
        "/assets/img/category/1/Airdog-Type-07.jpg",
        90,
        t3("Airdog CARE+", "Airdog CARE+", "Airdog CARE+"),
        t3(
            "A support service so you can use Airdog with peace of mind for years to come.",
            "为让您长久安心使用Airdog高性能空气净化器而提供的支持服务。",
            "為讓您長久安心使用Airdog高性能空氣清新機而提供的支援服務。",
        ),
    )
    add_cat(
        db,
        "medical",
        "/assets/img/campaign/medical_banner_20250119.jpg",
        15,
        t3(
            "For medical and care facilities",
            "医疗・护理机构专区",
            "醫療・護理機構專區",
        ),
        t3(
            "Airdog X Series offerings for medical and nursing facilities, including extended-warranty programs.",
            "面向医疗与护理机构的Airdog X系列，含延长保修等专属服务。",
            "面向醫療與護理機構的Airdog X系列，含延長保用等專屬服務。",
        ),
        nav=False,
    )

    disclaimer = t3(
        "Results were obtained in a sealed test chamber and are not demonstrated results in real living spaces. Effectiveness varies with the environment and room conditions.",
        "结果来自密闭试验空间，并非实际使用空间的实证结果。效果会因使用环境与房间条件而异。",
        "結果來自密閉試驗空間，並非實際使用空間的實證結果。效果會因使用環境與房間條件而異。",
    )

    products = [
        {
            "sku": "AIR-X1-H1W510",
            "slug": "airdog-x1d-white",
            "price": 66000,
            "color": "White",
            "size": "H31 × D35.5 × W12.4 cm",
            "featured": True,
            "order": 30,
            "image": "/assets/img/usr/slider/slider_x1d.jpg",
            "cat": x.id,
            "tr": {
                "en": {
                    "name": "Airdog X1D | White",
                    "subtitle": "The most compact X Series model",
                    "description": "The space-saving Airdog X1D keeps full Airdog performance in a slim body that fits on a desk. Use it for house-dust and virus-conscious spaces such as children’s rooms, studies, and bedside tables.",
                    "included": "① Airdog X1D White unit ② Collection filter ③ Remote control ④ Filter brush ⑤ Ionizing wire-frame cleaner ⑥ Manual / care guide / warranty / brand book. Pre-filter, ionizing wire frame, and ozone-removal filter are pre-installed.",
                    "specs": '[{"label":"Model","value":"Airdog X1D"},{"label":"Minimum particle size","value":"0.0146 μm"},{"label":"Clean air delivery","value":"23 m² of clean air in 30 minutes"},{"label":"Recommended space","value":"Desk / under-table, up to 7 tatami (JEM1467)"},{"label":"Sensors","value":"AQI sensor"},{"label":"Size","value":"H 31 × D 35.5 × W 12.4 cm"},{"label":"Weight","value":"4.25 kg (incl. AC adapter)"},{"label":"Noise","value":"27.2–47.7 dB"},{"label":"Power","value":"Sleep 6.7 W / L1 7.5 W / L2 10.51 W / L3 10.94 W / L4 20 W"},{"label":"Voltage","value":"DC 13 V; adapter AC 100–240 V 50/60 Hz"},{"label":"Rated power","value":"20 W"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog X1D｜白色",
                    "subtitle": "X系列最小机型",
                    "description": "省空间的Airdog X1D在纤薄机身内保留完整Airdog性能，可置于桌面。适用于儿童房、书房、床头等对粉尘与病毒防护有需求的场景。",
                    "included": "① Airdog X1D白色主机 ② 集尘滤网 ③ 遥控器 ④ 滤网刷 ⑤ 电离丝框专用清洁器 ⑥ 说明书／保养指南／保修卡／品牌手册。预滤网、电离丝框、臭氧去除滤网已预装于机身。",
                    "specs": '[{"label":"型号","value":"Airdog X1D"},{"label":"最小去除粒径","value":"0.0146 μm"},{"label":"洁净空气供给量","value":"30分钟供给23㎡洁净空气"},{"label":"建议使用空间","value":"桌面／桌下等，约7叠（JEM1467）"},{"label":"传感器","value":"AQI传感器"},{"label":"尺寸","value":"高31 × 深35.5 × 宽12.4 cm"},{"label":"质量","value":"4.25 kg（含适配器）"},{"label":"运行音","value":"27.2–47.7 dB"},{"label":"功耗","value":"Sleep 6.7 W / L1 7.5 W / L2 10.51 W / L3 10.94 W / L4 20 W"},{"label":"电压","value":"DC 13 V；适配器 AC 100–240 V 50/60 Hz"},{"label":"额定功率","value":"20 W"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog X1D｜白色",
                    "subtitle": "X系列最細型號",
                    "description": "慳位的Airdog X1D以纖薄機身保留完整Airdog性能，可放在桌面。適合兒童房、書房、床頭等需要粉塵與病毒防護的場景。",
                    "included": "① Airdog X1D白色主機 ② 集塵濾網 ③ 遙控器 ④ 濾網刷 ⑤ 電離絲框專用清潔器 ⑥ 說明書／保養指南／保用證／品牌手冊。預濾網、電離絲框、臭氧去除濾網已預裝於機身。",
                    "specs": '[{"label":"型號","value":"Airdog X1D"},{"label":"最小去除粒徑","value":"0.0146 μm"},{"label":"潔淨空氣供給量","value":"30分鐘供給23㎡潔淨空氣"},{"label":"建議使用空間","value":"桌面／桌下等，約7疊（JEM1467）"},{"label":"感應器","value":"AQI感應器"},{"label":"尺寸","value":"高31 × 深35.5 × 寬12.4 cm"},{"label":"質量","value":"4.25 kg（含火牛）"},{"label":"運行聲","value":"27.2–47.7 dB"},{"label":"耗電","value":"Sleep 6.7 W / L1 7.5 W / L2 10.51 W / L3 10.94 W / L4 20 W"},{"label":"電壓","value":"DC 13 V；火牛 AC 100–240 V 50/60 Hz"},{"label":"額定功率","value":"20 W"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-X3-H1W510",
            "slug": "airdog-x3d-white",
            "price": 109780,
            "color": "White",
            "size": "H56 × D26 × W27 cm",
            "featured": True,
            "order": 20,
            "image": "/assets/img/usr/slider/slider_x3d.jpg",
            "cat": x.id,
            "tr": {
                "en": {
                    "name": "Airdog X3D | White",
                    "subtitle": "Compact model — ideal for bedrooms",
                    "description": "A versatile compact model with light and motion sensors. Popular for bedrooms, children’s rooms, studies, and extra rooms at home. Three-way wide exhaust from the top and both sides.",
                    "included": "① Airdog X3D White unit ② Collection filter ③ Remote ④ Filter brush ⑤ Ionizing wire-frame cleaner ⑥ Manuals and warranty. Pre-filter, ionizing wire frame, and ozone-removal filter are pre-installed.",
                    "specs": '[{"label":"Model","value":"Airdog X3D"},{"label":"Minimum particle size","value":"0.0146 μm"},{"label":"Clean air delivery","value":"48 m² of clean air in 30 minutes"},{"label":"Recommended space","value":"Bedroom / kids’ room / meeting room, up to 17 tatami (JEM1467)"},{"label":"Sensors","value":"AQI, light & motion"},{"label":"Size","value":"H 56 × D 26 × W 27 cm"},{"label":"Weight","value":"6.4 kg (incl. AC adapter)"},{"label":"Noise","value":"22.3–45.5 dB"},{"label":"Power","value":"Sleep 8.7 W / L1 9.9 W / L2 11.1 W / L3 15.8 W / L4 27 W"},{"label":"Voltage","value":"DC 13 V; adapter AC 100 V 50/60 Hz"},{"label":"Rated power","value":"27 W"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog X3D｜白色",
                    "subtitle": "紧凑机型 — 卧室首选",
                    "description": "兼顾高性能与紧凑体积，配备光感与人体感应。适合卧室、儿童房、书房。顶部与左右共三处广角排气。",
                    "included": "① Airdog X3D白色主机 ② 集尘滤网 ③ 遥控器 ④ 滤网刷 ⑤ 电离丝框清洁器 ⑥ 说明书与保修卡。预滤网、电离丝框、臭氧去除滤网已预装。",
                    "specs": '[{"label":"型号","value":"Airdog X3D"},{"label":"最小去除粒径","value":"0.0146 μm"},{"label":"洁净空气供给量","value":"30分钟供给48㎡洁净空气"},{"label":"建议使用空间","value":"卧室／儿童房／会议室，约17叠（JEM1467）"},{"label":"传感器","value":"AQI、光感与人体感应"},{"label":"尺寸","value":"高56 × 深26 × 宽27 cm"},{"label":"质量","value":"6.4 kg（含适配器）"},{"label":"运行音","value":"22.3–45.5 dB"},{"label":"功耗","value":"Sleep 8.7 W / L1 9.9 W / L2 11.1 W / L3 15.8 W / L4 27 W"},{"label":"电压","value":"DC 13 V；适配器 AC 100 V 50/60 Hz"},{"label":"额定功率","value":"27 W"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog X3D｜白色",
                    "subtitle": "輕巧型號 — 睡房首選",
                    "description": "兼顧高性能與輕巧體積，配備光感與人體感應。適合睡房、兒童房、書房。頂部與左右共三處廣角排氣。",
                    "included": "① Airdog X3D白色主機 ② 集塵濾網 ③ 遙控器 ④ 濾網刷 ⑤ 電離絲框清潔器 ⑥ 說明書與保用證。預濾網、電離絲框、臭氧去除濾網已預裝。",
                    "specs": '[{"label":"型號","value":"Airdog X3D"},{"label":"最小去除粒徑","value":"0.0146 μm"},{"label":"潔淨空氣供給量","value":"30分鐘供給48㎡潔淨空氣"},{"label":"建議使用空間","value":"睡房／兒童房／會議室，約17疊（JEM1467）"},{"label":"感應器","value":"AQI、光感與人體感應"},{"label":"尺寸","value":"高56 × 深26 × 寬27 cm"},{"label":"質量","value":"6.4 kg（含火牛）"},{"label":"運行聲","value":"22.3–45.5 dB"},{"label":"耗電","value":"Sleep 8.7 W / L1 9.9 W / L2 11.1 W / L3 15.8 W / L4 27 W"},{"label":"電壓","value":"DC 13 V；火牛 AC 100 V 50/60 Hz"},{"label":"額定功率","value":"27 W"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-X3-H1B510",
            "slug": "airdog-x3d-black",
            "price": 114620,
            "color": "Matte Black",
            "size": "H56 × D26 × W27 cm",
            "order": 21,
            "image": "/assets/img/usr/slider/slider_x3d.jpg",
            "cat": x.id,
            "tr": {
                "en": {
                    "name": "Airdog X3D | Matte Black",
                    "subtitle": "Compact model in matte black",
                    "description": "The same compact X3D performance in a matte black finish that sits quietly in bedrooms and small meeting rooms. Functions match the white X3D.",
                    "included": "① Airdog X3D Matte Black unit ② Collection filter ③ Remote ④ Filter brush ⑤ Ionizing wire-frame cleaner ⑥ Manuals and warranty.",
                    "specs": '[{"label":"Model","value":"Airdog X3D"},{"label":"Color","value":"Matte Black"},{"label":"Minimum particle size","value":"0.0146 μm"},{"label":"Clean air delivery","value":"48 m² of clean air in 30 minutes"},{"label":"Recommended space","value":"Up to 17 tatami (JEM1467)"},{"label":"Sensors","value":"AQI, light & motion"},{"label":"Size","value":"H 56 × D 26 × W 27 cm"},{"label":"Weight","value":"6.4 kg"},{"label":"Noise","value":"22.3–45.5 dB"},{"label":"Rated power","value":"27 W"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog X3D｜哑光黑",
                    "subtitle": "紧凑机型哑光黑配色",
                    "description": "与白色X3D功能相同，哑光黑更易融入卧室与小型会议空间。",
                    "included": "① Airdog X3D哑光黑主机 ② 集尘滤网 ③ 遥控器 ④ 滤网刷 ⑤ 电离丝框清洁器 ⑥ 说明书与保修卡。",
                    "specs": '[{"label":"型号","value":"Airdog X3D"},{"label":"颜色","value":"哑光黑"},{"label":"最小去除粒径","value":"0.0146 μm"},{"label":"洁净空气供给量","value":"30分钟供给48㎡洁净空气"},{"label":"建议使用空间","value":"约17叠（JEM1467）"},{"label":"传感器","value":"AQI、光感与人体感应"},{"label":"尺寸","value":"高56 × 深26 × 宽27 cm"},{"label":"质量","value":"6.4 kg"},{"label":"运行音","value":"22.3–45.5 dB"},{"label":"额定功率","value":"27 W"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog X3D｜霧面黑",
                    "subtitle": "輕巧型號霧面黑",
                    "description": "與白色X3D功能相同，霧面黑更易融入睡房與小型會議空間。",
                    "included": "① Airdog X3D霧面黑主機 ② 集塵濾網 ③ 遙控器 ④ 濾網刷 ⑤ 電離絲框清潔器 ⑥ 說明書與保用證。",
                    "specs": '[{"label":"型號","value":"Airdog X3D"},{"label":"顏色","value":"霧面黑"},{"label":"最小去除粒徑","value":"0.0146 μm"},{"label":"潔淨空氣供給量","value":"30分鐘供給48㎡潔淨空氣"},{"label":"建議使用空間","value":"約17疊（JEM1467）"},{"label":"感應器","value":"AQI、光感與人體感應"},{"label":"尺寸","value":"高56 × 深26 × 寬27 cm"},{"label":"質量","value":"6.4 kg"},{"label":"運行聲","value":"22.3–45.5 dB"},{"label":"額定功率","value":"27 W"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-X5-H1W510",
            "slug": "airdog-x5d-white",
            "price": 146300,
            "color": "White",
            "size": "H65 × D30.6 × W31.6 cm",
            "featured": True,
            "order": 10,
            "image": "/assets/img/usr/slider/slider_x5d.jpg",
            "cat": x.id,
            "tr": {
                "en": {
                    "name": "Airdog X5D | White",
                    "subtitle": "Flagship performance model — ideal for living rooms",
                    "description": "The flagship living-room model with AQI and CO2 sensors, casters with roll-stop, one-button operation, auto and sleep modes, and a washable collection filter that does not require routine replacement. Removes particles as small as 0.0146 μm using patented TPA filter technology.",
                    "included": "① Airdog X5D White unit ② Collection filter ③ Remote ④ Collection-filter brush ⑤ Ionizing wire-frame cleaner ⑥ Manual / care guide / warranty / 30-day return guide / brand book. Pre-filter, ionizing wire frame, and ozone-removal filter are pre-installed.",
                    "specs": '[{"label":"Model","value":"Airdog X5D"},{"label":"Clean air delivery","value":"65 m² of clean air in 30 minutes"},{"label":"Minimum particle size","value":"0.0146 μm"},{"label":"Recommended space","value":"24 tatami — living room, shop, office (JEM1467)"},{"label":"Sensors","value":"AQI sensor, CO2 sensor"},{"label":"Size","value":"H 65 × D 31.6 × W 30.6 cm"},{"label":"Weight","value":"11.1 kg"},{"label":"Noise","value":"22.3–51 dB"},{"label":"Power","value":"Sleep 12 W / L1 15 W / L2 18 W / L3 23 W / L4 55 W"},{"label":"Power supply","value":"Body DC 13 V; adapter AC 100 V 50/60 Hz"},{"label":"Rated power","value":"27 W"}]',
                    "disclaimers": disclaimer["en"]
                    + " Air-cleaning capacity of X5D is equivalent to X5s used in some laboratory tests. CADR-based clean-air volume follows China GB/T 18801-2015 as tested by Vkan Certification & Testing Co., Ltd., not AHAM. Room height assumed 2.4 m.",
                },
                "zh-CN": {
                    "name": "Airdog X5D｜白色",
                    "subtitle": "旗舰性能机型 — 客厅首选",
                    "description": "客厅旗舰机型，配备AQI与CO2传感器、带止动脚轮、一键操作、自动与睡眠模式。集尘滤网可水洗、无需定期更换。采用专利TPA滤网技术，可去除小至0.0146μm的微粒。",
                    "included": "① Airdog X5D白色主机 ② 集尘滤网 ③ 遥控器 ④ 集尘滤网刷 ⑤ 电离丝框专用清洁器 ⑥ 说明书／保养指南／保修卡／退货说明／品牌手册。预滤网、电离丝框、臭氧去除滤网已预装。",
                    "specs": '[{"label":"型号","value":"Airdog X5D"},{"label":"洁净空气供给量","value":"30分钟供给65㎡洁净空气"},{"label":"最小去除粒径","value":"0.0146 μm"},{"label":"建议使用空间","value":"24叠 — 客厅、店铺、办公室（JEM1467）"},{"label":"传感器","value":"AQI传感器、CO2传感器"},{"label":"尺寸","value":"高65 × 深31.6 × 宽30.6 cm"},{"label":"质量","value":"11.1 kg"},{"label":"运行音","value":"22.3–51 dB"},{"label":"功耗","value":"Sleep 12 W / L1 15 W / L2 18 W / L3 23 W / L4 55 W"},{"label":"电源","value":"机身 DC 13 V；适配器 AC 100 V 50/60 Hz"},{"label":"额定功率","value":"27 W"}]',
                    "disclaimers": disclaimer["zh-CN"] + " X5D空气清净能力与部分试验所用X5s相当。洁净空气量依据中国GB/T 18801-2015由Vkan Certification & Testing Co., Ltd.测得的CADR，并非AHAM标准。房间高度按2.4米计算。",
                },
                "zh-HK": {
                    "name": "Airdog X5D｜白色",
                    "subtitle": "旗艦性能型號 — 客廳首選",
                    "description": "客廳旗艦型號，配備AQI與CO2感應器、帶止動腳輪、一鍵操作、自動與睡眠模式。集塵濾網可水洗、無需定期更換。採用專利TPA濾網技術，可去除小至0.0146μm的微粒。",
                    "included": "① Airdog X5D白色主機 ② 集塵濾網 ③ 遙控器 ④ 集塵濾網刷 ⑤ 電離絲框專用清潔器 ⑥ 說明書／保養指南／保用證／退貨說明／品牌手冊。預濾網、電離絲框、臭氧去除濾網已預裝。",
                    "specs": '[{"label":"型號","value":"Airdog X5D"},{"label":"潔淨空氣供給量","value":"30分鐘供給65㎡潔淨空氣"},{"label":"最小去除粒徑","value":"0.0146 μm"},{"label":"建議使用空間","value":"24疊 — 客廳、店鋪、辦公室（JEM1467）"},{"label":"感應器","value":"AQI感應器、CO2感應器"},{"label":"尺寸","value":"高65 × 深31.6 × 寬30.6 cm"},{"label":"質量","value":"11.1 kg"},{"label":"運行聲","value":"22.3–51 dB"},{"label":"耗電","value":"Sleep 12 W / L1 15 W / L2 18 W / L3 23 W / L4 55 W"},{"label":"電源","value":"機身 DC 13 V；火牛 AC 100 V 50/60 Hz"},{"label":"額定功率","value":"27 W"}]',
                    "disclaimers": disclaimer["zh-HK"] + " X5D空氣清淨能力與部分試驗所用X5s相當。潔淨空氣量依據中國GB/T 18801-2015由Vkan Certification & Testing Co., Ltd.測得的CADR，並非AHAM標準。房間高度按2.4米計算。",
                },
            },
        },
        {
            "sku": "AIR-X5-H1B510",
            "slug": "airdog-x5d-black",
            "price": 151140,
            "color": "Matte Black",
            "size": "H65 × D30.6 × W31.6 cm",
            "order": 11,
            "image": "/assets/img/usr/slider/slider_x5d.jpg",
            "cat": x.id,
            "tr": {
                "en": {
                    "name": "Airdog X5D | Matte Black",
                    "subtitle": "Flagship performance in matte black",
                    "description": "The X5D flagship in matte black. Same TPA filter, AQI and CO2 sensors, and washable collection filter as the white model.",
                    "included": "① Airdog X5D Matte Black unit ② Collection filter ③ Remote ④ Brushes and cleaners ⑥ Manuals and warranty.",
                    "specs": '[{"label":"Model","value":"Airdog X5D"},{"label":"Color","value":"Matte Black"},{"label":"Clean air delivery","value":"65 m² of clean air in 30 minutes"},{"label":"Minimum particle size","value":"0.0146 μm"},{"label":"Recommended space","value":"24 tatami (JEM1467)"},{"label":"Sensors","value":"AQI, CO2"},{"label":"Size","value":"H 65 × D 31.6 × W 30.6 cm"},{"label":"Weight","value":"11.1 kg"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog X5D｜哑光黑",
                    "subtitle": "旗舰性能哑光黑",
                    "description": "X5D旗舰的哑光黑配色，TPA滤网、AQI与CO2传感器、可水洗集尘滤网与白色机型相同。",
                    "included": "① Airdog X5D哑光黑主机 ② 集尘滤网 ③ 遥控器 ④ 刷具与清洁器 ⑥ 说明书与保修卡。",
                    "specs": '[{"label":"型号","value":"Airdog X5D"},{"label":"颜色","value":"哑光黑"},{"label":"洁净空气供给量","value":"30分钟供给65㎡洁净空气"},{"label":"最小去除粒径","value":"0.0146 μm"},{"label":"建议使用空间","value":"24叠（JEM1467）"},{"label":"传感器","value":"AQI、CO2"},{"label":"尺寸","value":"高65 × 深31.6 × 宽30.6 cm"},{"label":"质量","value":"11.1 kg"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog X5D｜霧面黑",
                    "subtitle": "旗艦性能霧面黑",
                    "description": "X5D旗艦的霧面黑配色，TPA濾網、AQI與CO2感應器、可水洗集塵濾網與白色型號相同。",
                    "included": "① Airdog X5D霧面黑主機 ② 集塵濾網 ③ 遙控器 ④ 刷具與清潔器 ⑥ 說明書與保用證。",
                    "specs": '[{"label":"型號","value":"Airdog X5D"},{"label":"顏色","value":"霧面黑"},{"label":"潔淨空氣供給量","value":"30分鐘供給65㎡潔淨空氣"},{"label":"最小去除粒徑","value":"0.0146 μm"},{"label":"建議使用空間","value":"24疊（JEM1467）"},{"label":"感應器","value":"AQI、CO2"},{"label":"尺寸","value":"高65 × 深31.6 × 寬30.6 cm"},{"label":"質量","value":"11.1 kg"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-X8-H1W510",
            "slug": "airdog-x8d-pro-white",
            "price": 367400,
            "color": "White",
            "size": "H77.8 × D40 × W40 cm (incl. casters)",
            "featured": True,
            "order": 1,
            "image": "/assets/img/usr/slider/slider_x8dpro.jpg",
            "cat": x.id,
            "tr": {
                "en": {
                    "name": "Airdog X8D Pro | White",
                    "subtitle": "Professional model — offices and stores",
                    "description": "The most powerful Airdog for offices, halls, and large meeting rooms. Dual-mode operation, large TPA filter, twin pre-filters, and 360° casters. Recommended for facilities, shops, and offices up to 74 tatami (GB/T, not JEM).",
                    "included": "① Airdog X8D Pro White unit ② Filters and accessories ③ Manuals and warranty.",
                    "specs": '[{"label":"Model","value":"X8D Pro Professional"},{"label":"Clean air delivery","value":"214 m² of clean air in 30 minutes"},{"label":"Recommended space","value":"Facilities / shops / offices, up to 74 tatami (GB/T 18801-2015)"},{"label":"Minimum particle size","value":"0.0146 μm"},{"label":"Rated voltage","value":"100 V / 50/60 Hz"},{"label":"Rated power","value":"100 W"},{"label":"Noise","value":"26.3–50.5 dB"},{"label":"Weight","value":"20.5 kg"},{"label":"Size","value":"76 × 38 × 38 cm; 77.8 × 40 × 40 cm with casters"},{"label":"Power cord","value":"1.8 m"},{"label":"Sensors","value":"AQI sensor, CO2 sensor"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog X8D Pro｜白色",
                    "subtitle": "专业机型 — 办公室与店铺",
                    "description": "面向办公室、大厅、大型会议室的最强Airdog。双模式、大型TPA滤网、双侧预滤网与360度脚轮。建议空间约74叠（GB/T，非JEM）。",
                    "included": "① Airdog X8D Pro白色主机 ② 滤网与附件 ③ 说明书与保修卡。",
                    "specs": '[{"label":"型号","value":"X8D Pro专业机型"},{"label":"洁净空气供给量","value":"30分钟供给214㎡洁净空气"},{"label":"建议使用空间","value":"设施／店铺／办公室，约74叠（GB/T 18801-2015）"},{"label":"最小去除粒径","value":"0.0146 μm"},{"label":"额定电压","value":"100 V / 50/60 Hz"},{"label":"额定功率","value":"100 W"},{"label":"运行音","value":"26.3–50.5 dB"},{"label":"质量","value":"20.5 kg"},{"label":"尺寸","value":"76 × 38 × 38 cm；含脚轮 77.8 × 40 × 40 cm"},{"label":"电源线","value":"1.8 m"},{"label":"传感器","value":"AQI传感器、CO2传感器"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog X8D Pro｜白色",
                    "subtitle": "專業型號 — 辦公室與店鋪",
                    "description": "面向辦公室、大廳、大型會議室的最強Airdog。雙模式、大型TPA濾網、雙側預濾網與360度腳輪。建議空間約74疊（GB/T，非JEM）。",
                    "included": "① Airdog X8D Pro白色主機 ② 濾網與配件 ③ 說明書與保用證。",
                    "specs": '[{"label":"型號","value":"X8D Pro專業型號"},{"label":"潔淨空氣供給量","value":"30分鐘供給214㎡潔淨空氣"},{"label":"建議使用空間","value":"設施／店鋪／辦公室，約74疊（GB/T 18801-2015）"},{"label":"最小去除粒徑","value":"0.0146 μm"},{"label":"額定電壓","value":"100 V / 50/60 Hz"},{"label":"額定功率","value":"100 W"},{"label":"運行聲","value":"26.3–50.5 dB"},{"label":"質量","value":"20.5 kg"},{"label":"尺寸","value":"76 × 38 × 38 cm；連腳輪 77.8 × 40 × 40 cm"},{"label":"電線","value":"1.8 m"},{"label":"感應器","value":"AQI感應器、CO2感應器"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-MN-H1W510",
            "slug": "airdog-mini-white",
            "price": 36300,
            "color": "White",
            "size": "H22 × D8.4 × W7.3 cm",
            "featured": True,
            "order": 40,
            "image": "/assets/img/usr/slider/slider_mini.jpg",
            "cat": mini.id,
            "tr": {
                "en": {
                    "name": "Airdog mini | White (corded)",
                    "subtitle": "Airdog’s smallest model — corded",
                    "description": "Bottle-size personal purifier for cars, restrooms, and closets. Supplies 4.3 m² of clean air in 30 minutes wherever you have power.",
                    "included": "① Airdog mini White unit ② AC adapter ③ Cleaning kit ④ Manual and warranty. Filters pre-installed.",
                    "specs": '[{"label":"Model","value":"Airdog mini"},{"label":"Clean air delivery","value":"4.3 m³ of clean air in 30 minutes"},{"label":"Power","value":"DC 5 V; adapter AC 100–240 V 50/60 Hz"},{"label":"Consumption","value":"8 W"},{"label":"Battery","value":"—"},{"label":"Noise","value":"30.23 / 36.19 / 54.23 dB"},{"label":"Size","value":"220 × 84 × 73 mm"},{"label":"Weight","value":"Approx. 630 g incl. adapter"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog mini｜白色（电源式）",
                    "subtitle": "Airdog最小机型 — 电源式",
                    "description": "瓶装大小的个人空气净化器，适合车内、卫生间、衣柜。有电源即可使用，30分钟供给4.3㎡洁净空气。",
                    "included": "① Airdog mini白色主机 ② 适配器 ③ 清洁套装 ④ 说明书与保修卡。滤网已预装。",
                    "specs": '[{"label":"型号","value":"Airdog mini"},{"label":"洁净空气供给量","value":"30分钟供给4.3 m³洁净空气"},{"label":"电源","value":"DC 5 V；适配器 AC 100–240 V 50/60 Hz"},{"label":"功耗","value":"8 W"},{"label":"电池","value":"—"},{"label":"运行音","value":"30.23 / 36.19 / 54.23 dB"},{"label":"尺寸","value":"220 × 84 × 73 mm"},{"label":"质量","value":"约630 g（含适配器）"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog mini｜白色（有線）",
                    "subtitle": "Airdog最細型號 — 有線",
                    "description": "樽裝大小的個人空氣清新機，適合車內、洗手間、衣櫃。有電源即可使用，30分鐘供給4.3㎡潔淨空氣。",
                    "included": "① Airdog mini白色主機 ② 火牛 ③ 清潔套裝 ④ 說明書與保用證。濾網已預裝。",
                    "specs": '[{"label":"型號","value":"Airdog mini"},{"label":"潔淨空氣供給量","value":"30分鐘供給4.3 m³潔淨空氣"},{"label":"電源","value":"DC 5 V；火牛 AC 100–240 V 50/60 Hz"},{"label":"耗電","value":"8 W"},{"label":"電池","value":"—"},{"label":"運行聲","value":"30.23 / 36.19 / 54.23 dB"},{"label":"尺寸","value":"220 × 84 × 73 mm"},{"label":"質量","value":"約630 g（含火牛）"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-MN-H1B510",
            "slug": "airdog-mini-black",
            "price": 36300,
            "color": "Matte Black",
            "size": "H22 × D8.4 × W7.3 cm",
            "order": 41,
            "image": "/assets/img/usr/slider/slider_mini.jpg",
            "cat": mini.id,
            "tr": {
                "en": {
                    "name": "Airdog mini | Matte Black (corded)",
                    "subtitle": "Airdog’s smallest model — corded",
                    "description": "The corded mini in matte black. Same personal-space performance as the white mini.",
                    "included": "① Airdog mini Matte Black unit ② AC adapter ③ Cleaning kit ④ Manual and warranty.",
                    "specs": '[{"label":"Model","value":"Airdog mini"},{"label":"Color","value":"Matte Black"},{"label":"Clean air delivery","value":"4.3 m³ in 30 minutes"},{"label":"Consumption","value":"8 W"},{"label":"Size","value":"220 × 84 × 73 mm"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog mini｜哑光黑（电源式）",
                    "subtitle": "Airdog最小机型 — 电源式",
                    "description": "电源式mini的哑光黑配色，性能与白色机型相同。",
                    "included": "① Airdog mini哑光黑主机 ② 适配器 ③ 清洁套装 ④ 说明书与保修卡。",
                    "specs": '[{"label":"型号","value":"Airdog mini"},{"label":"颜色","value":"哑光黑"},{"label":"洁净空气供给量","value":"30分钟4.3 m³"},{"label":"功耗","value":"8 W"},{"label":"尺寸","value":"220 × 84 × 73 mm"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog mini｜霧面黑（有線）",
                    "subtitle": "Airdog最細型號 — 有線",
                    "description": "有線mini的霧面黑配色，性能與白色型號相同。",
                    "included": "① Airdog mini霧面黑主機 ② 火牛 ③ 清潔套裝 ④ 說明書與保用證。",
                    "specs": '[{"label":"型號","value":"Airdog mini"},{"label":"顏色","value":"霧面黑"},{"label":"潔淨空氣供給量","value":"30分鐘4.3 m³"},{"label":"耗電","value":"8 W"},{"label":"尺寸","value":"220 × 84 × 73 mm"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-MN-H1W520",
            "slug": "airdog-mini-portable-white",
            "price": 38500,
            "color": "White",
            "size": "H22 × L8.4 × W7.3 cm",
            "order": 42,
            "image": "/assets/img/usr/slider/slider_mini.jpg",
            "cat": mini.id,
            "tr": {
                "en": {
                    "name": "Airdog mini portable | White (rechargeable, 2024)",
                    "subtitle": "Cordless personal purifier",
                    "description": "Rechargeable 2024 mini portable with lithium-ion battery. About 4 / 2.5 / 1 hours in quiet / normal / turbo. Includes car-seat attachment belt. Do not leave the unit in a hot car; follow the manual for in-car use.",
                    "included": "① Airdog mini portable unit ② AC adapter ③ USB cable ④ Car-seat attachment belt ⑤ Cleaning kit ⑥ Manual and warranty. Filters pre-installed.",
                    "specs": '[{"label":"Model","value":"Airdog mini portable"},{"label":"Clean air delivery","value":"4.3 m³ in 30 minutes"},{"label":"Battery","value":"Lithium-ion"},{"label":"Runtime","value":"Approx. 4 h quiet / 2.5 h normal / 1 h turbo"},{"label":"Charge time","value":"Approx. 1 hour"},{"label":"Noise","value":"30.23 / 36.19 / 54.23 dB"},{"label":"Size","value":"220 × 84 × 73 mm"},{"label":"Weight","value":"Approx. 650 g incl. adapter"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog mini portable｜白色（充电式，2024）",
                    "subtitle": "无线个人空气净化器",
                    "description": "2024充电式mini portable，内置锂离子电池。静音／标准／强力约4／2.5／1小时。含车用固定带。请勿将主机留置高温车内，车内使用请遵照说明书。",
                    "included": "① 主机 ② 适配器 ③ USB线 ④ 车用座椅固定带 ⑤ 清洁套装 ⑥ 说明书与保修卡。滤网已预装。",
                    "specs": '[{"label":"型号","value":"Airdog mini portable"},{"label":"洁净空气供给量","value":"30分钟4.3 m³"},{"label":"电池","value":"锂离子"},{"label":"续航","value":"静音约4小时／标准约2.5小时／强力约1小时"},{"label":"充电","value":"约1小时"},{"label":"运行音","value":"30.23 / 36.19 / 54.23 dB"},{"label":"尺寸","value":"220 × 84 × 73 mm"},{"label":"质量","value":"约650 g（含适配器）"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog mini portable｜白色（充電式，2024）",
                    "subtitle": "無線個人空氣清新機",
                    "description": "2024充電式mini portable，內置鋰離子電池。靜音／標準／強勁約4／2.5／1小時。含車用固定帶。請勿將主機留在高溫車內，車內使用請遵照說明書。",
                    "included": "① 主機 ② 火牛 ③ USB線 ④ 車用座椅固定帶 ⑤ 清潔套裝 ⑥ 說明書與保用證。濾網已預裝。",
                    "specs": '[{"label":"型號","value":"Airdog mini portable"},{"label":"潔淨空氣供給量","value":"30分鐘4.3 m³"},{"label":"電池","value":"鋰離子"},{"label":"續航","value":"靜音約4小時／標準約2.5小時／強勁約1小時"},{"label":"充電","value":"約1小時"},{"label":"運行聲","value":"30.23 / 36.19 / 54.23 dB"},{"label":"尺寸","value":"220 × 84 × 73 mm"},{"label":"質量","value":"約650 g（含火牛）"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-MN-H1B520",
            "slug": "airdog-mini-portable-black",
            "price": 38500,
            "color": "Matte Black",
            "size": "H22 × L8.4 × W7.3 cm",
            "order": 43,
            "image": "/assets/img/usr/slider/slider_mini.jpg",
            "cat": mini.id,
            "tr": {
                "en": {
                    "name": "Airdog mini portable | Matte Black (rechargeable, 2024)",
                    "subtitle": "Cordless personal purifier",
                    "description": "Rechargeable mini portable in matte black. Same battery runtime and accessories as the white 2024 model.",
                    "included": "① Airdog mini portable Matte Black ② Adapter ③ USB cable ④ Car-seat belt ⑤ Cleaning kit ⑥ Manual and warranty.",
                    "specs": '[{"label":"Model","value":"Airdog mini portable"},{"label":"Color","value":"Matte Black"},{"label":"Runtime","value":"Approx. 4 / 2.5 / 1 hours"},{"label":"Size","value":"220 × 84 × 73 mm"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog mini portable｜哑光黑（充电式，2024）",
                    "subtitle": "无线个人空气净化器",
                    "description": "充电式mini portable哑光黑，续航与附件与2024白色机型相同。",
                    "included": "① 哑光黑主机 ② 适配器 ③ USB线 ④ 车用固定带 ⑤ 清洁套装 ⑥ 说明书与保修卡。",
                    "specs": '[{"label":"型号","value":"Airdog mini portable"},{"label":"颜色","value":"哑光黑"},{"label":"续航","value":"约4 / 2.5 / 1小时"},{"label":"尺寸","value":"220 × 84 × 73 mm"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog mini portable｜霧面黑（充電式，2024）",
                    "subtitle": "無線個人空氣清新機",
                    "description": "充電式mini portable霧面黑，續航與配件與2024白色型號相同。",
                    "included": "① 霧面黑主機 ② 火牛 ③ USB線 ④ 車用固定帶 ⑤ 清潔套裝 ⑥ 說明書與保用證。",
                    "specs": '[{"label":"型號","value":"Airdog mini portable"},{"label":"顏色","value":"霧面黑"},{"label":"續航","value":"約4 / 2.5 / 1小時"},{"label":"尺寸","value":"220 × 84 × 73 mm"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-MOI-H1W",
            "slug": "airdog-moi-white",
            "price": 52800,
            "color": "White",
            "size": "3.2 L tank",
            "featured": True,
            "order": 50,
            "image": "/assets/img/usr/slider/slider_moi.jpg",
            "cat": moi.id,
            "tr": {
                "en": {
                    "name": "Airdog moi | Evaporative humidifier",
                    "subtitle": "Humidify with sanitized water",
                    "description": "Evaporative humidifier that sanitizes tank water so you always humidify with clean water. Auto mode senses room humidity. 3.2 L tank fills from the top.",
                    "included": "① Airdog moi unit ② Manual and warranty.",
                    "specs": '[{"label":"Model","value":"Airdog moi"},{"label":"Type","value":"Evaporative humidifier"},{"label":"Tank","value":"3.2 L, top-fill"},{"label":"Mode","value":"Auto humidity sensing"}]',
                    "disclaimers": disclaimer["en"],
                },
                "zh-CN": {
                    "name": "Airdog moi｜气化器加湿器",
                    "subtitle": "以除菌后的洁净水加湿",
                    "description": "对水箱内的水除菌，始终以洁净水源加湿。自动模式感应室内湿度。3.2升水箱可从上部补水。",
                    "included": "① Airdog moi主机 ② 说明书与保修卡。",
                    "specs": '[{"label":"型号","value":"Airdog moi"},{"label":"类型","value":"气化器加湿器"},{"label":"水箱","value":"3.2升，上部加水"},{"label":"模式","value":"湿度感应自动模式"}]',
                    "disclaimers": disclaimer["zh-CN"],
                },
                "zh-HK": {
                    "name": "Airdog moi｜氣化式加濕器",
                    "subtitle": "以除菌後的潔淨水加濕",
                    "description": "對水箱內的水除菌，時刻以潔淨水源加濕。自動模式感應室內濕度。3.2升水箱可從上部加水。",
                    "included": "① Airdog moi主機 ② 說明書與保用證。",
                    "specs": '[{"label":"型號","value":"Airdog moi"},{"label":"類型","value":"氣化式加濕器"},{"label":"水箱","value":"3.2升，上部加水"},{"label":"模式","value":"濕度感應自動模式"}]',
                    "disclaimers": disclaimer["zh-HK"],
                },
            },
        },
        {
            "sku": "AIR-TP-H1B",
            "slug": "airdog-top-plate-black",
            "price": 4950,
            "color": "Matte Black",
            "size": "Φ260 × 74 mm / 200 g (load approx. 5 kg)",
            "order": 70,
            "image": "/assets/img/usr/slider/slider_topplate.jpg",
            "cat": options.id,
            "tr": {
                "en": {
                    "name": "Airdog top plate | Matte Black",
                    "subtitle": "Optional top plate",
                    "description": "Optional matte-black top plate (Φ260 × 74 mm, 200 g, load about 5 kg).",
                    "included": "① Top plate",
                    "specs": '[{"label":"Size","value":"Φ260 × 74 mm"},{"label":"Weight","value":"200 g"},{"label":"Load","value":"Approx. 5 kg"},{"label":"Color","value":"Matte Black"}]',
                    "disclaimers": "",
                },
                "zh-CN": {
                    "name": "Airdog顶板｜哑光黑",
                    "subtitle": "选配顶板",
                    "description": "哑光黑选配顶板（Φ260×74 mm，200 g，承重约5 kg）。",
                    "included": "① 顶板",
                    "specs": '[{"label":"尺寸","value":"Φ260 × 74 mm"},{"label":"质量","value":"200 g"},{"label":"承重","value":"约5 kg"},{"label":"颜色","value":"哑光黑"}]',
                    "disclaimers": "",
                },
                "zh-HK": {
                    "name": "Airdog頂板｜霧面黑",
                    "subtitle": "選配頂板",
                    "description": "霧面黑選配頂板（Φ260×74 mm，200 g，承重約5 kg）。",
                    "included": "① 頂板",
                    "specs": '[{"label":"尺寸","value":"Φ260 × 74 mm"},{"label":"質量","value":"200 g"},{"label":"承重","value":"約5 kg"},{"label":"顏色","value":"霧面黑"}]',
                    "disclaimers": "",
                },
            },
        },
        {
            "sku": "AIR-CARE-PLUS",
            "slug": "airdog-care-plus",
            "price": 11000,
            "service": True,
            "order": 90,
            "image": "/assets/img/usr/slider/slider_airdogcare-plus.jpg",
            "cat": None,
            "tr": {
                "en": {
                    "name": "Airdog CARE+",
                    "subtitle": "Extended care program",
                    "description": "Join for ¥11,000 (tax included): 2-year extended warranty (3 years total with the standard 1-year warranty), free loaner during repair, free take-back when replacing an X Series unit (once), ¥11,000 coupon for later purchases of eligible models, and a thanks gift cleaner set. Damage caused by the customer is excluded.",
                    "included": "Service enrollment. Thanks gift: filter cleaner, ionizing wire-frame cleaner, collection-filter brush.",
                    "specs": '[{"label":"Fee","value":"¥11,000 tax included"},{"label":"Warranty","value":"+2 years (3 years from purchase)"},{"label":"Loaner","value":"Free during repair"},{"label":"Take-back","value":"X Series replacement, once"}]',
                    "disclaimers": "Repair coverage follows the warranty terms. Customer-caused damage or soiling is excluded.",
                },
                "zh-CN": {
                    "name": "Airdog CARE+",
                    "subtitle": "延长关爱计划",
                    "description": "11,000日元（含税）加入：产品2年延长保修（含原1年共3年无偿修理）、修理期间免费借机、换购X系列时免费回收旧机（限1次）、后续可用的11,000日元优惠券，以及感谢礼清洁套装。顾客原因导致的破损污损不在保修范围。",
                    "included": "服务加入。感谢礼：滤网清洁剂、电离丝框清洁器、集尘滤网刷。",
                    "specs": '[{"label":"费用","value":"含税 11,000日元"},{"label":"保修","value":"延长2年（自购买起共3年）"},{"label":"借机","value":"修理期间免费"},{"label":"回收","value":"换购X系列时限1次"}]',
                    "disclaimers": "修理内容以保修条款为准。顾客原因造成的破损、污损不在保修范围。",
                },
                "zh-HK": {
                    "name": "Airdog CARE+",
                    "subtitle": "延長關懷計劃",
                    "description": "11,000日圓（連稅）加入：產品2年延長保用（連原1年共3年免費修理）、修理期間免費借機、換購X系列時免費回收舊機（限1次）、其後可用的11,000日圓優惠券，以及感謝禮清潔套裝。顧客原因導致的破損污損不在保用範圍。",
                    "included": "服務登記。感謝禮：濾網清潔劑、電離絲框清潔器、集塵濾網刷。",
                    "specs": '[{"label":"費用","value":"連稅 11,000日圓"},{"label":"保用","value":"延長2年（自購買起共3年）"},{"label":"借機","value":"修理期間免費"},{"label":"回收","value":"換購X系列時限1次"}]',
                    "disclaimers": "修理內容以保用條款為準。顧客原因造成的破損、污損不在保用範圍。",
                },
            },
        },
    ]

    for item in products:
        cat_id = item.pop("cat")
        add_product(db, item, cat_id)

    news_items = [
        (
            "kumamoto-support-2026",
            datetime(2026, 8, 10),
            t3(
                "Airdog Japan, Inc. supports areas affected by the 2026 Kumamoto earthquake",
                "株式会社Airdog Japan实施「令和8年熊本地震」受灾地支援",
                "株式會社Airdog Japan實施「令和8年熊本地震」受災地支援",
            ),
            t3(
                "Airdog Japan carried out support activities for communities affected by the 2026 Kumamoto earthquake.",
                "Airdog Japan就令和8年熊本地震开展了受灾地支援。",
                "Airdog Japan就令和8年熊本地震開展了受災地支援。",
            ),
        ),
        (
            "kumamoto-shipping-2026",
            datetime(2026, 7, 29),
            t3(
                "Product deliveries following the 2026 Kumamoto earthquake",
                "关于伴随令和8年熊本地震的商品配送",
                "關於伴隨令和8年熊本地震的商品配送",
            ),
            t3(
                "Deliveries may be delayed in some regions due to the earthquake. We appreciate your understanding.",
                "受地震影响，部分地区配送可能延迟，敬请谅解。",
                "受地震影響，部分地區配送可能延遲，敬請見諒。",
            ),
        ),
        (
            "kumamoto-hotline-2026",
            datetime(2026, 7, 28),
            t3(
                "Free-dial connectivity after the Kumamoto earthquake",
                "熊本县地震导致免费电话暂未能接通",
                "熊本縣地震導致免費電話暫未能接通",
            ),
            t3(
                "Our free-dial line experienced connection issues after the earthquake. Please use the contact form if you cannot reach us by phone.",
                "地震后免费电话一度难以接通。如电话无法联系，请使用询价表单。",
                "地震後免費電話一度難以接通。如電話無法聯絡，請使用查詢表格。",
            ),
        ),
        (
            "typhoon-shipping-2026",
            datetime(2026, 6, 24),
            t3(
                "Product deliveries during typhoon conditions",
                "关于台风期间的商品配送",
                "關於颱風期間的商品配送",
            ),
            t3(
                "Typhoons may delay carriers. We will ship as soon as service resumes.",
                "台风可能导致承运延迟，服务恢复后将尽快发货。",
                "颱風可能導致承運延遲，服務恢復後將盡快發貨。",
            ),
        ),
        (
            "tokyo-great-bears-2026",
            datetime(2026, 4, 10),
            t3(
                "Official supplier agreement with professional volleyball team Tokyo Great Bears",
                "与职业排球队「东京GREAT BEARS」签订官方供应商合约",
                "與職業排球隊「東京GREAT BEARS」簽訂官方供應商合約",
            ),
            t3(
                "Airdog Japan has signed an official supplier agreement with the Tokyo Great Bears.",
                "Airdog Japan已与东京GREAT BEARS签订官方供应商合约。",
                "Airdog Japan已與東京GREAT BEARS簽訂官方供應商合約。",
            ),
        ),
    ]
    for slug, when, titles, bodies in news_items:
        n = News(slug=slug, published_at=when)
        db.add(n)
        db.flush()
        for loc in LOCALES:
            db.add(NewsTranslation(news_id=n.id, locale=loc, title=titles[loc], body=bodies[loc]))

    pages = _pages()
    for slug, loc, title, body in pages:
        db.add(Page(slug=slug, locale=loc, title=title, body=body))

    db.commit()


def _pages() -> list[tuple[str, str, str, str]]:
    data: list[tuple[str, str, str, str]] = []

    def add(slug: str, titles: dict, bodies: dict) -> None:
        for loc in LOCALES:
            data.append((slug, loc, titles[loc], bodies[loc]))

    add(
        "faq",
        t3("FAQ", "常见问题", "常見問題"),
        t3(
            """<h2>Orders and membership</h2>
<h3>Q. Can I order without registering?</h3>
<p>Membership is required so we can provide after-sales care and important notices. If you later wish to close the account, contact us from My Account or the contact form.</p>
<h3>Q. Receipts</h3>
<p>Because checkout on this overseas storefront is inquiry-based, a formal receipt is issued after we confirm and fulfill your order. Marketplace purchases must be receipted by those stores.</p>
<h3>Q. I cannot log in</h3>
<p>Please reset the password from the login page or contact us. For security, repeated failed attempts may temporarily lock the account.</p>
<h2>Products</h2>
<p>Choose your model on the product page for specifications, care, and troubleshooting. Washable collection filters do not need routine replacement.</p>""",
            """<h2>订购与会员</h2>
<h3>Q. 不注册可以下单吗？</h3>
<p>为便于售后保养与重要通知，需要注册会员。如需退会，请通过「我的账户」或联系表单办理。</p>
<h3>Q. 关于发票／收据</h3>
<p>本海外站以询价下单，确认并履行订单后开具正式收据。第三方平台购买请向该店铺索取收据。</p>
<h3>Q. 无法登录</h3>
<p>请在登录页重设密码，或与我们联系。出于安全，连续失败可能导致暂时锁定。</p>
<h2>关于商品</h2>
<p>规格、保养与故障排查请见各商品页。集尘滤网可水洗，通常无需定期更换。</p>""",
            """<h2>訂購與會員</h2>
<h3>Q. 不登記可以落單嗎？</h3>
<p>為方便售後保養與重要通知，需要登記會員。如需取消會員，請透過「我的帳戶」或聯絡表格辦理。</p>
<h3>Q. 關於收據</h3>
<p>本海外站以查詢落單，確認並履行訂單後開具正式收據。第三方平台購買請向該店鋪索取收據。</p>
<h3>Q. 無法登入</h3>
<p>請在登入頁重設密碼，或與我們聯絡。出於安全，連續失敗可能導致暫時鎖定。</p>
<h2>關於商品</h2>
<p>規格、保養與故障排查請見各商品頁。集塵濾網可水洗，通常無需定期更換。</p>""",
        ),
    )
    add(
        "guide",
        t3("Shopping guide", "购物指南", "購物指南"),
        t3(
            """<p>Thank you for visiting the Airdog official store for customers outside Japan. You may request products via this website. A specialist will confirm stock, shipping, and payment instructions after you submit an inquiry checkout.</p>
<p>Hours for follow-up: 9:00–18:00 (Japan time), excluding Sundays and public holidays.</p>""",
            """<p>感谢访问面向日本以外顾客的Airdog官方商城。您可通过本站提交商品询价。提交询价结算后，专员将确认库存、物流与付款说明。</p>
<p>跟进时间：日本时间 9:00–18:00（周日及节假日除外）。</p>""",
            """<p>感謝訪問面向日本以外顧客的Airdog官方商城。您可透過本站提交商品查詢。提交查詢結帳後，專員將確認庫存、物流與付款說明。</p>
<p>跟進時間：日本時間 9:00–18:00（星期日及公眾假期除外）。</p>""",
        ),
    )
    add(
        "shipping",
        t3("Shipping", "配送与运费", "配送與運費"),
        t3(
            """<p>We aim to dispatch within 3 business days after an inquiry is confirmed as an order. Dates may change during order surges or according to stock.</p>
<p>International freight, duties, and taxes are quoted after we review destination and cart contents. Japan domestic notes on the original site (Okinawa / remote islands) do not apply to this overseas storefront.</p>""",
            """<p>询价确认成单后，我们力争3个工作日内发货。订单集中或库存情况可能导致日期变动。</p>
<p>国际运费、关税与税费将在确认目的地与购物车内容后报价。原日本站关于冲绳／离岛的说明不适用于本海外站。</p>""",
            """<p>查詢確認成單後，我們力爭3個工作天內發貨。訂單集中或庫存情況可能導致日期變動。</p>
<p>國際運費、關稅與稅費將在確認目的地與購物車內容後報價。原日本站關於沖繩／離島的說明不適用於本海外站。</p>""",
        ),
    )
    add(
        "warranty",
        t3("Warranty", "保修说明", "保用說明"),
        t3(
            """<p>Airdog units include a 1-year manufacturer repair warranty. Airdog CARE+ adds 2 further years (3 years from purchase). Customer-caused damage or soiling is excluded. Medical/care facility purchases may include an extra complimentary year when ordered through the dedicated program.</p>""",
            """<p>Airdog主机含1年厂商修理保修。Airdog CARE+再延长2年（自购买起共3年）。顾客原因造成的破损污损不在范围内。经医疗护理专区计划购买的，可能另获1年免费延长保修。</p>""",
            """<p>Airdog主機含1年廠商修理保用。Airdog CARE+再延長2年（自購買起共3年）。顧客原因造成的破損污損不在範圍內。經醫療護理專區計劃購買的，可能另獲1年免費延長保用。</p>""",
        ),
    )
    add(
        "import-attention",
        t3("Notice on parallel imports", "关于平行进口的注意事项", "關於平行進口的注意事項"),
        t3(
            """<p>Airdog Japan, Inc. is the authorized importer for Japan. Units obtained via unauthorized parallel import may not be eligible for official warranty, parts, or CARE+. Please purchase from authorized channels.</p>""",
            """<p>Airdog Japan, Inc.为日本授权进口商。经非授权平行进口取得的主机，可能无法享受官方保修、零件或CARE+。请通过授权渠道购买。</p>""",
            """<p>Airdog Japan, Inc.為日本授權進口商。經非授權平行進口取得的主機，可能無法享受官方保用、零件或CARE+。請透過授權渠道購買。</p>""",
        ),
    )
    add(
        "privacy",
        t3("Privacy policy", "隐私政策", "私隱政策"),
        t3(
            """<p>We collect the account, cart, and inquiry information you submit in order to respond to orders and support requests. We do not sell personal data. Cookies are used for login, cart, and language preference. See also the site terms.</p>""",
            """<p>我们收集您提交的账户、购物车与询价信息，用于回复订单与支持请求。我们不会出售个人数据。Cookie用于登录、购物车与语言偏好。详见网站使用条款。</p>""",
            """<p>我們收集您提交的帳戶、購物車與查詢資料，用於回覆訂單與支援請求。我們不會出售個人資料。Cookie用於登入、購物車與語言偏好。詳見網站使用條款。</p>""",
        ),
    )
    add(
        "company",
        t3("Company", "公司概要", "公司概要"),
        t3(
            """<h2>COMPANY</h2>
<table class="spec-table"><tbody>
<tr><th>Name</th><td>Airdog Japan, Inc. (株式会社エアドッグジャパン)</td></tr>
<tr><th>Directors</th><td>Representative Directors Shigemitsu Kitamura and Yoshinori Matsuura</td></tr>
<tr><th>Business</th><td>Import, sales, and wholesale of Airdog</td></tr>
<tr><th>Address</th><td>15F Shiodome City Center, 1-5-2 Higashi-Shimbashi, Minato-ku, Tokyo 105-7115, Japan</td></tr>
</tbody></table>
<p>Inquiries: use the contact form on this site.</p>""",
            """<h2>公司概要</h2>
<table class="spec-table"><tbody>
<tr><th>公司名称</th><td>株式会社エアドッグジャパン（英文：Airdog Japan, Inc.）</td></tr>
<tr><th>负责人</th><td>代表取缔役 北村 重光、代表取缔役 柗浦 好纪</td></tr>
<tr><th>业务内容</th><td>Airdog的进口、销售与批发</td></tr>
<tr><th>所在地</th><td>〒105-7115 东京都港区东新桥1-5-2 汐留City Center 15楼</td></tr>
</tbody></table>
<p>咨询请使用本站联系表单。</p>""",
            """<h2>公司概要</h2>
<table class="spec-table"><tbody>
<tr><th>公司名稱</th><td>株式會社エアドッグジャパン（英文：Airdog Japan, Inc.）</td></tr>
<tr><th>負責人</th><td>代表取締役 北村 重光、代表取締役 柗浦 好紀</td></tr>
<tr><th>業務內容</th><td>Airdog的進口、銷售與批發</td></tr>
<tr><th>所在地</th><td>〒105-7115 東京都港區東新橋1-5-2 汐留City Center 15樓</td></tr>
</tbody></table>
<p>查詢請使用本站聯絡表格。</p>""",
        ),
    )
    add(
        "seller-info",
        t3("Seller information", "销售者信息", "銷售者資料"),
        t3(
            """<p>This storefront is operated for customers outside Japan. It is not a Specified Commercial Transactions Act listing for domestic Japan e-commerce.</p>
<table class="spec-table"><tbody>
<tr><th>Seller</th><td>Airdog Japan, Inc.</td></tr>
<tr><th>Address</th><td>15F Shiodome City Center, 1-5-2 Higashi-Shimbashi, Minato-ku, Tokyo 105-7115, Japan</td></tr>
<tr><th>Contact</th><td>Contact form on this website</td></tr>
<tr><th>Pricing</th><td>Prices displayed in Japanese yen (tax-included JP list). International quotes follow inquiry checkout.</td></tr>
<tr><th>Payment</th><td>Arranged after inquiry confirmation (no online card capture on this site).</td></tr>
<tr><th>Returns</th><td>First-unit 30-day refund policy may apply as described on product pages; return shipping is paid by the customer unless the item is defective.</td></tr>
</tbody></table>""",
            """<p>本商城面向日本以外顾客运营，并非日本《特定商交易法》国内电商公示页。</p>
<table class="spec-table"><tbody>
<tr><th>销售者</th><td>Airdog Japan, Inc.</td></tr>
<tr><th>地址</th><td>东京都港区东新桥1-5-2 汐留City Center 15楼</td></tr>
<tr><th>联系</th><td>本站联系表单</td></tr>
<tr><th>价格</th><td>页面显示含税日元标价；国际报价在询价结算后确认。</td></tr>
<tr><th>支付</th><td>询价确认后另行安排（本站不在线扣款）。</td></tr>
<tr><th>退货</th><td>商品页所述首次购买30日退款政策可能适用；非质量问题的退货运费由顾客承担。</td></tr>
</tbody></table>""",
            """<p>本商城面向日本以外顧客營運，並非日本《特定商交易法》國內電商公示頁。</p>
<table class="spec-table"><tbody>
<tr><th>銷售者</th><td>Airdog Japan, Inc.</td></tr>
<tr><th>地址</th><td>東京都港區東新橋1-5-2 汐留City Center 15樓</td></tr>
<tr><th>聯絡</th><td>本站聯絡表格</td></tr>
<tr><th>價格</th><td>頁面顯示連稅日圓標價；國際報價在查詢結帳後確認。</td></tr>
<tr><th>付款</th><td>查詢確認後另行安排（本站不線上扣款）。</td></tr>
<tr><th>退貨</th><td>商品頁所述首次購買30日退款政策可能適用；非質素問題的退貨運費由顧客承擔。</td></tr>
</tbody></table>""",
        ),
    )
    add(
        "terms-of-sales",
        t3("Terms of sale", "销售条款", "銷售條款"),
        t3(
            """<p>By submitting an inquiry checkout you request a quotation and order confirmation. A contract is formed only when we accept the inquiry. Prices are in yen unless a separate quote is issued. We may decline orders that exceed parts-quantity limits or appear to be unauthorized resale.</p>""",
            """<p>提交询价结算即表示您请求报价与订单确认。仅在我方接受询价后合同成立。除非另有报价，价格以日元计。超出零件数量限制或疑似未经授权转售的订单可能被拒绝。</p>""",
            """<p>提交查詢結帳即表示您請求報價與訂單確認。僅在我方接受查詢後合約成立。除非另有報價，價格以日圓計。超出零件數量限制或疑似未經授權轉售的訂單可能被拒絕。</p>""",
        ),
    )
    add(
        "terms-of-use",
        t3("Website terms of use", "网站使用条款", "網站使用條款"),
        t3(
            """<p>Please use this site lawfully. Do not attempt unauthorized access or disrupt services. Content, trademarks (including Airdog), and product photography remain the property of their owners. Cookies support login, cart, and language. We may update these terms; continued use constitutes acceptance.</p>""",
            """<p>请合法使用本站。禁止未经授权的访问或干扰服务。内容、商标（含Airdog）与产品图片归权利人所有。Cookie用于登录、购物车与语言。条款可能更新，继续使用即视为同意。</p>""",
            """<p>請合法使用本站。禁止未經授權的訪問或干擾服務。內容、商標（含Airdog）與產品圖片歸權利人所有。Cookie用於登入、購物車與語言。條款可能更新，繼續使用即視為同意。</p>""",
        ),
    )
    add(
        "terms-of-airdogcare",
        t3("Airdog CARE+ terms", "Airdog CARE+ 使用条款", "Airdog CARE+ 使用條款"),
        t3(
            """<p>CARE+ is an optional paid support program. Benefits include extended warranty, loaner, limited take-back, coupon, and gift as described on the CARE+ page. Coverage follows the product warranty booklet. Customer-caused damage is excluded. Coupon use and gift contents may change.</p>""",
            """<p>CARE+为可选付费支持服务。权益包括延长保修、借机、有限回收、优惠券与赠品，详见CARE+页面。范围以产品保修条款为准。顾客原因损坏除外。优惠券使用与赠品内容可能调整。</p>""",
            """<p>CARE+為可選付費支援服務。權益包括延長保用、借機、有限回收、優惠券與贈品，詳見CARE+頁面。範圍以產品保用條款為準。顧客原因損壞除外。優惠券使用與贈品內容可能調整。</p>""",
        ),
    )
    add(
        "medical",
        t3("For medical and care facilities", "医疗・护理机构", "醫療・護理機構"),
        t3(
            """<p class="lead">To bring peace of mind to the front line of medical and nursing care.</p>
<p>We offer respect to those providing care every day. By improving air quality we hope to reduce burden and unease inside facilities.</p>
<p><strong>Complimentary 1-year manufacturer warranty + 1-year extension</strong> for corporate purchases of Airdog X8D Pro, X5D, X3D, or X1D placed through this medical/care page (facility orders only; veterinary hospitals and personal purchases are excluded). Program noted from 22 January 2026 on the Japan site.</p>
<ul>
<li>Removes particles down to 0.0146 μm with patented TPA filter technology (chamber tests; 99.9%+ of a test virus in 29 minutes at L4 in a 25 m³ space, Kitasato Research Center for Environmental Science).</li>
<li>Washable collection filter — no routine filter-replacement cost.</li>
<li>Quiet design suitable for 24-hour operation.</li>
</ul>""",
            """<p class="lead">为医疗与护理一线送去「安心」。</p>
<p>向每日奋战在护理一线的各位致以敬意。我们希望通过提升空气质量，减轻负担、消除设施内的不安。</p>
<p><strong>免费提供1年厂商保修＋1年延长保修</strong>，适用于经本医疗护理专区订购Airdog X8D Pro、X5D、X3D、X1D的法人订单（限设施直接订购；动物医院与个人购买除外）。日本站标注自2026年1月22日起。</p>
<ul>
<li>专利TPA滤网可去除小至0.0146μm的微粒（密闭试验；北里环境科学中心在25m³、L4下29分钟对一种浮游病毒去除99.9%以上）。</li>
<li>集尘滤网可水洗，无需定期更换费用。</li>
<li>静音设计，适合24小时运转。</li>
</ul>""",
            """<p class="lead">為醫療與護理一線送上「安心」。</p>
<p>向每日奮戰在護理一線的各位致意。我們希望透過提升空氣質素，減輕負擔、消除設施內的不安。</p>
<p><strong>免費提供1年廠商保用＋1年延長保用</strong>，適用於經本醫療護理專區訂購Airdog X8D Pro、X5D、X3D、X1D的法人訂單（限設施直接訂購；動物醫院與個人購買除外）。日本站標註自2026年1月22日起。</p>
<ul>
<li>專利TPA濾網可去除小至0.0146μm的微粒（密閉試驗；北里環境科學中心在25m³、L4下29分鐘對一種浮游病毒去除99.9%以上）。</li>
<li>集塵濾網可水洗，無需定期更換費用。</li>
<li>靜音設計，適合24小時運轉。</li>
</ul>""",
        ),
    )
    add(
        "care-plus",
        t3("Airdog CARE+", "Airdog CARE+", "Airdog CARE+"),
        t3(
            """<p>Airdog CARE+ is a support service so you can use Airdog with confidence. Enrollment is ¥11,000 including tax.</p>
<ol>
<li>2-year extended product warranty (3 years from purchase together with the standard 1-year warranty).</li>
<li>Free loaner unit during repair.</li>
<li>Free take-back of an X Series unit when you purchase a replacement X Series (once).</li>
<li>¥11,000 coupon for later eligible purchases (single items ¥30,000+ excl. tax such as X Series, mini, moi).</li>
<li>Thanks gift: dedicated cleaner set (filter cleaner, ionizing wire-frame cleaner, collection-filter brush).</li>
</ol>
<p>Add CARE+ from the product catalog or submit an inquiry with your cart.</p>""",
            """<p>Airdog CARE+ 是为长久安心使用Airdog而设的支持服务。加入费用含税11,000日元。</p>
<ol>
<li>产品2年延长保修（与原1年合计自购买起3年无偿修理）。</li>
<li>修理时免费借出替代机。</li>
<li>换购X系列时免费回收旧X系列（限1次）。</li>
<li>后续可用的11,000日元优惠券（适用于税前3万日元以上的单品，如X系列、mini、moi）。</li>
<li>感谢礼：专用清洁套装。</li>
</ol>
<p>可从商品目录加入CARE+，或连同购物车提交询价。</p>""",
            """<p>Airdog CARE+ 是為長久安心使用Airdog而設的支援服務。加入費用連稅11,000日圓。</p>
<ol>
<li>產品2年延長保用（與原1年合計自購買起3年免費修理）。</li>
<li>修理時免費借出替代機。</li>
<li>換購X系列時免費回收舊X系列（限1次）。</li>
<li>其後可用的11,000日圓優惠券（適用於稅前3萬日圓以上的單品，如X系列、mini、moi）。</li>
<li>感謝禮：專用清潔套裝。</li>
</ol>
<p>可從商品目錄加入CARE+，或連同購物車提交查詢。</p>""",
        ),
    )
    add(
        "filter-service",
        t3("Filter replacement service", "滤网更换服务", "濾網更換服務"),
        t3(
            """<p>The dedicated filter-exchange portal <a href="https://airdogjapan-service.jp/" target="_blank" rel="noreferrer">airdogjapan-service.jp</a> is operated for customers in Japan. TPA collection filters are washable and do not require routine replacement. For overseas maintenance parts, please use the contact form or add parts to your cart and send an inquiry.</p>""",
            """<p>专用滤网更换门户 <a href="https://airdogjapan-service.jp/" target="_blank" rel="noreferrer">airdogjapan-service.jp</a> 面向日本顾客运营。TPA集尘滤网可水洗，通常无需定期更换。海外保养零件请使用联系表单，或将零件加入购物车后提交询价。</p>""",
            """<p>專用濾網更換門戶 <a href="https://airdogjapan-service.jp/" target="_blank" rel="noreferrer">airdogjapan-service.jp</a> 面向日本顧客營運。TPA集塵濾網可水洗，通常無需定期更換。海外保養零件請使用聯絡表格，或將零件加入購物車後提交查詢。</p>""",
        ),
    )
    add(
        "returns",
        t3("Cancellations and returns", "取消与退货", "取消與退貨"),
        t3(
            """<p>For a first-time purchase of one unit, returns may be accepted within 30 days of arrival even after opening. Return shipping is paid by the customer. Unopened returns within 8 days may also be accepted. Beyond the window, or for customer-caused damage, we cannot refund. Defective units are handled under warranty.</p>""",
            """<p>首次购买且限1台时，到货后30日内即使已开封也可申请退货。退货运费由顾客承担。8日内未开封亦可受理。逾期或因顾客原因损坏无法退款。不良品按保修处理。</p>""",
            """<p>首次購買且限1台時，到貨後30日內即使已開封亦可申請退貨。退貨運費由顧客承擔。8日內未開封亦可受理。逾期或因顧客原因損壞無法退款。不良品按保用處理。</p>""",
        ),
    )
    return data
