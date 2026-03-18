import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, FancyBboxPatch
import numpy as np

st.set_page_config(page_title="Visualizador de Acordes + Círculo de Quintas", 
                   page_icon="🎸", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #1a1a2e;
    }
    h1, h2, h3 {
        color: #E94560 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador de Acordes + Campo Armónico")
st.markdown("---")

# Configuración musical
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_to_num = {note: i for i, note in enumerate(notes)}
num_to_note = {i: note for i, note in enumerate(notes)}

# Círculo de quintas ordenado (sentido horario: quintas ascendentes)
circle_of_fifths_major = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
circle_of_fifths_minor = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

# Colores para cada grado del campo armónico
grade_colors = {
    'I': '#FF4757',      # Tónica - Rojo
    'ii': '#FFA502',     # Supertonica - Naranja
    'iii': '#FFD93D',    # Mediante - Amarillo
    'IV': '#2ED573',     # Subdominante - Verde
    'V': '#1E90FF',      # Dominante - Azul
    'vi': '#9B59B6',     # Submediante - Púrpura
    'vii°': '#747D8C'    # Sensibile - Gris
}

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

def get_harmonic_field_in_circle(root):
    """
    Retorna las posiciones del campo armónico en el círculo de quintas
    para la tonalidad dada
    """
    root_idx = circle_of_fifths_major.index(root)
    
    # Mapeo de grados a posiciones en el círculo de quintas
    # I está en la tónica
    # V está una quinta arriba (+1)
    # IV está una quinta abajo (-1)
    # vi es la relativa menor (misma posición, círculo interior)
    # iii es la relativa del V (+1 interior)
    # ii es la relativa del IV (-1 interior)
    # vii° es la sensible, 5 quintas arriba (o medio tono debajo de la tónica)
    
    harmonic_positions = {
        'I': {'idx': root_idx, 'type': 'major', 'note': root, 'name': root},
        'V': {'idx': (root_idx + 1) % 12, 'type': 'major', 'note': circle_of_fifths_major[(root_idx + 1) % 12], 'name': circle_of_fifths_major[(root_idx + 1) % 12]},
        'IV': {'idx': (root_idx - 1) % 12, 'type': 'major', 'note': circle_of_fifths_major[(root_idx - 1) % 12], 'name': circle_of_fifths_major[(root_idx - 1) % 12]},
        'vi': {'idx': root_idx, 'type': 'minor', 'note': circle_of_fifths_minor[root_idx], 'name': circle_of_fifths_minor[root_idx]},
        'iii': {'idx': (root_idx + 1) % 12, 'type': 'minor', 'note': circle_of_fifths_minor[(root_idx + 1) % 12], 'name': circle_of_fifths_minor[(root_idx + 1) % 12]},
        'ii': {'idx': (root_idx - 1) % 12, 'type': 'minor', 'note': circle_of_fifths_minor[(root_idx - 1) % 12], 'name': circle_of_fifths_minor[(root_idx - 1) % 12]},
        'vii°': {'idx': (root_idx + 5) % 12, 'type': 'major', 'note': circle_of_fifths_major[(root_idx + 5) % 12], 'name': circle_of_fifths_major[(root_idx + 5) % 12] + '°'}
    }
    
    return harmonic_positions

def draw_harmonic_circle(ax, root):
    """Dibuja el círculo de quintas resaltando solo el campo armónico"""
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    
    # Obtener posiciones del campo armónico
    harmonic = get_harmonic_field_in_circle(root)
    
    # Conjunto de índices resaltados para fácil búsqueda
    highlighted_indices = set()
    for grade, info in harmonic.items():
        highlighted_indices.add((info['idx'], info['type']))
    
    # Dibujar todos los sectores primero (atenuados)
    for i in range(12):
        angle = np.pi/2 - i * (2*np.pi/12)
        
        # Verificar si esta posición está en el campo armónico
        is_major_highlight = (i, 'major') in highlighted_indices
        is_minor_highlight = (i, 'minor') in highlighted_indices
        
        # Dibujar círculo mayor exterior
        if is_major_highlight:
            # Encontrar qué grado es
            grade_name = [g for g, info in harmonic.items() if info['idx'] == i and info['type'] == 'major'][0]
            color = grade_colors[grade_name]
            alpha = 1.0
            radius = 1.0
            linewidth = 3
        else:
            color = '#37474F'
            alpha = 0.2
            radius = 1.0
            linewidth = 1
            
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=linewidth)
        ax.add_patch(wedge)
        
        # Dibujar círculo menor interior
        if is_minor_highlight:
            grade_name = [g for g, info in harmonic.items() if info['idx'] == i and info['type'] == 'minor'][0]
            color = grade_colors[grade_name]
            alpha = 1.0
            radius_inner = 0.6
            linewidth = 3
        else:
            color = '#37474F'
            alpha = 0.2
            radius_inner = 0.6
            linewidth = 1
            
        wedge_inner = Wedge((0, 0), radius_inner, np.degrees(angle - np.pi/12), 
                           np.degrees(angle + np.pi/12), 
                           facecolor=color, alpha=alpha, edgecolor='white', linewidth=linewidth)
        ax.add_patch(wedge_inner)
    
    # Ahora dibujar las etiquetas del campo armónico
    for grade, info in harmonic.items():
        angle = np.pi/2 - info['idx'] * (2*np.pi/12)
        
        if info['type'] == 'major':
            # Posición exterior
            x_note = 0.8 * np.cos(angle)
            y_note = 0.8 * np.sin(angle)
            x_grade = 1.15 * np.cos(angle)
            y_grade = 1.15 * np.sin(angle)
            
            # Nota musical
            ax.text(x_note, y_note, info['note'], ha='center', va='center', 
                   fontsize=12, fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.3', facecolor=grade_colors[grade], edgecolor='white', linewidth=2))
            
            # Grado romano
            ax.text(x_grade, y_grade, grade, ha='center', va='center',
                   fontsize=11, fontweight='bold', color=grade_colors[grade],
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=grade_colors[grade], alpha=0.9))
        else:
            # Posición interior
            x_note = 0.4 * np.cos(angle)
            y_note = 0.4 * np.sin(angle)
            x_grade = 0.15 * np.cos(angle)
            y_grade = 0.15 * np.sin(angle)
            
            # Nota musical menor
            ax.text(x_note, y_note, info['note'], ha='center', va='center', 
                   fontsize=10, fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.2', facecolor=grade_colors[grade], edgecolor='white', linewidth=2))
            
            # Grado romano
            ax.text(x_grade, y_grade, grade, ha='center', va='center',
                   fontsize=9, fontweight='bold', color='white')
    
    # Círculo central con la tónica
    center_circle = Circle((0, 0), 0.12, facecolor=grade_colors['I'], edgecolor='white', linewidth=3)
    ax.add_patch(center_circle)
    ax.text(0, 0, root, ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Título
    ax.set_title(f'Campo Armónico de {root} Mayor', color='white', fontsize=16, fontweight='bold', pad=20)

# Layout
col1, col2, col3 = st.columns([1, 1.5, 2.5])

with col1:
    st.subheader("🎵 Configuración")
    root_note = st.selectbox("Nota Raíz:", notes, index=0)
    chord_type = st.selectbox("Tipo de Acorde:", list(chord_types.keys()), index=0)
    
    intervals = chord_types[chord_type]
    root_num = note_to_num[root_note]
    
    chord_notes = []
    for interval in intervals:
        note_num = (root_num + interval) % 12
        chord_notes.append((notes[note_num], interval))
    
    st.markdown("---")
    st.subheader("🎹 Grados del Campo Armónico")
    
    harmonic = get_harmonic_field_in_circle(root_note)
    
    for grade in ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']:
        info = harmonic[grade]
        color = grade_colors[grade]
        
        col_grade, col_info = st.columns([1, 3])
        with col_grade:
            st.markdown(f"<h2 style='color: {color}; margin: 0; text-align: center;'>{grade}</h2>", unsafe_allow_html=True)
        with col_info:
            chord_type_name = 'Mayor' if grade in ['I', 'IV', 'V'] else 'Menor' if grade in ['ii', 'iii', 'vi'] else 'Disminuido'
            st.markdown(f"<div style='color: white; font-size: 16px;'><b>{info['name']}</b> ({chord_type_name})</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 5px 0; border-color: #333;'>", unsafe_allow_html=True)

with col2:
    st.subheader("🔄 Círculo de Quintas")
    
    fig_circle, ax_circle = plt.subplots(figsize=(7, 7))
    fig_circle.patch.set_facecolor('#1a1a2e')
    draw_harmonic_circle(ax_circle, root_note)
    st.pyplot(fig_circle)
    
    # Leyenda visual
    st.markdown("""
    <div style="background-color: #263238; padding: 15px; border-radius: 10px; margin-top: 10px; border: 2px solid #37474F;">
        <h4 style="color: white; margin-bottom: 10px;">Funciones:</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
    """, unsafe_allow_html=True)
    
    for grade in ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']:
        color = grade_colors[grade]
        name = {'I': 'Tónica', 'ii': 'Supertonica', 'iii': 'Mediante', 
                'IV': 'Subdominante', 'V': 'Dominante', 'vi': 'Submediante', 'vii°': 'Sensible'}[grade]
        st.markdown(f"""
            <div style="background-color: {color}33; padding: 5px 10px; border-radius: 5px; border-left: 3px solid {color};">
                <b style="color: {color};">{grade}</b> <span style="color: #ccc; font-size: 12px;">{name}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with col3:
    st.subheader("🎸 Diapasón (22 Trastes)")
    
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
    ax.plot([12], [2.5], "wo", markersize=8)
    ax.plot([12], [3.5], "wo", markersize=8)
    
    # Dibujar notas del acorde
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
                           fontsize=9, fontweight='bold', color='white', zorder=6)
                    if interval != 0:
                        ax.text(fret, string - 0.35, str(interval), ha='center', va='center',
                               fontsize=7, color=color, fontweight='bold', zorder=6)
                    break
    
    ax.set_xlim(-0.5, num_frets + 0.5)
    ax.set_ylim(-0.5, num_strings - 0.5)
    ax.set_yticks(range(num_strings))
    ax.set_yticklabels(tuning[::-1], fontsize=11, fontweight='bold', color='white')
    ax.set_xticks(range(num_frets + 1))
    ax.set_xticklabels(range(num_frets + 1), fontsize=9, color='white')
    ax.set_xlabel('Número de Traste', fontsize=12, fontweight='bold', color='white')
    ax.invert_yaxis()
    
    for i, note in enumerate(tuning[::-1]):
        ax.text(-0.8, i, note, fontsize=11, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))
    
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")
st.markdown(f"""
<center>
    <h4>Campo Armónico de <span style="color: #E94560;">{root_note} Mayor</span>: 
    {' - '.join([harmonic[g]['name'] for g in ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']])}</h4>
</center>
""", unsafe_allow_html=True)
