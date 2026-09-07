from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Diário do Café", page_icon="☕", layout="centered"
)

# --- NOVO: Função que cria a janela de sucesso ---
@st.dialog("Sucesso! 🎉")
def janela_sucesso():
    st.write("A avaliação do seu café foi salva com sucesso!")
    if st.button("Voltar"):
        st.rerun()  # Recarrega a página inicial
# ------------------------------------------------

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
aba_registro, aba_historico, aba_calibracao = st.tabs(["📝 Nova Avaliação", "📊 Histórico e Rankings", "🎯 Calibrações Definidas"])
with aba_registro:
    # Seleção de Avaliador
    avaliador = st.selectbox("Quem está avaliando?", ["Gian", "Mari"])
    tipo_consumo = st.radio(
        "Como foi o consumo?", ["Sozinho 👤", "Em conjunto 👥"], horizontal=True
    )
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
    
    id_ultimo = ""
    cafe_anterior_str = "Nenhum"
    veredito = "Primeiro café"
    obs_comparacao = ""
    

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
        st.subheader("🥊 A Batalha: Desafiante vs Campeão")
        
        # Filtra o histórico para achar o campeão do avaliador atual
        if not df.empty and "Avaliador" in df.columns:
            # Pega apenas os cafés normais (ignora as calibrações) da pessoa selecionada
            df_avaliador = df[(df["Avaliador"] == avaliador) & (df["Veredito"] != "RECEITA DE OURO 👑")]
            
            # O campeão é o último que recebeu "Melhor 🏆"
            df_vencedores = df_avaliador[df_avaliador["Veredito"].str.contains("Melhor", na=False)]
            
            if not df_vencedores.empty:
                campeao = df_vencedores.iloc[-1] # Pega a última linha dos vencedores
            elif not df_avaliador.empty:
                campeao = df_avaliador.iloc[-1] # Se ninguém ganhou ainda, o último vira o campeão por padrão
            else:
                campeao = None
        else:
            campeao = None

        # Exibe o ringue de batalha
        if campeao is not None:
            st.info(f"👑 **CAMPEÃO ATUAL A BATER:**\n\n**{campeao.get('Marca', '')} {campeao.get('Linha', '')}**\n\nMétodo **{campeao.get('Metodo', '')}** com **{campeao.get('Moagem', '')} cliques** (Proporção {campeao.get('Proporcao', '')}).")
            
            id_enfrentado = campeao.get("ID", "Desconhecido")
            cafe_enfrentado_nome = f"{campeao.get('Marca', '')} {campeao.get('Linha', '')}"
            
            veredito = st.radio(
                "Comparado a esse Campeão, o café que você está bebendo AGORA ficou:", 
                ["Melhor 🏆", "Pior 👎", "Igual ⚖️"],
                horizontal=True
            )
        else:
            st.info("Primeiro café registrado! Ele será o primeiro Campeão automaticamente.")
            id_enfrentado = "Nenhum"
            cafe_enfrentado_nome = "Nenhum"
            veredito = "Melhor 🏆" # Força a ser o campeão inicial
        
            
        
        
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
            'Tipo_Consumo': tipo_consumo,
            "Marca": marca_final,
            "Linha": linha_final,
            "Moagem": moagem,
            "Metodo": metodo_final,
            "Po_g": po_g,
            "Agua_ml": agua_ml,
            "Proporcao": proporcao_str,
            "Tempo": tempo,
            "Observacoes": observacoes,
            "ID_Ultimo_Cafe": id_enfrentado,
            "Cafe_Anterior": cafe_enfrentado_nome,
            "Veredito": veredito,
            "Obs_Comparacao": obs_comparacao,
        }
    
        # Adicionar ao DataFrame e atualizar planilha
        df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        try:
          conn.update(data=df_novo)
          janela_sucesso()  # <--- Abre a janela pop-up aqui
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
            # --- O GRANDE CAMPEÃO (REI DA COLINA) ---
            st.markdown("---")
            st.subheader("👑 O Grande Campeão Atual")
    
            if "Veredito" in df_stats.columns and not df_stats.empty:
                # Tira as calibrações da jogada para olhar só as batalhas diárias
                df_batalhas = df_stats[df_stats["Veredito"] != "RECEITA DE OURO 👑"]
                
                # Filtra apenas os que ganharam a coroa
                df_campeoes = df_batalhas[df_batalhas["Veredito"].str.contains("Melhor", na=False)]
                
                if not df_campeoes.empty:
                    campeao_atual = df_campeoes.iloc[-1] # O último a desbancar o rei assume o trono
                    
                    # Conta quantas vezes o campeão precisou defender o trono (quantos cafés vieram depois dele)
                    idx_campeao = df_batalhas.index.get_loc(campeao_atual.name)
                    defesas_de_trono = len(df_batalhas) - 1 - idx_campeao
                    
                    st.success(f"### 🏆 {campeao_atual.get('Marca', '')} - {campeao_atual.get('Linha', '')}\n\n"
                               f"**Método {campeao_atual.get('Metodo', '')}**\n\n"
                               f"⚙️ **Moagem:** {campeao_atual.get('Moagem', '')} cliques | 💧 **Proporção:** {campeao_atual.get('Proporcao', '')}\n\n"
                               f"🛡️ **Defesas de Trono:** Sobreviveu a {defesas_de_trono} desafiantes desde que ganhou!\n\n"
                               f"📅 **Data da Coroação:** {campeao_atual.get('Data', '')}")
                else:
                    st.info("Nenhum campeão coroado ainda para este filtro.")
            else:
                 st.info("Ainda não há dados suficientes para exibir um campeão.")


            st.subheader("🏆 Destaques")
            
            
            
            # Marca mais consumida para o filtro selecionado
            if "Marca" in df_stats.columns:
                marca_favorita = df_stats["Marca"].mode()[0] if not df_stats["Marca"].dropna().empty else "N/A"
            
            if "Proporcao" in df_stats.columns:
                proporcao_favorita = df_stats["Proporcao"].mode()[0] if not df_stats["Proporcao"].dropna().empty else "N/A"

                
            
            if "Po_g" in df_stats.columns and "Agua_ml" in df_stats.columns and not df_stats.empty:
                df_calc = df_stats.copy()
                df_calc["Po_g_num"] = pd.to_numeric(df_calc["Po_g"], errors="coerce").fillna(0)
                df_calc["Agua_ml_num"] = pd.to_numeric(df_calc["Agua_ml"], errors="coerce").fillna(0)
    
                # Se foi em conjunto, divide por 2 para o somatório total
                if "Tipo_Consumo" in df_calc.columns:
                    condicao_conjunto = df_calc["Tipo_Consumo"].str.contains("conjunto", case=False, na=False)
                    df_calc.loc[condicao_conjunto, "Po_g_num"] = df_calc.loc[condicao_conjunto, "Po_g_num"] / 2
                    df_calc.loc[condicao_conjunto, "Agua_ml_num"] = df_calc.loc[condicao_conjunto, "Agua_ml_num"] / 2
    
                total_gramas = df_calc["Po_g_num"].sum()
                total_ml = df_calc["Agua_ml_num"].sum()
    
                # Conversão inteligente para Café (Gramas ou Quilogramas)
                if total_gramas >= 1000:
                    cafe_formatado = f"{total_gramas / 1000:.2f} kg"
                else:
                    cafe_formatado = f"{total_gramas:.1f} g"
    
                # Conversão para Água (Litros)
                total_litros = total_ml / 1000
                agua_formatada = f"{total_litros:.2f} L"
    
                # Exibe em duas métricas lado a lado
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Total de Café Utilizado", cafe_formatado)
                with col_m2:
                    st.metric("Total de Café Tomado (l)", agua_formatada)
                with col_m3:
                    st.metric("Marca mais utilizada", marca_favorita)
            else:
                st.info("Colunas de peso de café ou água não encontradas para o cálculo.")
            
            
            
            
            # Rankings mais utilizados baseados na visão escolhida
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.markdown("**Top Marcas**")
                if "Marca" in df_stats.columns:
                    st.write(df_stats["Marca"].value_counts().reset_index(name="Total"))
                    
            with col_r2:
                st.markdown("**Top Linhas**")
                if "Marca" in df_stats.columns and "Linha" in df_stats.columns:
                    # Junta a Marca e a Linha (ex: Kroma - Premium) e faz a contagem
                    marca_linha = df_stats["Marca"].astype(str) + " - " + df_stats["Linha"].astype(str)
                    resultado = marca_linha.value_counts().reset_index()
                    resultado.columns = ["Marca - Linha", "Total"]
                    
                    st.write(resultado)
                elif "Linha" in df_stats.columns:
                    # Fallback de segurança caso a coluna Marca dê erro
                    st.write(df_stats["Linha"].value_counts().reset_index(name="Total"))
                    
            with col_r3:
                st.markdown("**Top Moagens**")
                if "Moagem" in df_stats.columns:
                    st.write(df_stats["Moagem"].value_counts().reset_index(name="Total"))
                    
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r2:
                st.markdown("**Top Proporções**")
                if "Proporcao" in df_stats.columns:
                    st.write(df_stats["Proporcao"].value_counts().reset_index(name="Total"))
                    
        # --- CAFÉ CAMPEÃO DAS BATALHAS ---

        st.markdown("---")
        st.subheader("📋 Todos os Registros")
        
        # Mostra a tabela completa (ou você pode filtrar se preferir mostrar tudo)
        st.dataframe(df, use_container_width=True)

with aba_calibracao:
    st.header("🎯 Calibrações Definidas (Receitas de Ouro)")
    st.write("Terminou seus testes? Salve aqui a conclusão para nunca mais esquecer a receita perfeita!")
    
    # Lê a aba secundária
    try:
        df_calib = conn.read(worksheet="Calibracoes", ttl=0)
    except Exception as e:
        st.error("Erro ao ler a aba de calibrações. Verifique se você criou a aba 'Calibracoes' na planilha.")
        df_calib = pd.DataFrame()
    
    avaliador_calib = st.radio(
        "Quem está definindo esta calibração?",
        ["Gian", "Mari"],
        horizontal=True,
        key="radio_calib"
    )
    
    # --- BUSCANDO DADOS DA ABA PRINCIPAL (Marcas e Métodos) ---
    marcas_existentes = sorted(df["Marca"].dropna().unique().tolist()) if not df.empty and "Marca" in df.columns else []
    linhas_existentes = sorted(df["Linha"].dropna().unique().tolist()) if not df.empty and "Linha" in df.columns else []
    metodos_existentes = sorted(df["Metodo"].dropna().unique().tolist()) if not df.empty and "Metodo" in df.columns else ["V60", "Prensa Francesa", "Espresso", "Italiana (Moka)", "Outro"]

    # --- BUSCANDO FOCOS DE CALIBRAÇÃO (A mágica da lista dinâmica) ---
    focos_base = ["Moagem ⚙️", "Proporção 💧", "Tempo ⏳", "Temperatura 🌡️"]
    focos_planilha = df_calib["Parametro_Foco"].dropna().unique().tolist() if not df_calib.empty and "Parametro_Foco" in df_calib.columns else []
    
    # Junta os padrões com os que você já criou no passado, sem duplicar
    lista_focos = []
    for f in focos_base + focos_planilha:
        if f not in lista_focos and "Outro" not in f:
            lista_focos.append(f)
    lista_focos.append("Outro ➕") # Adiciona o botão de Outro sempre no final

    st.markdown("---")
    st.subheader("🎯 Qual parâmetro você calibrou nesta sessão?")
    
    # IMPORTANTE: Isso fica FORA do form para a caixinha aparecer na mesma hora!
    escolha_foco = st.radio("Foco principal do teste:", lista_focos, horizontal=True)
    
    foco_novo = ""
    if escolha_foco == "Outro ➕":
        foco_novo = st.text_input("Qual foi o novo parâmetro? (Ex: Filtro de Papel, Agitação)")

    with st.form("form_calibracao"):
        st.markdown("---")
        st.subheader("📌 Receita Campeã (O que foi testado?)")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            marca_sel = st.selectbox("Marca", ["Selecione..."] + marcas_existentes)
            marca_nova = st.text_input("Ou adicione nova Marca:")
        with col_c2:
            linha_sel = st.selectbox("Linha", ["Selecione..."] + linhas_existentes)
            linha_nova = st.text_input("Ou adicione nova Linha:")
        with col_c3:
            metodo_sel = st.selectbox("Método", ["Selecione..."] + metodos_existentes)
            metodo_novo = st.text_input("Ou adicione novo Método:")
        
        st.markdown("---")
        st.subheader("🏆 Resultados da Calibração")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            moagem_ideal = st.number_input("Moagem Ideal (cliques)", min_value=1.0, step=1.0, value=20.0)
        with col_r2:
            proporcao_ideal = st.text_input("Proporção Ideal (ex: 1:15)")
        with col_r3:
            tempo_temp = st.text_input("Tempo/Temp (ex: 2:30 / 92ºC)")
            
        obs_calib = st.text_area("Descreva a conclusão (ex: 'Testei os cliques 16, 20 e 24. A moagem 20 foi a melhor.')")
        
        submit_calib = st.form_submit_button("Salvar Receita de Ouro")
        
    if submit_calib:
        marca_final_c = marca_nova.strip() if marca_nova.strip() else (marca_sel if marca_sel != "Selecione..." else "")
        linha_final_c = linha_nova.strip() if linha_nova.strip() else (linha_sel if linha_sel != "Selecione..." else "")
        metodo_final_c = metodo_novo.strip() if metodo_novo.strip() else (metodo_sel if metodo_sel != "Selecione..." else "")
        
        # Decide qual foco salvar na planilha
        foco_final = foco_novo.strip() if escolha_foco == "Outro ➕" and foco_novo.strip() else escolha_foco

        if not marca_final_c or not linha_final_c:
            st.warning("Por favor, preencha a Marca e a Linha para salvar a calibração.")
        elif escolha_foco == "Outro ➕" and not foco_novo.strip():
            st.warning("Você selecionou 'Outro', por favor digite qual foi o parâmetro calibrado.")
        else:
            novo_registro_calib = {
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Avaliador": avaliador_calib,
                "Parametro_Foco": foco_final, 
                "Marca": marca_final_c,
                "Linha": linha_final_c,
                "Metodo": metodo_final_c,
                "Moagem_Ideal": moagem_ideal,
                "Proporcao_Ideal": proporcao_ideal,
                "Tempo_Temperatura": tempo_temp,  
                "Observacoes": obs_calib,
            }
            
            df_novo_c = pd.concat([df_calib, pd.DataFrame([novo_registro_calib])], ignore_index=True)
            
            try:
                conn.update(worksheet="Calibracoes", data=df_novo_c)
                janela_sucesso()
            except Exception as e:
                st.error(f"Erro ao salvar na planilha de calibrações: {e}")
                
    st.markdown("---")
    st.subheader(f"📖 Livro de Receitas ({avaliador_calib})")
    
    if not df_calib.empty and "Avaliador" in df_calib.columns:
        df_calibracoes_filtrado = df_calib[df_calib["Avaliador"] == avaliador_calib]
        
        if not df_calibracoes_filtrado.empty:
            # Inverte a ordem para mostrar o mais recente primeiro (opcional, mas fica melhor!)
            for _, row in df_calibracoes_filtrado.iloc[::-1].iterrows():
                foco_atual = row.get('Parametro_Foco', 'Não informado')
                
                st.success(f"### {row.get('Marca', '')} - {row.get('Linha', '')} no {row.get('Metodo', '')}\n"
                           f"**🎯 Foco do Teste:** {foco_atual}\n\n"
                           f"⚙️ **Moagem:** {row.get('Moagem_Ideal', '')} | 💧 **Proporção:** {row.get('Proporcao_Ideal', '')} | ⏳ **Tempo/Temp:** {row.get('Tempo_Temperatura', '-')}\n\n"
                           f"📝 **Conclusão:** {row.get('Observacoes', '')}")
        else:
            st.info(f"Nenhuma receita definitiva salva por {avaliador_calib} ainda.")
    else:
        st.info("O livro de receitas está vazio.")