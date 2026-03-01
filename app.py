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
        
        # 1. NUEVOS PARÁMETROS DINÁMICOS
        base_total = float(data.get('base_total', 50))
        base_buffer = float(data.get('base_buffer', 10))
        base_primers = float(data.get('base_primers', 2))
        base_polimerasa = float(data.get('base_polimerasa', 0.4))
        
        # 2. CÁLCULO INTELIGENTE DEL AGUA
        # El agua se calcula sola restando los demás componentes al total
        base_agua = base_total - (base_buffer + (base_primers * 2) + base_polimerasa + volumen_adn)
        
        # 3. MULTIPLICACIÓN POR NÚMERO DE REACCIONES
        agua_base = num_reacciones * base_agua
        buffer_base = num_reacciones * base_buffer
        fw_base = num_reacciones * base_primers
        rv_base = num_reacciones * base_primers
        adn_base = num_reacciones * volumen_adn
        polimerasa_base = num_reacciones * base_polimerasa
        total_base = num_reacciones * base_total
        
        factor_extra = 1 + (porcentaje_extra / 100)
        
        resultados = {
            # Valores por reacción (para mostrarlos en la tabla)
            'base_agua': round(base_agua, 2),
            'base_buffer': base_buffer,
            'base_primers': base_primers,
            'base_polimerasa': base_polimerasa,
            'base_total': base_total,
            
            # Totales con porcentaje extra (excepto ADN)
            'agua': round(agua_base * factor_extra, 1),
            'buffer': round(buffer_base * factor_extra, 1),
            'fw': round(fw_base * factor_extra, 1),
            'rv': round(rv_base * factor_extra, 1),
            'adn': round(adn_base, 1),
            'polimerasa': round(polimerasa_base * factor_extra, 1),
            'total_con_extra': round((total_base - adn_base) * factor_extra + adn_base, 1),
            
            # Datos generales
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
    
# ==========================================
# RUTAS PARA NIVEL 1 (LV1) - LIGACIONES
# ==========================================
@app.route('/api/lv1', methods=['POST'])
def calcular_lv1():
    try:
        data = request.get_json()
        ligaciones_input = data.get('ligaciones', [])
        
        resultados_ligaciones = []
        
        # Parámetros fijos por reacción (Asumiendo 15 µl finales)
        VOL_TOTAL = 15.0
        VOL_BUFFER_T4 = 1.5   # 10X Buffer (1.5 µl en 15 µl)
        VOL_BSAI = 1.0        # Enzima de restricción
        VOL_T4_LIGASA = 0.5   # Ligasa
        
        # FMOLES OBJETIVO PARA GOLDEN GATE
        FMOLES_OBJETIVO = 40.0
        
        for ligacion in ligaciones_input:
            # 1. Extraer datos (con valores por defecto por si acaso)
            c_frag = float(ligacion.get('conc_fragmento', 0))
            pb_frag = float(ligacion.get('pb_fragmento', 1))
            dilucion = float(ligacion.get('dilucion', 1))
            
            c_p1 = float(ligacion.get('conc_plasmid1', 0))
            pb_p1 = float(ligacion.get('pb_plasmid1', 1))
            
            c_p2 = float(ligacion.get('conc_plasmid2', 0))
            pb_p2 = float(ligacion.get('pb_plasmid2', 1))
            
            # 2. Calcular fmol/µl reales para cada componente
            fmol_ul_frag_puro = (c_frag * 1000000) / (pb_frag * 660) if pb_frag > 0 else 0
            fmol_ul_frag_diluido = fmol_ul_frag_puro / dilucion if dilucion > 0 else fmol_ul_frag_puro
            
            fmol_ul_p1 = (c_p1 * 1000000) / (pb_p1 * 660) if pb_p1 > 0 else 0
            fmol_ul_p2 = (c_p2 * 1000000) / (pb_p2 * 660) if pb_p2 > 0 else 0
            
            # 3. Calcular qué volumen (µl) necesito pipetear para obtener 40 fmoles
            vol_frag = FMOLES_OBJETIVO / fmol_ul_frag_diluido if fmol_ul_frag_diluido > 0 else 0
            vol_p1 = FMOLES_OBJETIVO / fmol_ul_p1 if fmol_ul_p1 > 0 else 0
            vol_p2 = FMOLES_OBJETIVO / fmol_ul_p2 if fmol_ul_p2 > 0 else 0
            
            # 4. Calcular el Agua para aforar a 15 µl
            vol_componentes = VOL_BUFFER_T4 + VOL_BSAI + VOL_T4_LIGASA + vol_frag + vol_p1 + vol_p2
            agua = VOL_TOTAL - vol_componentes
            
            # Si el agua da negativo, significa que los componentes están muy diluidos y rebasan los 15ul
            agua_final = max(0, agua) 
            
            # 5. Guardar el resultado formateado a 2 decimales
            resultado = {
                'tipo_ligacion': ligacion.get('tipo_ligacion', 'N/A'),
                'agua': round(agua_final, 2),
                'buffer_t4': VOL_BUFFER_T4,
                'bsai': VOL_BSAI,
                't4_ligasa': VOL_T4_LIGASA,
                'fragmento_pcr': round(vol_frag, 2),
                'plasmid1': round(vol_p1, 2),
                'plasmid2': round(vol_p2, 2),
                'total': VOL_TOTAL,
                
                # Datos moleculares para mostrar en los detalles (puramente informativos)
                'fmoles_fragmento': FMOLES_OBJETIVO,
                'fmoles_diluidos_fragmento': round(fmol_ul_frag_diluido, 2),
                'fmoles_plasmid1': FMOLES_OBJETIVO,
                'fmoles_plasmid2': FMOLES_OBJETIVO
            }
            
            resultados_ligaciones.append(resultado)

        return jsonify({'ligaciones': resultados_ligaciones})

    except Exception as e:
        return jsonify({'error': f"Error en cálculo Lv1: {str(e)}"}), 400
# NIVEL 2
@app.route('/api/lv2', methods=['POST'])
def calcular_lv2():
    try:
        data = request.get_json()
        num_guias = int(data.get('num_guias', 1))
        
        # Parámetros de Plásmidos
        conc_plasmid1 = float(data.get('conc_plasmid1', 132.2))
        pb_plasmid1 = float(data.get('pb_plasmid1', 6234))
        conc_plasmid2 = float(data.get('conc_plasmid2', 137))
        pb_plasmid2 = float(data.get('pb_plasmid2', 9623))
        
        # Parámetros fijos
        volumen_total = 20
        buffer_t4 = 2
        bpii = 1
        t4_ligasa = 0.5
        
        # Cálculos de pmoles plásmidos
        pmoles_plasmid1 = (conc_plasmid1 * 1000000) / (660 * pb_plasmid1) * 1000
        pmoles_plasmid2 = (conc_plasmid2 * 1000000) / (660 * pb_plasmid2) * 1000
        
        # Volúmenes plásmidos
        vol_plasmid1 = 40 / (pmoles_plasmid1 / 1000) if pmoles_plasmid1 > 0 else 0
        vol_plasmid2 = 40 / (pmoles_plasmid2 / 1000) if pmoles_plasmid2 > 0 else 0
        
        # Procesar lista de guías dinámicas
        guias_data = data.get('guias', [])
        volumen_guias_total = 0
        resultados_guias = {}
        fmol_guias = {}
        
        for i in range(num_guias):
            # Obtener datos de cada guía, si no existe toma un valor por defecto
            if i < len(guias_data):
                conc_g = float(guias_data[i].get('conc', 180.2))
                pb_g = float(guias_data[i].get('pb', 4588))
            else:
                conc_g = 180.2
                pb_g = 4588
                
            pmol_g = (conc_g * 1000000) / (660 * pb_g) * 1000
            vol_g = 40 / (pmol_g / 1000) if pmol_g > 0 else 0
            
            resultados_guias[f'guia{i+1}_vol'] = round(vol_g, 2)
            fmol_guias[f'guia{i+1}'] = round(pmol_g / 1000, 2)
            volumen_guias_total += vol_g
            
        # Calcular agua
        suma_fija = buffer_t4 + bpii + t4_ligasa
        suma_variable = vol_plasmid1 + vol_plasmid2 + volumen_guias_total
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
            'fmol_plasmid1': round(pmoles_plasmid1 / 1000, 2),
            'fmol_plasmid2': round(pmoles_plasmid2 / 1000, 2),
            'fmol_guias': fmol_guias # Diccionario con fmoles de cada guía
        }
        
        # Agregar los volúmenes de cada guía al resultado principal
        resultados.update(resultados_guias)
        
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
    
# ==========================================
# RUTAS PARA MOLARIDAD
# ==========================================
@app.route('/molaridad')
def molaridad_page():
    return render_template('molaridad.html')

@app.route('/api/molaridad', methods=['POST'])
def calcular_molaridad():
    try:
        data = request.get_json()
        tipo_calculo = data.get('tipo_calculo') # 'gramos' o 'molaridad'
        peso_molecular = float(data.get('peso_molecular', 0))
        volumen_ml = float(data.get('volumen_ml', 0))
        
        # Convertir ml a Litros para la fórmula (M = mol/L)
        volumen_l = volumen_ml / 1000.0
        
        resultados = {
            'tipo_calculo': tipo_calculo,
            'peso_molecular': peso_molecular,
            'volumen_ml': volumen_ml,
            'volumen_l': volumen_l
        }
        
        if tipo_calculo == 'gramos':
            # Escenario A: Calcular Gramos a pesar
            concentracion_m = float(data.get('concentracion_m', 0))
            # Fórmula: Gramos = Molaridad * Volumen(L) * Peso Molecular
            gramos = concentracion_m * volumen_l * peso_molecular
            
            resultados['concentracion_m'] = concentracion_m
            resultados['gramos_resultado'] = round(gramos, 4)
            
        elif tipo_calculo == 'molaridad':
            # Escenario B: Calcular Molaridad resultante
            gramos_pesados = float(data.get('gramos_pesados', 0))
            # Fórmula: Molaridad = Gramos / (Peso Molecular * Volumen(L))
            molaridad = gramos_pesados / (peso_molecular * volumen_l) if (peso_molecular * volumen_l) > 0 else 0
            
            resultados['gramos_pesados'] = gramos_pesados
            resultados['molaridad_resultado'] = round(molaridad, 4)
            
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # ==========================================
# RUTAS PARA CÁLCULOS GENERALES
# ==========================================
@app.route('/calculos_generales')
def calculos_generales_page():
    return render_template('calculos_generales.html')

@app.route('/api/diluciones', methods=['POST'])
def calc_diluciones():
    try:
        data = request.get_json()
        c1 = float(data.get('c1', 0))
        c2 = float(data.get('c2', 0))
        v2 = float(data.get('v2', 0))
        
        if c1 == 0:
            return jsonify({'error': 'La concentración inicial (C1) no puede ser 0.'}), 400
        if c2 > c1:
            return jsonify({'error': 'La concentración final (C2) no puede ser mayor que la inicial (C1).'}), 400
            
        # Fórmula C1V1 = C2V2 -> V1 = (C2 * V2) / C1
        v1 = (c2 * v2) / c1
        solvente = v2 - v1
        
        return jsonify({
            'v1': round(v1, 4),
            'solvente': round(solvente, 4),
            'v2': v2
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/primers', methods=['POST'])
def calc_primers():
    try:
        data = request.get_json()
        nmol = float(data.get('nmol', 0))
        conc_final = float(data.get('conc_final', 100)) # Por defecto 100 uM
        
        if conc_final == 0:
            return jsonify({'error': 'La concentración final no puede ser 0.'}), 400
            
        # Fórmula: µl de TE = (nmol * 1000) / Concentración final (µM)
        vol_ul = (nmol * 1000) / conc_final
        
        return jsonify({
            'volumen_ul': round(vol_ul, 2),
            'nmol': nmol,
            'conc_final': conc_final
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/digestion', methods=['POST'])
def calc_digestion():
    try:
        data = request.get_json()
        reacciones = float(data.get('reacciones', 1))
        extra = float(data.get('extra', 10)) / 100.0
        
        vol_total = float(data.get('vol_total', 20))
        vol_adn = float(data.get('vol_adn', 1))
        vol_enzima1 = float(data.get('vol_enzima1', 0.5))
        vol_enzima2 = float(data.get('vol_enzima2', 0))
        
        # Buffer es típicamente el 10% del volumen total (10X)
        vol_buffer = vol_total * 0.10
        
        vol_agua = vol_total - (vol_adn + vol_enzima1 + vol_enzima2 + vol_buffer)
        
        if vol_agua < 0:
            return jsonify({'error': 'El volumen de los componentes supera el volumen total de la reacción.'}), 400
            
        factor = reacciones * (1 + extra)
        
        return jsonify({
            'agua_rx': round(vol_agua, 2),
            'agua_mm': round(vol_agua * factor, 2),
            'buffer_rx': round(vol_buffer, 2),
            'buffer_mm': round(vol_buffer * factor, 2),
            'enzima1_rx': round(vol_enzima1, 2),
            'enzima1_mm': round(vol_enzima1 * factor, 2),
            'enzima2_rx': round(vol_enzima2, 2),
            'enzima2_mm': round(vol_enzima2 * factor, 2),
            'adn_rx': round(vol_adn, 2),
            'total_rx': round(vol_total, 2),
            'reacciones': reacciones,
            'extra': data.get('extra', 10)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==========================================
# RUTAS PARA RECETAS DE LABORATORIO
# ==========================================
@app.route('/recetas')
def recetas_page():
    return render_template('recetas.html')

# ============================
# EJECUCIÓN
# ============================
if __name__ == '__main__':
    app.run(debug=True)