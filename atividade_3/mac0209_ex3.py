import matplotlib.pyplot as plt
from datetime import datetime
import json
import numpy as np
from pyproj import Proj, transform

"""# Carregando o arquivo de dados do KartaView

Vamos agora analisar os dados coletados através da plataforma KartaView.

Esses dados estão formatados usando-se o formato JSON de JavaScript Object Notation.

Um arquivo JSON é um arquivo de texto com uma mensagem estruturada com o formato JSON.
"""

# Vamos carregar os pontos (do JSON filtrado) na variável pontos.
arquivo_pontos = "cleaned_sample2.json"

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


"""### def get_point_coords_proj(index, points_object)

Essa função auxiliar faz exatamente o mesmo que a anterior, contudo os pontos aqui são reprojetados para a projeção EPSG:3857, que usa como unidade métrica o 'metro' ao invés de graus de ângulo.
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
    return p


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
    return np.sqrt(np.sum((v1-v2)**2))


"""# Modelagem e predições

Vamos amostrar agora um trecho do trajeto e com base nesta amostra vamos calcular a velocidade média ao longo do trajeto principal, em várias partes do trajeto. Além disso também vamos tentar predizer com este modelo qual a posição do veículo (i.e. distância percorrida ao longo do trajeto) em instantes de tempo que não foram amostrados.

## Exercício 1 - Distância e tempo decorrido até um ponto dado

A projeção de coordenadas esféricas para o plano cartesiano é uma operação computacionalmente demorada. Assim, executamos previamente a projeção das coordenadas do sistema de coordenadas EPSG:4326 (coordenadas esféricas) para o sistema de coordenadas EPSG:3857 (com coordenadas no plano cartesiano e unidades em metros). As coordenadas convertidas foram armazenadas no próprio arquivo json com os pontos de cada foto. As novas propriedades se chamam `easting` indicando em metros a posição da foto no eixo horizontal e `northing` indicando também em metros a posição da foto no eixo vertical.

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

tinicio = 3000
tfim = 3180
pontos_intervalo = get_points_in_time_interval(tinicio, tfim, pontos)
print(f"Número de pontos no intervalo: {len(pontos_intervalo)}") 
print(f"Instante inicial do intervalo: {pontos_intervalo[0]['tempo_decorrido']} segundos")
print(f"Instante final do intervalo: {pontos_intervalo[-1]['tempo_decorrido']} segundos")

# Os pontos abaixos foram selecionados de forma que entre cada um deles se passam exatamente 18 segundos.
sample_points = [pontos_intervalo[i] for i in [0, 13, 25, 38, 51, 64, 76, 89, 101, 113, 126]]

print(f"Número de pontos amostrados: {len(sample_points)}")

"""## Exercício 2. Usando os pontos selecionados acima, calcule a velocidade média em cada trecho e compare com a velocidade média no trecho todo (tinicio=3000 até tfim=3180). 

Para organizar melhor seu trabalho para os próximos exercícios, crie três vetores:
- tempos - vetor com a lista dos tempo em que cada ponto foi alcançado
- distancias - vetor com a lista das distâncias acumuladas em cada trecho (entre cada um ponto e outro). 
- velocidades - vetor com a lista de velocidades médias em cada trecho.
"""



"""### Visualização das amostras - O código abaixo serve para você visualizar a posição do carro em função do tempo."""

def plot_dist_time(dist_vec, time_vec, marker='.', **kwargs):
    fig, ax = plt.subplots(1, **kwargs)
    #fig, ax = plt.subplots(1, figsize=(16,8))
    ax.scatter(time_vec, dist_vec, marker=marker)
    ax.set_xlabel('tempo decorrido (s)', fontsize=14);
    ax.set_ylabel('distância percorrida (m)', fontsize=14);
    return fig, ax

fig, ax = plot_dist_time(distancias, tempos, marker='x')
#plt.scatter(tempos, distancias, marker='x')
#plt.xlabel('tempo (s)')
#plt.ylabel('distância (m)')

"""## Exercício 3. Faça agora um gráfico das velocidades médias calculadas.

"""



"""## Exercício 4. Faça o mesmo para o trajeto completo, isto é, do primeiro ponto até o último ponto do arquivo cleaned_sample3.json.

Se você fez o gráfico corretamente, você verá três trechos em que a velocidade é aproximadamente constante. 

## Exercício 5. Calcule a velocidade média em cada trecho em que a velocidade é aproximadamente constante.

## Exercício 6. Tente explicar em palavras o que acontece nas descontinuidades do gráfico.


"""



"""## Exercício 7. Usando as velocidades médias calculadas no exercício 5, estabeleça uma posição inicial para cada trecho e calcule a posição do veículo para 50 pontos de acordo com o modelo de movimento uniforme e compare, medindo o erro entre a posição calculada e a posição observada do veículo. Faça um gráfico da dispersão dos erros para cada trecho. """