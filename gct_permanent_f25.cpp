// Exact finite-field exclusion for the permanent three-plane locus.
// Build and run with: c++ -O3 -std=c++17 gct_permanent_f25.cpp -o /tmp/gct_permanent_f25 && /tmp/gct_permanent_f25

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {

constexpr int prime = 5;
constexpr int field_size = 25;
using Field = std::uint8_t;
using Matrix = std::array<Field, 10>;  // Upper triangular entries in row order.
using Triple = std::array<Field, 3>;
using Basis = std::array<Matrix, 9>;

Field addition[field_size][field_size];
Field multiplication[field_size][field_size];
Field negative[field_size];

constexpr int packed_index[4][4] = {
    {0, 1, 2, 3}, {1, 4, 5, 6}, {2, 5, 7, 8}, {3, 6, 8, 9},
};

int residue(int n) {
    int r = n % prime;
    return r < 0 ? r + prime : r;
}

void initialize_field() {
    // Encode a + b*omega by a + 5*b, where omega^2 + omega + 1 = 0.
    for (int left = 0; left < field_size; ++left) {
        for (int right = 0; right < field_size; ++right) {
            const int a = left % prime, b = left / prime;
            const int c = right % prime, d = right / prime;
            addition[left][right] = residue(a + c) + prime * residue(b + d);
            multiplication[left][right] = residue(a*c - b*d) + prime * residue(a*d + b*c - b*d);
            if (addition[left][right] == 0) {
                negative[left] = right;
            }
        }
    }
    const Field omega = prime;
    assert(addition[addition[multiplication[omega][omega]][omega]][1] == 0);
    for (int element = 1; element < field_size; ++element) {
        const auto& multiples = multiplication[element];
        assert(std::find(std::begin(multiples), std::end(multiples), 1) != std::end(multiples));
    }
}

Field permanent(const Matrix& matrix) {
    const auto [a, e, f, g, b, h, i, c, j, d] = matrix;
    const Field e2 = multiplication[e][e], f2 = multiplication[f][f];
    const Field g2 = multiplication[g][g], h2 = multiplication[h][h];
    const Field i2 = multiplication[i][i], j2 = multiplication[j][j];
    const Field ab = multiplication[a][b], ac = multiplication[a][c], ad = multiplication[a][d];
    const Field bc = multiplication[b][c], bd = multiplication[b][d], cd = multiplication[c][d];
    // Identity, single transpositions, and double transpositions.
    Field value = multiplication[ab][cd];
    for (Field term : {multiplication[e2][cd], multiplication[f2][bd], multiplication[g2][bc],
                       multiplication[h2][ad], multiplication[i2][ac], multiplication[j2][ab],
                       multiplication[e2][j2], multiplication[f2][i2], multiplication[g2][h2]}) {
        value = addition[value][term];
    }
    // A cycle and its opposite orientation have equal products.
    const Field ef = multiplication[e][f], ei = multiplication[e][i], fj = multiplication[f][j];
    const Field gh = multiplication[g][h], gj = multiplication[g][j], hi = multiplication[h][i];
    Field cycle_sum = 0;
    for (Field term : {multiplication[ef][multiplication[h][d]], multiplication[ei][multiplication[g][c]],
                       multiplication[fj][multiplication[g][b]], multiplication[hi][multiplication[j][a]],
                       multiplication[multiplication[e][h]][gj], multiplication[ei][fj],
                       multiplication[gh][multiplication[f][i]]}) {
        cycle_sum = addition[cycle_sum][term];
    }
    return addition[value][multiplication[2][cycle_sum]];
}

Field permanent_by_permutations(const Matrix& matrix) {
    std::array<int, 4> permutation = {0, 1, 2, 3};
    Field value = 0;
    do {
        Field term = 1;
        for (int row = 0; row < 4; ++row) {
            term = multiplication[term][matrix[packed_index[row][permutation[row]]]];
        }
        value = addition[value][term];
    } while (std::next_permutation(permutation.begin(), permutation.end()));
    return value;
}

Field gram_entry(const Matrix& left, const Matrix& right) {
    // Polar form of q_2, the trace pairing with (J-I) on both sides.
    Field value = 0;
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            for (int k = 0; k < 4; ++k) {
                for (int l = 0; l < 4; ++l) {
                    if (j != k && l != i) {
                        const Field term = multiplication[left[packed_index[i][j]]][right[packed_index[k][l]]];
                        value = addition[value][term];
                    }
                }
            }
        }
    }
    return value;
}

Basis eisenstein_basis() {
    constexpr int characters[4][4] = {
        {1, 1, 1, 1}, {1, 1, -1, -1}, {1, -1, 1, -1}, {1, -1, -1, 1},
    };
    const Field omega = prime, omega_squared = multiplication[omega][omega];
    Basis basis{};
    for (int row = 0; row < 4; ++row) {
        for (int col = row; col < 4; ++col) {
            const int index = packed_index[row][col];
            Triple w{};
            for (int j = 0; j < 3; ++j) {
                const auto& x = characters[j + 1];
                const auto& y = characters[(j + 1) % 3 + 1];
                const auto& z = characters[(j + 2) % 3 + 1];
                const int d = 4 * x[row] * x[col];  // 1/4 = 4 in F_5.
                const int c = 4 * (y[row] * z[col] + z[row] * y[col]);
                const int b = 4 * (x[row] + x[col]);
                basis[2*j][index] = residue(2*d + c + b);
                basis[2*j+1][index] = residue(2 * (2*d - c - b));  // 1/8 = 2.
                w[j] = residue(3*c + b);
            }
            basis[6][index] = addition[w[0]][addition[multiplication[omega][w[1]]][multiplication[omega_squared][w[2]]]];
            basis[7][index] = addition[w[0]][addition[multiplication[omega_squared][w[1]]][multiplication[omega][w[2]]]];
            basis[8][index] = addition[w[0]][addition[w[1]][w[2]]];  // 36 = 1 in F_5.
        }
    }
    for (std::size_t i = 0; i < basis.size(); ++i) {
        Field entry_sum = 0;
        for (const auto& row : packed_index) {
            for (int index : row) {
                entry_sum = addition[entry_sum][basis[i][index]];
            }
        }
        assert(entry_sum == 0);
        for (std::size_t j = 0; j < basis.size(); ++j) {
            const bool paired = (i < 8 && j == (i ^ 1)) || (i == 8 && j == 8);
            assert(gram_entry(basis[i], basis[j]) == paired);
        }
    }
    return basis;
}

bool level_direction(const Matrix& direction) {
    // Entries sum to zero and q_2 is zero by construction. The tests below
    // then impose q_4 = 0 and q_3 + q_4 = 0 respectively.
    if (permanent(direction) != 0) {
        return false;
    }
    Matrix shifted;
    for (std::size_t index = 0; index < direction.size(); ++index) {
        shifted[index] = addition[direction[index]][1];
    }
    return permanent(shifted) == 24 % prime;
}

struct Column {
    Matrix direction;
    Triple residual;
    Triple dual;
};

using MatrixTriple = std::array<Matrix, 3>;
using Multiples = std::array<std::array<Matrix, field_size>, 3>;

Multiples all_multiples(const MatrixTriple& matrices) {
    Multiples result;
    for (int j = 0; j < 3; ++j) {
        for (int scalar = 0; scalar < field_size; ++scalar) {
            for (std::size_t index = 0; index < matrices[j].size(); ++index) {
                result[j][scalar][index] = multiplication[scalar][matrices[j][index]];
            }
        }
    }
    return result;
}

std::vector<Column> level_columns(int j, const MatrixTriple& pivot, const MatrixTriple& dual,
                                  const MatrixTriple& complement) {
    const auto complement_multiples = all_multiples(complement);
    const auto dual_multiples = all_multiples(dual);
    const int first = (j + 1) % 3, second = (j + 2) % 3;
    std::vector<Column> columns;
    for (Field u = 0; u < field_size; ++u) {
        for (Field v = 0; v < field_size; ++v) {
            for (Field w = 0; w < field_size; ++w) {
                // Minus half the residual q_2, since the complement has Gram
                // <u,v>=1 and <w,w>=36. Thus d = -uv - 18w^2.
                const Field d = negative[addition[multiplication[u][v]][multiplication[3][multiplication[w][w]]]];
                Matrix fixed;
                for (std::size_t index = 0; index < fixed.size(); ++index) {
                    const Field a = addition[pivot[j][index]][complement_multiples[0][u][index]];
                    const Field b = addition[complement_multiples[1][v][index]][complement_multiples[2][w][index]];
                    fixed[index] = addition[addition[a][b]][dual_multiples[j][d][index]];
                }
                for (Field r = 0; r < field_size; ++r) {
                    Matrix partial;
                    for (std::size_t index = 0; index < partial.size(); ++index) {
                        partial[index] = addition[fixed[index]][dual_multiples[first][r][index]];
                    }
                    for (Field s = 0; s < field_size; ++s) {
                        Matrix candidate;
                        for (std::size_t index = 0; index < candidate.size(); ++index) {
                            candidate[index] = addition[partial[index]][dual_multiples[second][s][index]];
                        }
                        if (level_direction(candidate)) {
                            Triple dual_coordinates;
                            dual_coordinates[j] = d;
                            dual_coordinates[first] = r;
                            dual_coordinates[second] = s;
                            columns.push_back({candidate, {u, v, w}, dual_coordinates});
                        }
                    }
                }
            }
        }
    }
    return columns;
}

bool compatible(int i, int j, const Column& left, const Column& right) {
    const auto [u, v, w] = left.residual;
    const auto [x, y, z] = right.residual;
    const Field residual_gram = addition[addition[multiplication[u][y]][multiplication[v][x]]][multiplication[w][z]];
    if (addition[left.dual[j]][residual_gram] != negative[right.dual[i]]) {
        return false;
    }
    for (Field scalar : {1, 2, 3}) {
        Matrix direction;
        for (std::size_t index = 0; index < direction.size(); ++index) {
            direction[index] = addition[left.direction[index]][multiplication[scalar][right.direction[index]]];
        }
        if (!level_direction(direction)) {
            return false;
        }
    }
    return true;
}

using Edges = std::vector<std::vector<std::size_t>>;

Edges compatible_pairs(int i, int j, const std::vector<Column>& left, const std::vector<Column>& right,
                       const std::vector<bool>& use_left) {
    Edges neighbors(left.size());
    for (std::size_t a = 0; a < left.size(); ++a) {
        if (!use_left[a]) {
            continue;
        }
        for (std::size_t b = 0; b < right.size(); ++b) {
            if (compatible(i, j, left[a], right[b])) {
                neighbors[a].push_back(b);
            }
        }
    }
    return neighbors;
}

bool no_triangle(const Basis& basis, const std::array<int, 3>& pivot_indices, int omitted_pair) {
    MatrixTriple pivot, dual;
    for (int j = 0; j < 3; ++j) {
        pivot[j] = basis[pivot_indices[j]];
        dual[j] = basis[pivot_indices[j] ^ 1];
    }
    const MatrixTriple complement = {basis[2*omitted_pair], basis[2*omitted_pair+1], basis[8]};
    const auto a = level_columns(0, pivot, dual, complement);
    const auto b = level_columns(1, pivot, dual, complement);
    const auto c = level_columns(2, pivot, dual, complement);
    const auto ab = compatible_pairs(0, 1, a, b, std::vector<bool>(a.size(), true));
    std::vector<bool> use_a(a.size()), use_b(b.size());
    std::uint64_t edge_count = 0;
    for (std::size_t i = 0; i < ab.size(); ++i) {
        use_a[i] = !ab[i].empty();
        for (std::size_t j : ab[i]) {
            use_b[j] = true;
            ++edge_count;
        }
    }
    const auto ac = compatible_pairs(0, 2, a, c, use_a);
    const auto bc = compatible_pairs(1, 2, b, c, use_b);
    bool has_triangle = false;
    for (std::size_t i = 0; i < ab.size(); ++i) {
        for (std::size_t j : ab[i]) {
            for (std::size_t k : ac[i]) {
                has_triangle = has_triangle || std::binary_search(bc[j].begin(), bc[j].end(), k);
            }
        }
    }
    std::cout << "columns " << a.size() << ", " << b.size() << ", " << c.size()
              << "; first-pair edges " << edge_count << "; triangle present " << std::boolalpha << has_triangle << '\n';
    return !has_triangle;
}

}  // namespace

int main() {
    initialize_field();
    int state = 17;
    for (int trial = 0; trial < 128; ++trial) {
        Matrix matrix;
        for (Field& entry : matrix) {
            state = (31 * state + 17) % 997;
            entry = state % field_size;
        }
        assert(permanent(matrix) == permanent_by_permutations(matrix));
    }
    const auto basis = eisenstein_basis();
    const bool first = no_triangle(basis, {0, 2, 4}, 3);
    const bool second = no_triangle(basis, {1, 2, 4}, 3);
    const bool third = no_triangle(basis, {0, 2, 6}, 2);
    return first && second && third ? 0 : 1;
}
