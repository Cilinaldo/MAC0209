import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def dados_acelerometro():
    acelerometro = pd.read_csv("https://www.ime.usp.br/~cesar/courses/mac0209/quedaLivreData.csv")

    acelerometro = np.array(acelerometro)

    x = acelerometro[:, 0]
    y = acelerometro[:, 4]

    fig, ax = plt.subplots()
    plt.plot(x,y)
    plt.title('Dados do acelerometro')
    ax.set_xlabel('Tempo (segundos)')
    ax.set_ylabel('Resultante (forca g)')

    plt.show()

    # zoom na queda
    t0 = 500
    tf = 800

    x = acelerometro[t0:tf, 0]
    y = acelerometro[t0:tf, 4]

    fig, ax = plt.subplots()
    plt.plot(x, y)
    plt.title('Dados do acelerometro: zoom na queda')
    ax.set_xlabel('Tempo (segundos)')
    ax.set_ylabel('Resultante (forca g)')

    plt.show()

    # zoom na queda + passagem
    t0 = 500
    tf = 4700

    x = acelerometro[t0:tf,0]
    y = acelerometro[t0:tf,4]

    fig, ax = plt.subplots()
    plt.plot(x, y)
    plt.title('Dados do acelerometro: zoom na queda + passagem')
    ax.set_xlabel('Tempo (segundos)')
    ax.set_ylabel('Resultante (forca g)')

    plt.show()


if __name__ == '__main__':
    dados_acelerometro()