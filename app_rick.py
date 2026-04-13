import streamlit as st
import requests
import random
import pandas as pd

# --- 1. DESIGN: CONFIGURAÇÃO DA PÁGINA (ÍCONE NO NAVEGADOR) ---
st.set_page_config(page_title="Rick & Morty App", page_icon="🥒", layout="wide")

# --- 2. DESIGN: INJETAR ESTILO (CSS) TEMA "PORTAL VERDE" ---
st.markdown("""
<style>
/* Títulos com brilho verde neon (estilo portal) */
h1, h2, h3 {
    color: #97ce4c !important;
    text-shadow: 0px 0px 8px rgba(151, 206, 76, 0.6);
}
/* Estilizar os botões primários */
div.stButton > button:first-child {
    border: 2px solid #97ce4c;
    border-radius: 8px;
    transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background-color: #97ce4c;
    color: black !important;
    border: 2px solid #97ce4c;
    box-shadow: 0px 0px 10px #97ce4c;
}
/* Sublinhado verde subtil nas caixas de texto */
div[data-baseweb="input"] > div {
    border-bottom: 2px solid #97ce4c !important;
}
</style>
""", unsafe_allow_html=True)

# --- MEMÓRIA GLOBAL DOS FAVORITOS ---
if 'favoritos' not in st.session_state: 
    st.session_state.favoritos = []

# --- MENU DE NAVEGAÇÃO PRINCIPAL ---
# --- 3. DESIGN: LOGÓTIPO OFICIAL NA BARRA LATERAL ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b1/Rick_and_Morty.svg", use_container_width=True)
st.sidebar.divider()

st.sidebar.title("Navegação 🗺️")
menu_escolhido = st.sidebar.radio("Ir para:", [
    "Explorador de Personagens", 
    "Explorador de Localizações",
    "Explorador de Episódios",
    "Os Meus Favoritos ⭐"
])
st.sidebar.divider()

# =====================================================================
# PÁGINA 1: EXPLORADOR DE PERSONAGENS 
# =====================================================================
if menu_escolhido == "Explorador de Personagens":
    st.title("Explorador de Personagens 🛸")
    
    if 'pagina_char' not in st.session_state: st.session_state.pagina_char = 1
    if 'pesquisa_char' not in st.session_state: st.session_state.pesquisa_char = ""
    if 'estado_char' not in st.session_state: st.session_state.estado_char = "Todos"
    if 'genero_char' not in st.session_state: st.session_state.genero_char = "Todos"

    st.sidebar.header("Filtros de Personagens 🎛️")
    filtro_estado = st.sidebar.radio("Estado de Vida", ["Todos", "Alive", "Dead", "unknown"])
    st.sidebar.divider()
    filtro_genero = st.sidebar.radio("Género", ["Todos", "Female", "Male", "Genderless", "unknown"])
    st.sidebar.divider() 

    if st.sidebar.button("Surpreende-me! 🎲"):
        resposta_info = requests.get("https://rickandmortyapi.com/api/character")
        if resposta_info.status_code == 200:
            total_personagens = resposta_info.json()["info"]["count"]
            id_aleatorio = random.randint(1, total_personagens)
            url_aleatorio = f"https://rickandmortyapi.com/api/character/{id_aleatorio}"
            resposta_aleatoria = requests.get(url_aleatorio)
            
            if resposta_aleatoria.status_code == 200:
                personagem = resposta_aleatoria.json()
                st.success(f"Foste surpreendido com a personagem #{id_aleatorio}!")
                col1, col2 = st.columns([1, 2])
                with col1: st.image(personagem["image"], width=150)
                with col2:
                    st.subheader(personagem["name"])
                    st.write(f"**Espécie:** {personagem['species']}")
                    st.write(f"**Estado:** {personagem['status']}")
                st.divider()

    pesquisa = st.text_input("Pesquisa por uma personagem (ex: Rick, Morty, Summer):")

    if (pesquisa != st.session_state.pesquisa_char or 
        filtro_estado != st.session_state.estado_char or 
        filtro_genero != st.session_state.genero_char):
        st.session_state.pagina_char = 1
        st.session_state.pesquisa_char = pesquisa
        st.session_state.estado_char = filtro_estado
        st.session_state.genero_char = filtro_genero

    url = f"https://rickandmortyapi.com/api/character/?page={st.session_state.pagina_char}"
    if pesquisa: url += f"&name={pesquisa}"
    if filtro_estado != "Todos": url += f"&status={filtro_estado}"
    if filtro_genero != "Todos": url += f"&gender={filtro_genero}"

    resposta = requests.get(url)

    if resposta.status_code == 200:
        dados = resposta.json()
        personagens = dados["results"]
        total_paginas = dados["info"]["pages"]
        
        st.write("### 📊 Estatísticas desta Página")
        contagem_estados = {"Alive": 0, "Dead": 0, "unknown": 0}
        contagem_especies = {}

        for p in personagens:
            estado = p["status"]
            especie = p["species"]
            if estado in contagem_estados: contagem_estados[estado] += 1
            contagem_especies[especie] = contagem_especies.get(especie, 0) + 1

        col_grafico1, col_grafico2 = st.columns(2)
        with col_grafico1:
            st.bar_chart(pd.DataFrame(list(contagem_estados.items()), columns=["Estado", "Quantidade"]).set_index("Estado"))
        with col_grafico2:
            st.bar_chart(pd.DataFrame(list(contagem_especies.items()), columns=["Espécie", "Quantidade"]).set_index("Espécie"))
        st.divider()
        
        st.info(f"Mostrando {len(personagens)} personagens. (Página {st.session_state.pagina_char} de {total_paginas})")

        for personagem in personagens:
            col1, col2 = st.columns([1, 2])
            with col1: st.image(personagem["image"], width=150)
            with col2:
                st.subheader(personagem["name"])
                st.write(f"**Espécie:** {personagem['species']}")
                st.write(f"**Estado:** {personagem['status']}")
                st.write(f"**Género:** {personagem['gender']}")
            
            with st.expander(f"🎬 Ver episódios com {personagem['name']}"):
                numeros_episodios = [ep.split("/")[-1] for ep in personagem["episode"]]
                st.write(f"**Aparece nos episódios:** {', '.join(numeros_episodios)}")
            
            if personagem['id'] in st.session_state.favoritos:
                if st.button("❌ Remover dos Favoritos", key=f"rem_{personagem['id']}"):
                    st.session_state.favoritos.remove(personagem['id'])
                    st.rerun()
            else:
                if st.button("⭐ Adicionar aos Favoritos", key=f"add_{personagem['id']}"):
                    st.session_state.favoritos.append(personagem['id'])
                    st.rerun()

            st.divider() 
        
        col_esq, col_dir = st.columns(2)
        with col_esq:
            if st.session_state.pagina_char > 1:
                if st.button("⬅️ Página Anterior"):
                    st.session_state.pagina_char -= 1
                    st.rerun()
        with col_dir:
            if st.session_state.pagina_char < total_paginas:
                if st.button("Próxima Página ➡️"):
                    st.session_state.pagina_char += 1
                    st.rerun()

    elif resposta.status_code == 404:
        st.warning("Não encontrámos nenhuma personagem com esses filtros.")

# =====================================================================
# PÁGINA 2: EXPLORADOR DE LOCALIZAÇÕES
# =====================================================================
elif menu_escolhido == "Explorador de Localizações":
    st.title("Explorador de Localizações 🪐")
    
    if 'pagina_loc' not in st.session_state: st.session_state.pagina_loc = 1
    if 'pesquisa_loc' not in st.session_state: st.session_state.pesquisa_loc = ""

    pesquisa_loc = st.text_input("Pesquisa por um planeta ou dimensão:")

    if pesquisa_loc != st.session_state.pesquisa_loc:
        st.session_state.pagina_loc = 1
        st.session_state.pesquisa_loc = pesquisa_loc

    url_loc = f"https://rickandmortyapi.com/api/location/?page={st.session_state.pagina_loc}"
    if pesquisa_loc: url_loc += f"&name={pesquisa_loc}"

    resposta_loc = requests.get(url_loc)

    if resposta_loc.status_code == 200:
        dados_loc = resposta_loc.json()
        localizacoes = dados_loc["results"]
        total_paginas_loc = dados_loc["info"]["pages"]
        
        st.info(f"Encontrámos {dados_loc['info']['count']} locais! (Página {st.session_state.pagina_loc} de {total_paginas_loc})")

        for loc in localizacoes:
            st.subheader(f"📍 {loc['name']}")
            st.write(f"**Tipo:** {loc['type']}")
            st.write(f"**Dimensão:** {loc['dimension']}")
            
            numero_habitantes = len(loc['residents'])
            
            if numero_habitantes == 0:
                st.write("**População:** Local desabitado. 👻")
                st.divider()
            else:
                st.write(f"**População conhecida:** {numero_habitantes} habitantes registados.")
                
                with st.expander(f"👥 Ver os habitantes de {loc['name']}"):
                    ids_habitantes = [res.split("/")[-1] for res in loc['residents']]
                    ids_formatados = ",".join(ids_habitantes)
                    url_habitantes = f"https://rickandmortyapi.com/api/character/{ids_formatados}"
                    resposta_hab = requests.get(url_habitantes)
                    
                    if resposta_hab.status_code == 200:
                        dados_hab = resposta_hab.json()
                        if isinstance(dados_hab, dict): dados_hab = [dados_hab]
                        
                        num_cols = 4 
                        for i in range(0, len(dados_hab), num_cols):
                            cols = st.columns(num_cols)
                            chunk = dados_hab[i : i + num_cols]
                            
                            for col_idx, habitante in enumerate(chunk):
                                with cols[col_idx]:
                                    img_col, text_col = st.columns([1, 2.5])
                                    with img_col: st.image(habitante["image"], width=70)
                                    with text_col:
                                        st.write(f"**{habitante['name']}**")
                                        st.caption(f"{habitante['status']} | {habitante['species']}")
                    else:
                        st.error("Erro ao carregar os dados dos habitantes.")
                st.divider()

        col_esq, col_dir = st.columns(2)
        with col_esq:
            if st.session_state.pagina_loc > 1:
                if st.button("⬅️ Anterior"):
                    st.session_state.pagina_loc -= 1
                    st.rerun()
        with col_dir:
            if st.session_state.pagina_loc < total_paginas_loc:
                if st.button("Próxima ➡️"):
                    st.session_state.pagina_loc += 1
                    st.rerun()

    elif resposta_loc.status_code == 404:
        st.warning("Localização não encontrada.")

# =====================================================================
# PÁGINA 3: EXPLORADOR DE EPISÓDIOS
# =====================================================================
elif menu_escolhido == "Explorador de Episódios":
    st.title("Explorador de Episódios 📺")
    
    if 'pagina_ep' not in st.session_state: st.session_state.pagina_ep = 1
    if 'pesquisa_ep' not in st.session_state: st.session_state.pesquisa_ep = ""

    pesquisa_ep = st.text_input("Pesquisa por Nome ou Código da Temporada:")

    if pesquisa_ep != st.session_state.pesquisa_ep:
        st.session_state.pagina_ep = 1
        st.session_state.pesquisa_ep = pesquisa_ep

    url_ep = f"https://rickandmortyapi.com/api/episode/?page={st.session_state.pagina_ep}"
    
    if pesquisa_ep:
        if pesquisa_ep.upper().startswith("S0") or pesquisa_ep.upper().startswith("S1"):
            url_ep += f"&episode={pesquisa_ep.upper()}"
        else:
            url_ep += f"&name={pesquisa_ep}"

    resposta_ep = requests.get(url_ep)

    if resposta_ep.status_code == 200:
        dados_ep = resposta_ep.json()
        episodios = dados_ep["results"]
        total_paginas_ep = dados_ep["info"]["pages"]
        
        st.info(f"Encontrámos {dados_ep['info']['count']} episódios! (Página {st.session_state.pagina_ep} de {total_paginas_ep})")

        for ep in episodios:
            st.subheader(f"🎬 {ep['episode']} - {ep['name']}")
            st.write(f"**Data de Transmissão:** {ep['air_date']}")
            st.write(f"**Total de Personagens:** {len(ep['characters'])}")
            
            with st.expander(f"🎭 Ver o elenco do episódio"):
                ids_personagens = [c.split("/")[-1] for c in ep['characters']]
                ids_formatados = ",".join(ids_personagens)
                url_elenco = f"https://rickandmortyapi.com/api/character/{ids_formatados}"
                resposta_elenco = requests.get(url_elenco)
                
                if resposta_elenco.status_code == 200:
                    dados_elenco = resposta_elenco.json()
                    if isinstance(dados_elenco, dict): dados_elenco = [dados_elenco]
                    
                    num_cols = 4 
                    for i in range(0, len(dados_elenco), num_cols):
                        cols = st.columns(num_cols)
                        chunk = dados_elenco[i : i + num_cols]
                        
                        for col_idx, personagem in enumerate(chunk):
                            with cols[col_idx]:
                                img_col, text_col = st.columns([1, 2.5])
                                with img_col: st.image(personagem["image"], width=70)
                                with text_col:
                                    st.write(f"**{personagem['name']}**")
                                    st.caption(f"{personagem['status']} | {personagem['species']}")
                else:
                    st.error("Erro ao carregar o elenco.")
            st.divider()

        col_esq, col_dir = st.columns(2)
        with col_esq:
            if st.session_state.pagina_ep > 1:
                if st.button("⬅️ Anterior"):
                    st.session_state.pagina_ep -= 1
                    st.rerun()
        with col_dir:
            if st.session_state.pagina_ep < total_paginas_ep:
                if st.button("Próxima ➡️"):
                    st.session_state.pagina_ep += 1
                    st.rerun()

    elif resposta_ep.status_code == 404:
        st.warning("Episódio não encontrado.")

# =====================================================================
# PÁGINA 4: OS MEUS FAVORITOS ⭐
# =====================================================================
elif menu_escolhido == "Os Meus Favoritos ⭐":
    st.title("A Minha Coleção ⭐")
    
    if len(st.session_state.favoritos) == 0:
        st.info("Ainda não tens nenhuma personagem guardada. Vai ao 'Explorador de Personagens' e clica na ⭐ para começares a tua coleção!")
    else:
        st.success(f"Tens **{len(st.session_state.favoritos)}** personagens nos teus favoritos!")
        
        ids_formatados = ",".join(map(str, st.session_state.favoritos))
        url_favs = f"https://rickandmortyapi.com/api/character/{ids_formatados}"
        
        resposta_favs = requests.get(url_favs)
        
        if resposta_favs.status_code == 200:
            dados_favs = resposta_favs.json()
            
            if isinstance(dados_favs, dict): 
                dados_favs = [dados_favs]
            
            num_cols = 4 
            for i in range(0, len(dados_favs), num_cols):
                cols = st.columns(num_cols)
                chunk = dados_favs[i : i + num_cols]
                
                for col_idx, personagem in enumerate(chunk):
                    with cols[col_idx]:
                        img_col, text_col = st.columns([1, 2.5])
                        with img_col: st.image(personagem["image"], width=70)
                        with text_col:
                            st.write(f"**{personagem['name']}**")
                            st.caption(f"{personagem['status']} | {personagem['species']}")
                            
                            if st.button("❌ Remover", key=f"fav_page_rem_{personagem['id']}"):
                                st.session_state.favoritos.remove(personagem['id'])
                                st.rerun()