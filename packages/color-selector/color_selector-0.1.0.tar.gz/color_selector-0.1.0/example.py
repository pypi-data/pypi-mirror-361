import streamlit as st
from color_selector import color_selector

st.set_page_config(
    page_title="Color Selector Demo",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Color Selector - Demonstração")

st.markdown("""
Este componente permite selecionar cores de uma lista, incluindo cores sólidas e gradientes lineares.
""")

# Exemplos de cores sólidas e gradientes
colors = [
    {"name": "Vermelho", "color": "#FF0000"},
    {"name": "Azul", "color": "#0000FF"},
    {"name": "Verde", "color": "#00FF00"},
    {"name": "Amarelo", "color": "#FFFF00"},
    {"name": "Roxo", "color": "#800080"},
    {"name": "Laranja", "color": "#FFA500"},
    {"name": "Rosa", "color": "#FFC0CB"},
    {"name": "Ciano", "color": "#00FFFF"},
    {"name": "Marrom", "color": "#A52A2A"},
    {"name": "Cinza", "color": "#808080"},
    {"name": "Gradiente Azul-Verde", "color": ["#0000FF", "#00FF00"]},
    {"name": "Gradiente Vermelho-Amarelo", "color": ["#FF0000", "#FFFF00"]},
    {"name": "Gradiente Arco-íris", "color": ["#FF0000", "#00FF00", "#0000FF"]},
    {"name": "Gradiente Rosa-Roxo", "color": ["#FFC0CB", "#800080"]},
    {"name": "Gradiente Dourado", "color": ["#FFD700", "#FFA500"]}
]

# Usar o componente
selected_color = color_selector(colors=colors, key="color_picker")

# Mostrar resultado
if selected_color:
    st.success(f"✅ **Cor selecionada:** {selected_color['name']}")
    
    # Mostrar a cor visualmente
    if isinstance(selected_color['color'], list):
        # É um gradiente
        st.markdown("**Gradiente:**")
        gradient_css = f"background: linear-gradient(90deg, {', '.join(selected_color['color'])});"
        st.markdown(f"""
        <div style="
            {gradient_css}
            height: 50px; 
            border-radius: 10px; 
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        ">
            {selected_color['name']}
        </div>
        """, unsafe_allow_html=True)
        
        st.code(f"Gradiente: {selected_color['color']}")
    else:
        # É uma cor sólida
        st.markdown("**Cor sólida:**")
        st.markdown(f"""
        <div style="
            background-color: {selected_color['color']}; 
            height: 50px; 
            border-radius: 10px; 
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        ">
            {selected_color['name']}
        </div>
        """, unsafe_allow_html=True)
        
        st.code(f"Cor: {selected_color['color']}")
else:
    st.info("ℹ️ Selecione uma cor acima")

# Seção de informações
with st.expander("ℹ️ Sobre o Componente"):
    st.markdown("""
    ### Funcionalidades:
    - ✅ Seleção visual de cores com bolinhas coloridas
    - ✅ Suporte a cores sólidas (hex, rgb, hsl)
    - ✅ Suporte a gradientes lineares
    - ✅ Layout responsivo e minimalista
    - ✅ Interface limpa sem títulos extras
    
    ### Formato das Cores:
    
    **Cores Sólidas:**
    ```python
    {"name": "Vermelho", "color": "#FF0000"}
    ```
    
    **Gradientes Lineares:**
    ```python
    {"name": "Gradiente", "color": ["#FF0000", "#00FF00"]}
    ```
    
    ### Como usar:
    ```python
    import streamlit as st
    from color_selector import color_selector
    
    colors = [
        {"name": "Vermelho", "color": "#FF0000"},
        {"name": "Gradiente", "color": ["#FF0000", "#00FF00"]}
    ]
    
    selected = color_selector(colors=colors, key="picker")
    ```
    """)

# Footer
st.markdown("---")
st.markdown("🎨 **Color Selector** - Um componente Streamlit para seleção de cores")
