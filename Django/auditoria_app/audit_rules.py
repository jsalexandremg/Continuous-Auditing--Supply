def verificar_valor_vs_mercado(linha, valor_mercado, impostos):
    valor_real = linha['valor_compra']
    localidade = linha['localidade']
    if valor_real > valor_mercado * (1 + impostos / 100):
        return f"Valor acima do mercado ({valor_real} > {valor_mercado})"
    return None
