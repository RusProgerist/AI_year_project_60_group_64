import urllib.request
import urllib.parse
import re
import os
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

texts = [
    # Чехов
    ("chekhov_toska", "https://ru.wikisource.org/wiki/Тоска_(Чехов)"),
    ("chekhov_spat", "https://ru.wikisource.org/wiki/Спать_хочется_(Чехов)"),
    ("chekhov_ionych", "https://ru.wikisource.org/wiki/Ионыч"),
    ("chekhov_dushechka", "https://ru.wikisource.org/wiki/Душечка_(Чехов)"),
    ("chekhov_dama_s_sobachkoy", "https://ru.wikisource.org/wiki/Дама_с_собачкой_(Чехов)"),
    ("chekhov_palata_6", "https://ru.wikisource.org/wiki/Палата_№_6_(Чехов)"),
    ("chekhov_kryzhovnik", "https://ru.wikisource.org/wiki/Крыжовник_(Чехов)"),
    ("chekhov_chelovek_v_futlyare", "https://ru.wikisource.org/wiki/Человек_в_футляре_(Чехов)"),
    ("chekhov_skuchnaya_istoriya", "https://ru.wikisource.org/wiki/Скучная_история_(Чехов)"),
    ("chekhov_cherny_monah", "https://ru.wikisource.org/wiki/Чёрный_монах_(Чехов)"),
    ("chekhov_strahi", "https://ru.wikisource.org/wiki/Страхи_(Чехов)"),
    ("chekhov_nervy", "https://ru.wikisource.org/wiki/Нервы_(Чехов)"),
    ("chekhov_dyadya_vanya", "https://ru.wikisource.org/wiki/Дядя_Ваня_(Чехов)"),
    ("chekhov_tri_sestry", "https://ru.wikisource.org/wiki/Три_сестры_(Чехов)"),
    ("chekhov_vishnevy_sad", "https://ru.wikisource.org/wiki/Вишнёвый_сад_(Чехов)"),
    ("chekhov_smert_chinovnika", "https://ru.wikisource.org/wiki/Смерть_чиновника_(Чехов)"),
    
    # Пушкин
    ("pushkin_evgeny_onegin", "https://ru.wikisource.org/wiki/Евгений_Онегин_(Пушкин)"),
    ("pushkin_pikovaya_dama", "https://ru.wikisource.org/wiki/Пиковая_дама_(Пушкин)"),
    ("pushkin_medny_vsadnik", "https://ru.wikisource.org/wiki/Медный_всадник_(Пушкин)"),
    ("pushkin_stancionny_smotritel", "https://ru.wikisource.org/wiki/Станционный_смотритель_(Пушкин)"),
    ("pushkin_dubrovsky", "https://ru.wikisource.org/wiki/Дубровский_(Пушкин)"),
    ("pushkin_vystrel", "https://ru.wikisource.org/wiki/Выстрел_(Пушкин)"),
    
    # Лермонтов
    ("lermontov_geroi_nashego_vremeni", "https://ru.wikisource.org/wiki/Герой_нашего_времени_(Лермонтов)"),
    ("lermontov_maska_rad", "https://ru.wikisource.org/wiki/Маскарад_(Лермонтов)"),
    ("lermontov_mcyri", "https://ru.wikisource.org/wiki/Мцыри_(Лермонтов)"),
    
    # Гоголь
    ("gogol_shinel", "https://ru.wikisource.org/wiki/Шинель_(Гоголь)"),
    ("gogol_zapiski_sumasshedshego", "https://ru.wikisource.org/wiki/Записки_сумасшедшего_(Гоголь)"),
    ("gogol_portret", "https://ru.wikisource.org/wiki/Портрет_(Гоголь)"),
    ("gogol_nevsky_prospekt", "https://ru.wikisource.org/wiki/Невский_проспект_(Гоголь)"),
    ("gogol_taras_bulba", "https://ru.wikisource.org/wiki/Тарас_Бульба_(Гоголь)"),
    
    # Тургенев
    ("turgenev_otcy_i_deti", "https://ru.wikisource.org/wiki/Отцы_и_дети_(Тургенев)"),
    ("turgenev_dvoryanskoe_gnezdo", "https://ru.wikisource.org/wiki/Дворянское_гнездо_(Тургенев)"),
    ("turgenev_asya", "https://ru.wikisource.org/wiki/Ася_(Тургенев)"),
    ("turgenev_mumu", "https://ru.wikisource.org/wiki/Муму_(Тургенев)"),
    ("turgenev_dnevnik_lishnego_cheloveka", "https://ru.wikisource.org/wiki/Дневник_лишнего_человека_(Тургенев)"),
    
    # Достоевский
    ("dostoevsky_prestuplenie_i_nakazanie", "https://ru.wikisource.org/wiki/Преступление_и_наказание_(Достоевский)"),
    ("dostoevsky_idiot", "https://ru.wikisource.org/wiki/Идиот_(Достоевский)"),
    ("dostoevsky_belye_nochi", "https://ru.wikisource.org/wiki/Белые_ночи_(Достоевский)"),
    ("dostoevsky_zapiski_iz_podpolya", "https://ru.wikisource.org/wiki/Записки_из_подполья"),
    ("dostoevsky_igrok", "https://ru.wikisource.org/wiki/Игрок_(Достоевский)"),
    ("dostoevsky_dvoynik", "https://ru.wikisource.org/wiki/Двойник_(Достоевский)"),
    ("dostoevsky_gospodin_proharhin", "https://ru.wikisource.org/wiki/Господин_Прохарчин"),
    ("dostoevsky_son_smeshnogo_cheloveka", "https://ru.wikisource.org/wiki/Сон_смешного_человека"),
    
    # Толстой
    ("tolstoy_anna_karenina", "https://ru.wikisource.org/wiki/Анна_Каренина_(Толстой)"),
    ("tolstoy_smert_ivana_ilicha", "https://ru.wikisource.org/wiki/Смерть_Ивана_Ильича"),
    ("tolstoy_voskresenie", "https://ru.wikisource.org/wiki/Воскресение_(Толстой)"),
    ("tolstoy_holstomer", "https://ru.wikisource.org/wiki/Холстомер"),
    ("tolstoy_otets_sergiy", "https://ru.wikisource.org/wiki/Отец_Сергий"),
    ("tolstoy_kavkazsky_plennik", "https://ru.wikisource.org/wiki/Кавказский_пленник_(Толстой)"),
    ("tolstoy_zapiski_sumasshedshego", "https://ru.wikisource.org/wiki/Записки_сумасшедшего_(Толстой)"),
    
    # Салтыков-Щедрин, Бунин, Горький, Куприн, Короленко
    ("saltykov_gospoda_golovlevy", "https://ru.wikisource.org/wiki/Господа_Головлёвы"),
    ("saltykov_ubezhische_monrepo", "https://ru.wikisource.org/wiki/Убежище_Монрепо"),
    ("bunin_gospodin_iz_san_francisko", "https://ru.wikisource.org/wiki/Господин_из_Сан-Франциско"),
    ("bunin_tyomnye_allei", "https://ru.wikisource.org/wiki/Тёмные_аллеи"),
    ("gorky_na_dne", "https://ru.wikisource.org/wiki/На_дне"),
    ("gorky_staruha_izergil", "https://ru.wikisource.org/wiki/Старуха_Изергиль"),
    ("kuprin_granatovy_braslet", "https://ru.wikisource.org/wiki/Гранатовый_браслет"),
    ("kuprin_poedinok", "https://ru.wikisource.org/wiki/Поединок_(Куприн)"),
    ("korolenko_v_durnom_obshchestve", "https://ru.wikisource.org/wiki/В_дурном_обществе"),
]

raw_dir = "data/raw/"
os.makedirs(raw_dir, exist_ok=True)

success = 0
fail = 0
skipped = 0

for file_id, url in texts:
    filepath = os.path.join(raw_dir, f"{file_id}.txt")
    
    # Если файл уже есть — удаляем его, чтобы скачать заново чистый
    if os.path.exists(filepath):
        os.remove(filepath)
        
    print(f"Скачиваю: {file_id}...")
    try:
        url_encoded = urllib.parse.quote(url, safe=':/?&=')
        req = urllib.request.Request(url_encoded, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        response = urllib.request.urlopen(req, timeout=15)
        html_bytes = response.read()
        
        try:
            html = html_bytes.decode('utf-8')
        except UnicodeDecodeError:
            html = html_bytes.decode('windows-1251', errors='ignore')
        
        html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', html)
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        print(f"  ✅ {len(clean_text)} символов")
        success += 1
    except Exception as e:
        print(f"  ❌ {e}")
        fail += 1
    time.sleep(1)

print(f"\nИтог: {success} скачано, {fail} ошибок")