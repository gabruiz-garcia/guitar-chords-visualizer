import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
import numpy as np

st.set_page_config(page_title="Visualizador de Acordes de Guitarra", 
                   page_icon="🎸", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a2e;
    }
    .stSelectbox label, .stSelectbox div {
        color: white !important;
    }
    h1, h2, h3 {
        color: #E94560 !important;
    }
    .stMarkdown {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador de Acordes - Guitarra Eléctrica (22 Trastes)")
st.markdown("---")

# Configuración
tuning = ['E', 'B', 'G', 'D', 'A', 'E']  # De aguda a grave
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_to_num = {note: i for i, note in enumerate(notes)}

chord_types = {
    'Triada Mayor': [0, 4, 7],
    'Triada Menor': [0, 3, 7],
    'Triada Disminuida': [0, 3, 6],
    'Triada Aumentada': [0, 4, 8],
    'Mayor 7 (Maj7)': [0, 4, 7, 11],
    'Dominante 7 (7)': [0, 4, 7, 10],
    'Menor 7 (m7)': [0, 3, 7, 10],
    'Semi-disminuido (m7b5)': [0, 3, 6, 10],
    'Disminuido 7 (dim7)': [0, 3, 6, 9],
    'Sus4': [0, 5, 7],
    'Sus2': [0, 2, 7]
}

colors = {
    0: '#FF4757', 3: '#3742FA', 4: '#2ED573', 5: '#FFA502',
    2: '#FF6348', 6: '#747D8C', 7: '#1E90FF', 8: '#A55EEA',
    9: '#26C6DA', 10: '#FFD93D', 11: '#6BCB77'
}

interval_names = {
    0: 'Raíz (1)', 2: '2ª Mayor', 3: '3ª Menor', 4: '3ª Mayor',
    5: '4ª Justa', 6: '5ª Disminuida', 7: '5ª Justa', 
    8: '5ª Aumentada', 9: '6ª Mayor', 10: '7ª Menor', 11: '7ª Mayor'
}

# Layout de columnas
col1, col2 = st.columns([1, 4])

with col1:
    st.subheader("Configuración")
    root_note = st.selectbox("Nota Raíz:", notes, index=0)
    chord_type = st.selectbox("Tipo de Acorde:", list(chord_types.keys()), index=0)
    
    intervals = chord_types[chord_type]
    root_num = note_to_num[root_note]
    
    # Calcular notas del acorde
    chord_notes = []
    for interval in intervals:
        note_num = (root_num + interval) % 12
        chord_notes.append((notes[note_num], interval))
    
    st.markdown("---")
    st.subheader("Composición del Acorde")
    for note, interval in chord_notes:
        color = colors[interval]
        st.markdown(f"<span style='color:{color}; font-size:20px; font-weight:bold;'>●</span> "
                   f"<b>{note}</b> - {interval_names[interval]}", 
                   unsafe_allow_html=True)
    
    # Mostrar fórmula
    formula = " - ".join([interval_names[i] for _, i in chord_notes])
    st.markdown(f"<br><b>Fórmula:</b><br>{formula}", unsafe_allow_html=True)

with col2:
    # Crear figura de matplotlib
    fig, ax = plt.subplots(figsize=(16, 6))
    fig.patch.set_facecolor('#263238')
    ax.set_facecolor('#263238')
    
    num_frets = 22
    num_strings = 6
    
    # Dibujar mástil
    ax.add_patch(patches.Rectangle((-0.5, -0.5), num_frets + 1.5, num_strings, 
                                  linewidth=0, facecolor='#3E2723', alpha=0.8))
    
    # Trastes
    for fret in range(num_frets + 2):
        x = fret
        color = '#FFD700' if fret in [3, 5, 7, 9, 12, 15, 17, 19, 21] else '#B0BEC5'
        width = 3 if fret in [3, 5, 7, 9, 12, 15, 17, 19, 21] else 1.5
        ax.axvline(x=x, color=color, linewidth=width, alpha=0.8)
    
    # Cuerdas
    for string in range(num_strings):
        y = string
        width = 4 - (string * 0.5)
        ax.axhline(y=y, color='#ECEFF1', linewidth=width, alpha=0.9)
    
    # Marcadores de traste 12
    ax.plot([12], [2.5], "wo", markersize=10, markerfacecolor='white')
    ax.plot([12], [3.5], "wo", markersize=10, markerfacecolor='white')
    
    # Dibujar notas del acorde
    for string in range(num_strings):
        for fret in range(num_frets + 1):
            open_note = tuning[string]
            open_num = note_to_num[open_note]
            current_num = (open_num + fret) % 12
            current_note = notes[current_num]
            
            # Verificar si es parte del acorde
            for chord_note, interval in chord_notes:
                if current_note == chord_note:
                    color = colors[interval]
                    size = 400 if interval == 0 else 300
                    
                    # Dibujar círculo
                    circle = Circle((fret, string), 0.3, facecolor=color, 
                                  edgecolor='white', linewidth=2, zorder=5, alpha=0.9)
                    ax.add_patch(circle)
                    
                    # Texto de la nota
                    ax.text(fret, string, chord_note, ha='center', va='center', 
                           fontsize=9, fontweight='bold', color='white', zorder=6)
                    
                    # Número de intervalo pequeño
                    if interval != 0:
                        ax.text(fret, string - 0.35, str(interval), ha='center', va='center',
                               fontsize=7, color=color, fontweight='bold', zorder=6)
                    break
    
    # Configuración del gráfico
    ax.set_xlim(-0.5, num_frets + 0.5)
    ax.set_ylim(-0.5, num_strings - 0.5)
    ax.set_yticks(range(num_strings))
    ax.set_yticklabels(tuning[::-1], fontsize=12, fontweight='bold', color='white')
    ax.set_xticks(range(num_frets + 1))
    ax.set_xticklabels(range(num_frets + 1), fontsize=9, color='white')
    ax.set_xlabel('Número de Traste', fontsize=12, fontweight='bold', color='white')
    ax.invert_yaxis()
    
    # Afinación en el lateral izquierdo
    for i, note in enumerate(tuning[::-1]):
        ax.text(-0.8, i, note, fontsize=11, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))
    
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")
st.markdown("<center><h4>Desarrollado con ❤️ para guitarristas</h4></center>", 
            unsafe_allow_html=True)