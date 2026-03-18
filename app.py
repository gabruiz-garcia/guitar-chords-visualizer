import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, FancyBboxPatch
import numpy as np

st.set_page_config(page_title="Visualizador de Acordes + Círculo de Quintas", 
                   page_icon="🎸", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a2e;
    }
    h1, h2, h3 {
        color: #E94560 !important;
    }
    .stSelectbox label {
        color: white !important;
    }
    .grade-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador de Acordes + Círculo de Quintas")
st.markdown("---")

# Configuración musical
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_to_num = {note: i for i, note in enumerate(notes)}
num_to_note = {i: note for i, note in enumerate(notes)}

# Círculo de quintas ordenado
circle_of_fifths_major = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
circle_of_fifths_minor = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

# Colores para el círculo
colors_circle = ['#FF6B6B', '#FFA07A', '#FFD93D', '#6BCB77', '#4D96FF', '#9B59B6', 
                 '#E74C3C', '#F39C12', '#2ECC71', '#3498DB', '#9B59B6', '#1ABC9C']

tuning = ['E', 'B', 'G', 'D', 'A', 'E']
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

colors_intervals = {
    0: '#FF4757', 3: '#3742FA', 4: '#2ED573', 5: '#FFA502',
    2: '#FF6348', 6: '#747D8C', 7: '#1E90FF', 8: '#A55EEA',
    9: '#26C6DA', 10: '#FFD93D', 11: '#6BCB77'
}

interval_names = {
    0: 'Raíz (1)', 2: '2ª Mayor', 3: '3ª Menor', 4: '3ª Mayor',
    5: '4ª Justa', 6: '5ª Disminuida', 7: '5ª Justa', 
    8: '5ª Aumentada', 9: '6ª Mayor', 10: '7ª Menor', 11: '7ª Mayor'
}

def get_scale_degrees(root):
    """Obtiene los 7 grados de la escala mayor con sus acordes"""
    root_idx = note_to_num[root]
    scale = []
    
    # Intervalos de la escala mayor: 0, 2, 4, 5, 7, 9, 11
    intervals = [0, 2, 4, 5, 7, 9, 11]
    chord_types_scale = ['Mayor', 'Menor', 'Menor', 'Mayor', 'Mayor', 'Menor', 'Disminuido']
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    
    for i, (interval, chord_type, numeral) in enumerate(zip(intervals, chord_types_scale, roman_numerals)):
        note_idx = (root_idx + interval) % 12
        note = notes[note_idx]
        scale.append({
            'grado': numeral,
            'nota': note,
            'tipo': chord_type,
            'intervalo': interval
        })
    
    return scale

def draw_circle_of_fifths(ax, selected_root):
    """Dibuja el círculo de quintas resaltando la nota seleccionada"""
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    
    # Encontrar índice de la nota seleccionada en el círculo
    selected_idx = circle_of_fifths_major.index(selected_root) if selected_root in circle_of_fifths_major else 0
    
    # Dibujar círculo exterior (notas mayores)
    for i, (note, color) in enumerate(zip(circle_of_fifths_major, colors_circle)):
        angle = np.pi/2 - i * (2*np.pi/12)  # Empezar desde arriba (12 en punto)
        
        # Si es la nota seleccionada, resaltar; si no, atenuar
        is_selected = (i == selected_idx)
        alpha = 1.0 if is_selected else 0.2
        linewidth = 3 if is_selected else 1
        radius = 1.0 if is_selected else 0.9
        
        # Dibujar sector
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=linewidth)
        ax.add_patch(wedge)
        
        # Posición del texto
        text_radius = 0.75
        x = text_radius * np.cos(angle)
        y = text_radius * np.sin(angle)
        
        # Nota mayor (exterior)
        ax.text(x, y, note, ha='center', va='center', 
               fontsize=14 if is_selected else 10, 
               fontweight='bold' if is_selected else 'normal',
               color='white', 
               bbox=dict(boxstyle='circle,pad=0.3', 
                        facecolor=color if is_selected else 'gray',
                        alpha=0.9 if is_selected else 0.3))
        
        # Nota menor (interior)
        minor_note = circle_of_fifths_minor[i]
        x_inner = 0.45 * np.cos(angle)
        y_inner = 0.45 * np.sin(angle)
        ax.text(x_inner, y_inner, minor_note, ha='center', va='center',
               fontsize=11 if is_selected else 8,
               color='white' if is_selected else 'gray',
               fontweight='bold' if is_selected else 'normal')
    
    # Círculo central
    center_circle = Circle((0, 0), 0.25, facecolor='#E94560', edgecolor='white', linewidth=3)
    ax.add_patch(center_circle)
    ax.text(0, 0, selected_root, ha='center', va='center', 
           fontsize=16, fontweight='bold', color='white')
    
    # Título
    ax.set_title(f'Círculo de Quintas - Tonalidad: {selected_root} Mayor', 
                color='white', fontsize=14, fontweight='bold', pad=20)

# Layout
col1, col2, col3 = st.columns([1.2, 2, 2])

with col1:
    st.subheader("🎵 Configuración")
    root_note = st.selectbox("Nota Raíz:", notes, index=0)
    chord_type = st.selectbox("Tipo de Acorde:", list(chord_types.keys()), index=0)
    
    intervals = chord_types[chord_type]
    root_num = note_to_num[root_note]
    
    # Calcular notas del acorde seleccionado
    chord_notes = []
    for interval in intervals:
        note_num = (root_num + interval) % 12
        chord_notes.append((notes[note_num], interval))
    
    st.markdown("---")
    st.subheader("🎹 Campo Armónico")
    
    # Mostrar grados de la escala
    scale_degrees = get_scale_degrees(root_note)
    
    for degree in scale_degrees:
        color = '#E94560' if degree['grado'] in ['I', 'IV', 'V'] else '#3742FA' if degree['grado'] in ['II', 'III', 'VI'] else '#747D8C'
        st.markdown(f"""
        <div style="background-color: {color}33; padding: 8px; border-radius: 5px; 
                    margin: 3px 0; border-left: 4px solid {color};">
            <b style="color: {color}; font-size: 18px;">{degree['grado']}</b> 
            <span style="color: white;">{degree['nota']} {degree['tipo']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎸 Notas del Acorde")
    for note, interval in chord_notes:
        color = colors_intervals[interval]
        st.markdown(f"<span style='color:{color}; font-size:20px;'>●</span> "
                   f"<b style='color: white;'>{note}</b> - <span style='color: #aaa;'>{interval_names[interval]}</span>", 
                   unsafe_allow_html=True)

with col2:
    st.subheader("🔄 Círculo de Quintas")
    
    # Dibujar círculo de quintas
    fig_circle, ax_circle = plt.subplots(figsize=(6, 6))
    fig_circle.patch.set_facecolor('#1a1a2e')
    draw_circle_of_fifths(ax_circle, root_note)
    st.pyplot(fig_circle)
    
    # Leyenda
    st.markdown("""
    <div style="background-color: #263238; padding: 15px; border-radius: 10px; margin-top: 10px;">
        <b style="color: #E94560;">Campo Armónico en {0} Mayor:</b><br>
        <span style="color: #FFD93D;">● Tónica (I)</span> | 
        <span style="color: #4ECDC4;">● Subdominante (IV)</span> | 
        <span style="color: #FF6B6B;">● Dominante (V)</span>
    </div>
    """.format(root_note), unsafe_allow_html=True)

with col3:
    st.subheader("🎸 Diapasón (22 Trastes)")
    
    # Crear figura del diapasón
    fig, ax = plt.subplots(figsize=(14, 5))
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
    ax.plot([12], [2.5], "wo", markersize=8)
    ax.plot([12], [3.5], "wo", markersize=8)
    
    # Dibujar notas del acorde en el diapasón
    for string in range(num_strings):
        for fret in range(num_frets + 1):
            open_note = tuning[string]
            open_num = note_to_num[open_note]
            current_num = (open_num + fret) % 12
            current_note = notes[current_num]
            
            for chord_note, interval in chord_notes:
                if current_note == chord_note:
                    color = colors_intervals[interval]
                    circle = Circle((fret, string), 0.3, facecolor=color, 
                                  edgecolor='white', linewidth=2, zorder=5, alpha=0.9)
                    ax.add_patch(circle)
                    ax.text(fret, string, chord_note, ha='center', va='center', 
                           fontsize=8, fontweight='bold', color='white', zorder=6)
                    if interval != 0:
                        ax.text(fret, string - 0.35, str(interval), ha='center', va='center',
                               fontsize=6, color=color, fontweight='bold', zorder=6)
                    break
    
    ax.set_xlim(-0.5, num_frets + 0.5)
    ax.set_ylim(-0.5, num_strings - 0.5)
    ax.set_yticks(range(num_strings))
    ax.set_yticklabels(tuning[::-1], fontsize=10, fontweight='bold', color='white')
    ax.set_xticks(range(num_frets + 1))
    ax.set_xticklabels(range(num_frets + 1), fontsize=8, color='white')
    ax.set_xlabel('Traste', fontsize=11, fontweight='bold', color='white')
    ax.invert_yaxis()
    
    # Afinación lateral
    for i, note in enumerate(tuning[::-1]):
        ax.text(-0.8, i, note, fontsize=10, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))
    
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")
st.markdown(f"""
<center>
    <h4>Desarrollado para guitarristas | Tonalidad seleccionada: <span style="color: #E94560;">{root_note} Mayor</span></h4>
    <p style="color: #666;">Campo Armónico: {' - '.join([d['nota'] + d['tipo'][0] for d in scale_degrees])}</p>
</center>
""", unsafe_allow_html=True)
