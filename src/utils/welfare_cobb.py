def calculate_welfare_cobb_douglas(sugar: float, spicy: float, sugarm: float, spicym: float) -> float:
    """
    Cobb-Douglas Welfare Function.
    Считает благосостояние агента на основе имеющегося сахара, специй и его метаболических коэффициентов.
    """
    m_total = sugarm + spicym
    if m_total == 0:
        return 0.0
    s = max(0.0, sugar)
    p = max(0.0, spicy)
    return (s ** (sugarm / m_total)) * (p ** (spicym / m_total))
