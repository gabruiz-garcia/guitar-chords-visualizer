import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, Rectangle
import numpy as np

st.set_page_config(page_title="Visualizador Profesional de Acordes", 
                   page_icon="🎸", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    h1 { color: #E94560 !important; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 15px 25px;
        font-weight: bold;
        color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #E94560 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador Profesional: Acordes, Escalas y Campo Armónico")
st.markdown("---")

# Configuración musical
notes_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
note_to_num = {note: i for i, note in enumerate(notes_sharp)}

def get_preferred_notes(root):
    flat_roots = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb', 'Gb']
    return notes_flat if root in flat_roots else notes_sharp

# Círculo de quintas TRADICIONAL (sentido horario: quintas ascendentes)
# Posiciones fijas en el círculo
CIRCLE_MAJOR = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
CIRCLE_MINOR = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

# Armaduras (cantidad de alteraciones)
KEY_SIGNATURES = {
    'C': ('0', 'natural'), 'G': ('1', '#'), 'D': ('2', '#'), 'A': ('3', '#'),
    'E': ('4', '#'), 'B': ('5', '#'), 'F#': ('6', '#'), 'C#': ('7', '#'),
    'Ab': ('4', 'b'), 'Eb': ('3', 'b'), 'Bb': ('2', 'b'), 'F': ('1', 'b')
}

GRADE_COLORS = {
    'I': '#FF4757', 'II': '#FF8C42', 'III': '#FFD93D',
    'IV': '#6BCB77', 'V': '#4D96FF', 'VI': '#9B59B6', 'VII': '#B8B8B8'
}

CHORD_TYPES = {
    'Triada Mayor': {'intervals': [0, 4, 7], 'formula': '1 - 3 - 5', 'type': 'Mayor'},
    'Triada Menor': {'intervals': [0, 3, 7], 'formula': '1 - b3 - 5', 'type': 'Menor'},
    'Triada Disminuida': {'intervals': [0, 3, 6], 'formula': '1 - b3 - b5', 'type': 'Disminuido'},
    'Triada Aumentada': {'intervals': [0, 4, 8], 'formula': '1 - 3 - #5', 'type': 'Aumentado'},
    'Mayor 7 (Maj7)': {'intervals': [0, 4, 7, 11], 'formula': '1 - 3 - 5 - 7', 'type': 'Maj7'},
    'Dominante 7 (7)': {'intervals': [0, 4, 7, 10], 'formula': '1 - 3 - 5 - b7', 'type': '7'},
    'Menor 7 (m7)': {'intervals': [0, 3, 7, 10], 'formula': '1 - b3 - 5 - b7', 'type': 'm7'},
    'Semi-disminuido (m7b5)': {'intervals': [0, 3, 6, 10], 'formula': '1 - b3 - b5 - b7', 'type': 'ø7'},
    'Disminuido 7 (dim7)': {'intervals': [0, 3, 6, 9], 'formula': '1 - b3 - b5 - bb7', 'type': 'dim7'},
    'Sus4': {'intervals': [0, 5, 7], 'formula': '1 - 4 - 5', 'type': 'Sus4'},
    'Sus2': {'intervals': [0, 2, 7], 'formula': '1 - 2 - 5', 'type': 'Sus2'},
}

TUNING = ['E', 'B', 'G', 'D', 'A', 'E']

def get_scale_notes(root):
    notes = get_preferred_notes(root)
    root_idx = note_to_num[root] if root in note_to_num else notes_sharp.index(root)
    intervals = [0, 2, 4, 5, 7, 9, 11]
    return [(notes[(root_idx + i) % 12], i) for i in intervals]

def get_harmonic_field(root):
    scale = get_scale_notes(root)
    harmonic = {}
    chord_defs = [
        ('I', 'Mayor'), ('II', 'Menor'), ('III', 'Menor'),
        ('IV', 'Mayor'), ('V', 'Mayor'), ('VI', 'Menor'), ('VII', 'Disminuido')
    ]
    for i, (degree, quality) in enumerate(chord_defs):
        note = scale[i][0]
        harmonic[degree] = {
            'root': note,
            'quality': quality,
            'color': GRADE_COLORS[degree]
        }
    return harmonic

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
        'Estado Fundamental': notes,
        '1ra Inversión': notes[1:] + [notes[0]],
        '2da Inversión': notes[2:] + notes[:2]
    }
    if len(notes) == 4:
        inversions['3ra Inversión'] = [notes[3]] + notes[:3]
    return inversions

def draw_traditional_circle(ax, root):
    """Dibuja el círculo de quintas tradicional: mayores afuera, menores adentro"""
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0f172a')
    
    # Obtener información de armadura
    sig_info = KEY_SIGNATURES.get(root, ('0', 'natural'))
    num_acc, acc_type = sig_info
    
    # Título con armadura
    title_suffix = f"({num_acc} {acc_type})" if acc_type != 'natural' else "(Sin alteraciones)"
    ax.set_title(f'Círculo de Quintas: {root} Mayor {title_suffix}', 
                color='white', fontsize=18, fontweight='bold', pad=20)
    
    harmonic = get_harmonic_field(root)
    harmonic_notes = {info['root'] for info in harmonic.values()}
    
    # Dibujar anillos completos primero (fondo)
    outer_circle = Circle((0, 0), 1.0, fill=False, edgecolor='#475569', linewidth=2, alpha=0.3)
    ax.add_patch(outer_circle)
    inner_circle = Circle((0, 0), 0.6, fill=False, edgecolor='#475569', linewidth=2, alpha=0.3)
    ax.add_patch(inner_circle)
    
    # Dibujar sectores y notas
    for i, (major_note, minor_note) in enumerate(zip(CIRCLE_MAJOR, CIRCLE_MINOR)):
        angle = np.pi/2 - i * (2*np.pi/12)  # Empezar desde arriba
        
        # Determinar si está en el campo armónico
        is_in_harmonic = major_note in harmonic_notes
        is_tonic = (major_note == root)
        
        # Color según función o atenuado
        if is_tonic:
            color = GRADE_COLORS['I']
            alpha = 1.0
            radius = 1.0
            linewidth = 4
            text_size = 18
            zorder = 10
        elif is_in_harmonic:
            # Buscar qué grado es
            for deg, info in harmonic.items():
                if info['root'] == major_note:
                    color = info['color']
                    break
            alpha = 0.9
            radius = 0.95
            linewidth = 3
            text_size = 16
            zorder = 5
        else:
            color = '#475569'
            alpha = 0.3
            radius = 0.9
            linewidth = 1
            text_size = 12
            zorder = 1
        
        # Sector exterior (Mayor)
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=linewidth, zorder=zorder)
        ax.add_patch(wedge)
        
        # Nota Mayor (exterior)
        x_maj = 0.8 * np.cos(angle)
        y_maj = 0.8 * np.sin(angle)
        
        # Círculo de fondo para la nota
        note_bg = Circle((x_maj, y_maj), 0.12 if is_tonic else 0.10, 
                        facecolor=color, edgecolor='white', linewidth=2, zorder=zorder+1)
        ax.add_patch(note_bg)
        
        ax.text(x_maj, y_maj, major_note, ha='center', va='center', 
               fontsize=text_size, fontweight='bold' if is_in_harmonic else 'normal',
               color='white', zorder=zorder+2)
        
        # Mostrar cantidad de alteraciones arriba de la nota mayor
        if major_note in KEY_SIGNATURES:
            num_alt, tipo_alt = KEY_SIGNATURES[major_note]
            if num_alt != '0':
                x_alt = 1.15 * np.cos(angle)
                y_alt = 1.15 * np.sin(angle)
                symbol = '♯' if tipo_alt == '#' else '♭'
                ax.text(x_alt, y_alt, f"{num_alt}{symbol}", ha='center', va='center',
                       fontsize=11, color='#FFD93D' if is_in_harmonic else '#64748b', 
                       fontweight='bold', alpha=1.0 if is_in_harmonic else 0.4)
        
        # Sector interior (Menor)
        if is_in_harmonic:
            # Buscar el relativo menor del grado
            rel_minor = None
            for deg, info in harmonic.items():
                if info['root'] == major_note:
                    rel_minor = minor_note
                    break
            alpha_min = 0.7
            color_min = color
            linewidth_min = 2
        else:
            alpha_min = 0.2
            color_min = '#475569'
            linewidth_min = 1
        
        wedge_min = Wedge((0, 0), 0.6, np.degrees(angle - np.pi/12), 
                         np.degrees(angle + np.pi/12), 
                         facecolor=color_min, alpha=alpha_min, edgecolor='white', 
                         linewidth=linewidth_min)
        ax.add_patch(wedge_min)
        
        # Nota Menor (interior)
        x_min = 0.35 * np.cos(angle)
        y_min = 0.35 * np.sin(angle)
        
        if is_in_harmonic:
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.2', facecolor=color_min, 
                            edgecolor='white', linewidth=1.5))
        else:
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=9, color='#64748b', alpha=0.5)
        
        # Líneas de división
        x_line_outer = 1.0 * np.cos(angle + np.pi/12)
        y_line_outer = 1.0 * np.sin(angle + np.pi/12)
        x_line_inner = 0.6 * np.cos(angle + np.pi/12)
        y_line_inner = 0.6 * np.sin(angle + np.pi/12)
        ax.plot([x_line_inner, x_line_outer], [y_line_inner, y_line_outer], 
               'w-', linewidth=1, alpha=0.3)
    
    # Círculo central
    center_bg = Circle((0, 0), 0.25, facecolor=GRADE_COLORS['I'], 
                      edgecolor='white', linewidth=4, zorder=20)
    ax.add_patch(center_bg)
    ax.text(0, 0, root, ha='center', va='center', fontsize=24, 
           fontweight='bold', color='white', zorder=21)
    
    # Indicar relativo menor en el centro también
    relative_minor_idx = (note_to_num[root] + 9) % 12  # Sexta menor = tónica - 3 semitonos
    # Buscar el nombre correcto del relativo menor
    rel_minor_name = CIRCLE_MINOR[CIRCLE_MAJOR.index(root)]
    ax.text(0, -0.12, f"↔ {rel_minor_name}", ha='center', va='center', 
           fontsize=10, color='white', alpha=0.8, zorder=21)

def draw_fretboard(ax, root, chord_type_name):
    ax.set_facecolor('#263238')
    num_frets = 22
    num_strings = 6
    
    ax.add_patch(Rectangle((-0.5, -0.5), num_frets + 1.5, num_strings, 
                          facecolor='#3E2723', alpha=0.8))
    
    for fret in range(num_frets + 2):
        x = fret
        color = '#FFD700' if fret in [3, 5, 7, 9, 12, 15, 17, 19, 21] else '#B0BEC5'
        width = 3 if fret in [3, 5, 7, 9, 12, 15, 17, 19, 21] else 1.5
        ax.axvline(x=x, color=color, linewidth=width, alpha=0.8)
    
    for string in range(num_strings):
        y = string
        width = 4 - (string * 0.5)
        ax.axhline(y=y, color='#ECEFF1', linewidth=width, alpha=0.9)
    
    ax.plot([12], [2.5], "wo", markersize=8)
    ax.plot([12], [3.5], "wo", markersize=8)
    
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
    
    for i, note in enumerate(TUNING[::-1]):
        ax.text(-0.8, i, note, fontsize=11, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))

# Interfaz principal
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    root_note = st.selectbox("🎵 Tonalidad:", CIRCLE_MAJOR, index=0)
with col2:
    chord_type = st.selectbox("🎸 Tipo de Acorde:", list(CHORD_TYPES.keys()), index=0)
with col3:
    sig_num, sig_type = KEY_SIGNATURES.get(root_note, ('0', 'natural'))
    sig_symbol = '♯' if sig_type == '#' else '♭' if sig_type == 'b' else ''
    st.markdown(f"### {root_note} Mayor")
    st.markdown(f"**Armadura:** {sig_num} {sig_symbol}" if sig_symbol else "**Armadura:** Natural")
    st.markdown(f"**Fórmula:** {CHORD_TYPES[chord_type]['formula']}")

st.markdown("---")

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["🔄 Círculo de Quintas", "🎹 Campo Armónico", 
                                  "🎸 Acordes e Inversiones", "🎸 Diapasón"])

with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        fig, ax = plt.subplots(figsize=(12, 12))
        fig.patch.set_facecolor('#0f172a')
        draw_traditional_circle(ax, root_note)
        st.pyplot(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Armaduras de Clave")
        
        st.markdown("""
        <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="color: #E94560; margin-top: 0;">Sostenidos (♯)</h4>
            <p style="color: white; font-size: 16px; line-height: 2;">
        """, unsafe_allow_html=True)
        
        sharps = [k for k, v in KEY_SIGNATURES.items() if v[1] == '#']
        sharps.sort(key=lambda x: int(KEY_SIGNATURES[x][0]))
        for note in sharps:
            num, _ = KEY_SIGNATURES[note]
            is_selected = (note == root_note)
            color = '#FFD93D' if is_selected else '#64748b'
            st.markdown(f"<span style='color: {color}; font-size: 18px; font-weight: {'bold' if is_selected else 'normal'};'>{note}: {num}♯</span>", unsafe_allow_html=True)
        
        st.markdown("</p></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #1e293b; padding: 20px; border-radius: 10px;">
            <h4 style="color: #4ECDC4; margin-top: 0;">Bemoles (♭)</h4>
            <p style="color: white; font-size: 16px; line-height: 2;">
        """, unsafe_allow_html=True)
        
        flats = [k for k, v in KEY_SIGNATURES.items() if v[1] == 'b']
        flats.sort(key=lambda x: int(KEY_SIGNATURES[x][0]), reverse=True)
        for note in flats:
            num, _ = KEY_SIGNATURES[note]
            is_selected = (note == root_note)
            color = '#FFD93D' if is_selected else '#64748b'
            st.markdown(f"<span style='color: {color}; font-size: 18px; font-weight: {'bold' if is_selected else 'normal'};'>{note}: {num}♭</span>", unsafe_allow_html=True)
        
        st.markdown("</p></div>", unsafe_allow_html=True)
        
        # Relativo menor
        rel_minor = CIRCLE_MINOR[CIRCLE_MAJOR.index(root_note)]
        st.markdown(f"""
        <div style="background-color: #263238; padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center;">
            <p style="color: #94a3b8; margin: 0;">Relativo Menor</p>
            <h2 style="color: #9B59B6; margin: 5px 0;">{rel_minor}</h2>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader(f"Campo Armónico de {root_note} Mayor")
    harmonic = get_harmonic_field(root_note)
    
    cols = st.columns(7)
    for col, (degree, info) in zip(cols, harmonic.items()):
        with col:
            color = info['color']
            chord_notes_list = get_chord_notes(info['root'], 'Triada Mayor' if info['quality'] == 'Mayor' else 'Triada Menor' if info['quality'] == 'Menor' else 'Triada Disminuida')
            notes_str = ' - '.join(chord_notes_list)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                        border: 3px solid {color}; border-radius: 15px; padding: 15px; text-align: center;">
                <h1 style="color: {color}; margin: 0; font-size: 42px;">{degree}</h1>
                <h3 style="color: white; margin: 10px 0;">{info['root']}</h3>
                <p style="color: #aaa; font-size: 14px;">{info['quality']}</p>
                <hr style="border-color: {color}; margin: 10px 0;">
                <p style="color: #4ECDC4; font-family: monospace; font-size: 16px;">{notes_str}</p>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader(f"Inversiones: {root_note} {CHORD_TYPES[chord_type]['type']}")
    inversions = get_inversions(root_note, chord_type)
    
    if inversions:
        cols = st.columns(len(inversions))
        for col, (inv_name, notes) in zip(cols, inversions.items()):
            with col:
                st.markdown(f"<h4 style='text-align: center; color: #4ECDC4;'>{inv_name}</h4>", unsafe_allow_html=True)
                for i, note in enumerate(notes):
                    colors = ['#FF4757', '#3742FA', '#2ED573', '#FFD93D']
                    st.markdown(f"""
                    <div style="background-color: {colors[i]}; color: white; padding: 20px; 
                                margin: 10px 0; border-radius: 10px; text-align: center;
                                font-size: 28px; font-weight: bold;">
                        {note}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #64748b;'>Bajo: {notes[0]}</p>", unsafe_allow_html=True)

with tab4:
    fig, ax = plt.subplots(figsize=(18, 6))
    draw_fretboard(ax, root_note, chord_type)
    st.pyplot(fig, use_container_width=True)

st.markdown("---")
st.markdown("<center><h4>Desarrollado para Estudio Musical Profesional</h4></center>", unsafe_allow_html=True)
