import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, FancyBboxPatch, Rectangle
import numpy as np

st.set_page_config(page_title="Visualizador Profesional de Acordes", 
                   page_icon="🎸", layout="wide")

# CSS personalizado para mejor apariencia
st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    h1 { color: #E94560 !important; font-size: 2.5rem !important; }
    h2 { color: #4ECDC4 !important; font-size: 1.8rem !important; }
    h3 { color: #FFD93D !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 15px 25px;
        font-weight: bold;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E94560 !important;
    }
    .grade-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .formula-box {
        background-color: #334155;
        border-radius: 6px;
        padding: 8px;
        margin-top: 8px;
        font-family: monospace;
        color: #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador Profesional: Acordes, Escalas y Campo Armónico")
st.markdown("---")

# ============================================
# CONFIGURACIÓN MUSICAL
# ============================================
notes_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
note_to_num = {note: i for i, note in enumerate(notes_sharp)}

# Preferencias de notación según tonalidad
def get_preferred_notes(root):
    """Retorna si usar sostenidos o bemoles según la tonalidad"""
    flat_roots = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return notes_flat if root in flat_roots else notes_sharp

# Círculo de quintas
circle_fifths = ['C', 'G', 'D', 'A', 'E', 'B', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']

# Colores para grados
GRADE_COLORS = {
    'I': '#FF4757',      # Tónica - Rojo
    'II': '#FF8C42',     # Supertónica - Naranja  
    'III': '#FFD93D',    # Mediante - Amarillo
    'IV': '#6BCB77',     # Subdominante - Verde
    'V': '#4D96FF',      # Dominante - Azul
    'VI': '#9B59B6',     # Submediante - Púrpura
    'VII': '#B8B8B8'     # Sensible - Gris
}

# Tipos de acordes disponibles
CHORD_TYPES = {
    'Triada Mayor': {'intervals': [0, 4, 7], 'formula': '1 - 3 - 5', 'type': 'Mayor'},
    'Triada Menor': {'intervals': [0, 3, 7], 'formula': '1 - b3 - 5', 'type': 'Menor'},
    'Triada Disminuida': {'intervals': [0, 3, 6], 'formula': '1 - b3 - b5', 'type': 'Disminuido'},
    'Triada Aumentada': {'intervals': [0, 4, 8], 'formula': '1 - 3 - #5', 'type': 'Aumentado'},
    'Mayor 7 (Maj7)': {'intervals': [0, 4, 7, 11], 'formula': '1 - 3 - 5 - 7', 'type': 'Mayor 7'},
    'Dominante 7 (7)': {'intervals': [0, 4, 7, 10], 'formula': '1 - 3 - 5 - b7', 'type': '7'},
    'Menor 7 (m7)': {'intervals': [0, 3, 7, 10], 'formula': '1 - b3 - 5 - b7', 'type': 'm7'},
    'Menor/Mayor 7 (mMaj7)': {'intervals': [0, 3, 7, 11], 'formula': '1 - b3 - 5 - 7', 'type': 'mMaj7'},
    'Semi-disminuido (m7b5)': {'intervals': [0, 3, 6, 10], 'formula': '1 - b3 - b5 - b7', 'type': 'ø7'},
    'Disminuido 7 (dim7)': {'intervals': [0, 3, 6, 9], 'formula': '1 - b3 - b5 - bb7', 'type': 'dim7'},
    'Sus4': {'intervals': [0, 5, 7], 'formula': '1 - 4 - 5', 'type': 'Sus4'},
    'Sus2': {'intervals': [0, 2, 7], 'formula': '1 - 2 - 5', 'type': 'Sus2'},
    '6 Mayor': {'intervals': [0, 4, 7, 9], 'formula': '1 - 3 - 5 - 6', 'type': '6'},
    '6 Menor': {'intervals': [0, 3, 7, 9], 'formula': '1 - b3 - 5 - 6', 'type': 'm6'}
}

# Afinación guitarra
TUNING = ['E', 'B', 'G', 'D', 'A', 'E']

# ============================================
# FUNCIONES MUSICALES
# ============================================
def get_scale_notes(root):
    """Obtiene las notas de la escala mayor"""
    notes = get_preferred_notes(root)
    root_idx = note_to_num[root] if root in note_to_num else notes_sharp.index(root)
    intervals = [0, 2, 4, 5, 7, 9, 11]
    return [(notes[(root_idx + i) % 12], i) for i in intervals]

def get_harmonic_field(root):
    """Obtiene el campo armónico completo con notas de cada acorde"""
    scale = get_scale_notes(root)
    harmonic = {}
    
    # Definir acordes del campo armónico según grados
    chord_defs = [
        ('I', 'Mayor', 'Triada Mayor'),
        ('II', 'Menor', 'Triada Menor'),
        ('III', 'Menor', 'Triada Menor'),
        ('IV', 'Mayor', 'Triada Mayor'),
        ('V', 'Mayor', 'Triada Mayor'),
        ('VI', 'Menor', 'Triada Menor'),
        ('VII', 'Disminuido', 'Triada Disminuida')
    ]
    
    for i, (degree, quality, chord_type) in enumerate(chord_defs):
        note = scale[i][0]
        intervals = CHORD_TYPES[chord_type]['intervals']
        chord_notes = [get_preferred_notes(root)[(note_to_num[note] + interval) % 12] 
                      for interval in intervals]
        
        harmonic[degree] = {
            'root': note,
            'quality': quality,
            'chord_type': chord_type,
            'notes': chord_notes,
            'formula': CHORD_TYPES[chord_type]['formula'],
            'intervals': intervals,
            'color': GRADE_COLORS[degree]
        }
    
    return harmonic

def get_chord_notes(root, chord_type_name):
    """Obtiene las notas de un acorde específico"""
    if chord_type_name not in CHORD_TYPES:
        return []
    
    intervals = CHORD_TYPES[chord_type_name]['intervals']
    root_idx = note_to_num[root]
    notes = get_preferred_notes(root)
    
    return [notes[(root_idx + interval) % 12] for interval in intervals]

def get_inversions(root, chord_type_name):
    """Obtiene las inversiones de un acorde"""
    notes = get_chord_notes(root, chord_type_name)
    if len(notes) < 3:
        return {}
    
    inversions = {
        'Raíz': notes,
        '1ra Inversión': notes[1:] + [notes[0]],
        '2da Inversión': notes[2:] + notes[:2]
    }
    
    if len(notes) == 4:
        inversions['3ra Inversión'] = [notes[3]] + notes[:3]
    
    return inversions

# ============================================
# VISUALIZACIÓN
# ============================================
def draw_large_circle(ax, root):
    """Dibuja el círculo de quintas grande resaltando el campo armónico"""
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0f172a')
    
    harmonic = get_harmonic_field(root)
    
    # Dibujar círculo completo de quintas
    for i, note in enumerate(circle_fifths):
        angle = np.pi/2 - i * (2*np.pi/12)
        
        # Verificar si esta nota está en el campo armónico
        in_harmonic = False
        degree_info = None
        for degree, info in harmonic.items():
            if info['root'] == note:
                in_harmonic = True
                degree_info = (degree, info)
                break
        
        # Dibujar sector
        if in_harmonic:
            color = degree_info[1]['color']
            alpha = 1.0
            radius = 1.0
            linewidth = 4
        else:
            color = '#334155'
            alpha = 0.2
            radius = 0.95
            linewidth = 1
            
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=linewidth)
        ax.add_patch(wedge)
        
        # Nota musical
        x_note = 0.75 * np.cos(angle)
        y_note = 0.75 * np.sin(angle)
        fontsize = 20 if in_harmonic else 12
        fontweight = 'bold' if in_harmonic else 'normal'
        
        ax.text(x_note, y_note, note, ha='center', va='center', 
               fontsize=fontsize, fontweight=fontweight, color='white',
               bbox=dict(boxstyle='circle,pad=0.4' if in_harmonic else 'circle,pad=0.2', 
                        facecolor=color if in_harmonic else '#475569',
                        edgecolor='white', linewidth=3 if in_harmonic else 1,
                        alpha=0.95))
        
        # Grado romano (solo para campo armónico)
        if in_harmonic:
            x_grade = 1.25 * np.cos(angle)
            y_grade = 1.25 * np.sin(angle)
            ax.text(x_grade, y_grade, degree_info[0], 
                   ha='center', va='center', fontsize=16, fontweight='bold',
                   color=color,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=color, linewidth=2))
    
    # Centro - Tónica
    center_circle = Circle((0, 0), 0.2, facecolor=GRADE_COLORS['I'], 
                          edgecolor='white', linewidth=4)
    ax.add_patch(center_circle)
    ax.text(0, 0, root, ha='center', va='center', fontsize=24, 
           fontweight='bold', color='white')

def draw_fretboard(ax, root, chord_type_name):
    """Dibuja el diapasón con notas"""
    ax.set_facecolor('#263238')
    num_frets = 22
    num_strings = 6
    
    # Mástil
    ax.add_patch(Rectangle((-0.5, -0.5), num_frets + 1.5, num_strings, 
                          facecolor='#3E2723', alpha=0.8))
    
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
    
    # Marcadores
    ax.plot([12], [2.5], "wo", markersize=8)
    ax.plot([12], [3.5], "wo", markersize=8)
    
    # Notas del acorde seleccionado
    if chord_type_name in CHORD_TYPES:
        intervals = CHORD_TYPES[chord_type_name]['intervals']
        root_idx = note_to_num[root]
        notes = get_preferred_notes(root)
        
        for string in range(num_strings):
            for fret in range(num_frets + 1):
                open_note = TUNING[string]
                open_idx = note_to_num[open_note]
                current_idx = (open_idx + fret) % 12
                
                # Verificar si está en el acorde
                for i, interval in enumerate(intervals):
                    if (root_idx + interval) % 12 == current_idx:
                        color = ['#FF4757', '#3742FA', '#2ED573', '#FFD93D'][i % 4]
                        
                        circle = Circle((fret, string), 0.28, facecolor=color, 
                                      edgecolor='white', linewidth=2, zorder=5)
                        ax.add_patch(circle)
                        
                        note_name = notes[current_idx]
                        ax.text(fret, string, note_name, ha='center', va='center', 
                               fontsize=8, fontweight='bold', color='white', zorder=6)
                        
                        # Intervalo
                        if fret > 0:
                            ax.text(fret, string - 0.35, f'{interval}', 
                                   ha='center', va='center', fontsize=7, 
                                   color=color, fontweight='bold', zorder=6)
                        break
    
    ax.set_xlim(-0.5, num_frets + 0.5)
    ax.set_ylim(-0.5, num_strings - 0.5)
    ax.set_yticks(range(num_strings))
    ax.set_yticklabels(TUNING[::-1], fontsize=11, fontweight='bold', color='white')
    ax.set_xticks(range(0, num_frets + 1, 2))
    ax.set_xticklabels(range(0, num_frets + 1, 2), fontsize=9, color='white')
    ax.set_xlabel('Traste', fontsize=12, fontweight='bold', color='white')
    ax.invert_yaxis()
    
    # Afinación lateral
    for i, note in enumerate(TUNING[::-1]):
        ax.text(-0.8, i, note, fontsize=11, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))

# ============================================
# INTERFAZ PRINCIPAL
# ============================================
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    root_note = st.selectbox("🎵 Nota Raíz:", notes_sharp, index=0)
with col2:
    chord_type = st.selectbox("🎸 Tipo de Acorde:", list(CHORD_TYPES.keys()), index=0)
with col3:
    st.markdown(f"### Acorde Seleccionado: **{root_note}** {CHORD_TYPES[chord_type]['type']}")
    st.markdown(f"**Fórmula:** {CHORD_TYPES[chord_type]['formula']}")

st.markdown("---")

# PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs(["🎹 Escala y Grados", "🎼 Campo Armónico Detallado", 
                                  "🔄 Acordes e Inversiones", "🎸 Diapasón"])

# ============================================
# TAB 1: ESCALA Y GRADOS
# ============================================
with tab1:
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.subheader("Escala Mayor de " + root_note)
        scale = get_scale_notes(root_note)
        
        for i, (note, interval) in enumerate(scale):
            degree = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][i]
            color = GRADE_COLORS[degree]
            
            st.markdown(f"""
            <div class="grade-card" style="border-left-color: {color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: {color}; font-size: 28px; font-weight: bold;">{degree}</span>
                        <span style="color: white; font-size: 20px; margin-left: 15px;">{note}</span>
                    </div>
                    <div style="color: #94a3b8; font-size: 14px;">
                        Intervalo: +{interval} semitonos
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.subheader("Círculo de Quintas - Campo Armónico")
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('#0f172a')
        draw_large_circle(ax, root_note)
        st.pyplot(fig, use_container_width=True)

# ============================================
# TAB 2: CAMPO ARMÓNICO DETALLADO
# ============================================
with tab2:
    st.subheader(f"Campo Armónico de {root_note} Mayor - Notas de cada Acorde")
    
    harmonic = get_harmonic_field(root_note)
    
    # Grid de 7 columnas (una por grado)
    cols = st.columns(7)
    
    for idx, (col, (degree, info)) in enumerate(zip(cols, harmonic.items())):
        with col:
            color = info['color']
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                        border: 3px solid {color}; border-radius: 15px; padding: 15px; 
                        text-align: center; height: 100%;">
                <h2 style="color: {color}; margin: 0; font-size: 36px;">{degree}</h2>
                <h3 style="color: white; margin: 10px 0;">{info['root']}</h3>
                <p style="color: #94a3b8; margin: 5px 0;">{info['quality']}</p>
                <hr style="border-color: {color}; margin: 10px 0;">
                <p style="color: #4ECDC4; font-weight: bold; font-size: 14px; margin: 5px 0;">
                    {info['formula']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Notas del acorde
            for note in info['notes']:
                st.markdown(f"<p style='text-align: center; color: white; font-size: 18px; margin: 5px 0;'><b>{note}</b></p>", unsafe_allow_html=True)
            
            # Fórmula visual
            intervals = info['intervals']
            st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
            for i, interval in enumerate(intervals):
                interval_colors = ['#FF4757', '#3742FA', '#2ED573', '#FFD93D']
                st.markdown(f"""
                <span style="background-color: {interval_colors[i % 4]}; color: white; 
                            padding: 2px 8px; border-radius: 10px; font-size: 12px; 
                            margin: 0 2px;">+{interval}</span>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# TAB 3: ACORDES E INVERSIONES
# ============================================
with tab3:
    st.subheader(f"Inversiones del Acorde {root_note} {CHORD_TYPES[chord_type]['type']}")
    
    inversions = get_inversions(root_note, chord_type)
    
    if inversions:
        cols = st.columns(len(inversions))
        
        for col, (inv_name, notes) in zip(cols, inversions.items()):
            with col:
                st.markdown(f"""
                <div style="background-color: #1e293b; border-radius: 15px; 
                            padding: 20px; text-align: center; border: 2px solid #4ECDC4;">
                    <h3 style="color: #4ECDC4; margin-bottom: 20px;">{inv_name}</h3>
                """, unsafe_allow_html=True)
                
                # Visualización del acorde (notas apiladas)
                for i, note in enumerate(notes):
                    colors = ['#FF4757', '#3742FA', '#2ED573', '#FFD93D']
                    bg_color = colors[i % 4]
                    st.markdown(f"""
                    <div style="background-color: {bg_color}; color: white; 
                                padding: 15px; margin: 10px 0; border-radius: 10px;
                                font-size: 24px; font-weight: bold;">
                        {note}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Indicar el bajo
                st.markdown(f"""
                    <p style="color: #94a3b8; margin-top: 15px; font-size: 14px;">
                        Bajo: <b style="color: white;">{notes[0]}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Análisis de intervalos
    st.markdown("---")
    st.subheader("Análisis de Intervalos")
    
    intervals = CHORD_TYPES[chord_type]['intervals']
    notes_list = get_chord_notes(root_note, chord_type)
    
    col_ints = st.columns(len(intervals))
    for col, interval, note in zip(col_ints, intervals, notes_list):
        with col:
            colors = ['#FF4757', '#3742FA', '#2ED573', '#FFD93D']
            color = colors[intervals.index(interval) % 4]
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; 
                        background-color: {color}22; border-radius: 10px;
                        border: 2px solid {color};">
                <h1 style="color: {color}; margin: 0; font-size: 48px;">{note}</h1>
                <p style="color: white; font-size: 24px; margin: 10px 0;">+{interval} semi</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# TAB 4: DIAPASÓN
# ============================================
with tab4:
    st.subheader("Visualización en Diapasón de 22 Trastes")
    
    fig, ax = plt.subplots(figsize=(18, 6))
    draw_fretboard(ax, root_note, chord_type)
    st.pyplot(fig, use_container_width=True)
    
    # Leyenda
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px;">
        <div style="text-align: center;">
            <span style="background-color: #FF4757; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold;">Raíz (1)</span>
        </div>
        <div style="text-align: center;">
            <span style="background-color: #3742FA; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold;">3ra</span>
        </div>
        <div style="text-align: center;">
            <span style="background-color: #2ED573; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold;">5ta</span>
        </div>
        <div style="text-align: center;">
            <span style="background-color: #FFD93D; padding: 10px 20px; border-radius: 20px; color: black; font-weight: bold;">7ma</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<center><h4>Campo Armónico Completo: {' - '.join([get_harmonic_field(root_note)[d]['root'] + get_harmonic_field(root_note)[d]['quality'][0] for d in ['I','II','III','IV','V','VI','VII']])}</h4></center>", unsafe_allow_html=True)
