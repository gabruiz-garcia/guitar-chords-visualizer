import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, Rectangle, FancyBboxPatch
import numpy as np

st.set_page_config(page_title="Campo Armónico Visual", page_icon="🎸", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    h1 { color: #E94560 !important; font-size: 2rem !important; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2a; border-radius: 8px 8px 0 0;
        padding: 12px 20px; font-weight: bold; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #E94560 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Círculo de Quintas - Campo Armónico Visual")
st.markdown("---")

# Configuración
notes_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
note_to_num = {note: i for i, note in enumerate(notes_sharp)}

def get_notes(root):
    return notes_flat if root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb'] else notes_sharp

CIRCLE_MAJOR = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
CIRCLE_MINOR = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

KEY_SIGS = {
    'C': (0, ''), 'G': (1, '#'), 'D': (2, '#'), 'A': (3, '#'),
    'E': (4, '#'), 'B': (5, '#'), 'F#': (6, '#'), 'C#': (7, '#'),
    'Ab': (4, 'b'), 'Eb': (3, 'b'), 'Bb': (2, 'b'), 'F': (1, 'b')
}

GRADE_COLORS = {
    'I': '#FF0000',    # Rojo intenso
    'II': '#FF8C00',   # Naranja
    'III': '#FFD700',  # Amarillo/Dorado
    'IV': '#FF1493',   # Rosa/DeepPink
    'V': '#FF4500',    # NaranjaRojo
    'VI': '#FFA500',   # Naranja
    'VII': '#32CD32'   # Verde
}

CHORD_TYPES = {
    'Mayor (I, IV, V)': {'intervals': [0, 4, 7], 'formula': '1 - 3 - 5'},
    'Menor (ii, iii, vi)': {'intervals': [0, 3, 7], 'formula': '1 - b3 - 5'},
    'Disminuido (vii°)': {'intervals': [0, 3, 6], 'formula': '1 - b3 - b5'},
    'Mayor 7': {'intervals': [0, 4, 7, 11], 'formula': '1 - 3 - 5 - 7'},
    'Menor 7': {'intervals': [0, 3, 7, 10], 'formula': '1 - b3 - 5 - b7'},
    'Dominante 7': {'intervals': [0, 4, 7, 10], 'formula': '1 - 3 - 5 - b7'},
    'Semi-disminuido': {'intervals': [0, 3, 6, 10], 'formula': '1 - b3 - b5 - b7'}
}

TUNING = ['E', 'B', 'G', 'D', 'A', 'E']

def get_harmonic_field(root):
    """Retorna {posición_círculo: (grado, tipo, nota)}"""
    idx = CIRCLE_MAJOR.index(root)
    field = {}
    
    # Mapeo exacto del campo armónico en el círculo
    field[idx] = ('I', 'Mayor', CIRCLE_MAJOR[idx])                    # Tónica
    field[(idx + 1) % 12] = ('V', 'Mayor', CIRCLE_MAJOR[(idx + 1) % 12])  # Dominante (+1 quinta)
    field[(idx - 1) % 12] = ('IV', 'Mayor', CIRCLE_MAJOR[(idx - 1) % 12]) # Subdominante (-1 quinta)
    field[(idx + 2) % 12] = ('II', 'Menor', CIRCLE_MAJOR[(idx + 2) % 12]) # Supertónica (+2 quintas)
    field[(idx - 2) % 12] = ('VI', 'Menor', CIRCLE_MAJOR[(idx - 2) % 12]) # Submediante (-2 quintas)
    field[(idx + 3) % 12] = ('III', 'Menor', CIRCLE_MAJOR[(idx + 3) % 12])# Mediante (+3 quintas)
    field[(idx + 4) % 12] = ('VII', 'Disminuido', CIRCLE_MAJOR[(idx + 4) % 12]) # Sensible (+4 quintas)
    
    return field

def draw_focused_circle(ax, root):
    """Dibuja el círculo mostrando SOLO el campo armónico con grados romanos"""
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0a0a0a')
    
    field = get_harmonic_field(root)
    sig_num, sig_type = KEY_SIGS[root]
    sig_str = f"{sig_num}{'♯' if sig_type == '#' else '♭' if sig_type == 'b' else ''}" if sig_num > 0 else "Natural"
    
    ax.set_title(f'{root} Mayor - Armadura: {sig_str}', 
                color='white', fontsize=18, fontweight='bold', pad=20)
    
    # Dibujar los 12 sectores
    for i, (major_note, minor_note) in enumerate(zip(CIRCLE_MAJOR, CIRCLE_MINOR)):
        angle = np.pi/2 - i * (2*np.pi/12)  # 12 en punto es C
        
        is_in_field = i in field
        is_tonic = (major_note == root)
        
        if is_in_field:
            grade, quality, _ = field[i]
            color = GRADE_COLORS[grade]
            alpha = 1.0
            radius = 1.0
            linewidth = 4
        else:
            # Fuera del campo armónico - casi invisible
            color = '#1a1a1a'
            alpha = 0.3
            radius = 0.9
            linewidth = 0.5
        
        # Sector exterior
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white' if is_in_field else '#333', 
                     linewidth=linewidth)
        ax.add_patch(wedge)
        
        # Sector interior (menor)
        if is_in_field:
            wedge_inner = Wedge((0, 0), 0.6, np.degrees(angle - np.pi/12), 
                               np.degrees(angle + np.pi/12), 
                               facecolor=color, alpha=0.6, edgecolor='white', linewidth=2)
            ax.add_patch(wedge_inner)
        
        if is_in_field:
            grade, quality, _ = field[i]
            
            # GRADO ROMANO (grande, arriba)
            x_grade = 0.8 * np.cos(angle)
            y_grade = 0.95 * np.sin(angle)
            
            display_grade = grade if quality == 'Mayor' else grade.lower()
            if quality == 'Disminuido':
                display_grade = 'vii°' if grade == 'VII' else grade.lower() + '°'
            
            # Símbolo del grado
            ax.text(x_grade, y_grade, display_grade, ha='center', va='center',
                   fontsize=22, fontweight='bold', color='white',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='black', 
                            edgecolor=color, linewidth=3), zorder=10)
            
            # NOTA MAYOR (debajo del grado)
            x_note = 0.8 * np.cos(angle)
            y_note = 0.75 * np.sin(angle)
            
            ax.text(x_note, y_note, major_note, ha='center', va='center',
                   fontsize=16, fontweight='bold', color=color, zorder=10)
            
            # Armadura pequeña
            num_alt, tipo_alt = KEY_SIGS[major_note]
            if num_alt > 0:
                x_alt = 1.08 * np.cos(angle)
                y_alt = 1.08 * np.sin(angle)
                symbol = '♯' if tipo_alt == '#' else '♭'
                ax.text(x_alt, y_alt, f"{num_alt}{symbol}", ha='center', va='center',
                       fontsize=11, color='#FFD700', fontweight='bold',
                       bbox=dict(boxstyle='circle', facecolor='#222', alpha=0.8))
            
            # NOTA MENOR (interior)
            x_min = 0.35 * np.cos(angle)
            y_min = 0.35 * np.sin(angle)
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white', zorder=10,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='#000', alpha=0.7))
        else:
            # Notas fuera del campo - muy tenues
            x = 0.8 * np.cos(angle)
            y = 0.8 * np.sin(angle)
            ax.text(x, y, major_note, ha='center', va='center',
                   fontsize=10, color='#444', alpha=0.4)
            
            x_min = 0.35 * np.cos(angle)
            y_min = 0.35 * np.sin(angle)
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=8, color='#333', alpha=0.3)
    
    # Centro
    if True:
        center_bg = Circle((0, 0), 0.2, facecolor=GRADE_COLORS['I'], 
                          edgecolor='white', linewidth=3)
        ax.add_patch(center_bg)
        ax.text(0, 0, root, ha='center', va='center', fontsize=24, 
               fontweight='bold', color='white')
        ax.text(0, -0.12, 'I', ha='center', va='center', fontsize=12, color='white')

def get_chord_notes(root, intervals):
    root_idx = note_to_num[root]
    notes = get_notes(root)
    return [notes[(root_idx + i) % 12] for i in intervals]

def get_inversions(notes):
    if len(notes) < 3:
        return {}
    invs = {
        'Raíz': notes,
        '1ª Inv': notes[1:] + [notes[0]],
        '2ª Inv': notes[2:] + notes[:2]
    }
    if len(notes) == 4:
        invs['3ª Inv'] = [notes[3]] + notes[:3]
    return invs

# Interfaz
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    root_note = st.selectbox("Tonalidad:", CIRCLE_MAJOR, index=0)
    chord_sel = st.selectbox("Tipo:", list(CHORD_TYPES.keys()), index=0)
    
    intervals = CHORD_TYPES[chord_sel]['intervals']
    notes_chord = get_chord_notes(root_note, intervals)
    
    st.markdown("### Notas del Acorde")
    for i, note in enumerate(notes_chord):
        st.markdown(f"<h3 style='color: {['#FF0000', '#00FF00', '#0000FF', '#FFD700'][i]}; margin: 5px;'>{note}</h3>", unsafe_allow_html=True)

with col2:
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#0a0a0a')
    draw_focused_circle(ax, root_note)
    st.pyplot(fig, use_container_width=True)

with col3:
    st.subheader("Grados Activos")
    field = get_harmonic_field(root_note)
    
    # Orden funcional
    orden = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    for grado_romano in orden:
        for pos, (grado, tipo, nota) in field.items():
            if grado == grado_romano:
                color = GRADE_COLORS[grado]
                display = grado if tipo == 'Mayor' else grado.lower()
                if tipo == 'Disminuido':
                    display = 'vii°'
                
                st.markdown(f"""
                <div style="background-color: {color}22; border-left: 4px solid {color}; 
                            padding: 10px; margin: 5px 0; border-radius: 0 8px 8px 0;">
                    <span style="color: {color}; font-size: 24px; font-weight: bold;">{display}</span>
                    <span style="color: white; font-size: 18px; margin-left: 10px;">{nota}</span>
                    <span style="color: #888; font-size: 12px; float: right;">{tipo}</span>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
tab1, tab2 = st.tabs(["🎸 Inversiones", "🎸 Diapasón"])

with tab1:
    st.subheader(f"Inversiones - {root_note} {chord_sel.split()[0]}")
    invs = get_inversions(notes_chord)
    
    cols = st.columns(len(invs))
    for col, (name, notes) in zip(cols, invs.items()):
        with col:
            st.markdown(f"<h4 style='text-align: center; color: #4ECDC4;'>{name}</h4>", unsafe_allow_html=True)
            for i, note in enumerate(notes):
                color = ['#FF0000', '#00FF00', '#0000FF', '#FFD700'][i]
                st.markdown(f"""
                <div style="background-color: {color}; color: white; padding: 15px; 
                            margin: 5px 0; text-align: center; border-radius: 8px;
                            font-size: 20px; font-weight: bold;">
                    {note}
                </div>
                """, unsafe_allow_html=True)

with tab2:
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.set_facecolor('#1a1a2a')
    
    # Dibujar diapasón básico
    for fret in range(23):
        color = '#FFD700' if fret in [3,5,7,9,12,15,17,19,21] else '#666'
        ax.axvline(fret, color=color, linewidth=2)
    for string in range(6):
        ax.axhline(string, color='#DDD', linewidth=3-string*0.3, alpha=0.6)
    
    # Notas
    for string in range(6):
        for fret in range(22):
            open_idx = note_to_num[TUNING[string]]
            curr_idx = (open_idx + fret) % 12
            
            for i, inter in enumerate(intervals):
                if (note_to_num[root_note] + inter) % 12 == curr_idx:
                    color = ['#FF0000', '#00FF00', '#0000FF', '#FFD700'][i]
                    circle = Circle((fret, string), 0.25, facecolor=color, edgecolor='white', linewidth=2)
                    ax.add_patch(circle)
                    ax.text(fret, string, notes_sharp[curr_idx], ha='center', va='center', 
                           fontsize=8, color='white', fontweight='bold')
    
    ax.set_xlim(-0.5, 22.5)
    ax.set_ylim(-0.5, 5.5)
    ax.set_yticks(range(6))
    ax.set_yticklabels(TUNING[::-1], color='white')
    ax.invert_yaxis()
    st.pyplot(fig, use_container_width=True)
