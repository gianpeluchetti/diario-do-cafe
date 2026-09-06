from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Diário do Café", page_icon="☕", layout="centered"
)

st.title("☕ Diário do Café")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lê os dados existentes na planilha
try:
    df = conn.read(ttl=0)
except Exception as e:
    st.error(f"Erro ao conectar com a planilha. Verifique suas credenciais. {e}")
    df = pd.DataFrame()

# Criando as Abas na tela principal
aba_registro, aba_historico = st.tabs(["📝 Nova Avaliação", "📊 Histórico e Rankings"])
with aba_registro:
    # Seleção de Avaliador
    avaliador = st.selectbox("Quem está avaliando?", ["Gian", "Mari"])
    
    st.markdown("---")
    st.subheader("Nova Avaliação")
    
    # 1. SELEÇÃO DA MARCA (FORA DO FORMULÁRIO para atualizar a tela na mesma hora)
    marcas_historico = (
        df["Marca"].dropna().unique().tolist()
        if not df.empty and "Marca" in df.columns
        else []
    )
    marcas_padrao = ["Kroma", "Minelis"]
    todas_marcas = list(set(marcas_padrao + marcas_historico))
    todas_marcas.sort()
    
    
    col1, col2 = st.columns(2)
    with col1:
        marca_selecionada = st.selectbox("Marca do Café", todas_marcas)  
    with col2:
        marca_nova = st.text_input("Ou adicione uma nova marca:")
    marca_final = marca_nova.strip() if marca_nova.strip() else marca_selecionada
    
    
    
    # ABRINDO O FORMULÁRIO PRINCIPAL (Apenas um único st.form)
    # --- BATALHA DE CAFÉS (FORA DO FORMULÁRIO para aparecer a lista suspensa) ---
    st.markdown("---")
    st.subheader("Batalha de Cafés ⚔️")
    
    id_ultimo = ""
    cafe_anterior_str = "Nenhum"
    veredito = "Primeiro café"
    obs_comparacao = ""
    
    if df.empty:
        st.info("Este será o primeiro café avaliado.")
    else:
        tipo_comparacao = st.radio(
            "Modo de Comparação:",
            ["Comparar com o meu último café", "Comparar com um ID específico (qualquer um)"],
            horizontal=True
        )
    
        cafe_referencia = None
    
        if tipo_comparacao == "Comparar com o meu último café":
            df_avaliador = df[df["Avaliador"] == avaliador] if "Avaliador" in df.columns else pd.DataFrame()
            if not df_avaliador.empty:
                cafe_referencia = df_avaliador.iloc[-1]
            elif not df.empty:
                cafe_referencia = df.iloc[-1]
        else:
            if "ID" in df.columns and not df.empty:
                opcoes_ids = {}
                for idx, row in df.iterrows():
                    raw_id = row.get('ID', idx + 1)
                    try:
                        cafe_id = int(float(raw_id))
                    except:
                        cafe_id = raw_id
                        
                    marca = row.get('Marca', 'Desconhecida')
                    linha = row.get('Linha', '')
                    data = row.get('Data')
                    avaliador_reg = row.get('Avaliador', 'N/A')
                    
                    label = f"ID {cafe_id} - {data} {marca} {linha} ({avaliador_reg})"
                    opcoes_ids[label] = row
                
                if opcoes_ids:
                    label_escolhido = st.selectbox("Selecione o café de referência:", list(opcoes_ids.keys()))
                    cafe_referencia = opcoes_ids[label_escolhido]
    
        if cafe_referencia is not None:
            raw_id_ref = cafe_referencia.get("ID", "")
            try:
                id_ultimo = int(float(raw_id_ref))
            except:
                id_ultimo = raw_id_ref
                
            cafe_anterior_str = (
                f"{cafe_referencia.get('Marca', '')} {cafe_referencia.get('Linha', '')} no"
                f"(a) {cafe_referencia.get('Metodo', '')} (ID: {id_ultimo})"
            )
            st.write(f"Comparando com: **{cafe_anterior_str}**")
    with st.form("form_cafe"):
        col1, col2 = st.columns(2)
        with col1:
            # 2. LINHA DO CAFÉ (Dinâmica baseada na marca escolhida acima)
            if not df.empty and "Marca" in df.columns and "Linha" in df.columns:
                linhas_historico = (
                    df[df["Marca"] == marca_final]["Linha"].dropna().unique().tolist()
                )
            else:
                linhas_historico = []
            
            linhas_padrao_por_marca = {
                "Kroma": ["Premium"],
                "Minelis": ["Naturals", "Dark Chocolate", "Brew Lush"],
            }
            
            linhas_padrao = linhas_padrao_por_marca.get(
                marca_final, ["Tradicional"]
            )
            todas_linhas = list(set(linhas_padrao + linhas_historico))
            todas_linhas.sort()
            
            linha_selecionada = st.selectbox(
                f"Linha do Café ({marca_final})", todas_linhas
            )
        with col2:
            linha_nova_linha = st.text_input("Ou adicione uma nova linha:")
        
        linha_final = (
            linha_nova_linha.strip()
            if linha_nova_linha.strip()
            else linha_selecionada
        )
    
        # Demais campos do café
        moagem = st.number_input("Moagem (cliques)", min_value=1.0, step=1.0, value=15.0)
        
        # Métodos dinâmicos
        metodos_historico = (
            df["Metodo"].dropna().unique().tolist()
            if not df.empty and "Metodo" in df.columns
            else []
        )
        metodos_padrao = ["V60", "Prensa Francesa", "Espresso", "Italiana (Moka)"]
        todas_metodos = list(set(metodos_padrao + metodos_historico))
        todas_metodos.sort()
        
        
        
        
        
        col1, col2 = st.columns(2)
        with col1:
            metodo_selecionado = st.selectbox("Método de Extração", todas_metodos)
            po_g = st.number_input("Café (g)", min_value=0.0, step=0.5, value=15.0)
        with col2:
            metodo_novo = st.text_input("Ou adicione um novo método:")
            agua_ml = st.number_input("Água (ml)", min_value=0.0, step=10.0, value=250.0)
        metodo_final = metodo_novo.strip() if metodo_novo.strip() else metodo_selecionado   
        
        
        tempo = st.text_input("Tempo de Extração (ex: 2:30)")
        observacoes = st.text_area("Observações Gerais sobre o Café")
        
        # Batalha de Cafés / Comparação
        if not df.empty and "Avaliador" in df.columns:
            df_avaliador = df[df["Avaliador"] == avaliador]
        else:
            df_avaliador = pd.DataFrame()
        
        if not df_avaliador.empty:
            ultimo_cafe = df_avaliador.iloc[-1]
            id_ultimo = ultimo_cafe.get("ID", "")
            cafe_anterior_str = (
                f"{ultimo_cafe.get('Marca', '')} {ultimo_cafe.get('Linha', '')} no"
                f"(a) {ultimo_cafe.get('Metodo', '')}"
            )
        
# Batalha de Cafés / Comparação com suporte a ID específico
# Batalha de Cafés / Comparação com suporte a ID específico
        st.markdown("---")
        st.subheader("Batalha de Cafés ⚔️")
        if not df.empty:
                veredito = st.radio(
                    "Comparado a esse café, como ficou o atual?",
                    ["Melhor 🏆", "Ficou Igual ⚖️", "Pior ❌"],
                    index=1,
                )
                obs_comparacao = st.text_input(
                    "Por que ficou melhor/pior? (Ex: mais doce, menos amargo)"
                )
        else:
                veredito = "Primeiro café"
                obs_comparacao = ""
        
        submit = st.form_submit_button("Salvar Avaliação")
    
    # Processo ao clicar em salvar
    if submit:
      if not marca_final or not linha_final:
        st.warning("Por favor, preencha a Marca e a Linha do café.")
      else:
        # Gerar novo ID sequencial
        if not df.empty and "ID" in df.columns:
          try:
            max_id = pd.to_numeric(df["ID"], errors="coerce").max()
            novo_id = int(max_id) + 1 if pd.notna(max_id) else 1
          except:
            novo_id = len(df) + 1
        else:
          novo_id = 1
        proporcao = agua_ml / po_g
        proporcao_str = f"1:{proporcao:.1f}"
        novo_registro = {
            "ID": novo_id,
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Avaliador": avaliador,
            "Marca": marca_final,
            "Linha": linha_final,
            "Moagem": moagem,
            "Metodo": metodo_final,
            "Po_g": po_g,
            "Agua_ml": agua_ml,
            "Proporcao": proporcao_str,
            "Tempo": tempo,
            "Observacoes": observacoes,
            "ID_Ultimo_Cafe": id_ultimo,
            "Cafe_Anterior": cafe_anterior_str,
            "Veredito": veredito,
            "Obs_Comparacao": obs_comparacao,
        }
    
        # Adicionar ao DataFrame e atualizar planilha
        df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        try:
          conn.update(data=df_novo)
          st.success("Avaliação salva com sucesso! 🎉")
          st.rerun()
        except Exception as e:
          st.error(f"Erro ao salvar na planilha: {e}")

with aba_historico:
    
    st.header("📊 Histórico e Estatísticas")

    if df.empty:
        st.info("Ainda não há cafés registrados na planilha.")
    else:
        # Seletor para escolher se quer ver conjunto ou por avaliador
        filtro_visao = st.radio(
            "Visualizar estatísticas:",
            ["Conjuntamente (Gian e Mari)", "Apenas Gian", "Apenas Mari"],
            horizontal=True
        )

        # Filtra o DataFrame de acordo com a escolha
        df_stats = df.copy()
        if filtro_visao == "Apenas Gian" and "Avaliador" in df.columns:
            df_stats = df[df["Avaliador"] == "Gian"]
        elif filtro_visao == "Apenas Mari" and "Avaliador" in df.columns:
            df_stats = df[df["Avaliador"] == "Mari"]

        if df_stats.empty:
            st.warning("Ainda não há registros para este avaliador.")
        else:
            # --- CAFÉ CAMPEÃO DAS BATALHAS (CONFRONTOS DIRETOS) ---
            st.subheader("👑 O Melhor Café (Ranking das Batalhas)")
            
            if "Veredito" in df_stats.columns and "ID" in df_stats.columns and not df_stats.empty:
                # Dicionário para guardar a pontuação de cada ID de café
                pontuacao = {}
                info_cafes = {}

                # Inicializa todos os cafés do dataset filtrado com 0 pontos (USANDO df_stats)
                for _, row in df_stats.iterrows():
                    # Tratamento seguro do ID
                    try:
                        cid = int(float(row["ID"]))
                    except:
                        continue
                    
                    marca = row.get("Marca", "")
                    linha = row.get("Linha", "")
                    proporcao = row.get("Proporcao", "")
                    moagem = int(row.get("Moagem", ""))
                    info_cafes[cid] = f"(ID {cid}) - {marca} - {linha} - Proporção: {proporcao} - Moagem: {moagem} cliques"
                    if cid not in pontuacao:
                        pontuacao[cid] = 0

                # Processa as batalhas
                for _, row in df_stats.iterrows():
                    try:
                        id_atual = int(float(row["ID"]))
                    except:
                        continue
                    
                    raw_ref = row.get("ID_Ultimo_Cafe", "")
                    try:
                        id_ref = int(float(raw_ref)) if pd.notna(raw_ref) and raw_ref != "" else None
                    except:
                        id_ref = None

                    veredito = str(row.get("Veredito", ""))

                    # Se tem referência válida e pontuação inicializada
                    if id_ref in pontuacao and id_atual in pontuacao:
                        if "Melhor" in veredito:
                            # O café atual é melhor que o de referência
                            pontuacao[id_atual] += 1
                        elif "Pior" in veredito:
                            # O de referência é melhor que o café atual (então o ref ganha o ponto)
                            pontuacao[id_ref] += 1
                        elif "Igual" in veredito:
                            # Empate: ambos ganham meio ponto
                            pontuacao[id_atual] += 0.5
                            pontuacao[id_ref] += 0.5

                if pontuacao:
                    # Encontra o ID com maior pontuação
                    melhor_id = max(pontuacao, key=pontuacao.get)
                    maior_pontos = pontuacao[melhor_id]

                    if maior_pontos > 0 and melhor_id in info_cafes:
                        st.success(f"🏆 **{info_cafes[melhor_id]}** é o campeão das batalhas com **{maior_pontos}** pontos em confrontos diretos!")
                        
                        # Opcional: mostrar o placar completo dos cafés
                        with st.expander("Ver placar completo dos cafés"):
                            df_ranking = pd.DataFrame(list(pontuacao.items()), columns=["ID", "Pontos"])
                            df_ranking["Café"] = df_ranking["ID"].map(info_cafes)
                            df_ranking = df_ranking.sort_values(by="Pontos", ascending=False).reset_index(drop=True)
                            st.dataframe(df_ranking[["ID", "Café", "Pontos"]], use_container_width=True)
                    else:
                        st.info("Ainda não há pontuações suficientes nas batalhas para definir um campeão.")
                else:
                    st.info("Nenhum confronto registrado.")
            else:
                st.info("Dados insuficientes para calcular o ranking de batalhas.")


            st.subheader("🏆 Destaques")
            
            # Marca mais consumida para o filtro selecionado
            if "Marca" in df_stats.columns:
                marca_favorita = df_stats["Marca"].mode()[0] if not df_stats["Marca"].dropna().empty else "N/A"
                st.metric("Marca Mais Consumida", marca_favorita)
                
            # Rankings mais utilizados baseados na visão escolhida
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.markdown("**Top Marcas**")
                if "Marca" in df_stats.columns:
                    st.write(df_stats["Marca"].value_counts().reset_index(name="Total"))
                    
            with col_r2:
                st.markdown("**Top Linhas**")
                if "Linha" in df_stats.columns:
                    st.write(df_stats["Linha"].value_counts().reset_index(name="Total"))
                    
            with col_r3:
                st.markdown("**Top Moagens**")
                if "Moagem" in df_stats.columns:
                    st.write(df_stats["Moagem"].value_counts().reset_index(name="Total"))
        # --- CAFÉ CAMPEÃO DAS BATALHAS ---

        st.markdown("---")
        st.subheader("📋 Todos os Registros")
        
        # Mostra a tabela completa (ou você pode filtrar se preferir mostrar tudo)
        st.dataframe(df, use_container_width=True)