import subprocess
import re


def run_lls(input_file, p_value=None):
    """
    Run the LLS command with optional -p value and return the result.
    """
    if p_value is None:
        command = f"python3 lls {input_file}"
    else:
        command = f"python3 lls {input_file} -p '<{p_value}'"
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    return result


def get_live_cells_count(output):
    """
    Extract the number of live cells from the LLS output.
    """
    match = re.search(r'live cells: (\d+)', output)
    if match:
        return int(match.group(1))
    return 0


def find_min_sat_p(input_file):
    """
    Use binary search to efficiently find the minimum satisfiable -p value.
    """
    # Initial run to get the maximum live cells
    initial_result = run_lls(input_file)
    max_live_cells = get_live_cells_count(initial_result.stdout)
    print(f"Initial run live cells: {max_live_cells}")

    # Set up the range for binary search
    low, high = 0, max_live_cells
    best_p_value = None
    best_output = ""

    # Binary search to find the minimum satisfiable -p value
    while low <= high:
        mid = (low + high) // 2
        print(f"Testing -p '<{mid}':", end=" ")
        result = run_lls(input_file, mid)

        if "Unsatisfiable" in result.stdout:
            print("UNSAT")
            low = mid + 1  # Increase the range
        else:
            print("SAT")
            best_p_value = mid
            best_output = result.stdout
            high = mid - 1  # Decrease the range

    # Return the smallest satisfiable p value and the corresponding output
    return best_p_value, best_output


if __name__ == "__main__":
    input_file = "../input.txt"

    min_sat_p_value, last_output = find_min_sat_p(input_file)
    if min_sat_p_value is not None:
        print(f"The minimum satisfiable -p value is: <{min_sat_p_value}>")
        print("Output for the minimum satisfiable case:")
        print(last_output)
    else:
        print("No satisfiable -p value found.")
