import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Diário do Café", page_icon="☕", layout="centered")

ARQUIVO_CSV = 'historico_cafes.csv'

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV)
    else:
        # Cria um DataFrame vazio com as colunas definidas
        colunas = ['ID', 'Data', 'Avaliador', 'Marca', 'Moagem', 'Metodo', 'Po_g', 'Agua_ml', 'Proporcao', 'Tempo', 'Observacoes', 'ID_Ultimo_Cafe', 'Cafe_Anterior', 'Veredito']
        return pd.DataFrame(columns=colunas)

# Função para salvar os dados
def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False)

df = carregar_dados()

st.title("☕ Diário do Café")
st.write("Avalie seus cafés de forma simples e progressiva!")

# Abas para separar o formulário do histórico
aba_novo, aba_historico = st.tabs(["Nova Avaliação", "Histórico e Ranking"])

with aba_novo:
    st.header("Registrar Novo Café")
    
    # IMPORTANTE: Colocar o avaliador FORA do formulário permite que a página 
    # atualize instantaneamente para buscar o "último café" correto da pessoa.
    avaliador = st.radio("Quem está avaliando?", ["Gian", "Mari"], horizontal=True)
    
    with st.form("form_cafe"):
        marca = st.text_input("Marca do Café")
        
        col1, col2 = st.columns(2)
        with col1:
            moagem = st.number_input("Moagem (Número/Cliques)", min_value=0.0, value=15.0, step=0.5)
            po_g = st.number_input("Quantidade de Pó (gramas)", min_value=1.0, value=20.0, step=1.0)
            
        with col2:
            # Lógica para métodos dinâmicos
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
            if marca:
                # Calcula proporção (ratio)
                ratio = int(agua_ml / po_g) if po_g > 0 else 0
                proporcao_str = f"1:{ratio}"
                
                # Define o método final
                metodo_final = metodo_novo.strip() if metodo_novo.strip() else metodo_selecionado
                
                novo_id = 1 if df.empty else df['ID'].max() + 1
                
                novo_registro = {
                    'ID': novo_id,
                    'Data': datetime.now().strftime("%d/%m/%Y"),
                    'Avaliador': avaliador,
                    'Marca': marca,
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
                
                # Adiciona o novo registro ao DataFrame
                df_novo = pd.DataFrame([novo_registro])
                df = pd.concat([df, df_novo], ignore_index=True)
                salvar_dados(df)
                
                st.success(f"Café salvo com sucesso! Proporção calculada: {proporcao_str}. Método usado: {metodo_final}")
            else:
                st.error("Por favor, preencha pelo menos a Marca do café.")

with aba_historico:
    st.header("Seu Histórico")
    if df.empty:
        st.info("Nenhum café registrado ainda. Faça sua primeira avaliação na aba ao lado!")
    else:
        # Mostra a tabela interativa
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Estatísticas Básicas")
        
        # Abas internas para ver estatísticas individuais
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
