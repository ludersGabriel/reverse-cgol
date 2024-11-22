#include <bits/stdc++.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

using namespace std;
#define uint unsigned


// splits a string
vector<string> split(const string& s, char delimiter)  
 {
    vector<string> tokens;
    stringstream ss(s);
    string token;

    while (getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }

    return tokens;
}

// runs lls with verbose 1
void run_lls(uint limit)
{
  char* cmd = (char*) malloc(sizeof(char) * 70);
  if (!cmd) {cout << "run lls malloc error"; exit(1);}

  if (limit == 0)
    limit = 0xFFFFFFFF;

  sprintf(
    cmd,
    "python3 lls-project/lls.py -v 1 -p '<=%u' < out.txt > result.txt",
    limit
  );

  system(cmd);
}


// Reads stdin, process it and write to a file out.txt
void process_input(uint lin, uint col)
{
  vector<vector<uint>> input (lin, vector<uint> (col));

  for (uint i = 0; i < lin; i++)
    for (uint j = 0; j < col; j++)
      cin >> input[i][j];

  vector<vector<char>> preproc (lin, vector<char> (col, '0'));

  for (int i = 0; i < lin; i++)
    for (int j = 0; j < col; j++)
      if (input[i][j]) {
        preproc[i - 1][j - 1] = '*';
        preproc[i - 1][j]     = '*';
        preproc[i - 1][j + 1] = '*';
        preproc[i][j - 1]     = '*';
        preproc[i][j]         = '*';
        preproc[i][j + 1]     = '*';
        preproc[i + 1][j - 1] = '*';
        preproc[i + 1][j]     = '*';
        preproc[i + 1][j + 1] = '*';
      }

  ofstream output ("out.txt");

  for (vector<char> line : preproc) {
    for (char c : line)
      output << c << ' ';
    output << endl;
  }
  
  output << endl << endl;

  for (vector<uint> line : input) {
    for (uint c : line)
      output << c << ' ';
    output << endl;
  }

  output.close();
}


// reads the result file and return number of cells alive
uint get_live_cells()
{
  ifstream result ("result.txt");

  string str;

  // get live cells line
  getline(result, str);
  vector<string> parts = split(str, ' ');
  uint live_cells = stoul(parts[2]);

  result.close();

  return live_cells;
}

// performas a bsearch narrowing the possible -p values
void b_search()
{
  run_lls(0);

  uint live_cells = get_live_cells();

  uint low = 0, high = live_cells;
  uint mid;
  uint best_p_value;

  string line;
  //Binary search to find the minimum satisfiable -p value
  while (low <= high) {
    mid = (low + high) / 2;

    run_lls(mid);

    live_cells = get_live_cells();

    // get result line
    ifstream result ("result.txt");

    getline(result, line);
    getline(result, line);

    result.close();

    if (line == "Unsatisfiable") {
      low = mid + 1;  // Increase the range
    }
    else {
      best_p_value = mid;
      high = mid - 1;  // Decrease the range
    }
  }
}


void print_result(uint lin, uint col)
{
  ifstream result ("result.txt");

  string str;

  // get live cells line
  getline(result, str);

  // remove header
  getline(result, str);
  getline(result, str);

  // print board
  char c;
  for (uint i = 0; i < lin; i++) {
    // remove first col
    result >> c;

    for (uint j = 0; j < col; j++) {
      result >> c;
      cout << c << ' ';
    }
    cout << endl;

    // remove last col and trail
    result >> c >> c;
  }
}


int main()
{
  uint lin, col;
  cin >> lin >> col;

  process_input(lin, col);

  b_search();

  print_result(lin, col);

  return 0;
}