import numpy as np
import matplotlib.pyplot as plt

def get_customs_fee(value_rub):
    """ Возвращает сумму таможенного сбора в зависимости от стоимости товара в рублях """
    if value_rub <= 200_000:
        return 1_067
    elif value_rub <= 450_000:
        return 2_134
    elif value_rub <= 1_200_000:
        return 4_269
    elif value_rub <= 2_700_000:
        return 11_746
    elif value_rub <= 4_200_000:
        return 16_524
    elif value_rub <= 5_500_000:
        return 21_344
    elif value_rub <= 7_000_000:
        return 27_540
    else:
        return 30_000

def calculate_critical_rate(P, C_delivery_aviation, C_delivery_sea, K0, T_aviation, T_sea, n, tax, customs_fee):
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
    numerator = P - (C_delivery_sea + customs_fee + (P + C_delivery_sea) * tax)
    denominator = K0 - (C_delivery_aviation + customs_fee + (P + C_delivery_aviation) * tax)
    
    if denominator <= 0 or numerator <= 0:
        return np.nan
    
    power = 1 / (n * (T_sea - T_aviation))
    ratio = numerator / denominator
    
    if ratio <= 0:
        return np.nan
    
    r_critical = n * (ratio ** power - 1)
    return r_critical

def monte_carlo_simulation(n_simulations=100000, exchange_rate=90):
    # Фиксированные параметры
    P = 3000          # Стоимость сервера ($)
    C_aviation = 120  # Стоимость авиадоставки ($)
    C_sea = 50        # Стоимость морской доставки ($)
    K0 = P
    n = 12            # Начисление процентов раз в год
    tax = 0.2         # Налог (20%)
    
    # Диапазон случайных сроков доставки
    sea_weeks_min, sea_weeks_max = 8, 16
    avia_weeks_min, avia_weeks_max = 1, 3

    critical_rates = []
    
    for _ in range(n_simulations):
        T_aviation = np.random.uniform(avia_weeks_min, avia_weeks_max) / 52
        T_sea = np.random.uniform(sea_weeks_min, sea_weeks_max) / 52
        
        customs_fee = get_customs_fee(P) / 90
        
        r_crit = calculate_critical_rate(
            P, C_aviation, C_sea, K0, T_aviation, T_sea, n, tax, customs_fee
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
