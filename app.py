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
        'Estado Fundamental': notes,
        '1ra Inversión': notes[1:] + [notes[0]],
        '2da Inversión': notes[2:] + notes[:2]
    }
    if len(notes) == 4:
        inversions['3ra Inversión'] = [notes[3]] + notes[:3]
    return inversions

def get_harmonic_field_full(root):
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
        
        ax.text(x_m
