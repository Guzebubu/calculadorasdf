from flask import Flask, render_template, request, jsonify
import math
import traceback  # Agrega esto al inicio, junto con los otros imports

app = Flask(__name__)

# Configuración
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ============================
# RUTAS PRINCIPALES
# ============================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pcr_dream_taq')
def pcr_dream_taq_page():
    return render_template('pcr_dream_taq.html')

@app.route('/lv1')
def lv1_page():
    return render_template('lv1.html')

@app.route('/lv2')
def lv2_page():
    return render_template('lv2.html')

@app.route('/medios')
def medios_page():
    return render_template('medios.html')

# ============================
# API ENDPOINTS PARA CÁLCULOS
# ============================

# PCR INICIAL
@app.route('/api/pcr_inicial', methods=['POST'])
def calcular_pcr_inicial():
    try:
        data = request.get_json()
        num_reacciones = float(data.get('num_reacciones', 21))
        volumen_adn = float(data.get('volumen_adn', 1.5))
        porcentaje_extra = float(data.get('porcentaje_extra', 10))
        
        # Cálculos
        agua_base = num_reacciones * 32.6
        buffer_base = num_reacciones * 10
        fw_base = num_reacciones * 2
        rv_base = num_reacciones * 2
        adn_base = num_reacciones * volumen_adn
        polimerasa_base = num_reacciones * 0.4
        total_base = num_reacciones * 50
        
        factor_extra = 1 + (porcentaje_extra / 100)
        
        resultados = {
            'agua': round(agua_base * factor_extra, 1),
            'buffer': round(buffer_base * factor_extra, 1),
            'fw': round(fw_base * factor_extra, 1),
            'rv': round(rv_base * factor_extra, 1),
            'adn': round(adn_base, 1),
            'polimerasa': round(polimerasa_base * factor_extra, 1),
            'total_base': round(total_base, 1),
            'total_con_extra': round((total_base - adn_base) * factor_extra + adn_base, 1),
            'num_reacciones': num_reacciones,
            'porcentaje_extra': porcentaje_extra,
            'vol_master_mix': round((total_base - adn_base) * factor_extra, 1),
            'vol_adn_total': round(adn_base, 1)
        }
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# PCR DREAM TAQ - CON PORCENTAJE EXTRA
# PCR DREAM TAQ - CON PORCENTAJE EXTRA (VERSIÓN DEBUG)
@app.route('/api/pcr_dream_taq', methods=['POST'])
def calcular_pcr_dream_taq():
    try:
        data = request.get_json()
        num_reacciones = float(data.get('num_reacciones', 8))
        porcentaje_extra = float(data.get('porcentaje_extra', 10))
        volumen_total = 10  # µL por reacción
        
        # Componentes por reacción (1x) en µL
        valores_1x = {
            'buffer': 1,
            'dntps': 0.2,
            'fw': 0.4,
            'rv': 0.4,
            'dream_taq': 0.08,
            'dna': 1
        }
        
        # Calcular agua por reacción
        suma_componentes = sum([valores_1x['buffer'], valores_1x['dntps'], 
                                valores_1x['fw'], valores_1x['rv'], valores_1x['dream_taq']])
        valores_1x['agua'] = volumen_total - (suma_componentes + valores_1x['dna'])
        
        # Calcular factor extra
        factor_extra = 1 + (porcentaje_extra / 100)
        
        # Volúmenes base (sin extra)
        agua_base = valores_1x['agua'] * num_reacciones
        buffer_base = valores_1x['buffer'] * num_reacciones
        dntps_base = valores_1x['dntps'] * num_reacciones
        fw_base = valores_1x['fw'] * num_reacciones
        rv_base = valores_1x['rv'] * num_reacciones
        dream_taq_base = valores_1x['dream_taq'] * num_reacciones
        dna_base = valores_1x['dna'] * num_reacciones
        
        # Volúmenes con extra (solo para master mix, no para ADN)
        agua_con_extra = agua_base * factor_extra
        buffer_con_extra = buffer_base * factor_extra
        dntps_con_extra = dntps_base * factor_extra
        fw_con_extra = fw_base * factor_extra
        rv_con_extra = rv_base * factor_extra
        dream_taq_con_extra = dream_taq_base * factor_extra
        
        # Master mix sin ADN
        master_mix_sin_adn_base = (valores_1x['agua'] + valores_1x['buffer'] + 
                                  valores_1x['dntps'] + valores_1x['fw'] + 
                                  valores_1x['rv'] + valores_1x['dream_taq']) * num_reacciones
        
        master_mix_sin_adn_con_extra = master_mix_sin_adn_base * factor_extra
        
        # Totales
        total_base = volumen_total * num_reacciones
        total_con_extra = master_mix_sin_adn_con_extra + dna_base
        
        resultados = {
            'agua': round(agua_con_extra, 2),
            'buffer': round(buffer_con_extra, 2),
            'dntps': round(dntps_con_extra, 2),
            'fw': round(fw_con_extra, 2),
            'rv': round(rv_con_extra, 2),
            'dream_taq': round(dream_taq_con_extra, 2),
            'dna': round(dna_base, 2),
            'total_base': round(total_base, 2),
            'total_con_extra': round(total_con_extra, 2),
            'por_tubo': volumen_total,
            'num_reacciones': num_reacciones,
            'porcentaje_extra': porcentaje_extra,
            'master_mix_sin_adn': round(master_mix_sin_adn_con_extra, 2),
            'master_mix_sin_adn_base': round(master_mix_sin_adn_base, 2),
            'vol_adn_total': round(dna_base, 2),
            'factor_extra': factor_extra
        }
        
        print(f"DEBUG - Resultados enviados: {resultados}")  # Para debug en consola
        return jsonify(resultados)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
# NIVEL 1 - PARA MÚLTIPLES LIGACIONES INDEPENDIENTES
@app.route('/api/lv1', methods=['POST'])
def calcular_lv1():
    try:
        data = request.get_json()
        
        # Ahora podemos recibir múltiples ligaciones
        ligaciones = data.get('ligaciones', [])
        resultados = []
        
        for ligacion_data in ligaciones:
            # Parámetros de entrada para cada ligación
            tipo_ligacion = ligacion_data.get('tipo_ligacion', 'ligacion1')
            conc_fragmento = float(ligacion_data.get('conc_fragmento', 139.7))
            pb_fragmento = float(ligacion_data.get('pb_fragmento', 164))
            conc_plasmid1 = float(ligacion_data.get('conc_plasmid1', 146.9))
            pb_plasmid1 = float(ligacion_data.get('pb_plasmid1', 4968))
            conc_plasmid2 = float(ligacion_data.get('conc_plasmid2', 61.7))
            pb_plasmid2 = float(ligacion_data.get('pb_plasmid2', 2323))
            dilucion = float(ligacion_data.get('dilucion', 15))
            
            # Parámetros fijos
            volumen_total = 15
            buffer_t4 = 1.5
            bsai = 0.8
            t4_ligasa = 0.4
            
            # Cálculos
            fmoles_fragmento = (conc_fragmento * 1000000) / (660 * pb_fragmento) * 1000
            fmoles_plasmid1 = (conc_plasmid1 * 1000000) / (660 * pb_plasmid1) * 1000
            fmoles_plasmid2 = (conc_plasmid2 * 1000000) / (660 * pb_plasmid2) * 1000
            
            # Fragmento después de dilución (en fmol/µl)
            fmoles_diluidos_fragmento = fmoles_fragmento / dilucion
            
            # Cálculo de volúmenes (corregido)
            vol_fragmento = 40 / (fmoles_diluidos_fragmento / 1000) if fmoles_diluidos_fragmento > 0 else 0
            vol_plasmid1 = 40 / (fmoles_plasmid1 / 1000) if fmoles_plasmid1 > 0 else 0
            vol_plasmid2 = 40 / (fmoles_plasmid2 / 1000) if fmoles_plasmid2 > 0 else 0
            
            # Calcular agua
            suma_componentes = buffer_t4 + bsai + t4_ligasa + vol_fragmento + vol_plasmid1 + vol_plasmid2
            agua = max(0, volumen_total - suma_componentes)
            
            resultados.append({
                'tipo_ligacion': tipo_ligacion,
                'agua': round(agua, 3),
                'buffer_t4': round(buffer_t4, 3),
                'bsai': round(bsai, 3),
                't4_ligasa': round(t4_ligasa, 3),
                'fragmento_pcr': round(vol_fragmento, 3),
                'plasmid1': round(vol_plasmid1, 3),
                'plasmid2': round(vol_plasmid2, 3),
                'total': round(volumen_total, 3),
                'fmoles_fragmento': round(fmoles_fragmento, 3),
                'fmoles_diluidos_fragmento': round(fmoles_diluidos_fragmento, 3),
                'fmoles_plasmid1': round(fmoles_plasmid1, 3),
                'fmoles_plasmid2': round(fmoles_plasmid2, 3),
                'dilucion': dilucion
            })
        
        return jsonify({'ligaciones': resultados})
    except Exception as e:
        print(f"Error en cálculo de LV1: {str(e)}")
        return jsonify({'error': str(e)}), 400

# NIVEL 2
@app.route('/api/lv2', methods=['POST'])
def calcular_lv2():
    try:
        data = request.get_json()
        num_guias = int(data.get('num_guias', 1))
        
        # Parámetros de entrada
        conc_plasmid1 = float(data.get('conc_plasmid1', 132.2))
        pb_plasmid1 = float(data.get('pb_plasmid1', 6234))
        conc_plasmid2 = float(data.get('conc_plasmid2', 137))
        pb_plasmid2 = float(data.get('pb_plasmid2', 9623))
        conc_guia = float(data.get('conc_guia', 180.2))
        pb_guia = float(data.get('pb_guia', 4588))
        
        # Parámetros según número de guías
        volumen_total = 20
        buffer_t4 = 2
        bpii = 1
        t4_ligasa = 0.5
        
        # Cálculos de pmoles
        pmoles_plasmid1 = (conc_plasmid1 * 1000000) / (660 * pb_plasmid1) * 1000
        pmoles_plasmid2 = (conc_plasmid2 * 1000000) / (660 * pb_plasmid2) * 1000
        pmoles_guia = (conc_guia * 1000000) / (660 * pb_guia) * 1000
        
        # Volúmenes
        vol_plasmid1 = 40 / (pmoles_plasmid1 / 1000) if pmoles_plasmid1 > 0 else 0
        vol_plasmid2 = 40 / (pmoles_plasmid2 / 1000) if pmoles_plasmid2 > 0 else 0
        vol_guia = 40 / (pmoles_guia / 1000) if pmoles_guia > 0 else 0
        
        # Calcular agua
        suma_fija = buffer_t4 + bpii + t4_ligasa
        suma_variable = vol_plasmid1 + vol_plasmid2 + (vol_guia * num_guias)
        agua = max(0, volumen_total - (suma_fija + suma_variable))
        
        # Resultados
        resultados = {
            'agua': round(agua, 2),
            'buffer_t4': buffer_t4,
            'bpii': bpii,
            't4_ligasa': t4_ligasa,
            'plasmid1': round(vol_plasmid1, 2),
            'plasmid2': round(vol_plasmid2, 2),
            'volumen_total': volumen_total,
            'num_guias': num_guias,
            'pmoles_plasmid1': round(pmoles_plasmid1, 2),
            'pmoles_plasmid2': round(pmoles_plasmid2, 2),
            'pmoles_guia': round(pmoles_guia, 2),
            'vol_guia': round(vol_guia, 2)
        }
        
        # Agregar cada guía individualmente
        for i in range(1, num_guias + 1):
            resultados[f'guia{i}_vol'] = round(vol_guia, 2)
        
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# MEDIOS DE CULTIVO
@app.route('/api/medios', methods=['POST'])
def calcular_medios():
    try:
        data = request.get_json()
        tipo_medio = data.get('tipo_medio', 'germinacion')
        volumen_preparar = float(data.get('volumen_preparar', 1000))
        
        resultados = {}
        
        if tipo_medio == 'germinacion':
            resultados = {
                'h2o_ml': volumen_preparar,
                'ms_g': round((volumen_preparar * 2.4) / 1000, 2),
                'sacarosa_g': round((volumen_preparar * 15) / 1000, 2),
                'agar_g': round((volumen_preparar * 8) / 1000, 2),
                'ph': 5.8
            }
        elif tipo_medio == 'co_culture':
            resultados = {
                'h2o_ml': volumen_preparar,
                'ms_g': round((volumen_preparar * 4.8) / 1000, 2),
                'sacarosa_g': round((volumen_preparar * 30) / 1000, 2),
                'agar_g': round((volumen_preparar * 8) / 1000, 2),
                'd24_ul': round((volumen_preparar * 0.2) / 1000, 2),
                'kinetina_ul': round((volumen_preparar * 0.1) / 1000, 2),
                'ph': 5.8
            }
        elif tipo_medio == 'selection':
            resultados = {
                'h2o_ml': volumen_preparar,
                'ms_g': round((volumen_preparar * 4.8) / 1000, 2),
                'sacarosa_g': round((volumen_preparar * 30) / 1000, 2),
                'agar_g': round((volumen_preparar * 8) / 1000, 2),
                'tzeatina_ul': round((volumen_preparar * 2) / 1000, 2),
                'meropenem_ul': round((volumen_preparar * 25) / 1000, 2),
                'kanamicina_ul': round((volumen_preparar * 75) / 1000, 2),
                'ph': 5.8
            }
        elif tipo_medio == 'rooting':
            resultados = {
                'h2o_ml': volumen_preparar,
                'ms_g': round((volumen_preparar * 4.8) / 1000, 2),
                'sacarosa_g': round((volumen_preparar * 30) / 1000, 2),
                'agar_g': round((volumen_preparar * 8) / 1000, 2),
                'iaa_ul': round((volumen_preparar * 1) / 1000, 2),
                'meropenem_ul': round((volumen_preparar * 30) / 1000, 2),
                'kanamicina_ul': round((volumen_preparar * 75) / 1000, 2),
                'ph': 5.8
            }
        
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================
# EJECUCIÓN
# ============================
if __name__ == '__main__':
    app.run(debug=True)