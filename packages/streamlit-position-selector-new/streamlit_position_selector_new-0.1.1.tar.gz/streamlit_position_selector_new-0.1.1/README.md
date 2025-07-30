# Streamlit Chart Positions

Um componente Streamlit para seleção e gerenciamento de posições de gráficos em layouts responsivos.

## Instalação

```sh
pip install streamlit-chart-positions
```

## Como usar

```python
import streamlit as st
from my_component import my_component

# Lista de posições disponíveis para o gráfico
positions = [
    "ROW2, COL1", "ROW2, COL2", "ROW2, COL3",
    "ROW3, COL1", "ROW3, COL2", "ROW3, COL3",
    "ROW4, COL1", "ROW4, COL2", "ROW4, COL3",
    "ROW5, COL1", "ROW5, COL2", "FULL ROW 6",
    "ROW7, COL1", "ROW7, COL2", "ROW7, COL3",
    "ROW1, COL1(Auto Select)", "ROW1, COL2(Auto Select)", "ROW1, COL3(Auto Select)"
]

# Usar o componente
selected_position = my_component(positions=positions, key="chart_positions")
st.write(f"Posição selecionada: {selected_position}")
```

## Funcionalidades

- Seleção visual de posições de gráficos
- Layout responsivo com grid system
- Suporte a seleção automática
- Integração perfeita com Streamlit

## Desenvolvimento

Para executar em modo de desenvolvimento:

```sh
cd template/my_component/frontend
npm install
npm run start
```

Em outro terminal:
```sh
streamlit run template/example.py
```

---

### Passos para corrigir e publicar:

1. **Limpe os arquivos antigos:**
   ```sh
   rmdir /s /q dist
   rmdir /s /q streamlit_chart_positions.egg-info
   ```

2. **Reconstrua o pacote:**
   ```sh
   python -m build
   ```

3. **Tente publicar novamente:**
   ```sh
   twine upload dist/*
   ```

---

Se quiser, posso executar esses comandos para você.  
Deseja que eu faça isso automaticamente?