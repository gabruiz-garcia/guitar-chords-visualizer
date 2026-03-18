import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, Rectangle, FancyBboxPatch
import numpy as np

st.set_page_config(page_title="Visualizador de Campo Armónico", 
                   page_icon="🎸", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    h1 { color: #E94560 !important; font-size: 2.2rem !important; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b; border-radius: 8px 8px 0 0;
        padding: 12px 20px; font-weight: bold; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #E94560 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎸 Círculo de Quintas con Campo Armónico y Armaduras")
st.markdown("---")

# Configuración musical tradicional
CIRCLE_ORDER = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
MINOR_RELATIVES = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

# Armaduras: (cantidad, tipo)
KEY_SIGS = {
    'C': (0, ''), 'G': (1, '#'), 'D': (2, '#'), 'A': (3, '#'),
    'E': (4, '#'), 'B': (5, '#'), 'F#': (6, '#'), 'C#': (7, '#'),
    'Ab': (4, 'b'), 'Eb': (3, 'b'), 'Bb': (2, 'b'), 'F': (1, 'b')
}

# Colores para cada función armónica (según imagen tradicional)
GRADE_COLORS = {
    'I': '#E63946',    # Rojo fuerte (Tónica)
    'V': '#F4A261',    # Naranja (Dominante)
    'IV': '#F72585',   # Rosa/Magenta (Subdominante)
    'ii': '#FB8500',   # Naranja claro (Supertónica)
    'iii': '#FFD60A',  # Amarillo (Mediante)
    'vi': '#FFB703',   # Amarillo/Dorado (Submediante)
    'vii': '#2ECC71'   # Verde (Sensible)
}

# Notas y acordes
notes_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_to_num = {note: i for i, note in enumerate(notes_sharp)}

CHORD_TYPES = {
    'Triada Mayor': {'intervals': [0, 4, 7], 'formula': '1 - 3 - 5'},
    'Triada Menor': {'intervals': [0, 3, 7], 'formula': '1 - b3 - 5'},
    'Triada Disminuida': {'intervals': [0, 3, 6], 'formula': '1 - b3 - b5'},
    'Mayor 7': {'intervals': [0, 4, 7, 11], 'formula': '1 - 3 - 5 - 7'},
    'Dominante 7': {'intervals': [0, 4, 7, 10], 'formula': '1 - 3 - 5 - b7'},
    'Menor 7': {'intervals': [0, 3, 7, 10], 'formula': '1 - b3 - 5 - b7'},
    'm7b5': {'intervals': [0, 3, 6, 10], 'formula': '1 - b3 - b5 - b7'},
}

def get_harmonic_field_grades(root):
    """Retorna mapeo de posición en círculo -> grado para la tonalidad dada"""
    root_idx = CIRCLE_ORDER.index(root)
    
    # Mapeo específico: posición relativa -> grado
    # En C Mayor: C=I(0), G=V(+1), F=IV(-1), D=ii(+2), A=vi(-2), E=iii(+3), B=vii(+4)
    grade_map = {}
    
    # I (Tónica) - posición actual
    grade_map[root_idx] = ('I', 'Mayor', CIRCLE_ORDER[root_idx])
    
    # V (Dominante) - +1 quinta
    pos_v = (root_idx + 1) % 12
    grade_map[pos_v] = ('V', 'Mayor', CIRCLE_ORDER[pos_v])
    
    # IV (Subdominante) - -1 quinta
    pos_iv = (root_idx - 1) % 12
    grade_map[pos_iv] = ('IV', 'Mayor', CIRCLE_ORDER[pos_iv])
    
    # ii (Supertónica) - +2 quintas (relativo menor de IV)
    pos_ii = (root_idx + 2) % 12
    grade_map[pos_ii] = ('ii', 'Menor', CIRCLE_ORDER[pos_ii])
    
    # vi (Submediante) - -2 quintas (relativo menor de I)
    pos_vi = (root_idx - 2) % 12
    grade_map[pos_vi] = ('vi', 'Menor', CIRCLE_ORDER[pos_vi])
    
    # iii (Mediante) - +3 quintas (relativo menor de V)
    pos_iii = (root_idx + 3) % 12
    grade_map[pos_iii] = ('iii', 'Menor', CIRCLE_ORDER[pos_iii])
    
    # vii° (Sensible) - +4 quintas (relativo menor de ii, disminuido)
    pos_vii = (root_idx + 4) % 12
    grade_map[pos_vii] = ('vii', 'Disminuido', CIRCLE_ORDER[pos_vii])
    
    return grade_map

def draw_study_circle(ax, root):
    """Dibuja el círculo de quintas estilo estudio con grados romanos y armaduras"""
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0f172a')
    
    grade_map = get_harmonic_field_grades(root)
    root_sig_num, root_sig_type = KEY_SIGS[root]
    
    # Título con información de armadura
    sig_text = f"({root_sig_num} {root_sig_type})" if root_sig_num > 0 else "(Natural)"
    ax.set_title(f'{root} Mayor {sig_text}', color='white', fontsize=22, fontweight='bold', pad=30)
    
    # Dibujar anillos de referencia (grises)
    for r in [0.6, 1.0]:
        circle = Circle((0, 0), r, fill=False, edgecolor='#475569', linewidth=2, alpha=0.3)
        ax.add_patch(circle)
    
    # Dibujar cada uno de los 12 sectores
    for i, (major_note, minor_note) in enumerate(zip(CIRCLE_ORDER, MINOR_RELATIVES)):
        angle = np.pi/2 - i * (2*np.pi/12)  # 12 en punto es C
        
        is_in_field = i in grade_map
        is_tonic = (major_note == root)
        
        # Determinar color y estilo
        if is_tonic:
            color = GRADE_COLORS['I']
            alpha = 1.0
            radius = 1.0
            lw = 4
            text_size = 20
            grade_text_size = 18
            zorder = 10
        elif is_in_field:
            grade_name = grade_map[i][0]
            color = GRADE_COLORS[grade_name]
            alpha = 0.9
            radius = 0.95
            lw = 3
            text_size = 18
            grade_text_size = 16
            zorder = 5
        else:
            color = '#334155'
            alpha = 0.15
            radius = 0.9
            lw = 1
            text_size = 12
            zorder = 1
        
        # Dibujar sector exterior (Mayor)
        wedge = Wedge((0, 0), radius, np.degrees(angle - np.pi/12), 
                     np.degrees(angle + np.pi/12), 
                     facecolor=color, alpha=alpha, edgecolor='white', linewidth=lw, zorder=zorder)
        ax.add_patch(wedge)
        
        # Dibujar sector interior (Menor/Relativo)
        wedge_inner = Wedge((0, 0), 0.6, np.degrees(angle - np.pi/12), 
                           np.degrees(angle + np.pi/12), 
                           facecolor=color, alpha=alpha*0.7, edgecolor='white', linewidth=lw, zorder=zorder)
        ax.add_patch(wedge_inner)
        
        # NOTA MAYOR (exterior)
        x_maj = 0.8 * np.cos(angle)
        y_maj = 0.8 * np.sin(angle)
        
        # Fondo para nota mayor
        circle_bg = Circle((x_maj, y_maj), 0.14 if is_in_field else 0.10, 
                          facecolor=color, edgecolor='white', linewidth=2, zorder=zorder+1)
        ax.add_patch(circle_bg)
        
        ax.text(x_maj, y_maj, major_note, ha='center', va='center', 
               fontsize=text_size, fontweight='bold', color='white', zorder=zorder+2)
        
        # ARMADURA (cantidad de alteraciones) - arriba de la nota
        num_alt, tipo_alt = KEY_SIGS[major_note]
        if num_alt > 0:
            x_sig = 1.15 * np.cos(angle)
            y_sig = 1.15 * np.sin(angle)
            symbol = '♯' if tipo_alt == '#' else '♭'
            
            # Color según si está en el campo armónico
            color_sig = '#FFD60A' if is_in_field else '#64748b'
            weight = 'bold' if is_in_field else 'normal'
            
            ax.text(x_sig, y_sig, f"{num_alt}{symbol}", ha='center', va='center',
                   fontsize=14, color=color_sig, fontweight=weight, 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b' if is_in_field else 'none', 
                            edgecolor=color_sig if is_in_field else 'none', alpha=0.9))
        
        # NOTA MENOR (interior)
        x_min = 0.35 * np.cos(angle)
        y_min = 0.35 * np.sin(angle)
        
        if is_in_field:
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=13, fontweight='bold', color='white', zorder=zorder+2,
                   bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f172a', 
                            edgecolor='white', linewidth=1.5, alpha=0.9))
        else:
            ax.text(x_min, y_min, minor_note, ha='center', va='center',
                   fontsize=10, color='#64748b', alpha=0.4)
        
        # GRADO ROMANO (dentro del sector, entre mayor y menor)
        if is_in_field:
            grade_name, quality, _ = grade_map[i]
            x_grade = 0.58 * np.cos(angle)
            y_grade = 0.58 * np.sin(angle)
            
            # Para grados menores, mostrar minúsculas y ° si es disminuido
            display_grade = grade_name
            if quality == 'Disminuido':
                display_grade = 'vii°'
            elif quality == 'Menor':
                display_grade = grade_name.lower()
            
            ax.text(x_grade, y_grade, display_grade, ha='center', va='center',
                   fontsize=grade_text_size, fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.25', facecolor='#0f172a', 
                            edgecolor=color, linewidth=2), zorder=zorder+3)
        
        # Líneas divisorias
        x_line_out = 1.0 * np.cos(angle + np.pi/12)
        y_line_out = 1.0 * np.sin(angle + np.pi/12)
        x_line_in = 0.6 * np.cos(angle + np.pi/12)
        y_line_in = 0.6 * np.sin(angle + np.pi/12)
        ax.plot([x_line_in, x_line_out], [y_line_in, y_line_out], 
               color='white', linewidth=1, alpha=0.3, zorder=0)
    
    # Centro - Tónica destacada
    center_bg = Circle((0, 0), 0.22, facecolor=GRADE_COLORS['I'], 
                      edgecolor='white', linewidth=4, zorder=20)
    ax.add_patch(center_bg)
    ax.text(0, 0.02, root, ha='center', va='center', fontsize=26, 
           fontweight='bold', color='white', zorder=21)
    ax.text(0, -0.10, 'I', ha='center', va='center', fontsize=14, 
           color='white', alpha=0.9, zorder=21)

# Interfaz
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    root_note = st.selectbox("🎵 Tonalidad:", CIRCLE_ORDER, index=0)
    chord_type = st.selectbox("🎸 Acorde:", list(CHORD_TYPES.keys()), index=0)
    
    sig_num, sig_type = KEY_SIGS[root_note]
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E63946 0%, #F4A261 100%); 
                padding: 15px; border-radius: 10px; text-align: center; margin-top: 20px;">
        <h3 style="color: white; margin: 0;">{root_note} Mayor</h3>
        <p style="color: white; font-size: 18px; margin: 5px 0;">
            {'Natural' if sig_num == 0 else f'{sig_num} {"sostenidos" if sig_type == "#" else "bemoles"} {sig_type}'}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    fig, ax = plt.subplots(figsize=(11, 11))
    fig.patch.set_facecolor('#0f172a')
    draw_study_circle(ax, root_note)
    st.pyplot(fig, use_container_width=True)

with col3:
    st.subheader("Grados del Campo Armónico")
    grade_map = get_harmonic_field_grades(root_note)
    
    # Ordenar por grados I, ii, iii, IV, V, vi, vii
    order = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii']
    for grade in order:
        for pos, (g, q, note) in grade_map.items():
            if g == grade:
                color = GRADE_COLORS[grade]
                display = 'vii°' if grade == 'vii' else (grade.lower() if q == 'Menor' else grade)
                
                st.markdown(f"""
                <div style="background-color: {color}22; border-left: 4px solid {color}; 
                            padding: 12px; margin: 8px 0; border-radius: 0 8px 8px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: {color}; font-size: 24px; font-weight: bold;">{display}</span>
                        <span style="color: white; font-size: 18px;">{note} {q}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                break
    
    st.markdown("---")
    st.subheader("Leyenda Funcional")
    functions = [
        ('I', 'Tónica'), ('V', 'Dominante'), ('IV', 'Subdominante'),
        ('ii', 'Supertónica'), ('iii', 'Mediante'), 
        ('vi', 'Submediante'), ('vii°', 'Sensible')
    ]
    for grade, name in functions:
        color = GRADE_COLORS[grade.replace('°', '')]
        st.markdown(f"<span style='color: {color}; font-weight: bold;'>{grade}</span> : {name}", unsafe_allow_html=True)

st.markdown("---")
tab1, tab2 = st.tabs(["🎸 Diapasón", "🎼 Análisis de Acorde"])

with tab1:
    # Código del diapasón simplificado
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.set_facecolor('#263238')
    
    # Dibujar trastes y cuerdas básicas
    for fret in range(23):
        color = '#FFD700' if fret in [3,5,7,9,12,15,17,19,21] else '#B0BEC5'
        ax.axvline(fret, color=color, linewidth=2)
    for string in range(6):
        ax.axhline(string, color='#ECEFF1', linewidth=3-string*0.3, alpha=0.8)
    
    # Notas del acorde seleccionado
    if chord_type in CHORD_TYPES:
        intervals = CHORD_TYPES[chord_type]['intervals']
        root_idx = note_to_num[root_note]
        
        for string in range(6):
            for fret in range(22):
                open_n = note_to_num[TUNING[string]]
                curr = (open_n + fret) % 12
                
                for i, inter in enumerate(intervals):
                    if (root_idx + inter) % 12 == curr:
                        colors = ['#E63946', '#457B9D', '#2A9D8F', '#E9C46A']
                        c = colors[i % 4]
                        circle = Circle((fret, string), 0.25, facecolor=c, edgecolor='white', linewidth=2)
                        ax.add_patch(circle)
                        note_name = notes_sharp[curr]
                        ax.text(fret, string, note_name, ha='center', va='center', 
                               fontsize=8, fontweight='bold', color='white')
                        break
    
    ax.set_xlim(-0.5, 22.5)
    ax.set_ylim(-0.5, 5.5)
    ax.set_yticks(range(6))
    ax.set_yticklabels(TUNING[::-1], color='white')
    ax.set_xticks(range(0, 23, 2))
    ax.set_xticklabels(range(0, 23, 2), color='white')
    ax.invert_yaxis()
    st.pyplot(fig, use_container_width=True)

with tab2:
    cols = st.columns(3)
    notes_chord = []
    if chord_type in CHORD_TYPES:
        intervals = CHORD_TYPES[chord_type]['intervals']
        root_idx = note_to_num[root_note]
        notes_chord = [notes_sharp[(root_idx + i) % 12] for i in intervals]
    
    with cols[0]:
        st.markdown("### Notas del Acorde")
        for i, note in enumerate(notes_chord):
            colors = ['#E63946', '#457B9D', '#2A9D8F', '#E9C46A']
            st.markdown(f"<h2 style='color: {colors[i]}; text-align: center;'>{note}</h2>", unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("### Fórmula")
        st.markdown(f"<h3 style='color: #4ECDC4; text-align: center;'>{CHORD_TYPES[chord_type]['formula']}</h3>", unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("### Intervalos")
        for i, inter in enumerate(CHORD_TYPES[chord_type]['intervals']):
            colors = ['#E63946', '#457B9D', '#2A9D8F', '#E9C46A']
            st.markdown(f"<p style='color: {colors[i]}; text-align: center; font-size: 20px;'>+{inter} semi</p>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center><h4>Estudio Musical: Campo Armónico de 7 Grados</h4></center>", unsafe_allow_html=True)
