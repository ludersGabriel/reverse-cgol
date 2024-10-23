#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

/*
As regras que definem a evolução de um estado para outro do jogo são:

  - toda célula morta com exatamente três vizinhos vivos torna-se viva;
  - toda célula viva com menos de dois vizinhos vivos morre;
  - toda célula viva com mais de três vizinhos vivos morre;
  - toda célula viva com dois ou três vizinhos vivos permanece viva.

  Uma instância é dada por um arquivo texto no seguinte formato:

  - a primeira linha do arquivo tem 2 números inteiros n e m,
    separados por espaço, onde n é o número de linhas do tabuleiro e
    m é o número de colunas do tabuleiro;

  - o restante do arquivo contém n linhas com m números inteiros cada,
    separados por espaços, o valor 0 representa uma célula morta e o
    valor 1 representa uma célula viva;

  - todas células das bordas da matriz, da primeira e da última linha
    e da primeira e da última coluna estão mortas;

  - o exemplo abaixo é uma instância do jogo com 4 linhas e 6 colunas:

  4 6
  0 0 0 0 0 0
  0 0 1 1 0 0
  0 0 0 1 1 0
  0 0 0 0 0 0

  - As regras são aplicadas simultaneamente em todas as células para chegar
  ao próximo estado do jogo.

  - A vizinhança de uma célula é dada pelos seus 8 vizinhos adjacentes.
  - A vizinhança das células das bordas do tabuleiro deve considerar os vizinhos
inexistentes como células mortas.

  - O objetivo do seu programa é reverter o jogo, encontrar um estado
  imediatamente anterior ao estado dado como entrada. Ainda, o estado
  anterior a ser encontrado deve minimizar o número de células vivas da matriz.

  - A saída do seu programa deve ser pela saída padrão do sistema e deve conter
uma matriz, no mesmo formato e tamanho da matriz dada como entrada, que
represente um estado imediatamente anterior ao estado dado na entrada.  
*/

typedef struct {
  int n;
  int m;
  int** board;
} Game;

void freeBoard(Game* game) {
  for (int i = 0; i < game->n; i++) {
    free(game->board[i]);
  }
  free(game->board);
}

void readInput(Game* game) {
  int n, m;
  int** board;
  scanf("%d %d", &n, &m);
  board = (int**)malloc(n * sizeof(int*));
  for (int i = 0; i < n; i++) {
    board[i] = (int*)malloc(m * sizeof(int));
    for (int j = 0; j < m; j++) {
      scanf("%d", &board[i][j]);
    }
  }
  game->n = n;
  game->m = m;
  game->board = board;
}

void printBoard(Game* game) {
  for (int i = 0; i < game->n; i++) {
    for (int j = 0; j < game->m; j++) {
      printf("%d ", game->board[i][j]);
    }
    printf("\n");
  }
}

void prettyPrint(Game* game) {
  for (int i = 0; i < game->n; i++) {
    for (int j = 0; j < game->m; j++) {
      if (game->board[i][j] == 1) {
        printf("X ");
      } else {
        printf("  ");
      }
    }
    printf("\n");
  }
}

int neighbours(Game* game, int i, int j) {
  int count = 0;
  for (int x = i - 1; x <= i + 1; x++) {
    for (int y = j - 1; y <= j + 1; y++) {
      if (x >= 0 && x < game->n && y >= 0 && y < game->m) {
        count += game->board[x][y];
      }
    }
  }
  return count - game->board[i][j];
}

void nextGeneration(Game* game) {
  int** newBoard = (int**)malloc(game->n * sizeof(int*));
  for (int i = 0; i < game->n; i++) {
    newBoard[i] = (int*)malloc(game->m * sizeof(int));
    for (int j = 0; j < game->m; j++) {
      int count = neighbours(game, i, j);
      if (game->board[i][j] == 1) {
        if (count < 2 || count > 3) {
          newBoard[i][j] = 0;
        } else {
          newBoard[i][j] = 1;
        }
      } else {
        if (count == 3) {
          newBoard[i][j] = 1;
        } else {
          newBoard[i][j] = 0;
        }
      }
    }
  }

  freeBoard(game);
  game->board = newBoard;
}

int main() {
  Game game;
  readInput(&game);

  system("clear");
  while (1) {
    prettyPrint(&game);
    nextGeneration(&game);
    sleep(1);
    system("clear");
  }

  freeBoard(&game);

  return 0;
}