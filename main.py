import numpy as np
import matplotlib.pyplot as plt

def calculate_critical_rate(P, C_delivery_aviation, C_delivery_sea, K0, T_aviation, T_sea, n, fee, tax):
    """
    Вычисляет критическую банковскую ставку по заданной формуле
    
    P - стоимость сервера ($3000)
    C_delivery_aviation - стоимость авиадоставки ($120)
    C_delivery_sea - стоимость морской доставки ($50)
    K0 - начальные инвестиции (принимаем равными P)
    T_aviation - время авиадоставки в годах
    T_sea - время морской доставки в годах
    n - количество начислений процентов в год (по умолчанию 1)
    """
    numerator = P - (C_delivery_sea + (P + C_delivery_sea) * (fee + tax))
    denominator = K0 - (C_delivery_aviation + (P + C_delivery_aviation) * (fee + tax))
    
    if denominator <= 0 or numerator <= 0:
        return np.nan
    
    power = 1 / (n * (T_sea - T_aviation))
    ratio = numerator / denominator
    
    if ratio <= 0:
        return np.nan
    
    r_critical = n * (ratio ** power - 1)
    return r_critical

def monte_carlo_simulation(n_simulations=100000):
    # Фиксированные параметры
    P = 3000          # Стоимость сервера ($)
    C_aviation = 120  # Стоимость авиадоставки ($)
    C_sea = 50        # Стоимость морской доставки ($)
    K0 = P
    n = 12            # Начисление процентов раз в год
    fee = 0.2         # Процент налога
    tax = 0.2         # Процент пошлины
    
    # Диапазон случайных сроков доставки
    sea_weeks_min, sea_weeks_max = 8, 16
    avia_weeks_min, avia_weeks_max = 1, 3

    critical_rates = []
    
    for _ in range(n_simulations):
        T_sea = np.random.uniform(sea_weeks_min, sea_weeks_max) / 52
        T_aviation = np.random.uniform(avia_weeks_min, avia_weeks_max) / 52
        
        r_crit = calculate_critical_rate(
            P, C_aviation, C_sea, K0, T_aviation, T_sea, n, fee, tax
        )
        
        if not np.isnan(r_crit):
            critical_rates.append(r_crit)
    
    critical_rates = [r for r in critical_rates if r > 0 and r < 1]
    
    mean_rate = np.mean(critical_rates)
    median_rate = np.median(critical_rates)
    
    print(f"Средняя критическая ставка: {mean_rate:.2%}")
    print(f"Медианная критическая ставка: {median_rate:.2%}")
    print(f"Минимальная ставка: {np.min(critical_rates):.2%}")
    print(f"Максимальная ставка: {np.max(critical_rates):.2%}")
    
    plt.figure(figsize=(12, 6))
    plt.hist(critical_rates, bins=50, color='skyblue', edgecolor='black', density=True)
    plt.axvline(mean_rate, color='red', linestyle='--', label=f'Средняя: {mean_rate:.2%}')
        
    plt.title('Распределение критических банковских ставок\nМетод Монте-Карло')
    plt.xlabel('Критическая банковская ставка')
    plt.ylabel('Плотность вероятности')
    plt.legend()
    plt.grid(True)
    plt.show()

monte_carlo_simulation()
