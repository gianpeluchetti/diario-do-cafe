import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Diário do Café", page_icon="☕", layout="centered")

st.title("☕ Diário do Café (Nuvem)")
st.write("Avalie seus cafés salvando direto no Google Sheets!")

# Conexão com o Google Sheets
# Nota: O Streamlit vai procurar as credenciais no arquivo .streamlit/secrets.toml
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lemos a aba 'Respostas' (ou o nome que você der na sua planilha)
    # ttl=0 garante que ele sempre pegue o dado mais atualizado, sem usar cache antigo
    df = conn.read(worksheet="Página1", ttl=0)
    # Limpa linhas vazias que o Google Sheets pode retornar
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"Erro ao conectar com a planilha. Verifique suas credenciais. Erro: {e}")
    df = pd.DataFrame()

# Se a planilha for nova e não tiver colunas, criamos a estrutura básica na memória
colunas_esperadas = ['ID', 'Data', 'Avaliador', 'Marca', 'Moagem', 'Metodo', 'Po_g', 'Agua_ml', 'Proporcao', 'Tempo', 'Observacoes', 'ID_Ultimo_Cafe', 'Cafe_Anterior', 'Veredito']
if df.empty or len(df.columns) < len(colunas_esperadas):
    df = pd.DataFrame(columns=colunas_esperadas)

# Abas para separar o formulário do histórico
aba_novo, aba_historico = st.tabs(["Nova Avaliação", "Histórico e Ranking"])

with aba_novo:
    st.header("Registrar Novo Café")
    
    avaliador = st.radio("Quem está avaliando?", ["Gian", "Mari"], horizontal=True)
    
    with st.form("form_cafe"):
        marcas_historico = df['Marca'].dropna().unique().tolist() if not df.empty else []
        marcas_padrao = ["Orfeu", "Baggio", "Três Corações"] # Você pode colocar marcas que já usa aqui
        todas_marcas = list(set(marcas_padrao + marcas_historico))
        todas_marcas.sort()
        
        marca_selecionada = st.selectbox("Marca do Café", todas_marcas)
        marca_nova = st.text_input("Ou adicione uma nova marca:")
        
        col1, col2 = st.columns(2)
        with col1:
            moagem = st.number_input("Moagem (Número/Cliques)", min_value=0.0, value=15.0, step=0.5)
            po_g = st.number_input("Quantidade de Pó (gramas)", min_value=1.0, value=20.0, step=1.0)
            
        with col2:
            metodos_historico = df['Metodo'].dropna().unique().tolist() if not df.empty else []
            metodos_padrao = ["V60", "Prensa Francesa", "Aeropress", "Moka", "Espresso"]
            todos_metodos = list(set(metodos_padrao + metodos_historico))
            todos_metodos.sort()
            
            metodo_selecionado = st.selectbox("Método", todos_metodos)
            metodo_novo = st.text_input("Ou adicione um novo método:")
            
            agua_ml = st.number_input("Quantidade de Água (ml)", min_value=10.0, value=300.0, step=10.0)
            
        tempo = st.text_input("Tempo de Extração (ex: 02:30)")
        observacoes = st.text_area("Observações (opcional)", placeholder="Ficou mais doce? Amargo? Desceu rápido demais?")
        
        # Filtra o histórico apenas para o avaliador atual
        df_avaliador = df[df['Avaliador'] == avaliador]
        
        id_ultimo = None
        cafe_anterior_str = "Nenhum"
        veredito = "Sem base de comparação"
        
        if not df_avaliador.empty:
            ultimo_cafe = df_avaliador.iloc[-1]
            id_ultimo = ultimo_cafe['ID']
            cafe_anterior_str = f"{ultimo_cafe['Marca']} no(a) {ultimo_cafe['Metodo']}"
            
            st.markdown("---")
            st.subheader("Batalha de Cafés ⚔️")
            st.write(f"O **SEU** último café avaliado foi: **{cafe_anterior_str}**")
            veredito = st.radio(
                "Comparado a esse último, como ficou o atual?",
                ["Melhor 🏆", "Ficou Igual ⚖️", "Pior ❌"],
                index=1
            )
        else:
            st.info(f"Este será o primeiro café avaliado por {avaliador}.")
        
        submit = st.form_submit_button("Salvar Avaliação")
        
        if submit:
            # Define a marca final (usa a nova se foi digitada, senão usa a selecionada)
            marca_final = marca_nova.strip() if marca_nova.strip() else marca_selecionada
            if marca_final:
                ratio = int(agua_ml / po_g) if po_g > 0 else 0
                proporcao_str = f"1:{ratio}"
                metodo_final = metodo_novo.strip() if metodo_novo.strip() else metodo_selecionado
                novo_id = 1 if df.empty else df['ID'].max() + 1
                
                novo_registro = {
                    'ID': novo_id,
                    'Data': datetime.now().strftime("%d/%m/%Y"),
                    'Avaliador': avaliador,
                    'Marca': marca_final,
                    'Moagem': moagem,
                    'Metodo': metodo_final,
                    'Po_g': po_g,
                    'Agua_ml': agua_ml,
                    'Proporcao': proporcao_str,
                    'Tempo': tempo,
                    'Observacoes': observacoes,
                    'ID_Ultimo_Cafe': id_ultimo,
                    'Cafe_Anterior': cafe_anterior_str,
                    'Veredito': veredito
                }
                
                # Atualiza o DataFrame com o novo registro
                df_novo = pd.DataFrame([novo_registro])
                df = pd.concat([df, df_novo], ignore_index=True)
                
                # Salva os dados no Google Sheets
                conn.update(worksheet="Página1", data=df)
                st.cache_data.clear() # Limpa o cache para forçar a leitura nova
                
                st.success(f"Café salvo no Google Sheets! Proporção: {proporcao_str}. Método: {metodo_final}")
            else:
                st.error("Por favor, preencha pelo menos a Marca do café.")

with aba_historico:
    st.header("Seu Histórico")
    if df.empty:
        st.info("Nenhum café registrado ainda. Faça sua primeira avaliação na aba ao lado!")
    else:
        st.dataframe(df, use_container_width=True)
        st.markdown("---")
        st.subheader("Estatísticas Básicas")
        
        aba_geral, aba_gian, aba_mari = st.tabs(["Geral", "Gian", "Mari"])
        
        def mostrar_metricas(df_stats):
            if df_stats.empty:
                st.write("Ainda sem dados para mostrar.")
                return
            col1, col2 = st.columns(2)
            with col1:
                vitorias = df_stats[df_stats['Veredito'] == 'Melhor 🏆'].shape[0]
                st.metric("Cafés que superaram o anterior", vitorias)
            with col2:
                metodo_fav = df_stats['Metodo'].value_counts().index[0]
                st.metric("Método mais usado", metodo_fav)

        with aba_geral:
            mostrar_metricas(df)
        with aba_gian:
            mostrar_metricas(df[df['Avaliador'] == 'Gian'])
        with aba_mari:
            mostrar_metricas(df[df['Avaliador'] == 'Mari'])
