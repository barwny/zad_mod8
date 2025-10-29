import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values
import base64
import requests
import os

# przekazanie klucza OpenAI do zmiennej api_key z secrets (Streamlit Cloud) lub .env
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY") or dotenv_values(".env").get("OPENAI_API_KEY")

api_key = (api_key or "").strip()

if not api_key or not (api_key.startswith("sk-") or api_key.startswith("sk-proj-")):
    st.error("Brak lub niepoprawny OPENAI_API_KEY. Na Streamlit Cloud dodaj w Secrets: OPENAI_API_KEY = \"sk-...\" i zrestartuj aplikację.")
    st.stop()

# utworzenie klienta OpenAI do komunikacji z LLM
openai_client = OpenAI(api_key=api_key)

# nagłówek aplikacji
st.markdown(
    """
    <h3 style='text-align: center;
               color: #808080;
               font-size: 20px;
               font-weight: bold;
               font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
               line-height: 1.4;
               margin-bottom: 20px;'>
        🧙‍♂️ Witaj! W tej wersji aplikacji wyczaruję dla ciebie twórcze aktywności<br>
        na spędzenie wolnego czasu.<br>
        Z menu po lewej wybierz odpowiednie opcje, żebym wiedział dla kogo czaruję 🪄
    </h3>
    """,
    unsafe_allow_html=True
)

# sprawdzenie stanu sesji dla wygebrowanych obrazów i opowiadania
if "generated_images" not in st.session_state:
    st.session_state["generated_images"] = {}
if "generated_stories" not in st.session_state:
    st.session_state["generated_stories"] = {}

# menu boczne (filtry)
with st.sidebar:
    st.markdown("Używając poniższych fitrów opisz siebie:")
    person = st.radio("Kim jestem:", ['Dziewczynka', 'Chłopiec'])
    age = st.selectbox("Wiek:", ['3-5 lat', '6-9 lat', '9-12 lat'])

# przypisanie do tabs wartosci nazw tabów (zakładek)
tabs = ["Kolorowanka", "Połącz kropki", "Pisanie po śladzie",
        "Znajdź ukryte przedmioty", "Stwórz obraz", "Krótkie opowiadanie",]

# utworzenie zakładek (opcji) na ekranie głównym
tab_obj = st.tabs(tabs)

# iteracja po nazwach zakładek - przypisanie odpowiedniego działania 
for i, tab in enumerate(tab_obj):
    with tab:

        # warunki dla zakładki "Stwórz obraz"
        if tabs[i] == "Stwórz obraz":
            user_prompt = st.text_area(
            "🧙‍♂️ Opisz jaki obraz mam wyczarować, lub zdaj się na mnie..",
            key=f"free_{i}",
            placeholder="np. 'kot i pies bawią się w parku', 'dinozaur na hulajnodze'..."
            )
        else:
            user_prompt = ""
        # przycisk dla każdej zakładki przekazujący warunki danej zakładki
        if st.button("Wyczaruj...🪄", key=f"create_{i}"):
            with st.spinner(""):

                # przypisanie do zmiennej user_desc string konfiguarcji filtrów
                user_desc = f"Dziecko, {person}, wiek: {age}"

                # warunki dla zakładki "Krótkie opowiadanie"
                if tabs[i] != "Krótkie opowiadanie":
                    
                    # warunki dla zakładki Kolorowanka
                    if tabs[i] == "Kolorowanka":
                        full_prompt = (
                            "Stwórz prosty czarno-biały rysunek-kolorowankę. "
                            "Temat: 'dowolny'. "
                            f"Dostosuj rysunek do odbiorcy: {user_desc}"
                            "Styl: wyraźne linie, brak koloru, idealne do druku jako kolorowanka lub zadanie."
                        )

                    # warunki dla zakładki "Połącz kropki"
                    elif tabs[i] == "Połącz kropki":
                        full_prompt = (
                            "Stwórz czarno-białą łamigłówkę typu 'połącz kropki / śledzenie konturu' do druku (line art, 1024x1024). "
                            "Temat kształtu: 'dowolny'. "
                            f"Dostosuj do odbiorcy: {user_desc}. "
                            "Narysuj obraz złożony WYŁĄCZNIE z kropek lub krótkich przerywanych odcinków wyznaczających kontury motywu. "
                            "Kropki równomiernie rozmieszczone wzdłuż wszystkich linii konturu i ważniejszych detali; "
                            "dla młodszych: większe kropki i mniejsze odstępy; dla starszych: drobniejsze kropki i większe odstępy."
                            "NIE umieszczaj żadnych numerów, liter, strzałek ani linii łączących kropki. "
                            "Nie pokazuj gotowego ciągłego konturu — tylko kropki/przerywane linie do samodzielnego połączenia. "
                            "Tło proste, bez zbędnych detali i napisów. "
                            "Styl: wyraźne czarne punkty/kreski; brak koloru, idealne do druku jako kolorowanka lub zadanie."
                        )

                    # warunki dla zakładki "Pisanie po śladzie"
                    elif tabs[i] == "Pisanie po śladzie":
                        full_prompt = (
                        "Stwórz czarno-białą kartę pracy 'pisanie po śladzie' (line art, 1024x1024). "
                        f"Dostosuj kartę do odbiorcy: {user_desc}. "
                        "Podziel stronę na 5 POZIOMYCH WIERSZY ćwiczeń o równym odstępie. "
                        "W każdym wierszu umieść jeden powtarzany wzór narysowany PRZERYWANĄ linią (kropki lub krótkie kreski) do odrysowania: "
                        "fale, zygzaki, łuki 'górki‑dołki', pętelki/ósemki, proste spiralki lub meandry. "
                        "Na początku wiersza umieść małą kropkę START, na końcu małą gwiazdkę META. "
                        "Zachowaj równe marginesy (~5% dookoła). "
                        "Bez liczb, liter, strzałek i podpisów. "
                        "Styl: wyraźny, czarny kontur kropek/kreskowania; tylko czerń i biel (bez szarości); wysoki kontrast; idealne do druku."
                        )

                    # warunki dla zakładki "Znajdź ukryte przedmioty"
                    elif tabs[i] == "Znajdź ukryte przedmioty":
                        full_prompt = (
                            "Stwórz czarno-białą łamigłówkę typu 'znajdź ukryte przedmioty' (line art, 1024x1024). "
                            "Samodzielnie wybierz prosty, przyjazny dzieciom motyw sceny (np. las, kosmos, farma, park). "
                            f"Dostosuj rysunek do odbiorcy: {user_desc}"
                            "Następnie samodzielnie wybierz 2 proste przedmioty PO POLSKU (rzeczowniki, 2 słowa, np. klucz, gwiazda, serce) "
                            "i sprytnie ukryj je w scenie (co najmniej po 1 raz), zachowując rozpoznawalne kształty. "
                            "Nie dodawaj żadnego tekstu w głównej scenie. "
                            "Każdy przedmiot musi wystąpić co najmniej 2 razy, być czytelny w zarysie, nie w 100% zasłonięty, "
                            "o wielkości min. ~3% szerokości kadru. Tło ma być proste, żeby przedmioty dało się znaleźć. "
                            "Nie umieszczaj żadnego tekstu w głównej scenie. "
                            "Na dole narysuj biały pasek/ramkę o wys. ~15% z czarną obwódką. "
                            "W ramce dodaj tytuł 'Znajdz:' i wypunktowaną listę DOKŁADNIE tych 2 wybranych słów. "
                            "LISTA MUSI DOKŁADNIE ODWZOROWYWAĆ PRZEDMIOTY narysowane w scenie; "
                            "jeśli zmienisz którykolwiek przedmiot, zaktualizuj listę. "
                            "Użyj dużych, prostych drukowanych liter, czarny tekst na białym tle, wyrównanie do lewej. "
                            "Styl: wyraźne, czarne kontury, wysoki kontrast, tylko czerń i biel (bez szarości)."
                        )

                    # warunki dla zakładki "Stwórz obraz"
                    elif tabs[i] == "Stwórz obraz":
                            text = user_prompt.strip()
                            if text:
                                # użytkownik wprowadził opis w zmiennej text
                                full_prompt = (
                                    "Stwórz kolorową ilustrację w stylu przyjaznym dzieciom. "
                                    f"Temat: '{text}'. "
                                    f"Dostosuj ilustrację do odbiorcy: {user_desc}. "
                                    "Styl: żywe, przyjazne kolory; wyraźne, czyste kontury; proste, nieprzeładowane tło; "
                                    "brak tekstu i znaków wodnych; format 1024x1024."
                                )
                            else:
                                # użytkonik nie wprowadził opsiu w zmiennej text
                                full_prompt = (
                                    "Stwórz kolorową ilustrację w stylu przyjaznym dzieciom. "
                                    f"Dostosuj ilustrację do odbiorcy: {user_desc}. "
                                    "Samodzielnie wybierz prosty, pogodny motyw odpowiedni do wieku (np. zwierzęta, zabawa, pojazdy, kosmos). "
                                    "Styl: żywe, przyjazne kolory; wyraźne, czyste kontury; proste, nieprzeładowane tło; "
                                    "brak tekstu i znaków wodnych; format 1024x1024."
                                )
                       
# MAIN PROGRAM

                    # generowanie obrazu na podstawie warunków z danej zakładki
                    image = openai_client.images.generate(
                        model="gpt-image-1",
                        prompt=full_prompt,
                        size="1024x1024",
                    )

                    img_data = image.data[0]
                    image_url = getattr(img_data, "url", None)
                    caption = f"{tabs[i]} – motyw auto"

                    # wyświetlenie wygenerowanego obrazu istniejącego w image_url + możliwość pobrania
                    if image_url:
                        st.image(image_url, caption=caption, use_container_width=True)
                        st.download_button(
                            label="🧙‍♂️ Pobierz obraz",
                            data=requests.get(image_url).content,
                            file_name=f"{tabs[i].lower().replace(' ', '_')}.png",
                            mime="image/png"
                        )

                        # zapis obrazu w stanie sesji
                        st.session_state["generated_images"][tabs[i]] = image_url

                    # wyświetlenie wygenerowanego przechowanego w zmiennej image_bytes )w formacie base64) + możliwość pobrania
                    elif hasattr(img_data, "b64_json") and img_data.b64_json:
                        image_bytes = base64.b64decode(img_data.b64_json)
                        st.image(image_bytes, caption=caption, use_container_width=True)
                        st.download_button(
                            label="💾 Pobierz obraz",
                            data=image_bytes,
                            file_name=f"{tabs[i].lower().replace(' ', '_')}.png",
                            mime="image/png"
                        )

                        # zapis obrazu w stanie sesji
                        st.session_state["generated_images"][tabs[i]] = img_data.b64_json

                    else:
                        st.error("🧙‍♂️ Nie udało się wyczarować, spróbuj ponownie.")

                # warunki dla zakładki "Krótkie opowiadanie"
                else:
                    story_prompt = (
                        f"Napisz krótkie, wesołe opowiadanie dla dziecka ({user_desc}). "
                        "Maksymalnie 10 zdań. "
                        "Język prosty, ciepły, przyjazny, pełen wyobraźni. "
                        "Temat może być dowolny, ale odpowiedni dla wieku dziecka."
                    )
                    # generowanie tesktu przez LLM
                    story_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Jesteś narratorem bajek dla dzieci."},
                            {"role": "user", "content": story_prompt}
                        ],
                        max_tokens=500
                    )

                    # wyświetlenie wygenerowanego tesktu
                    story = story_response.choices[0].message.content.strip()
                    st.markdown(f"### 🧙‍♂️ Twoje opowiadanie\n\n{story}")

                    # zapis opowiadnaia w stanie sesji
                    st.session_state["generated_stories"][tabs[i]] = story

                    # przysisk do porbania opowiadania
                    st.download_button(
                        label="🧙‍♂️ Pobierz opowiadanie",
                        data=story.encode("utf-8"),
                        file_name=f"opowiadanie_{person.lower()}_{age.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

    # utrzymanie wygenerowanych obrazów i tekstów w stanie sesji po pobraniu danego obrazu / opowiadania
        elif tabs[i] in st.session_state["generated_images"]:
            saved = st.session_state["generated_images"][tabs[i]]
            caption = f"{tabs[i]} – motyw auto"
            if saved.startswith("http"):
                st.image(saved, caption=caption, use_container_width=True)
            else:
                st.image(base64.b64decode(saved), caption=caption, use_container_width=True)

        elif tabs[i] in st.session_state["generated_stories"]:
            st.markdown(f"### 🧙‍♂️ Twoje opowiadanie\n\n{st.session_state['generated_stories'][tabs[i]]}")

