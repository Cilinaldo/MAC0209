import matplotlib.pyplot as plt
import json
import numpy as np
from pyproj import Proj, transform
import warnings
from datetime import datetime
from random import randint


""" para ignorar todos os warnings """
warnings.filterwarnings('ignore')

"""# Carregando o arquivo de dados do KartaView

Vamos agora analisar os dados coletados através da plataforma KartaView.

Esses dados estão formatados usando-se o formato JSON de JavaScript Object Notation.

Um arquivo JSON é um arquivo de texto com uma mensagem estruturada com o formato JSON.
"""

# Vamos carregar os pontos (do JSON filtrado) na variável pontos.
arquivo_pontos = "cleaned_sample2.json"
arquivo_pontos2 = "cleaned_sample3.json"

with open(arquivo_pontos, "r") as f:
    pontos = f.read()
    pontos = json.loads(pontos)


"""# Medindo distâncias

## Funções auxiliares

Para facilitar a escrita do código e terminarmos com código adequado ao problema que queremos resolver, ao invés de nos preocuparmos com
detalhes da estrutura interna dos dados, vamos definir aqui algumas funções auxiliares com a responsabilidade exclusiva de coletar uma propriedade específica da lista de pontos, possivelmente tratando o dado coletado.


### def get_point_coords(index, points_object)

Essa função irá nos auxiliar para coletar as coordenadas (e.g. longitude e latitude) de um ponto (na posição 'index') da lista de pontos passado também como parâmetro da função.

Note que as coordenadas dos pontos (no arquivo de dados) usam a projeção EPSG:4326, isso significa que estas coordenadas são angulos e portanto precisamos fazer uma conversão, ou mais precisamente uma (re)projeção em um outro sistema de coordenadas (i.e. CRS) que use unidades métricas (e.g. metros).
"""


def get_point_coords(index, points_object):
    """
    Essa função recebe um índice numérico correspondendo a uma
    posição na lista de pontos "points_object".
    
    Ela retorna um vetor do numpy com a longitude e latitude
    (propriedades 'lng' e 'lat') do ponto na posição 'index'.
    """
    lat = points_object[index]['lat']
    lat = float(lat)
    lng = points_object[index]['lng']
    lng = float(lng)
    return np.array((lng, lat))


"""
### def get_point_coords_proj(index, points_object)

Essa função auxiliar faz exatamente o mesmo que a anterior, contudo os pontos aqui são reprojetados para a projeção EPSG:3857, 
que usa como unidade métrica o 'metro' ao invés de graus de ângulo.
"""


def get_point_coords_proj(index, points_object):
    """
    Essa função é similar a get_point_coords, ela 
    recebe um índice numérico correspondendo a uma
    posição na lista de pontos "points_object".
    
    Contudo esta os pontos na projeção EPSG:3857 em
    que a unidade de medida é em metros e portanto
    podemos calcular a distância euclidiana entre dois
    pontos com base em suas coordenadas.
    
    Os pontos retornados são um vetor numpy em que
    a primeira posição é uma medida em metros no eixo
    horizontal e a segunda é num eixo vertical.
    O ponto de origem pode ser visto aqui https://epsg.io/3857
    """

    lat = points_object[index]['lat']
    lat = float(lat)
    lng = points_object[index]['lng']
    lng = float(lng)
    p = np.array((lng, lat))
    p = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), p[0], p[1])
    return np.asarray(p)


"""### def get_shot_time(index, points_object)

Esta função é um acessor para a propriedade 'shot_date' na lista de pontos. Essa propriedade indica o momento (dia e hora incluindo segundos) em que o ponto foi criado.
"""

FMT = '%Y-%m-%d %H:%M:%S'


def get_shot_time(index, points_object):
    """
    Retorna a data e hora em que o ponto 'index',
    da lista de pontos 'points_object', foi criado.
    
    O formato de retorno é uma string '%Y-%m-%d %H:%M:%S'
    (e.g. 2018-03-03 20:55:32)
    """
    t = points_object[index]['shot_date']
    t = datetime.strptime(t, FMT)
    return t


def get_points_in_time_interval(min_sec, max_sec, points_object):
    selected_points = []
    for i in range(len(points_object)):
        point = points_object[i]
        if point['tempo_decorrido'] < min_sec:
            continue
        if point['tempo_decorrido'] > max_sec:
            break
        selected_points.append(point)
    return selected_points


def distancia_euclidiana(v1, v2):
    """
    Tendo como parâmetros os vetores numpy 2D 'v1' e 'v2', crie uma
    função que retorne a distância euclidiana entre os dois vetores.
    """
    return np.sqrt(np.sum((v1 - v2) ** 2))


"""# Modelagem e predições

Vamos amostrar agora um trecho do trajeto e com base nesta amostra vamos calcular a velocidade média ao longo do 
trajeto principal, em várias partes do trajeto. Além disso também vamos tentar predizer com este modelo qual a posição do
veículo (i.e. distância percorrida ao longo do trajeto) em instantes de tempo que não foram amostrados.

## Exercício 1 - Distância e tempo decorrido até um ponto dado

A projeção de coordenadas esféricas para o plano cartesiano é uma operação computacionalmente demorada. 
Assim, executamos previamente a projeção das coordenadas do sistema de coordenadas EPSG:4326 (coordenadas esféricas) 
para o sistema de coordenadas EPSG:3857 (com coordenadas no plano cartesiano e unidades em metros). 
As coordenadas convertidas foram armazenadas no próprio arquivo json com os pontos de cada foto.
As novas propriedades se chamam `easting` indicando em metros a posição da foto no eixo horizontal e
`northing` indicando também em metros a posição da foto no eixo vertical.

O código abaixo ilustra como estas propriedades foram calculadas e como foram inseridas no arquivo json dos dados (i.e. `cleaned_sample2.json`):

```
from tqdm.auto import tqdm
for i in tqdm(range(len(pontos))):
    if pontos[i].get('easting') is not None:
        continue
    easting, northing = get_point_coords_proj(i, pontos)
    pontos[i]['easting'] = easting
    pontos[i]['northing'] = northing

with open('cleaned_sample2.json', 'w+') as f:
    json.dump(pontos, f, indent=2)
```

Exercício 1A - Usando o arquivo `cleaned_sample2.json` você deve calcular a distância percorrida desde o ínicio do trajeto escolhido até um ponto atual dado (em metros) usando as novas propriedades `easting` e `northing`. Assuma que a distância percorrida até o início do trajeto (primeiro ponto) é zero.

Exercício 1B - Você também deve calcular o tempo decorrido (em segundos) desde o ínicio do trajeto escolhido até o ponto atual dado.

Exercício 1C - Insira os valores calculados como novas propriedades dos pontos chamadas `distancia_percorrida` e `tempo_decorrido` (em segundos) e salve essa nova coleção de pontos num novo arquivo json chamado `cleaned_sample3.json`.
"""


# Dica, para pegar e calcular a diferença de tempo entre dois pontos você pode usar a função get_shot_time:
tdelta = get_shot_time(1, pontos)-get_shot_time(0, pontos)
print(f"A diferença entre dois objetos 'datetime' gera um objeto 'timedelta': {type(tdelta)}")
print(f"Exemplo do objeto 'timedelta': {tdelta}")
print(f'Segundos decorridos: {tdelta.seconds}')


# Exercício 1 A, B e C.
def exercicio_1(indice, pontos):
    """
    Calcula as distancias percorridas e o tempo transcorrido associado a cada ponto.
    Insere os valores como elementos de cada item no dicionário postos
    """
    for i in range(indice):
        if i == 0:
            pontos[i]['distancia_percorrida'] = 0
            pontos[i]['tempo_decorrido'] = 0
        else:
            s0 = np.asarray([pontos[i - 1]['easting'], pontos[i - 1]['northing']])
            sf = np.asarray([pontos[i]['easting'], pontos[i]['northing']])
            pontos[i]['distancia_percorrida'] = distancia_euclidiana(s0, sf) + pontos[i - 1]['distancia_percorrida']
            pontos[i]['tempo_decorrido'] = (get_shot_time(i, pontos) - get_shot_time(i - 1, pontos)).seconds + \
                                            pontos[i - 1]['tempo_decorrido']


exercicio_1(len(pontos), pontos)

print(pontos[3])
print(pontos[1000])
"""Se tudo der certo, um ponto no ínicio do trajeto (índice baixo) vai ser parecido com o abaixo:


`pontos[3]`

```
{'lat': '32.188302',
 'lng': '-81.195051',
 'heading': '124.32529',
 'shot_date': '2018-03-03 20:29:53',
 'easting': -9038591.73225388,
 'northing': 3788053.65048532,
 'tempo_decorrido': 17,
 'distancia_percorrida': 30.770423073027203}
```

e um ponto mais pro meio do trajeto vai parecer com algo assim:

`pontos[1000]`

```
{'lat': '32.450081',
 'lng': '-80.991726',
 'heading': '57.014393',
 'shot_date': '2018-03-03 20:53:26',
 'easting': -9015957.696788337,
 'northing': 3822536.8402403975,
 'tempo_decorrido': 1430,
 'distancia_percorrida': 43456.56002203702}
```

## Selecionando um intervalo para análise do movimento

Assumindo que o vetor de pontos (i.e. `pontos`) agora contém objetos com as propriedades `distancia_percorrida` e `tempo_decorrido` podemos usar estas novas propriedades para analisar o movimento.

Como exemplo, selecionamos um intervalo que irá conter pontos que ocorrem após `tinicio` segundos e antes de  `tfim` segundos após o ínicio do percurso. Esses pontos foram escolhidos pois correspondem a um trecho de estrada que parece-se com uma reta.
"""

# Escreve o arquivo cleaned_sample3.json
with open(arquivo_pontos2, "w") as f:
    f.write(json.dumps(pontos))


tinicio = 3000
tfim = 3180
pontos_intervalo = get_points_in_time_interval(tinicio, tfim, pontos)
print(f"Número de pontos no intervalo: {len(pontos_intervalo)}")
print(f"Instante inicial do intervalo: {pontos_intervalo[0]['tempo_decorrido']} segundos")
print(f"Instante final do intervalo: {pontos_intervalo[-1]['tempo_decorrido']} segundos")

# Os pontos abaixos foram selecionados de forma que entre cada um deles se passam exatamente 18 segundos.
sample_points = [pontos_intervalo[i] for i in [0, 13, 25, 38, 51, 64, 76, 89, 101, 113, 126]]

print(f"Número de pontos amostrados: {len(sample_points)}")

"""### Visualização das amostras - O código abaixo serve para você visualizar a posição do carro em função do tempo."""


def plot_dist_time(dist_vec, time_vec, marker='.', **kwargs):
    fig, ax = plt.subplots(1, **kwargs)
    # fig, ax = plt.subplots(1, figsize=(16,8))
    ax.scatter(time_vec, dist_vec, marker=marker)
    ax.set_xlabel('tempo decorrido (s)', fontsize=14);
    ax.set_ylabel('distância percorrida (m)', fontsize=14);
    return fig, ax


"""## Exercício 2. Usando os pontos selecionados acima, calcule a velocidade média em cada trecho e compare com a velocidade média no trecho todo (tinicio=3000 até tfim=3180).

Para organizar melhor seu trabalho para os próximos exercícios, crie três vetores:
- tempos - vetor com a lista dos tempo em que cada ponto foi alcançado
- distancias - vetor com a lista das distâncias acumuladas em cada trecho (entre cada um ponto e outro).
- velocidades - vetor com a lista de velocidades médias em cada trecho.
"""


tempos = [x['tempo_decorrido'] for x in sample_points]
distancias = [y['distancia_percorrida'] for y in sample_points]
velocidades = [(distancias[i] - distancias[i-1])/(tempos[i] - tempos[i-1]) for i in range(1, len(sample_points))]


velocidade_media = (distancias[-1] - distancias[0])/(tempos[-1] - tempos[0])

fig, ax0 = plot_dist_time(velocidades, tempos[1:], marker='x');
plt.hlines(velocidade_media, tempos[-1], tempos[0], colors='red', linestyle='--', label='vel. média do trecho')
plt.legend(loc='center right')
plt.xlabel('tempo (s)')
plt.ylabel('velocidade  (m/s)')
plt.show()


"""## Exercício 3. Faça agora um gráfico das velocidades médias calculadas.

"""
fig, ax = plot_dist_time(distancias, tempos, marker='.')
plt.show()



"""## Exercício 4. Faça o mesmo para o trajeto completo, isto é, do primeiro ponto até o último ponto do arquivo cleaned_sample3.json.

Se você fez o gráfico corretamente, você verá três trechos em que a velocidade é aproximadamente constante.

## Exercício 5. Calcule a velocidade média em cada trecho em que a velocidade é aproximadamente constante.

## Exercício 6. Tente explicar em palavras o que acontece nas descontinuidades do gráfico.


"""
with open(arquivo_pontos2, "r") as f:
    complete_points = f.read()
    complete_points = json.loads(complete_points)

distancias = [y['distancia_percorrida'] for y in complete_points]
tempos = [x['tempo_decorrido'] for x in complete_points]
velocidades = [(distancias[i] - distancias[i - 1]) / (tempos[i] - tempos[i - 1]) for i in range(1, len(complete_points))]
fig, ax = plot_dist_time(distancias, tempos, marker='.')
plt.show()

"""
Nota-se que os trechos são: 
trecho 1 -> tempos[0:1265] 
trecho 2 -> tempos[1266:2793] 
trecho 3 -> tempos[2794:7847] 

Os trechos do (tempos[1266] - tempos[1264]) = 381 segundos e (tempos[2794] - tempos[2792]) = 267 são momentos no qual o descolamento é praticamente nulo, 

"""

velocidade_media_trecho1 = (distancias[1264] - distancias[0])/(tempos[1264] - tempos[0])
print(f'velocidade no trecho 1 = {velocidade_media_trecho1} (m/s)')
velocidade_media_trecho2 = (distancias[2792] - distancias[1266])/(tempos[2792] - tempos[1266])
print(f'velocidade no trecho 2 = {velocidade_media_trecho2} (m/s)')
velocidade_media_trecho3 = (distancias[7847] - distancias[2794])/(tempos[7847] - tempos[2794])
print(f'velocidade no trecho 3 = {velocidade_media_trecho3} (m/s)')

print('As descontinuidades refletem momentos de repouso, ou seja, intervalos de tempo em que o registro de deslocamento é praticamente nulo')


"""## Exercício 7. Usando as velocidades médias calculadas no exercício 5, estabeleça uma posição inicial para cada trecho e calcule a posição do veículo para 50 pontos de acordo com o modelo de movimento uniforme e compare, medindo o erro entre a posição calculada e a posição observada do veículo. Faça um gráfico da dispersão dos erros para cada trecho. """

# PRIMEIRO TRECHO
## Equação horária do trecho 1
def equacao_horaria_trecho1(tempo, i):
    return distancias[0] + velocidade_media_trecho1*(tempo-complete_points[0]['tempo_decorrido'])

# pontos escolhidos com base no tempo
indices_trecho1 = sorted([ randint(0,1265) for i in range(50) ])


# posicoes observadas
posicoes_observadas = []
for i in indices_trecho1:
    posicoes_observadas.append(complete_points[i]['distancia_percorrida'])

# posições calculada para cada ponto de tempo escolhido
posicoes_calculadas = [equacao_horaria_trecho1(tempos[i], i) for i in indices_trecho1]


# calculo de erro
erros = [abs(posicoes_calculadas[i] - posicoes_observadas[i]) for i in range(50)]

t = [tempos[i] for i in indices_trecho1]
fig, ax0 = plot_dist_time(erros, t, marker='.')
plt.xlabel('Tempo (s)')
plt.ylabel('Erro (m)')
plt.title("Dispersão de erros no Trecho 1")
plt.show()


# SEGUNDO TRECHO
## Equação horária do trecho 2
def equacao_horaria_trecho2(tempo, i):
    return distancias[1266] + velocidade_media_trecho2*(tempo-complete_points[1266]['tempo_decorrido'])

# pontos escolhidos com base no tempo
indices_trecho2 = sorted([ randint(1266,2793) for i in range(50) ])


# posicoes observadas
posicoes_observadas = []
for i in indices_trecho2:
    posicoes_observadas.append(complete_points[i]['distancia_percorrida'])

# posições calculada para cada ponto de tempo escolhido
posicoes_calculadas = [equacao_horaria_trecho2(tempos[i], i) for i in indices_trecho2]


# calculo de erro
erros = [abs(posicoes_calculadas[i] - posicoes_observadas[i]) for i in range(50)]

t = [tempos[i] for i in indices_trecho2]
fig, ax0 = plot_dist_time(erros, t, marker='.')
plt.xlabel('Tempo (s)')
plt.ylabel('Erro (m)')
plt.title("Dispersão de erros no Trecho 2")
plt.show()


# TRECHO 3
## Equação horária do trecho 3
def equacao_horaria_trecho3(tempo, i):
    return distancias[2794] + velocidade_media_trecho3*(tempo-complete_points[2794]['tempo_decorrido'])

# pontos escolhidos com base no tempo
indices_trecho3 = sorted([ randint(2794,7847) for i in range(50) ])

# posicoes observadas
posicoes_observadas = []
for i in indices_trecho3:
    posicoes_observadas.append(complete_points[i]['distancia_percorrida'])

# posições calculada para cada ponto de tempo escolhido
posicoes_calculadas = [equacao_horaria_trecho3(tempos[i], i) for i in indices_trecho3]


# calculo de erro
erros = [abs(posicoes_calculadas[i] - posicoes_observadas[i]) for i in range(50)]

t = [tempos[i] for i in indices_trecho3]
fig, ax0 = plot_dist_time(erros, t, marker='.')
plt.xlabel('Tempo (s)')
plt.ylabel('Erro (m)')
plt.title("Dispersão de erros no Trecho 3")
plt.show()