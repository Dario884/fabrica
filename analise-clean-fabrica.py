import pandas as pd
import plotly.express as px
import random 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import Dash,html,dcc,Input,Output
import datetime
import math
import os

estoque = pd.read_excel('estoque_custo.xlsx')
vendas = pd.read_excel('vendas_lojas.xlsx')
produção = pd.read_excel('producao_diaria.xlsx')

vendas.rename(columns={'Nome da Peça':'Produto','Quantidade Vendida':'Quantidade','Método de Pagamento':'Pagamento','Nome da Loja':'Loja'}, inplace=True)
estoque.rename(columns={'Nome da Peça':'Produto','Custo de Produção':'Custo'}, inplace=True)
produção.rename(columns={'Nome da Peça':'Produto','Quantidade Produzida':'Quantidade'}, inplace=True)

prods = list(estoque['Produto'].unique())
cats = list(estoque['Categoria'].unique())
dic = {'Inverno':[],'Verão':[],'Esportivo':[],'Social':[],'Casual':[]}
for pos,p in enumerate(prods):
    if estoque.loc[pos,'Categoria']=='Inverno':
        dic['Inverno'].append(p)
    if estoque.loc[pos,'Categoria']=='Verão':
        dic['Verão'].append(p)
    if estoque.loc[pos,'Categoria']=='Esportivo':
        dic['Esportivo'].append(p)
    if estoque.loc[pos,'Categoria']=='Social':
        dic['Social'].append(p)
    if estoque.loc[pos,'Categoria']=='Casual':
        dic['Casual'].append(p)
for i in range(0,vendas.shape[0]):
    if vendas.loc[i,'Produto'] in dic['Inverno']:
        vendas.loc[i,'Categoria']='Inverno'
    if vendas.loc[i,'Produto'] in dic['Verão']:
        vendas.loc[i,'Categoria']='Verão'
    if vendas.loc[i,'Produto'] in dic['Esportivo']:
        vendas.loc[i,'Categoria']='Esportivo'
    if vendas.loc[i,'Produto'] in dic['Social']:
        vendas.loc[i,'Categoria']='Social'
    if vendas.loc[i,'Produto'] in dic['Casual']:
        vendas.loc[i,'Categoria']='Casual'
for i in range(0,produção.shape[0]):
    if produção.loc[i,'Produto'] in dic['Inverno']:
        produção.loc[i,'Categoria']='Inverno'
    if produção.loc[i,'Produto'] in dic['Verão']:
        produção.loc[i,'Categoria']='Verão'
    if produção.loc[i,'Produto'] in dic['Esportivo']:
        produção.loc[i,'Categoria']='Esportivo'
    if produção.loc[i,'Produto'] in dic['Social']:
        produção.loc[i,'Categoria']='Social'
    if produção.loc[i,'Produto'] in dic['Casual']:
        produção.loc[i,'Categoria']='Casual'
        
for i in range(0,estoque.shape[0]):
    estoque.loc[i,'Preço']=estoque.loc[i,'Custo']*2.5

for i in list(vendas.index):
    for c in range(estoque.shape[0]):
        if vendas.loc[i,'Produto']==estoque.loc[c,'Produto']:
            vendas.loc[i,'Preço']=estoque.loc[c,'Preço']
            vendas.loc[i,'Custo']=estoque.loc[c,'Custo']
for i in list(vendas.index):
    vendas.loc[i,'Valor final']=vendas.loc[i,'Quantidade']*vendas.loc[i,'Preço']
vendas['Lucro']=vendas['Valor final']-vendas['Quantidade']*vendas['Custo']


# faturamento / lucro por loja bar
fatluc = vendas[['Loja','Valor final','Lucro']].groupby('Loja').sum()
for i in list(fatluc.index):
    fatluc.loc[i,'Loja']=i
fatluc.rename(columns={'Valor final':'Faturamento'}, inplace=True)
fattotal = fatluc['Faturamento'].sum()
luctotal = fatluc['Lucro'].sum()
flxloja = px.bar(fatluc, x='Loja', y=['Faturamento','Lucro'], color_discrete_map={'Faturamento':'darkcyan','Lucro':'cyan'},
                title=f'Faturamento e lucro por loja (Fat. total: R${fattotal:.0f}, Luc. total: R${luctotal:.0f})', barmode='group', labels={'value':'Valor em R$','variable':'Variável'})


# quantidade vendida x categorias pie / 5 produtos mais vendidos bar
subplot1 = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'bar'},{'rowspan':2,'type':'domain'}],
                                               [None, None]], subplot_titles=['Produtos mais vendidos','Quantidade de peças vendidas x Categoria'])
subplot1.update_annotations(font_size=20)

topprod = vendas[['Produto','Quantidade']].groupby('Produto').sum()
p = []
q = []
for c in range(0,5):
    p.append(topprod.idxmax()['Quantidade'])
    q.append(topprod.max()['Quantidade'])
    for i in list(topprod.index):
        if topprod.loc[i,'Quantidade']==topprod.max()['Quantidade']:
            topprod = topprod.drop(i, axis=0)
            break
subplot1.add_trace(go.Bar(x=p, y=q, marker=dict(color='cyan'), name='TOP 5 produtos'), row=1, col=1)
subplot1.update_yaxes(title_text='Quantidade vendida', row=1, col=1)

topcat = vendas[['Categoria','Quantidade']].groupby('Categoria').sum()
c = []
q = []
for i in list(topcat.index):
    c.append(i)
    q.append(topcat.loc[i,'Quantidade'])
subplot1.add_trace(go.Pie(labels=c, values=q, marker=dict(colors=['darkcyan','cyan','royalblue','blue','lightcyan']), hole=0.3), row=1, col=2)


# produção geral line

produção['Data']=pd.to_datetime(produção['Data'])
prodpft = produção.query('Situação == "Não Defeituosa"')
diaxq = prodpft[['Quantidade','Data']].groupby('Data').sum()
for i in list(diaxq.index):
    diaxq.loc[i,'Data']=i
prodtotal = diaxq['Quantidade'].sum()
prodmedia = diaxq['Quantidade'].mean()
dxq = px.line(diaxq, x='Data', y='Quantidade', color_discrete_sequence=['blue'], title=f'Produção ao longo do mês ({prodtotal} peças produzidas, {prodmedia:.0f} em média por dia)', markers=True,
             labels={'Quantidade':'Peças produzidas'})


# produção por categoria bar + produtos mais vendidos na categoria (tive q criar produtos inventados em cada categoria)
topprod = vendas[['Produto','Quantidade']].groupby('Produto').sum()
for i in list(topprod.index):
    topprod.loc[i,'Produto']=i
for i in list(topprod.index):
    if topprod.loc[i,'Produto'] in dic['Inverno']:
        topprod.loc[i,'Categoria']='Inverno'
    if topprod.loc[i,'Produto'] in dic['Verão']:
        topprod.loc[i,'Categoria']='Verão'
    if topprod.loc[i,'Produto'] in dic['Social']:
        topprod.loc[i,'Categoria']='Social'
    if topprod.loc[i,'Produto'] in dic['Casual']:
        topprod.loc[i,'Categoria']='Casual'
    if topprod.loc[i,'Produto'] in dic['Esportivo']:
        topprod.loc[i,'Categoria']='Esportivo'
        
# INVERNO
prodinverno = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'domain'}, {'rowspan':2,'type':'bar'}],
                                                  [None, None]],
                           subplot_titles=['Vendas X Produtos da categoria: Inverno','Peças produzidas X Categoria'])
prodinverno.update_annotations(font_size=20)
prodxcat = prodpft[['Categoria','Quantidade']].groupby('Categoria').sum()
for i in list(prodxcat.index):
    prodxcat.loc[i,'Categoria']=i
prodinverno.add_trace(go.Bar(x=list(prodxcat['Categoria']), y=list(prodxcat['Quantidade']), marker=dict(color=['darkcyan','cyan','royalblue','blue','aquamarine']), name='Categorias'), row=1, col=2)
prodinverno.update_yaxes(title_text='Quantidade', row=1, col=2)

# PRODUTOS
inverno = topprod.query('Categoria == "Inverno"')
prodinverno.add_trace(go.Pie(labels=list(inverno['Produto']), values=list(inverno['Quantidade']), marker=dict(colors=['darkcyan','cyan','royalblue','blue']), hole=0.3), row=1, col=1)



# VERÃO
prodverao = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'domain'}, {'rowspan':2,'type':'bar'}],
                                                  [None, None]],
                           subplot_titles=['Vendas X Produtos da categoria: Verão','Peças produzidas X Categoria'])
prodverao.update_annotations(font_size=20)
prodverao.add_trace(go.Bar(x=list(prodxcat['Categoria']), y=list(prodxcat['Quantidade']), marker=dict(color=['darkcyan','cyan','royalblue','blue','aquamarine']), name='Categorias'), row=1, col=2)
prodverao.update_yaxes(title_text='Quantidade', row=1, col=2)

# PRODUTOS
verao = topprod.query('Categoria == "Verão"')
produtos = list(verao['Produto'])
produtos.append('Sunga')
valores = list(verao['Quantidade'])
valores.append(60)
prodverao.add_trace(go.Pie(labels=produtos, values=valores, marker=dict(colors=['darkcyan','cyan','royalblue','blue']), hole=0.3), row=1, col=1)


# ESPORTIVO
prodesportivo = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'domain'}, {'rowspan':2,'type':'bar'}],
                                                  [None, None]],
                           subplot_titles=['Vendas X Produtos da categoria: Esportivo','Peças produzidas X Categoria'])
prodesportivo.update_annotations(font_size=20)
prodesportivo.add_trace(go.Bar(x=list(prodxcat['Categoria']), y=list(prodxcat['Quantidade']), marker=dict(color=['darkcyan','cyan','royalblue','blue','aquamarine']), name='Categorias'), row=1, col=2)
prodesportivo.update_yaxes(title_text='Quantidade', row=1, col=2)

# PRODUTOS
esportivo = topprod.query('Categoria == "Esportivo"')
produtos = list(esportivo['Produto'])
produtos.append('Tênis de corrida')
produtos.append('Regata')
valores = list(esportivo['Quantidade'])
valores.append(70)
valores.append(80)
prodesportivo.add_trace(go.Pie(labels=produtos, values=valores, marker=dict(colors=['darkcyan','cyan','royalblue','blue']), hole=0.3), row=1, col=1)

# CASUAL
prodcasual = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'domain'}, {'rowspan':2,'type':'bar'}],
                                                  [None, None]],
                           subplot_titles=['Vendas X Produtos da categoria: Casual','Peças produzidas X Categoria'])
prodcasual.update_annotations(font_size=20)
prodcasual.add_trace(go.Bar(x=list(prodxcat['Categoria']), y=list(prodxcat['Quantidade']), marker=dict(color=['darkcyan','cyan','royalblue','blue','aquamarine']), name='Categorias'), row=1, col=2)
prodcasual.update_yaxes(title_text='Quantidade', row=1, col=2)

# PRODUTOS
casual = topprod.query('Categoria == "Casual"')
produtos = list(casual['Produto'])
produtos.append('Moletom')
produtos.append('Camiseta básica')
valores = list(casual['Quantidade'])
valores.append(40)
valores.append(90)
prodcasual.add_trace(go.Pie(labels=produtos, values=valores, marker=dict(colors=['darkcyan','cyan','royalblue','blue']), hole=0.3), row=1, col=1)

# SOCIAL
prodsocial = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'domain'}, {'rowspan':2,'type':'bar'}],
                                                  [None, None]],
                           subplot_titles=['Vendas X Produtos da categoria: Social','Peças produzidas X Categoria'])
prodsocial.update_annotations(font_size=20)
prodsocial.add_trace(go.Bar(x=list(prodxcat['Categoria']), y=list(prodxcat['Quantidade']), marker=dict(color=['darkcyan','cyan','royalblue','blue','aquamarine']), name='Categorias'), row=1, col=2)
prodsocial.update_yaxes(title_text='Quantidade', row=1, col=2)

# PRODUTOS
social = topprod.query('Categoria == "Social"')
produtos = list(social['Produto'])
produtos.append('Terno')
produtos.append('Calça linho')
produtos.append('Chapéu')
produtos.append('Camiseta linho')
valores = list(social['Quantidade'])
valores.append(100)
valores.append(30)
valores.append(40)
valores.append(35)
prodsocial.add_trace(go.Pie(labels=produtos, values=valores, marker=dict(colors=['darkcyan','cyan','royalblue','blue']), hole=0.3), row=1, col=1)

# métodos de pagamentos x vendas pie
pag = ['Pix','Débito','Dinheiro','Crédito']
v = []
pagxv = vendas[['Pagamento','Quantidade']].groupby('Pagamento').sum()
for p in pag:
    v.append(pagxv.loc[p,'Quantidade'])
metpag = px.pie(names=pag, values=v, title='Vendas X Método de pagamento', color_discrete_sequence=['darkcyan','cyan','royalblue','blue'], hole=0.3)

# CONTROLE DE ESTOQUE

vendidos = vendas[['Produto','Quantidade']].groupby('Produto').sum()
for i in list(vendidos.index):
    vendidos.loc[i,'Produto']=i
for i in list(vendidos.index):
    for p in list(estoque.index):
        if vendidos.loc[i,'Produto']==estoque.loc[p,'Produto']:
            vendidos.loc[i,'Estoque antigo']=estoque.loc[p,'Estoque Atual']
            break
vendidos.rename(columns={'Quantidade':'Quantidade vendida'}, inplace=True)
vendidos['Estoque Atual']=vendidos['Estoque antigo']-vendidos['Quantidade vendida']
control = px.bar(vendidos, x='Produto', y=['Estoque antigo','Quantidade vendida','Estoque Atual'], color_discrete_map={'Estoque antigo':'darkcyan','Quantidade vendida':'red','Estoque Atual':'cyan'},
                title='Controle de estoque', barmode='group', labels={'value':'Quantidade','variable':'Variável'})




# APP
app =  Dash(__name__)
server = app.server

# INSIDE
app.layout = html.Div(children=[
    html.H1(children='ANÁLISE DE VENDAS/PRODUÇÃO'),
    dcc.Graph(id = 'G1',figure=flxloja),
    dcc.Graph(id = 'G2',figure=subplot1),
    html.H3(children='Escolha a categoria abaixo'),
    dcc.Dropdown(['Inverno','Verão','Esportivo','Casual','Social'], value='Inverno', id = 'botao'),
    dcc.Graph(id = 'G3',figure=prodinverno),
    dcc.Graph(id = 'G4',figure=dxq),
    dcc.Graph(id = 'G5',figure=metpag),
    dcc.Graph(id = 'G6',figure=control),
])




# callbacks
@app.callback(Output('G3','figure'),
             Input('botao','value'))
def update_estprev(value):
    if value=='Inverno':
        return prodinverno
    if value=='Verão':
        return prodverao
    if value=='Esportivo':
        return prodesportivo
    if value=='Casual':
        return prodcasual
    if value=='Social':
        return prodsocial
        
# RODANDO
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050)) 
    app.run_server(debug=True, host="0.0.0.0", port=port)

