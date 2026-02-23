import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analisar_anomalia_coerencia(parquet_path, corpo_alvo="Mercury"):
    # 1. Carregar os dados
    df = pd.read_parquet(parquet_path)
    
    # Filtro sensível a maiúsculas/minúsculas para evitar erros entre JSON e Código
    corpo_alvo_formatado = corpo_alvo.capitalize()
    dados_planeta = df[df['corpo'] == corpo_alvo_formatado].sort_values('frame')
    
    if dados_planeta.empty:
        print(f"❌ Erro: O corpo '{corpo_alvo_formatado}' não foi encontrado no arquivo.")
        print(f"Corpos disponíveis: {df['corpo'].unique()}")
        return

    # 2. Extrair posições
    pos_sphy = dados_planeta[['pos_x', 'pos_y', 'pos_z']].values
    
    # Tratamento para Alpha (Se não existir no Parquet, calculamos a variação de energia)
    if 'alpha' in dados_planeta.columns:
        alphas = dados_planeta['alpha'].values
    else:
        # Estimativa de 'Alpha' baseada na variação do raio orbital (Coerência de campo)
        raios = np.linalg.norm(pos_sphy, axis=1)
        alphas = raios / np.max(raios) 

    # 3. Simulação Newtoniana de Referência
    pos0 = pos_sphy[0]
    dt = 0.05
    
    pos_newton = [pos0]
    # Velocidade inicial calculada via diferença finita (mais estável)
    vel = (pos_sphy[1] - pos_sphy[0]) / dt
    
    # Constante gravitacional G*M_sol ajustada para a escala do simulador
    # Em sistemas SPHY, isso costuma variar, aqui usamos a aproximação clássica
    dist_centro = np.linalg.norm(pos0)
    G_Ms = (np.linalg.norm(vel)**2) * dist_centro # Estimativa Kepleriana
    
    for i in range(1, len(pos_sphy)):
        r_vec = pos_newton[-1]
        r_mag = np.linalg.norm(r_vec)
        
        if r_mag < 0.1: r_mag = 0.1 # Evita singularidade no Sol
        
        acel = -G_Ms * r_vec / (r_mag**3)
        vel = vel + acel * dt
        nova_pos = pos_newton[-1] + vel * dt
        pos_newton.append(nova_pos)
        
    pos_newton = np.array(pos_newton)

    # 4. Cálculo do Desvio (A Prova da Anomalia SPHY)
    desvios = np.linalg.norm(pos_sphy - pos_newton, axis=1)

    # 5. Gráfico Cinematográfico
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Definir cor baseada no planeta (para resolver sua dúvida das duas Terras)
    cor_planeta = 'cyan' if corpo_alvo_formatado == "Earth" else 'royalblue'
    if corpo_alvo_formatado == "Mercury": cor_planeta = 'darkgray'
    if corpo_alvo_formatado == "Mars": cor_planeta = 'tomato'

    ax1.set_xlabel('Tempo (Frames)', fontsize=12, color='white')
    ax1.set_ylabel('Desvio Orbital (Erro Residual vs Newton)', color='tab:red', fontsize=12)
    ax1.plot(desvios, color='tab:red', label='Anomalia Gravitacional', linewidth=2, alpha=0.8)
    ax1.fill_between(range(len(desvios)), desvios, color='tab:red', alpha=0.1)
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.grid(True, linestyle='--', alpha=0.2)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Fator de Coerência (α)', color=cor_planeta, fontsize=12)
    ax2.plot(alphas, color=cor_planeta, linestyle=':', label=f'Assinatura de {corpo_alvo_formatado}', alpha=0.9)
    ax2.tick_params(axis='y', labelcolor=cor_planeta)

    plt.title(f'Análise de Coerência SPHY: {corpo_alvo_formatado}', fontsize=14, pad=20)
    
    # Legenda unificada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    fig.tight_layout()
    plt.show()

    # Relatório Final
    print(f"\n--- 🛰️ RELATÓRIO TÉCNICO HARPIA: {corpo_alvo_formatado} ---")
    print(f"● Status: {'⚠️ ANOMALIA DETECTADA' if np.max(desvios) > 0.01 else '✅ ÓRBITA ESTÁVEL'}")
    print(f"● Desvio Acumulado Total: {np.max(desvios):.8f} u.a.")
    print(f"● Variância da Coerência: {np.var(alphas):.8f}")
    if corpo_alvo_formatado == "Earth":
        print("● Nota: Identificada como Esfera Azul Clara (Interna).")
    elif corpo_alvo_formatado == "Neptune":
        print("● Nota: Identificada como Esfera Azul Marinho (Externa).")

if __name__ == "__main__":
    # Tente rodar com "Earth" para ver a diferença do azul
    analisar_anomalia_coerencia("telemetria_solar_sphy.parquet", "Mercury")