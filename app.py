import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, Rectangle, FancyBboxPatch
import numpy as np

st.set_page_config(page_title="Visualizador Profesional de Acordes", 
                   page_icon="🎸", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    h1 { color: #E94560 !important; font-size: 2.2rem !important; }
    h2 { color: #4ECDC4 !important; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b; border-radius: 8px 8px 0 0;
        padding: 15px 25px; font-weight: bold; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #E94560 !important; }
    .grade-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px; padding: 15px; margin: 10px 0;
        border-left: 5px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador Profesional: Círculo de Quintas, Campo Armónico y Acordes")
st.markdown("---")

# ============================================
# CONFIGURACIÓN MUSICAL COMPLETA
# ============================================
notes_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
note_to_num = {note: i for i, note in enumerate(notes_sharp)}

def get_preferred_notes(root):
    flat_roots = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
    return notes_flat if root in flat_roots else notes_sharp

# CÍRCULO DE QUINTAS TRADICIONAL (como la imagen)
CIRCLE_MAJOR = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
CIRCLE_MINOR = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

# Armaduras: (cantidad, tipo)
KEY_SIGS = {
    'C': (0, ''), 'G': (1, '#'), 'D': (2, '#'), 'A': (3, '#'),
    'E': (4, '#'), 'B': (5, '#'), 'F#': (6, '#'), 'C#': (7, '#'),
    'Ab': (4, 'b'), 'Eb': (3, 'b'), 'Bb': (2, 'b'), 'F': (1, 'b')
}

# Colores tradicionales para grados (como la imagen)
GRADE_COLORS = {
    'I': '#E63946',    # Rojo (Tónica)
    'ii': '#FB8500',   # Naranja (Supertónica)
    'iii': '#FFB703',  # Amarillo (Mediante)
    'IV': '#F72585',   # Rosa (Subdominante)
    'V': '#F4A261',    # Naranja claro (Dominante)
    'vi': '#FFD60A',   # Amarillo/Dorado (Submediante)
    'vii': '#2ECC71'   # Verde (Sensible)
}

# Todos los tipos de acordes (Triadas y Cuatríadas)
CHORD_TYPES = {
    'Triada Mayor': {'intervals': [0, 4, 7], 'formula': '1 - 3 - 5', 'type': 'Mayor'},
    'Triada Menor': {'intervals': [0, 3, 7], 'formula': '1 - b3 - 5', 'type': 'Menor'},
    'Triada Disminuida': {'intervals': [0, 3, 6], 'formula': '1 - b3 - b5', 'type': 'Disminuido'},
    'Triada Aumentada': {'intervals': [0, 4, 8], 'formula': '1 - 3 - #5', 'type': 'Aumentado'},
    'Mayor 7 (Maj7)': {'intervals': [0, 4, 7, 11], 'formula': '1 - 3 - 5 - 7', 'type': 'Maj7'},
    'Dominante 7 (7)': {'intervals': [0, 4, 7, 10], 'formula': '1 - 3 - 5 - b7', 'type': '7'},
    'Menor 7 (m7)': {'intervals': [0, 3, 7, 10], 'formula': '1 - b3 - 5 - b7', 'type': 'm7'},
    'Menor/Mayor 7 (mMaj7)': {'intervals': [0, 3, 7, 11], 'formula': '1 - b3 - 5 - 7', 'type': 'mMaj7'},
    'Mayor 6': {'intervals': [0, 4, 7, 9], 'formula': '1 - 3 - 5 - 6', 'type': '6'},
    'Menor 6': {'intervals': [0, 3, 7, 9], 'formula': '1 - b3 - 5 - 6', 'type': 'm6'},
    'Semi-disminuido (m7b5)': {'intervals': [0, 3, 6, 10], 'formula': '1 - b3 - b5 - b7', 'type': 'ø7'},
    'Disminuido 7 (dim7)': {'intervals': [0, 3, 6, 9], 'formula': '1 - b3 - b5 - bb7', 'type': 'dim7'},
    'Aumentado 7 (7#5)': {'intervals': [0, 4, 8, 10], 'formula': '1 - 3 - #5 - b7', 'type': '7#5'},
    'Sus4': {'intervals': [0, 5, 7], 'formula': '1 - 4 - 5', 'type': 'Sus4'},
    'Sus2': {'intervals': [0, 2, 7], 'formula': '1 - 2 - 5', 'type': 'Sus2'}
}

TUNING = ['E', 'B', 'G', 'D', 'A', 'E']

def get_harmonic_field_grades(root):
    """Mapeo de posición en círculo -> grado para tonalidad dada"""
    root_idx = CIRCLE_MAJOR.index(root)
    grade_map = {}
    
    # I (Tónica)
    grade_map[root_idx] = ('I', 'Mayor', CIRCLE_MAJOR[root_idx])
    # V (Dominante) - +1 quinta
    pos_v = (root_idx + 1) % 12
    grade_map[pos_v] = ('V', 'Mayor', CIRCLE_MAJOR[pos_v])
    # IV (Subdominante) - -1 quinta
    pos_iv = (root_idx - 1) % 12
    grade_map[pos_iv] = ('IV', 'Mayor', CIRCLE_MAJOR[pos_iv])
    # ii (Supertónica) - +2 quintas
    pos_ii = (root_idx + 2) % 12
    grade_map[pos_ii] = ('ii', 'Menor', CIRCLE_MAJOR[pos_ii])
    # vi (Submediante) - -2 quintas
    pos_vi = (root_idx - 2) % 12
    grade_map[pos_vi] = ('vi', 'Menor', CIRCLE_MAJOR[pos_vi])
    # iii (Mediante) - +3 quintas
    pos_iii = (root_idx + 3) % 12
    grade_map[pos_iii] = ('iii', 'Menor', CIRCLE_MAJOR[pos_iii])
    # vii° (Sensible) - +4 quintas
    pos_vii = (root_idx + 4) % 12
    grade_map[pos_vii] = ('vii', 'Disminuido', CIRCLE_MAJOR[pos_vii])
    
    return grade_map

def get_scale_notes(root):
    notes = get_preferred_notes(root)
    root_idx = note_to_num[root] if root in note_to_num else notes_sharp.index(root)
    intervals = [0, 2, 4, 5, 7, 9, 11]
    return [(notes[(root_idx + i) % 12], i) for i in intervals]

def get_chord_notes(root, chord_type_name):
    if chord_type_name not in CHORD_TYPES:
        return []
    intervals = CHORD_TYPES[chord_type_name]['intervals']
    root_idx = note_to_num[root]
    notes = get_preferred_notes(root)
    return [notes[(root_idx + interval) % 12] for interval in intervals]

def get_inversions(root, chord_type_name):
    notes = get_chord_notes(root, chord_type_name)
    if len(notes) < 3:
        return {}
    
    inversions = {
        'Estado Fundamental (Raíz)': notes,
        '1ra Inversión (3ra al bajo)': notes[1:] + [notes[0]],
        '2da Inversión (5ta al bajo)': notes[2:] + notes[:2]
    }
    
    if len(notes) == 4:
        inversions['3ra Inversión (7ma al bajo)'] = [notes[3]] + notes[:3]
    
    return inversions

def get_harmonic_field_full(root):
    """Campo armónico completo con notas de cada acorde"""
    scale = get_scale_notes(root)
    harmonic = {}
    chord_defs = [
        ('I', 'Mayor', 'Triada Mayor'), ('ii', 'Menor', 'Triada Menor'),
        ('iii', 'Menor', 'Triada Menor'), ('IV', 'Mayor', 'Triada Mayor'),
        ('V', 'Mayor', 'Triada Mayor'), ('vi', 'Menor', 'Triada Menor'),
        ('vii', 'Disminuido', 'Triada Disminuida')
    ]
    for i, (degree, quality, chord_type) in enumerate(chord_defs):
        note = scale[i][0]
        intervals = CHORD_TYPES[chord_type]['intervals']
        chord_notes = [get_preferred_notes(root)[(note_to_num[note] + interval) % 12] 
                      for interval in intervals]
        harmonic[degree] = {
            'root': note, 'quality': quality, 'chord_type': chord_type,
            'notes': chord_notes, 'formula': CHORD_TYPES[chord_type]['formula'],
            'color': GRADE_COLORS[degree]
        }
    return harmonic

# ============================================
# VISUALIZACIÓN DEL CÍRCULO (COMO LA IMAGEN)
# ============================================
def draw_study_circle(ax, root):
    """Círculo de quintas estilo imagen: 12 sectores, 7 grados marcados, armaduras"""
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0f172a')
    
    grade_map = get_harmonic_field_grades(root)
    sig_num, sig_type = KEY_SIGS[root]
    
    # Título
    sig_text = f"({sig_num} {sig_type})" if sig_num > 0 else "(Natural)"
    ax.set_title(f'Círculo de Quintas: {root} Mayor {sig_text}', 
                color='white', fontsize=20, fontweight='bold', pad=30)
    
    # Anillos de referencia
    for r in [0.6, 1.0]:
        circle = Circle((0, 0), r, fill=False, edgecolor='#475569', linewidth=2, alpha=0.3)
        ax.add_patch(circle)
    
    # Dibujar 12 sectores
    for i, (major_note, minor_note) in enumerate(zip(CIRCLE_MAJOR, CIRCLE_MINOR)):
        angle = np.pi/2 - i * (2*np.pi/12)  # 12 en punto = C
        
        is_in_field = i in grade_map
        is_tonic = (major_note == root)
        
        # Determinar color y estilo según grado
        if is_tonic:
            color = GRADE_COLORS['I']
            alpha = 1.0
            radius = 1.0
            lw = 4
        elif is_in_field:
            grade_name = grade_map[i][0]
            color = GRADE_COLORS[grade_name]
            alpha = 0.9
            radius = 0.95
            lw = 3
        else:
            color = '#334155'
            alpha = 0.15
            radius = 0.9
            lw = 1
        
        zorder = 10 if is_in_field else 1
        
        # Sector exterior (Mayor)
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=lw, zorder=zorder)
        ax.add_patch(wedge)
        
        # Sector interior (Menor)
        wedge_inner = Wedge((0, 0), 0.6, np.degrees(angle - np.pi/12), 
                           np.degrees(angle + np.pi/12), 
                           facecolor=color, alpha=alpha*0.7, edgecolor='white', linewidth=lw, zorder=zorder)
        ax.add_patch(wedge_inner)
        
        # NOTA MAYOR (exterior)
        x_maj = 0.8 * np.cos(angle)
        y_maj = 0.8 * np.sin(angle)
        
        circle_bg = Circle((x_maj, y_maj), 0.14 if is_in_field else 0.10, 
                          facecolor=color, edgecolor='white', linewidth=2, zorder=zorder+1)
        ax.add_patch(circle_bg)
        
        ax.text(x_maj, y_maj, major_note, ha='center', va='center', 
               fontsize=18 if is_in_field else 11, 
               fontweight='bold' if is_in_field else 'normal',
               color='white', zorder=zorder+2)
        
        # ARMADURA (cantidad de alteraciones) - arriba de la nota
        num_alt, tipo_alt = KEY_SIGS[major_note]
        if num_alt > 0 or major_note == 'C':
            x_sig = 1.18 * np.cos(angle)
            y_sig = 1.18 * np.sin(angle)
            symbol = '♯' if tipo_alt == '#' else '♭' if tipo_alt == 'b' else ''
            text_sig = f"{num_alt}{symbol}" if num_alt > 0 else "0"
            
            color_sig = '#FFD60A' if is_in_field else '#64748b'
            weight = 'bold' if is_in_field else 'normal'
            size_sig = 13 if is_in_field else 10
            
            ax.text(x_sig, y_sig, text_sig, ha='center', va='center',
                   fontsize=size_sig, color=color_sig, fontweight=weight, 
                   bbox=dict(boxstyle='round,pad=0.3', 
                            facecolor='#1e293b' if is_in_field else 'none', 
                            edgecolor=color_sig if is_in_field else 'none', 
                            alpha=0.9), zorder=15)
        
        # NOTA MENOR (interior)
        x_min = 0.35 * np.cos(angle)
        y_min = 0.35 * np.sin(angle)
        
        if is_in_field:
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white', zorder=zorder+2,
                   bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f172a', 
                            edgecolor='white', linewidth=1.5, alpha=0.9))
        else:
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=9, color='#64748b', alpha=0.4)
        
        # GRADO ROMANO (entre anillos, como la imagen)
        if is_in_field:
            grade_name, quality, _ = grade_map[i]
            x_grade = 0.58 * np.cos(angle)
            y_grade = 0.58 * np.sin(angle)
            
            # Formato: I, ii, iii, IV, V, vi, vii°
            if quality == 'Disminuido':
                display_grade = 'vii°'
            elif quality == 'Menor':
                display_grade = grade_name.lower()
            else:
                display_grade = grade_name
            
            ax.text(x_grade, y_grade, display_grade, ha='center', va='center',
                   fontsize=15, fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.25', facecolor='#0f172a', 
                            edgecolor=color, linewidth=2.5), zorder=zorder+3)
        
        # Líneas divisorias
        for r_line in [0.6, 1.0]:
            x_line = r_line * np.cos(angle + np.pi/12)
            y_line = r_line * np.sin(angle + np.pi/12)
            ax.plot([0, x_line], [0, y_line], color='white', linewidth=1, alpha=0.2, zorder=0)
    
    # Centro
    center_bg = Circle((0, 0), 0.22, facecolor=GRADE_COLORS['I'], 
                      edgecolor='white', linewidth=4, zorder=20)
    ax.add_patch(center_bg)
    ax.text(0, 0.02, root, ha='center', va='center', fontsize=26, 
           fontweight='bold', color='white', zorder=21)
    ax.text(0, -0.12, 'I', ha='center', va='center', fontsize=14, 
           color='white', alpha=0.9, zorder=21)

def draw_fretboard(ax, root, chord_type_name):
    """Diapasón con 22 trastes"""
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
    
    # Notas del acorde
    if chord_type_name in CHORD_TYPES:
        intervals = CHORD_TYPES[chord_type_name]['intervals']
        root_idx = note_to_num[root]
        notes = get_preferred_notes(root)
        
        for string in range(num_strings):
            for fret in range(num_frets + 1):
                open_note = TUNING[string]
                open_idx = note_to_num[open_note]
                current_idx = (open_idx + fret) % 12
                
                for i, interval in enumerate(intervals):
                    if (root_idx + interval) % 12 == current_idx:
                        colors = ['#FF4757', '#3742FA', '#2ED573', '#FFD93D']
                        color = colors[i % 4]
                        
                        circle = Circle((fret, string), 0.28, facecolor=color, 
                                      edgecolor='white', linewidth=2, zorder=5)
                        ax.add_patch(circle)
                        
                        note_name = notes[current_idx]
                        ax.text(fret, string, note_name, ha='center', va='center', 
                               fontsize=8, fontweight='bold', color='white', zorder=6)
                        
                        if interval != 0:
                            ax.text(fret, string - 0.35, str(interval), 
                                   ha='center', va='center', fontsize=7, 
                                   color=color, fontweight='bold', zorder=6)
                        break
    
    ax.set_xlim(-0.5, num_frets + 0.5)
    ax.set_ylim(-0.5, num_strings - 0.5)
    ax.set_yticks(range(num_strings))
    ax.set_yticklabels(TUNING[::-1], fontsize=11, fontweight='bold', color='white')
    ax.set_xticks(range(0, num_frets + 1, 2))
    ax.set_xticklabels(range(0, num_frets + 1, 2), fontsize=9, color='white')
    ax.set_xlabel('Número de Traste', fontsize=12, fontweight='bold', color='white')
    ax.invert_yaxis()
    
    # Afinación
    for i, note in enumerate(TUNING[::-1]):
        ax.text(-0.8, i, note, fontsize=11, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))

# ============================================
# INTERFAZ CON PESTAÑAS COMPLETA
# ============================================
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    root_note = st.selectbox("🎵 Tonalidad:", CIRCLE_MAJOR, index=0)
with col2:
    chord_type = st.selectbox("🎸 Tipo de Acorde:", list(CHORD_TYPES.keys()), index=0)
with col3:
    sig_num, sig_type = KEY_SIGS[root_note]
    sig_display = f"{sig_num} {sig_type}" if sig_num > 0 else "Natural"
    sig_symbol = '♯' if sig_type == '#' else '♭' if sig_type == 'b' else ''
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; text-align: center;">
        <h2 style="color: white; margin: 0; font-size: 32px;">{root_note}</h2>
        <p style="color: #FFD93D; font-size: 20px; margin: 10px 0; font-weight: bold;">
            {sig_display.replace('#', '♯').replace('b', '♭')}
        </p>
        <p style="color: white; font-size: 14px; margin: 0;">
            Fórmula: {CHORD_TYPES[chord_type]['formula']}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# PESTAÑAS COMPLETAS
tab1, tab2, tab3, tab4 = st.tabs(["🔄 Círculo de Quintas", "🎹 Campo Armónico", 
                                  "🎸 Acordes e Inversiones", "🎸 Diapasón"])

with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        fig, ax = plt.subplots(figsize=(12, 12))
        fig.patch.set_facecolor('#0f172a')
        draw_study_circle(ax, root_note)
        st.pyplot(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Campo Armónico en el Círculo")
        grade_map = get_harmonic_field_grades(root_note)
        
        # Mostrar grados ordenados
        order_display = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii']
        for grade in order_display:
            for pos, (g, q, note) in grade_map.items():
                if g == grade:
                    color = GRADE_COLORS[grade]
                    display = 'vii°' if grade == 'vii' else (grade.lower() if q == 'Menor' else grade)
                    armadura = KEY_SIGS[note]
                    arm_text = f"{armadura[0]}{'♯' if armadura[1] == '#' else '♭' if armadura[1] == 'b' else ''}"
                    
                    st.markdown(f"""
                    <div style="background-color: {color}22; border-left: 5px solid {color}; 
                                padding: 15px; margin: 10px 0; border-radius: 0 10px 10px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: {color}; font-size: 28px; font-weight: bold;">{display}</span>
                                <span style="color: white; font-size: 18px; margin-left: 10px;">{note}</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="color: #FFD93D; font-size: 16px; font-weight: bold;">{arm_text}</span>
                                <br>
                                <span style="color: #94a3b8; font-size: 12px;">{q}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    break
        
        # Leyenda funcional
        st.markdown("---")
        st.subheader("Funciones")
        funciones = {
            'I': 'Tónica', 'ii': 'Supertónica', 'iii': 'Mediante',
            'IV': 'Subdominante', 'V': 'Dominante', 
            'vi': 'Submediante', 'vii°': 'Sensible'
        }
        for grado, nombre in funciones.items():
            color = GRADE_COLORS[grado.replace('°', '')]
            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{grado}</span> - {nombre}", unsafe_allow_html=True)

with tab2:
    st.subheader(f"Campo Armónico Detallado de {root_note} Mayor")
    harmonic = get_harmonic_field_full(root_note)
    
    cols = st.columns(7)
    for col, (degree, info) in zip(cols, harmonic.items()):
        with col:
            color = info['color']
            notes_str = ' - '.join(info['notes'])
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}33 0%, {color}66 100%); 
                        border: 3px solid {color}; border-radius: 15px; padding: 15px; text-align: center; height: 100%;">
                <h1 style="color: {color}; margin: 0; font-size: 42px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{degree}</h1>
                <h3 style="color: white; margin: 10px 0; font-size: 24px;">{info['root']}</h3>
                <p style="color: #aaa; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">{info['quality']}</p>
                <hr style="border-color: {color}; margin: 15px 0;">
                <p style="color: #4ECDC4; font-family: monospace; font-size: 16px; font-weight: bold;">{info['formula']}</p>
                <p style="color: white; font-size: 18px; margin-top: 10px; letter-spacing: 2px;">{notes_str}</p>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader(f"Inversiones del Acorde: {root_note} {CHORD_TYPES[chord_type]['type']}")
    
    inversions = get_inversions(root_note, chord_type)
    
    if inversions:
        cols = st.columns(len(inversions))
        
        for col, (inv_name, notes) in zip(cols, inversions.items()):
            with col:
                st.markdown(f"""
                <div style="background-color: #1e293b; border-radius: 15px; 
                            padding: 20px; text-align: center; border: 2px solid #4ECDC4; height: 100%;">
                    <h4 style="color: #4ECDC4; margin-bottom: 20px; font-size: 16px;">{inv_name}</h4>
                """, unsafe_allow_html=True)
                
                # Visualización apilada de notas
                for i, note in enumerate(notes):
                    colors = ['#E63946', '#457B9D', '#2A9D8F', '#F4A261']
                    bg_color = colors[i % 4]
                    st.markdown(f"""
                    <div style="background-color: {bg_color}; color: white; padding: 15px; 
                                margin: 8px 0; border-radius: 8px; font-size: 24px; 
                                font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                        {note}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Indicar el bajo
                st.markdown(f"""
                    <p style="color: #64748b; margin-top: 15px; font-size: 14px;">
                        Bajo: <b style="color: {colors[0]}; font-size: 18px;">{notes[0]}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Análisis de intervalos
    st.markdown("---")
    st.subheader("Análisis Intervalístico")
    
    intervals = CHORD_TYPES[chord_type]['intervals']
    notes_list = get_chord_notes(root_note, chord_type)
    
    cols_int = st.columns(len(intervals))
    for col, interval, note in zip(cols_int, intervals, notes_list):
        with col:
            colors = ['#E63946', '#457B9D', '#2A9D8F', '#F4A261']
            color = colors[intervals.index(interval) % 4]
            interval_names = {0: 'Raíz', 3: '3ª menor', 4: '3ª Mayor', 5: '4ª', 
                            6: '5ª dism', 7: '5ª Justa', 8: '5ª Aum', 
                            9: '6ª', 10: '7ª menor', 11: '7ª Mayor'}
            int_name = interval_names.get(interval, f'+{interval}')
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; 
                        background-color: {color}22; border-radius: 10px;
                        border: 2px solid {color};">
                <h1 style="color: {color}; margin: 0; font-size: 36px;">{note}</h1>
                <p style="color: white; font-size: 14px; margin: 5px 0;">{int_name}</p>
                <p style="color: {color}; font-size: 20px; font-weight: bold; margin: 0;">+{interval}</p>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.subheader("Visualización en Diapasón de Guitarra (22 Trastes)")
    
    fig, ax = plt.subplots(figsize=(18, 6))
    draw_fretboard(ax, root_note, chord_type)
    st.pyplot(fig, use_container_width=True)
    
    # Leyenda
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px; flex-wrap: wrap;">
        <div style="text-align: center;">
            <span style="background-color: #FF4757; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold; display: inline-block;">1 Raíz</span>
        </div>
        <div style="text-align: center;">
            <span style="background-color: #3742FA; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold; display: inline-block;">3 Tercera</span>
        </div>
        <div style="text-align: center;">
            <span style="background-color: #2ED573; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold; display: inline-block;">5 Quinta</span>
        </div>
        <div style="text-align: center;">
            <span style="background-color: #FFD93D; padding: 10px 20px; border-radius: 20px; color: black; font-weight: bold; display: inline-block;">7 Séptima</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<center><h4>Campo Armónico Completo: {' - '.join([get_harmonic_field_full(root_note)[d]['root'] + ('' if get_harmonic_field_full(root_note)[d]['quality'] == 'Mayor' else 'm' if get_harmonic_field_full(root_note)[d]['quality'] == 'Menor' else '°') for d in ['I','ii','iii','IV','V','vi','vii']])}</h4></center>", unsafe_allow_html=True)
