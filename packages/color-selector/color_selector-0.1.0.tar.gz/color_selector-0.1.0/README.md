# Color Selector

Um componente Streamlit para seleção de cores com suporte a cores sólidas e gradientes lineares.

## Instalação

```sh
pip install color-selector
```

## Como usar

```python
import streamlit as st
from color_selector import color_selector

# Lista de cores disponíveis (cores sólidas e gradientes)
colors = [
    {"name": "Vermelho", "color": "#FF0000"},
    {"name": "Azul", "color": "#0000FF"},
    {"name": "Verde", "color": "#00FF00"},
    {"name": "Gradiente Azul-Verde", "color": ["#0000FF", "#00FF00"]},
    {"name": "Gradiente Vermelho-Amarelo", "color": ["#FF0000", "#FFFF00"]},
    {"name": "Gradiente Arco-íris", "color": ["#FF0000", "#00FF00", "#0000FF"]}
]

# Usar o componente
selected_color = color_selector(colors=colors, key="color_picker")
st.write(f"Cor selecionada: {selected_color}")
```

## Funcionalidades

- Seleção visual de cores com bolinhas coloridas
- Suporte a cores sólidas (hex, rgb, hsl)
- Suporte a gradientes lineares (lista de cores)
- Layout responsivo e minimalista
- Interface limpa sem títulos ou informações extras
- Integração perfeita com Streamlit

## Formato das Cores

### Cores Sólidas
```python
{"name": "Nome da Cor", "color": "#FF0000"}
```

### Gradientes Lineares
```python
{"name": "Nome do Gradiente", "color": ["#FF0000", "#00FF00"]}
```

## Desenvolvimento

Para executar em modo de desenvolvimento:

```sh
cd template_copy/color_selector/frontend
npm install
npm run start
```

Em outro terminal:
```sh
streamlit run template_copy/example.py
```

## Exemplo Completo

```python
import streamlit as st
from color_selector import color_selector

st.title("Seletor de Cores")

# Exemplos de cores
colors = [
    {"name": "Vermelho", "color": "#FF0000"},
    {"name": "Azul", "color": "#0000FF"},
    {"name": "Verde", "color": "#00FF00"},
    {"name": "Amarelo", "color": "#FFFF00"},
    {"name": "Roxo", "color": "#800080"},
    {"name": "Laranja", "color": "#FFA500"},
    {"name": "Gradiente Azul-Verde", "color": ["#0000FF", "#00FF00"]},
    {"name": "Gradiente Vermelho-Amarelo", "color": ["#FF0000", "#FFFF00"]},
    {"name": "Gradiente Arco-íris", "color": ["#FF0000", "#00FF00", "#0000FF"]}
]

# Usar o componente
selected_color = color_selector(colors=colors, key="color_picker")

if selected_color:
    st.write(f"**Cor selecionada:** {selected_color['name']}")
    st.write(f"**Valor:** {selected_color['color']}")
```