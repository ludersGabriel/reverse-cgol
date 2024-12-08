#include <bits/stdc++.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <chrono>

using namespace std;
#define uint unsigned

uint max_time = 290;
uint max_run = 30;
auto start = chrono::high_resolution_clock::now();

vector<string> split(const string& s, char delimiter);
void run_lls(uint limit);
void write_pos(vector<vector<char>>& preproc, int i, int j, char c);
void process_input(uint lin, uint col);
tuple<uint, bool, bool, bool> get_info();
bool b_search();
void print_result(uint lin, uint col);
void print_eden(uint lin, uint col);

int main() {
  uint lin, col;
  cin >> lin >> col;

  process_input(lin, col);

  bool is_eden = b_search();

#ifdef DEBUG
  long total_time_running = chrono::duration_cast<chrono::seconds>(
                                chrono::high_resolution_clock::now() - start)
                                .count();
  long time_left = max_time - total_time_running;

  cout << "Total time running: " << total_time_running << endl;
  cout << "Time left: " << time_left << endl << endl << flush;
#endif

  if (is_eden)
    print_eden(lin, col);
  else
    print_result(lin, col);

  return 0;
}

void print_eden(uint lin, uint col) {
  cout << lin << ' ' << col << endl;
  for (uint i = 0; i < lin; i++) {
    for (uint j = 0; j < col; j++) {
      cout << 0 << ' ';
    }
    cout << endl;
  }
}

// splits a string
vector<string> split(const string& s, char delimiter) {
  vector<string> tokens;
  stringstream ss(s);
  string token;

  while (getline(ss, token, delimiter)) {
    tokens.push_back(token);
  }

  return tokens;
}

// runs lls with verbose 1
void run_lls(uint limit) {
  char* cmd = (char*)malloc(sizeof(char) * 120);
  if (!cmd) {
    cout << "run lls malloc error";
    exit(1);
  }

  if (limit == 0) limit = 0xFFFFFFFF;

#ifdef DEBUG
  cout << "Teste p value: " << limit << endl << flush;
#endif
  long time_until_now = chrono::duration_cast<chrono::seconds>(
                            chrono::high_resolution_clock::now() - start)
                            .count();
  long time_limit = max_time - time_until_now;
  long timeoutLimit = max_run > time_limit ? time_limit : max_run;

#ifdef DEBUG
  cout << "Time running: " << time_until_now << endl << flush;
  cout << "Time remaining: " << time_limit << endl << flush;
  cout << "Time for the current run: " << timeoutLimit << endl << flush;
#endif

  sprintf(cmd,
          "python3 lls-project/lls.py -t %lu -v 1 -p '<=%u' < out.txt > "
          "result.txt",
          timeoutLimit, limit);

  system(cmd);
}

void write_pos(vector<vector<char>>& preproc, int i, int j, char c) {
  if (i < 0 || j < 0 || i >= preproc.size() || j >= preproc[0].size()) return;
  preproc[i][j] = c;
}

// Reads stdin, process it and write to a file out.txt
void process_input(uint lin, uint col) {
  vector<vector<uint>> input(lin, vector<uint>(col));

  for (uint i = 0; i < lin; i++)
    for (uint j = 0; j < col; j++) cin >> input[i][j];

  vector<vector<char>> preproc(lin, vector<char>(col, '*'));

  ofstream output("out.txt");

  for (vector<char> line : preproc) {
    for (char c : line) output << c << ' ';
    output << endl;
  }

  output << endl << endl;

  for (vector<uint> line : input) {
    for (uint c : line) output << c << ' ';
    output << endl;
  }

  output.close();
}

// reads the result file and return number of cells alive
tuple<uint, bool, bool, bool> get_info() {
  string str;
  ifstream result("result.txt");
  getline(result, str);  // get live cells line

  vector<string> parts = split(str, ' ');
  uint live_cells = stoul(parts[2]);

  getline(result, str);  // get unsat line

  result.close();

  long timeLeft = max_time - chrono::duration_cast<chrono::seconds>(
                                 chrono::high_resolution_clock::now() - start)
                                 .count();

  bool killed = str == "Timed out" && timeLeft > 0;
  bool unsat = str == "Unsatisfiable" || killed;
  bool timedout = str == "Timed out" && timeLeft <= 0;

  return {live_cells, unsat, timedout, killed};
}

bool b_search() {
  // run a limitless lls
  run_lls(0);

  auto [live_cells, unsat, timedout, killed] = get_info();
  if (unsat || timedout) return true;

#ifdef DEBUG
  cout << live_cells << " SAT" << endl << endl << flush;
#endif

  system("cp result.txt best_result.txt");

  int low = 0, high = live_cells;
  int mid = (low + high) / 2;

  while (low <= high) {
    run_lls(mid);

    auto [live_cells, unsat, timedout, killed] = get_info();
#ifdef DEBUG
    cout << live_cells << ' ' << flush;
#endif

    if (unsat) {
#ifdef DEBUG
      cout << "UNSAT, killed: " << killed << endl << endl << flush;
#endif
      low = mid + 1;
    } else if (timedout) {
#ifdef DEBUG
      cout << "TIMEOUT" << endl << endl << flush;
#endif
      return false;

    } else {
      system("cp result.txt best_result.txt");
#ifdef DEBUG
      cout << "SAT" << endl << endl << flush;
#endif
      high = live_cells - 1;
    }

    mid = (low + high) / 2;
  }

  return false;
}

void print_result(uint lin, uint col) {
  cout << lin << ' ' << col << endl;
  ifstream result("best_result.txt");

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
