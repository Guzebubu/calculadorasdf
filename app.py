from flask import Flask, render_template, request, jsonify
import math
import traceback
import os

app = Flask(__name__)

# Configuración
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ============================
# RUTAS PRINCIPALES (VISTAS)
# ============================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lv1')
def lv1_page():
    return render_template('lv1.html')

@app.route('/lv2')
def lv2_page():
    return render_template('lv2.html')

@app.route('/medios')
def medios_page():
    return render_template('medios.html')

@app.route('/molaridad')
def molaridad_page():
    return render_template('molaridad.html')

@app.route('/calculos_generales')
def calculos_generales_page():
    return render_template('calculos_generales.html')

@app.route('/recetas')
def recetas_page():
    return render_template('recetas.html')


# ============================
# API ENDPOINTS (CÁLCULOS)
# ============================

# MASTER MIX PCR
@app.route('/api/pcr_master', methods=['POST'])
def calcular_pcr_master():
    try:
        data = request.get_json()
        tipo_pcr = data.get('tipo_pcr', 'dream_taq') 
        num_reacciones = float(data.get('num_reacciones', 8))
        porcentaje_extra = float(data.get('porcentaje_extra', 10))
        factor_extra = 1 + (porcentaje_extra / 100)
        
        resultados = {}

        if tipo_pcr == 'inicial':
            volumen_adn = 1.5
            base_total = 50.0
            base_buffer = 10.0
            base_primers = 2.0
            base_polimerasa = 0.4
            base_agua = base_total - (base_buffer + (base_primers * 2) + base_polimerasa + volumen_adn)
            
            resultados = {
                'tipo_pcr': 'inicial', 'num_reacciones': num_reacciones, 'porcentaje_extra': porcentaje_extra, 'por_tubo': base_total, 'factor_extra': factor_extra,
                'base_agua': round(base_agua, 2), 'base_buffer': round(base_buffer, 2), 'base_primers': round(base_primers, 2), 'base_polimerasa': round(base_polimerasa, 2), 'base_adn': round(volumen_adn, 2), 'base_master_mix_tubo': round(base_total - volumen_adn, 2),
                'agua': round(num_reacciones * base_agua * factor_extra, 2), 'buffer': round(num_reacciones * base_buffer * factor_extra, 2), 'fw': round(num_reacciones * base_primers * factor_extra, 2), 'rv': round(num_reacciones * base_primers * factor_extra, 2), 'polimerasa': round(num_reacciones * base_polimerasa * factor_extra, 2), 'adn': round(num_reacciones * volumen_adn, 2),
                'master_mix_sin_adn': round((num_reacciones * (base_total - volumen_adn)) * factor_extra, 2), 'total_con_extra': round(((num_reacciones * (base_total - volumen_adn)) * factor_extra) + (num_reacciones * volumen_adn), 2)
            }

        elif tipo_pcr == 'dream_taq':
            volumen_total_dt = 10.0  
            base_adn_dt = 1.0        
            base_buffer_dt = 1.0
            base_dntps_dt = 0.2
            base_fw_dt = 0.4
            base_rv_dt = 0.4
            base_enzima_dt = 0.08
            suma_componentes = base_buffer_dt + base_dntps_dt + base_fw_dt + base_rv_dt + base_enzima_dt
            base_agua_dt = volumen_total_dt - (suma_componentes + base_adn_dt)
            
            resultados = {
                'tipo_pcr': 'dream_taq', 'num_reacciones': num_reacciones, 'porcentaje_extra': porcentaje_extra, 'por_tubo': volumen_total_dt, 'factor_extra': factor_extra,
                'base_agua': round(base_agua_dt, 2), 'base_buffer': round(base_buffer_dt, 2), 'base_dntps': round(base_dntps_dt, 2), 'base_fw': round(base_fw_dt, 2), 'base_rv': round(base_rv_dt, 2), 'base_dream_taq': round(base_enzima_dt, 2), 'base_adn': round(base_adn_dt, 2), 'base_master_mix_tubo': round(volumen_total_dt - base_adn_dt, 2),
                'agua': round(num_reacciones * base_agua_dt * factor_extra, 2), 'buffer': round(num_reacciones * base_buffer_dt * factor_extra, 2), 'dntps': round(num_reacciones * base_dntps_dt * factor_extra, 2), 'fw': round(num_reacciones * base_fw_dt * factor_extra, 2), 'rv': round(num_reacciones * base_rv_dt * factor_extra, 2), 'dream_taq': round(num_reacciones * base_enzima_dt * factor_extra, 2), 'adn': round(num_reacciones * base_adn_dt, 2),
                'master_mix_sin_adn': round((num_reacciones * (volumen_total_dt - base_adn_dt)) * factor_extra, 2), 'total_con_extra': round(((num_reacciones * (volumen_total_dt - base_adn_dt)) * factor_extra) + (num_reacciones * base_adn_dt), 2)
            }

        elif tipo_pcr == 'casera':
            volumen_adn = float(data.get('volumen_adn', 1.0))
            base_total = float(data.get('base_total', 10.0))
            base_buffer = float(data.get('base_buffer', 1.0))
            base_mgcl2 = float(data.get('base_mgcl2', 1.0))
            base_dntps = float(data.get('base_dntps', 0.2))
            base_fw = float(data.get('base_fw', 0.4))
            base_rv = float(data.get('base_rv', 0.4))
            base_polimerasa = float(data.get('base_polimerasa', 0.5))
            
            base_agua = base_total - (base_buffer + base_mgcl2 + base_dntps + base_fw + base_rv + base_polimerasa + volumen_adn)
            base_master_mix_tubo = base_total - volumen_adn
            
            resultados = {
                'tipo_pcr': 'casera', 'num_reacciones': num_reacciones, 'porcentaje_extra': porcentaje_extra, 'por_tubo': base_total, 'factor_extra': factor_extra,
                'base_agua': round(base_agua, 2), 'base_buffer': round(base_buffer, 2), 'base_mgcl2': round(base_mgcl2, 2), 'base_dntps': round(base_dntps, 2), 'base_fw': round(base_fw, 2), 'base_rv': round(base_rv, 2), 'base_polimerasa': round(base_polimerasa, 2), 'base_adn': round(volumen_adn, 2), 'base_master_mix_tubo': round(base_master_mix_tubo, 2),
                'agua': round(num_reacciones * base_agua * factor_extra, 2), 'buffer': round(num_reacciones * base_buffer * factor_extra, 2), 'mgcl2': round(num_reacciones * base_mgcl2 * factor_extra, 2), 'dntps': round(num_reacciones * base_dntps * factor_extra, 2), 'fw': round(num_reacciones * base_fw * factor_extra, 2), 'rv': round(num_reacciones * base_rv * factor_extra, 2), 'polimerasa': round(num_reacciones * base_polimerasa * factor_extra, 2), 'adn': round(num_reacciones * volumen_adn, 2),
                'master_mix_sin_adn': round((num_reacciones * base_master_mix_tubo) * factor_extra, 2), 'total_con_extra': round(((num_reacciones * base_master_mix_tubo) * factor_extra) + (num_reacciones * volumen_adn), 2)
            }

        return jsonify(resultados)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

# CALCULADORA DE MOLARIDAD
@app.route('/api/molaridad', methods=['POST'])
def calc_molaridad():
    try:
        data = request.get_json()
        tipo_calculo = data.get('tipo_calculo', 'gramos')
        peso_molecular = float(data.get('peso_molecular', 0))
        volumen_ml = float(data.get('volumen_ml', 0))
        
        if peso_molecular <= 0 or volumen_ml <= 0:
            return jsonify({'error': 'El peso molecular y el volumen deben ser mayores a cero.'}), 400
            
        volumen_l = volumen_ml / 1000.0
        resultados = {
            'tipo_calculo': tipo_calculo, 'peso_molecular': peso_molecular,
            'volumen_ml': volumen_ml, 'volumen_l': volumen_l
        }

        if tipo_calculo == 'gramos':
            concentracion_m = float(data.get('concentracion_m', 0))
            gramos = concentracion_m * peso_molecular * volumen_l
            resultados['concentracion_m'] = concentracion_m
            resultados['gramos_resultado'] = round(gramos, 4)
        else:
            gramos_pesados = float(data.get('gramos_pesados', 0))
            molaridad = gramos_pesados / (peso_molecular * volumen_l)
            resultados['gramos_pesados'] = gramos_pesados
            resultados['molaridad_resultado'] = round(molaridad, 4)
            
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# NIVEL 1 LIGACIONES
@app.route('/api/lv1', methods=['POST'])
def calcular_lv1():
    try:
        data = request.get_json()
        ligaciones_input = data.get('ligaciones', [])
        resultados_ligaciones = []
        VOL_TOTAL, VOL_BUFFER_T4, VOL_BSAI, VOL_T4_LIGASA, FMOLES_OBJETIVO = 15.0, 1.5, 1.0, 0.5, 40.0
        for ligacion in ligaciones_input:
            c_frag, pb_frag, dilucion = float(ligacion.get('conc_fragmento', 0)), float(ligacion.get('pb_fragmento', 1)), float(ligacion.get('dilucion', 1))
            c_p1, pb_p1 = float(ligacion.get('conc_plasmid1', 0)), float(ligacion.get('pb_plasmid1', 1))
            c_p2, pb_p2 = float(ligacion.get('conc_plasmid2', 0)), float(ligacion.get('pb_plasmid2', 1))
            fmol_ul_frag_diluido = ((c_frag * 1000000) / (pb_frag * 660)) / dilucion if pb_frag > 0 else 0
            fmol_ul_p1 = (c_p1 * 1000000) / (pb_p1 * 660) if pb_p1 > 0 else 0
            fmol_ul_p2 = (c_p2 * 1000000) / (pb_p2 * 660) if pb_p2 > 0 else 0
            vol_frag = FMOLES_OBJETIVO / fmol_ul_frag_diluido if fmol_ul_frag_diluido > 0 else 0
            vol_p1 = FMOLES_OBJETIVO / fmol_ul_p1 if fmol_ul_p1 > 0 else 0
            vol_p2 = FMOLES_OBJETIVO / fmol_ul_p2 if fmol_ul_p2 > 0 else 0
            agua = max(0, VOL_TOTAL - (VOL_BUFFER_T4 + VOL_BSAI + VOL_T4_LIGASA + vol_frag + vol_p1 + vol_p2))
            resultados_ligaciones.append({
                'tipo_ligacion': ligacion.get('tipo_ligacion', 'N/A'), 'agua': round(agua, 2), 'buffer_t4': VOL_BUFFER_T4, 'bsai': VOL_BSAI, 't4_ligasa': VOL_T4_LIGASA, 'fragmento_pcr': round(vol_frag, 2), 'plasmid1': round(vol_p1, 2), 'plasmid2': round(vol_p2, 2), 'total': VOL_TOTAL, 'fmoles_fragmento': FMOLES_OBJETIVO, 'fmoles_diluidos_fragmento': round(fmol_ul_frag_diluido, 2), 'fmoles_plasmid1': FMOLES_OBJETIVO, 'fmoles_plasmid2': FMOLES_OBJETIVO
            })
        return jsonify({'ligaciones': resultados_ligaciones})
    except Exception as e: return jsonify({'error': str(e)}), 400

# NIVEL 2 ENSAMBLAJES
@app.route('/api/lv2', methods=['POST'])
def calcular_lv2():
    try:
        data = request.get_json()
        num_guias = int(data.get('num_guias', 1))
        conc_plasmid1, pb_plasmid1 = float(data.get('conc_plasmid1', 132.2)), float(data.get('pb_plasmid1', 6234))
        conc_plasmid2, pb_plasmid2 = float(data.get('conc_plasmid2', 137)), float(data.get('pb_plasmid2', 9623))
        volumen_total, buffer_t4, bpii, t4_ligasa = 20, 2, 1, 0.5
        pmoles_plasmid1 = (conc_plasmid1 * 1000000) / (660 * pb_plasmid1) * 1000
        pmoles_plasmid2 = (conc_plasmid2 * 1000000) / (660 * pb_plasmid2) * 1000
        vol_plasmid1 = 40 / (pmoles_plasmid1 / 1000) if pmoles_plasmid1 > 0 else 0
        vol_plasmid2 = 40 / (pmoles_plasmid2 / 1000) if pmoles_plasmid2 > 0 else 0
        guias_data = data.get('guias', [])
        volumen_guias_total = 0
        resultados_guias, fmol_guias = {}, {}
        for i in range(num_guias):
            conc_g, pb_g = (float(guias_data[i].get('conc', 180.2)), float(guias_data[i].get('pb', 4588))) if i < len(guias_data) else (180.2, 4588)
            pmol_g = (conc_g * 1000000) / (660 * pb_g) * 1000
            vol_g = 40 / (pmol_g / 1000) if pmol_g > 0 else 0
            resultados_guias[f'guia{i+1}_vol'] = round(vol_g, 2)
            fmol_guias[f'guia{i+1}'] = round(pmol_g / 1000, 2)
            volumen_guias_total += vol_g
        agua = max(0, volumen_total - (buffer_t4 + bpii + t4_ligasa + vol_plasmid1 + vol_plasmid2 + volumen_guias_total))
        resultados = {
            'agua': round(agua, 2), 'buffer_t4': buffer_t4, 'bpii': bpii, 't4_ligasa': t4_ligasa, 'plasmid1': round(vol_plasmid1, 2), 'plasmid2': round(vol_plasmid2, 2), 'volumen_total': volumen_total, 'num_guias': num_guias, 'fmol_plasmid1': round(pmoles_plasmid1 / 1000, 2), 'fmol_plasmid2': round(pmoles_plasmid2 / 1000, 2), 'fmol_guias': fmol_guias
        }
        resultados.update(resultados_guias)
        return jsonify(resultados)
    except Exception as e: return jsonify({'error': str(e)}), 400

# MEDIOS DE CULTIVO
@app.route('/api/medios', methods=['POST'])
def calcular_medios():
    try:
        data = request.get_json()
        tipo_medio = data.get('tipo_medio', 'germinacion')
        volumen_preparar = float(data.get('volumen_preparar', 1000))
        if tipo_medio == 'germinacion':
            resultados = {'h2o_ml': volumen_preparar, 'ms_g': round((volumen_preparar * 2.4) / 1000, 2), 'sacarosa_g': round((volumen_preparar * 15) / 1000, 2), 'agar_g': round((volumen_preparar * 8) / 1000, 2), 'ph': 5.8}
        elif tipo_medio == 'co_culture':
            resultados = {'h2o_ml': volumen_preparar, 'ms_g': round((volumen_preparar * 4.8) / 1000, 2), 'sacarosa_g': round((volumen_preparar * 30) / 1000, 2), 'agar_g': round((volumen_preparar * 8) / 1000, 2), 'd24_ul': round(volumen_preparar * 0.2, 2), 'kinetina_ul': round(volumen_preparar * 0.1, 2), 'ph': 5.8}
        elif tipo_medio == 'selection':
            resultados = {'h2o_ml': volumen_preparar, 'ms_g': round((volumen_preparar * 4.8) / 1000, 2), 'sacarosa_g': round((volumen_preparar * 30) / 1000, 2), 'agar_g': round((volumen_preparar * 8) / 1000, 2), 'tzeatina_ul': round(volumen_preparar * 1.0, 2), 'meropenem_ul': round(volumen_preparar * 0.5, 2), 'kanamicina_ul': round(volumen_preparar * 0.75, 2), 'ph': 5.8}
        elif tipo_medio == 'rooting':
            resultados = {'h2o_ml': volumen_preparar, 'ms_g': round((volumen_preparar * 4.8) / 1000, 2), 'sacarosa_g': round((volumen_preparar * 30) / 1000, 2), 'agar_g': round((volumen_preparar * 8) / 1000, 2), 'iaa_ul': round(volumen_preparar * 1.0, 2), 'meropenem_ul': round(volumen_preparar * 0.5, 2), 'kanamicina_ul': round(volumen_preparar * 0.75, 2), 'ph': 5.8}
        return jsonify(resultados)
    except Exception as e: return jsonify({'error': str(e)}), 400

# GENERALES (DILUCIONES, PRIMERS, DIGESTIÓN)
@app.route('/api/diluciones', methods=['POST'])
def calc_diluciones():
    try:
        data = request.get_json()
        c1, c2, v2 = float(data.get('c1', 0)), float(data.get('c2', 0)), float(data.get('v2', 0))
        if c1 == 0 or c2 > c1: return jsonify({'error': 'C1 inválido o menor a C2.'}), 400
        v1 = (c2 * v2) / c1
        return jsonify({'v1': round(v1, 4), 'solvente': round(v2 - v1, 4), 'v2': v2})
    except Exception as e: return jsonify({'error': str(e)}), 400

@app.route('/api/primers', methods=['POST'])
def calc_primers():
    try:
        data = request.get_json()
        nmol, conc_final = float(data.get('nmol', 0)), float(data.get('conc_final', 100))
        if conc_final == 0: return jsonify({'error': 'La concentración no puede ser 0.'}), 400
        return jsonify({'volumen_ul': round((nmol * 1000) / conc_final, 2), 'nmol': nmol, 'conc_final': conc_final})
    except Exception as e: return jsonify({'error': str(e)}), 400

@app.route('/api/digestion', methods=['POST'])
def calc_digestion():
    try:
        data = request.get_json()
        reacciones, extra, vol_total, vol_adn, vol_enzima1, vol_enzima2 = float(data.get('reacciones', 1)), float(data.get('extra', 10)) / 100.0, float(data.get('vol_total', 20)), float(data.get('vol_adn', 1)), float(data.get('vol_enzima1', 0.5)), float(data.get('vol_enzima2', 0))
        vol_buffer = vol_total * 0.10
        vol_agua = vol_total - (vol_adn + vol_enzima1 + vol_enzima2 + vol_buffer)
        if vol_agua < 0: return jsonify({'error': 'Componentes superan el volumen total.'}), 400
        factor = reacciones * (1 + extra)
        return jsonify({'agua_rx': round(vol_agua, 2), 'agua_mm': round(vol_agua * factor, 2), 'buffer_rx': round(vol_buffer, 2), 'buffer_mm': round(vol_buffer * factor, 2), 'enzima1_rx': round(vol_enzima1, 2), 'enzima1_mm': round(vol_enzima1 * factor, 2), 'enzima2_rx': round(vol_enzima2, 2), 'enzima2_mm': round(vol_enzima2 * factor, 2), 'adn_rx': round(vol_adn, 2), 'total_rx': round(vol_total, 2), 'reacciones': reacciones, 'extra': data.get('extra', 10)})
    except Exception as e: return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)