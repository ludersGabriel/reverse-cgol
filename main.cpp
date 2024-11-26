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

  #ifdef DEBUG
  cout << "Teste p value: " << limit << endl << flush;
  #endif
  sprintf(
    cmd,
    "python3 lls-project/lls.py -v 1 -p '<=%u' < out.txt > result.txt",
    limit
  );

  system(cmd);
}

void write_pos(vector<vector<char>>& preproc, int i, int j, char c)
{
  if (i < 0 || j < 0 || i >= preproc.size() || j >= preproc[0].size()) return;
  preproc[i][j] = c;
}



// Reads stdin, process it and write to a file out.txt
void process_input(uint lin, uint col)
{
  vector<vector<uint>> input (lin, vector<uint> (col));

  for (uint i = 0; i < lin; i++)
    for (uint j = 0; j < col; j++)
      cin >> input[i][j];

  vector<vector<char>> preproc (lin, vector<char> (col, '0'));
  /*
  x x 0 x x 
  x 0 0 0 x
  0 0 1 0 0
  x 0 0 0 x
  x x 0 x x
  */
  for (int i = 0; i < lin; i++)
    for (int j = 0; j < col; j++)
      if (input[i][j]) {
        for (int l = -2; l < 2; l++)
          for (int k = -2; k < 2; k++) {
            if (abs(l) + abs(k) <= 2)
              write_pos(preproc, i + l, j + k, '*');
          }
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
pair<uint, bool> get_info()
{
  string str;
  ifstream result ("result.txt");
  getline(result, str); // get live cells line

  vector<string> parts = split(str, ' ');
  uint live_cells = stoul(parts[2]);

  getline(result, str); // get unsat line

  result.close();

  return {live_cells, str == "Unsatisfiable"};
}



// performs a bsearch narrowing the possible -p values
bool b_search()
{
  // run a limitless lls
  run_lls(0);

  auto [live_cells, unsat] = get_info();
  if (unsat)
    return true;

  #ifdef DEBUG
  cout << live_cells << " SAT" << endl << flush;
  #endif

  system("cp result.txt best_result.txt");

  uint low = 0, high = live_cells;
  uint mid = (low + high) / 2;

  string line;
  //Binary search to find the minimum satisfiable -p value

  bool increasing = false;
  while (low < high) {
    run_lls(mid);

    auto [live_cells, unsat] = get_info();
    #ifdef DEBUG
    cout << live_cells << ' ' << flush;
    #endif

    if (unsat) {
      #ifdef DEBUG
      cout << "UNSAT" << endl << flush; 
      #endif
      low = mid + 1;
    }
    else {
      system("cp result.txt best_result.txt");
      #ifdef DEBUG
      cout << "SAT" << endl << flush;
      #endif
      high = mid - 1;
    }

    mid = (low + high) / 2;
  }

  return false;
}

// // performs a bsearch narrowing the possible -p values
// bool b_search()
// {
//   // run a limitless lls
//   run_lls(0);

//   auto [live_cells, unsat] = get_info();
//   if (unsat)
//     return true;

//   #ifdef DEBUG
//   cout << live_cells << " SAT" << endl << flush;
//   #endif

//   system("cp result.txt best_result.txt");

//   uint test = live_cells - 10;
//   uint lim = live_cells;

//   string line;
//   //Binary search to find the minimum satisfiable -p value

//   bool increasing = false;
//   while (test < lim) {
//     run_lls(test);

//     auto [live_cells, unsat] = get_info();
//     #ifdef DEBUG
//     cout << live_cells << ' ' << flush;
//     #endif

//     if (unsat) {
//       #ifdef DEBUG
//       cout << "UNSAT" << endl << flush; 
//       #endif
//       test += 1; // Increase the range

//       increasing = true;
//     }
//     else {
//       system("cp result.txt best_result.txt");
//       #ifdef DEBUG
//       cout << "SAT" << endl << flush;
//       #endif

//       if (increasing)
//         break;

//       lim = test;
//       test -= 10;  // Decrease the range
//     }
//   }

//   return false;
// }



void print_result(uint lin, uint col)
{
  ifstream result ("best_result.txt");

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
      cout << (c == 'o' ? 1 : 0) << ' ';
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

  bool is_eden = b_search();

  if (is_eden)
    cout << "Eden" << endl;
  else
    print_result(lin, col);

  return 0;
}
