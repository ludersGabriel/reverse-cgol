def convert_rle_to_binary(rle_file, output_file):
    with open(rle_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            if not line.startswith("#") and not line.startswith("x ="):
                line = line.replace("b", "0 ").replace(
                    "o", "1 ").replace("$", "\n").strip()
                outfile.write(line)
                outfile.write("\n")


def add_stars_to_neighbors(grid):
    import copy
    rows, cols = len(grid), len(grid[0])
    # Copy the grid to avoid modifying the original
    new_grid = copy.deepcopy(grid)

    # Add stars within Manhattan distance of 3
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:  # If the cell is live
                grid[r][c] = '*'
                # Iterate over rows in the range [-3, 3]
                for dr in range(-2, 3):
                    # Iterate over columns in the range [-3, 3]
                    for dc in range(-2, 3):
                        if abs(dr) + abs(dc) <= 2:  # Check Manhattan distance
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < rows and 0 <= nc < cols and new_grid[nr][nc] != 1:
                                # Add a star if it's not a live cell
                                new_grid[nr][nc] = '*'
                new_grid[r][c] = '*'  # Restore the live cell

    return new_grid


def read_grid_from_file(file_name):
    with open(file_name, "r") as file:
        grid = []
        for line in file:
            grid.append([int(cell) if cell.isdigit()
                        else cell for cell in line.split()])
    return grid


def write_grid_to_file(grid, file_name):
    with open(file_name, "w") as file:
        for row in grid:
            file.write(" ".join(str(cell) for cell in row) + "\n")


# Main Execution
# Step 1: Convert RLE to binary format
convert_rle_to_binary("output.rle", "output_binary.txt")

# Step 2: Read the binary grid, process it, and write the new grid
binary_grid = read_grid_from_file("output_binary.txt")
updated_grid = add_stars_to_neighbors(binary_grid)
write_grid_to_file(updated_grid, "input.txt")
