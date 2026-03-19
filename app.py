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
        background-color: #1e293b; border-radius: 8px 8px 0 0;
        padding: 15px 25px; font-weight: bold; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #E94560 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Visualizador Profesional: Círculo de Quintas, Campo Armónico y Acordes")
st.markdown("---")

# CONFIGURACIÓN MUSICAL
notes_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
note_to_num = {note: i for i, note in enumerate(notes_sharp)}

def get_preferred_notes(root):
    flat_roots = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return notes_flat if root in flat_roots else notes_sharp

CIRCLE_MAJOR = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
CIRCLE_MINOR = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

KEY_SIGS = {
    'C': (0, ''), 'G': (1, '#'), 'D': (2, '#'), 'A': (3, '#'),
    'E': (4, '#'), 'B': (5, '#'), 'F#': (6, '#'), 'C#': (7, '#'),
    'Ab': (4, 'b'), 'Eb': (3, 'b'), 'Bb': (2, 'b'), 'F': (1, 'b')
}

GRADE_COLORS = {
    'I': '#E63946', 'ii': '#FB8500', 'iii': '#FFB703',
    'IV': '#F72585', 'V': '#F4A261', 'vi': '#FFD60A', 'vii': '#2ECC71'
}

CHORD_TYPES = {
    'Triada Mayor': {'intervals': [0, 4, 7], 'formula': '1 - 3 - 5', 'type': 'Mayor'},
    'Triada Menor': {'intervals': [0, 3, 7], 'formula': '1 - b3 - 5', 'type': 'Menor'},
    'Triada Disminuida': {'intervals': [0, 3, 6], 'formula': '1 - b3 - b5', 'type': 'Disminuido'},
    'Mayor 7 (Maj7)': {'intervals': [0, 4, 7, 11], 'formula': '1 - 3 - 5 - 7', 'type': 'Maj7'},
    'Menor 7 (m7)': {'intervals': [0, 3, 7, 10], 'formula': '1 - b3 - 5 - b7', 'type': 'm7'},
    'Dominante 7 (7)': {'intervals': [0, 4, 7, 10], 'formula': '1 - 3 - 5 - b7', 'type': '7'},
}

TUNING = ['E', 'B', 'G', 'D', 'A', 'E']

def get_harmonic_field_grades(root):
    idx = CIRCLE_MAJOR.index(root)
    grade_map = {}
    grade_map[idx] = ('I', 'Mayor', CIRCLE_MAJOR[idx])
    grade_map[(idx + 1) % 12] = ('V', 'Mayor', CIRCLE_MAJOR[(idx + 1) % 12])
    grade_map[(idx - 1) % 12] = ('IV', 'Mayor', CIRCLE_MAJOR[(idx - 1) % 12])
    grade_map[(idx + 2) % 12] = ('ii', 'Menor', CIRCLE_MAJOR[(idx + 2) % 12])
    grade_map[(idx - 2) % 12] = ('vi', 'Menor', CIRCLE_MAJOR[(idx - 2) % 12])
    grade_map[(idx + 3) % 12] = ('iii', 'Menor', CIRCLE_MAJOR[(idx + 3) % 12])
    grade_map[(idx + 4) % 12] = ('vii', 'Disminuido', CIRCLE_MAJOR[(idx + 4) % 12])
    return grade_map

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

def draw_study_circle(ax, root):
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0f172a')
    
    grade_map = get_harmonic_field_grades(root)
    sig_num, sig_type = KEY_SIGS[root]
    sig_text = f"({sig_num} {sig_type})" if sig_num > 0 else "(Natural)"
    ax.set_title(f'Círculo de Quintas: {root} Mayor {sig_text}', 
                color='white', fontsize=20, fontweight='bold', pad=30)
    
    for r in [0.6, 1.0]:
        circle = Circle((0, 0), r, fill=False, edgecolor='#475569', linewidth=2, alpha=0.3)
        ax.add_patch(circle)
    
    for i, (major_note, minor_note) in enumerate(zip(CIRCLE_MAJOR, CIRCLE_MINOR)):
        angle = np.pi/2 - i * (2*np.pi/12)
        
        is_in_field = i in grade_map
        is_tonic = (major_note == root)
        
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
        
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=lw, zorder=zorder)
        ax.add_patch(wedge)
        
        wedge_inner = Wedge((0, 0), 0.6, np.degrees(angle - np.pi/12), 
                           np.degrees(angle + np.pi/12), 
                           facecolor=color, alpha=alpha*0.7, edgecolor='white', linewidth=lw, zorder=zorder)
        ax.add_patch(wedge_inner)
        
        x_maj = 0.8 * np.cos(angle)
        y_maj = 0.8 * np.sin(angle)
        
        circle_bg = Circle((x_maj, y_maj), 0.14 if is_in_field else 0.10, 
                          facecolor=color, edgecolor='white', linewidth=2, zorder=zorder+1)
        ax.add_patch(circle_bg)
        
        ax.text(x_maj, y_maj, major_note, ha='center', va='center', 
               fontsize=18 if is_in_field else 11, 
               fontweight='bold' if is_in_field else 'normal',
               color='white', zorder=zorder+2)
        
        num_alt, tipo_alt = KEY_SIGS[major_note]
        if num_alt > 0 or major_note == 'C':
            x_sig = 1.15 * np.cos(angle)
            y_sig = 1.15 * np.sin(angle)
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
        
        if is_in_field:
            grade_name, quality, _ = grade_map[i]
            x_grade = 0.58 * np.cos(angle)
            y_grade = 0.58 * np.sin(angle)
            
            if quality == 'Disminuido':
                display_grade = 'vii°'
            elif quality == 'Menor':
                display_grade = grade_name
            else:
                display_grade = grade_name
            
            ax.text(x_grade, y_grade, display_grade, ha='center', va='center',
                   fontsize=15, fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.25', facecolor='#0f172a', 
                            edgecolor=color, linewidth=2.5), zorder=zorder+3)
        
        x_line_out = 1.0 * np.cos(angle + np.pi/12)
        y_line_out = 1.0 * np.sin(angle + np.pi/12)
        x_line_in = 0.6 * np.cos(angle + np.pi/12)
        y_line_in = 0.6 * np.sin(angle + np.pi/12)
        ax.plot([x_line_in, x_line_out], [y_line_in, y_line_out], 
               color='white', linewidth=1, alpha=0.3, zorder=0)
    
    center_bg = Circle((0, 0), 0.22, facecolor=GRADE_COLORS['I'], 
                      edgecolor='white', linewidth=4, zorder=20)
    ax.add_patch(center_bg)
    ax.text(0, 0.02, root, ha='center', va='center', fontsize=26, 
           fontweight='bold', color='white', zorder=21)
    ax.text(0, -0.12, 'I', ha='center', va='center', fontsize=14, 
           color='white', alpha=0.9, zorder=21)

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
    
    for i, note in enumerate(TUNING[::-1]):
        ax.text(-0.8, i, note, fontsize=11, ha='center', va='center', 
               fontweight='bold', color='#FFD700',
               bbox=dict(boxstyle='circle', facecolor='#37474F', edgecolor='#FFD700'))

# INTERFAZ
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    root_note = st.selectbox("🎵 Tonalidad:", CIRCLE_MAJOR, index=0)
with col2:
    chord_type = st.selectbox("🎸 Tipo de Acorde:", list(CHORD_TYPES.keys()), index=0)
with col3:
    sig_num, sig_type = KEY_SIGS[root_note]
    sig_display = f"{sig_num} {sig_type}" if sig_num > 0 else "Natural"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; text-align: center;">
        <h2 style="color: white; margin: 0; font-size: 32px;">{root_note}</h2>
        <p style="color: #FFD93D; font-size: 20px; margin: 10px 0; font-weight: bold;">
            {sig_display.replace('#', '♯').replace('b', '♭')}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🔄 Círculo de Quintas", "🎸 Inversiones", "🎸 Diapasón"])

with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        fig, ax = plt.subplots(figsize=(12, 12))
        fig.patch.set_facecolor('#0f172a')
        draw_study_circle(ax, root_note)
        st.pyplot(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Campo Armónico")
        grade_map = get_harmonic_field_grades(root_note)
        
        for grade in ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii']:
            for pos, (g, q, note) in grade_map.items():
                if g == grade:
                    color = GRADE_COLORS[grade]
                    display = 'vii°' if grade == 'vii' else grade
                    st.markdown(f"<h3 style='color: {color};'>{display} - {note}</h3>", unsafe_allow_html=True)

with tab2:
    st.subheader(f"Inversiones de {root_note}")
    inversions = get_inversions(root_note, chord_type)
    
    if inversions:
        cols = st.columns(len(inversions))
        for col, (name, notes) in zip(cols, inversions.items()):
            with col:
                st.markdown(f"**{name}**")
                for note in notes:
                    st.markdown(f"<h4>{note}</h4>", unsafe_allow_html=True)

with tab3:
    fig, ax = plt.subplots(figsize=(18, 6))
    draw_fretboard(ax, root_note, chord_type)
    st.pyplot(fig, use_container_width=True)
