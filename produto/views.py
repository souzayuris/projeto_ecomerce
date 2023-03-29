from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from . import models
from pprint import pprint
from django.db.models import Q  # Import para filtrar a busca


class ListaProtudos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 3

    ordering = ['-id']  # Ordena os itens de forma decrescente pelo ID


class Busca(ListaProtudos):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs

        self.request.session['termo'] = termo

        # Filtra a busca e faz a busca do termo
        # nos campos nome, descricao curta e descricao longa
        qs = qs.filter(
            Q(nome__icontains=termo) |
            Q(descricao_curta__icontains=termo) |
            Q(descricao_longa__icontains=termo)
        )

        self.request.session.save()

        return qs


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produtos'
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):

    # def get(self, *args, **kwargs):
    #    if self.request.session.get('carrinho'):
    #        del self.request.session['carrinho']
    #        self.request.session.save()

    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')

        )
        variacao_id = self.request.GET.get('vid')

        # Retorna uma mensagem de erro caso o usuário entre com um link de produto inexistente
        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe!'
            )
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        variacao_id = variacao_id
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque Insuficiente'
            )
            return redirect(http_referer)

        # Verificando se já existe sessão criada, caso não exista é criada uma sessão
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save

        carrinho = self.request.session['carrinho']

        # Verifica se a Variacao existe no carrinho
        if variacao_id in carrinho:
            # Variacao existe no carrinho
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque Insuficiente para {quantidade_carrinho}x no produto'
                    f' no produto "{produto_nome}". Adicionamos {variacao_estoque}x no seu carrinho'
                )
                quantidade_carrinho = variacao_estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * \
                quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * \
                quantidade_carrinho

        else:
            # Variacao não existe no carrinho
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem
            }

        self.request.session.save()

        # Mensagem de sucesso mostrando o item adicionado ao carrinho
        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome} adicionado ao seu carrinho '
            f'{carrinho[variacao_id]["quantidade"]}x.'
        )
        pprint(carrinho)
        return redirect(http_referer)


class RemoverDoCarrinho(ListView):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')

        )
        variacao_id = self.request.GET.get('vid')

        # Retorna o usuario para página anterior caso não exista variacao
        if not variacao_id:
            return redirect(http_referer)

        # Retorna o usuario caso não exista itens no carrinho
        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        # Retorna o usuario caso o item não exista no carrinho
        if variacao_id not in self.request.session['carrinho']:
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variacao_id]

        # Exibe a mensagem de sucesso para o cliente
        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} removido do carrinho'
        )

        # Exclui o produto do carrinho
        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()

        return redirect(http_referer)
        # return HttpResponse('RemoverDoCarrinho')


class Carrinho(ListView):
    def get(self, *args, **kwargs):
        return render(self.request, 'produto/carrinho.html')


class ResumoDaCompra(ListView):
    def get(self, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }

        return render(self.request, 'produto/resumodacompra.html', contexto)
