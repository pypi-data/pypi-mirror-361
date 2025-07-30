import streamlit as st
from my_component import my_component

# Título da aplicação
st.title("Teste Local - Seletor de Posições de Gráfico")

# Lista de posições disponíveis
positions = [
    "ROW2, COL1", "ROW2, COL2", "ROW2, COL3",
    "ROW3, COL1", "ROW3, COL2", "ROW3, COL3",
    "ROW4, COL1", "ROW4, COL2", "ROW4, COL3",
    "ROW5, COL1", "ROW5, COL2", "FULL ROW 6",
    "ROW7, COL1", "ROW7, COL2", "ROW7, COL3",
    "ROW1, COL1(Auto Select)", "ROW1, COL2(Auto Select)", "ROW1, COL3(Auto Select)"
]

st.write("### Selecione uma posição para o gráfico:")

# Usar o componente
selected_position = my_component(positions=positions, key="chart_positions")

# Mostrar a posição selecionada
if selected_position:
    st.success(f"✅ Posição selecionada: {selected_position}")
    
    # Exemplo de como usar a posição selecionada
    st.write("### Informações da posição:")
    if "ROW2, COL1" in selected_position:
        st.info("📊 Gráfico será posicionado em ROW2, COL1")
    elif "FULL ROW 6" in selected_position:
        st.info("📊 Gráfico ocupará toda a linha 6")
    elif "Auto Select" in selected_position:
        st.info("🤖 Posição com seleção automática")
    else:
        st.info(f"📊 Gráfico será posicionado em: {selected_position}")
else:
    st.warning("⚠️ Nenhuma posição selecionada ainda")

# Adicionar algumas informações extras para teste
st.write("---")
st.write("### Informações do teste:")
st.write(f"- Total de posições disponíveis: {len(positions)}")
st.write(f"- Componente carregado com sucesso: ✅")
st.write(f"- Versão do Streamlit: {st.__version__}") 