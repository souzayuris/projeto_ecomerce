def formata_preco(val):
    return f'R${val:.2f}'.replace('.', ',')


def cart_total_qtd(carrinho):
    if carrinho:
        return sum([item['quantidade'] for item in carrinho.values()])
    else:
        return 0


def cart_totals(carrinho):
    return sum(
        [
            item.get('preco_quantitativo_promocional')
            if item.get('preco_quantitativo_promocional')
            else item.get('preco_quantitativo')
            for item in carrinho.values()
        ]
    )
