import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def mapa_gradiente_unificacao(parquet_path):
    # 1. Carregar os dados
    df = pd.read_parquet(parquet_path)
    # Lista atualizada para incluir Ceres e garantir nomes capitalizados
    corpos = ["Mercury", "Venus", "Earth", "Mars", "Ceres", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    resultados = []
    dt = 0.05

    print("🛰️ Analisando gradientes de coerência pelo Sistema Solar...")

    for corpo in corpos:
        # Filtro insensível a maiúsculas para segurança
        data = df[df['corpo'].str.capitalize() == corpo.capitalize()].sort_values('frame')
        if data.empty: continue
        
        pos_sphy = data[['pos_x', 'pos_y', 'pos_z']].values
        distancia_media = np.mean(np.linalg.norm(pos_sphy, axis=1))
        
        # --- Simulação Newtoniana Adaptativa ---
        pos_n = [pos_sphy[0]]
        vel = (pos_sphy[1] - pos_sphy[0]) / dt
        
        # Ajuste dinâmico de G*Ms para a escala da órbita atual (Estabilidade de Kepler)
        r0 = np.linalg.norm(pos_sphy[0])
        v0 = np.linalg.norm(vel)
        g_ms_local = (v0**2) * r0 
        
        for i in range(1, len(pos_sphy)):
            r_vec = pos_n[-1]
            r_mag = np.linalg.norm(r_vec)
            if r_mag < 0.1: r_mag = 0.1
            
            acel = -g_ms_local * r_vec / (r_mag**3)
            vel = vel + acel * dt
            pos_n.append(pos_n[-1] + vel * dt)
        
        pos_n = np.array(pos_n)
        desvio_medio = np.mean(np.linalg.norm(pos_sphy - pos_n, axis=1))
        
        # Captura Alpha ou gera fallback
        alpha_m = data['alpha'].mean() if 'alpha' in data.columns else 1.0
        
        resultados.append({
            'corpo': corpo,
            'distancia': distancia_media,
            'taxa_desvio': desvio_medio,
            'alpha_medio': alpha_m
        })

    res_df = pd.DataFrame(resultados).sort_values('distancia')

    # --- GERAR GRÁFICO CIENTÍFICO ---
    plt.style.use('dark_background')
    plt.figure(figsize=(14, 8))
    ax = plt.gca()
    
    # Mapeamento de cores para resolver a confusão visual
    cores_map = {
        "Earth": "#00d4ff",   # Azul Ciano Vivo
        "Neptune": "#00008b", # Azul Marinho Profundo
        "Mars": "#ff4500",    # Vermelho Alaranjado
        "Venus": "#e6be8a",   # Creme/Ouro
        "Jupiter": "#ff9900", # Laranja Gasoso
        "Saturn": "#ebd38d"   # Amarelo Anel
    }

    # Plot principal
    for i, row in res_df.iterrows():
        cor = cores_map.get(row['corpo'], 'white')
        plt.loglog(row['distancia'], row['taxa_desvio'], 'o', 
                   markersize=12, color=cor, label=row['corpo'] if row['corpo'] in ["Earth", "Neptune"] else "")
        
        plt.annotate(row['corpo'], (row['distancia'], row['taxa_desvio']), 
                     xytext=(7, 7), textcoords='offset points', color=cor, 
                     fontsize=10, fontweight='bold')

    # Linha de tendência da Anomalia
    plt.loglog(res_df['distancia'], res_df['taxa_desvio'], color='red', alpha=0.3, linestyle='--', label='Tendência de Desvio')

    plt.title("MAPA DE GRADIENTE HARPIA: Desvio SPHY vs Newton", color='cyan', fontsize=16, pad=20)
    plt.xlabel("Distância Média do Sol (Escala Logarítmica)", color='gray', fontsize=12)
    plt.ylabel("Intensidade da Anomalia (Desvio Médio)", color='gray', fontsize=12)
    
    plt.grid(True, which="both", ls="-", alpha=0.1, color='white')
    plt.legend(loc='upper left', frameon=True, facecolor='#111')
    
    plt.tight_layout()
    plt.show()

    print("\n📊 TELEMETRIA DE UNIFICAÇÃO (ORDEM DISTÂNCIA):")
    # Formatação para melhor leitura dos desvios pequenos
    pd.options.display.float_format = '{:,.8f}'.format
    print(res_df[['corpo', 'distancia', 'taxa_desvio', 'alpha_medio']].to_string(index=False))

if __name__ == "__main__":
    mapa_gradiente_unificacao("telemetria_solar_sphy.parquet")