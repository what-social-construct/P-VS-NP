// Evaluate the three divided common-line resultants on the fixed face over F5.
// Each stdin line contains x0 x1 y0 y1 y2 in F_(5^7), with Y = sum(y) = 1.
// Stdout repeats the five packed inputs followed by G2 G3 G4. Build with C++17.
#include <algorithm>
#include <array>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
using namespace std;

void require(bool condition, const char *message) {
  if (!condition)
    throw runtime_error(message);
}

// Discrete logarithms in F_5[w]/(w^7+3w+3). Each input integer encodes the
// seven coefficients in base five, starting with the constant term.
constexpr int field_order = 78125, period = field_order - 1;
array<int, field_order> logarithm, powers, addition_log;
int reduce_exponent(int n) { return n >= period ? n - period : n; }
void initialize_field() {
  int a = 1;
  logarithm.fill(-1);
  for (int i = 0; i < period; i++) {
    require(logarithm[a] == -1, "field generator repeated early");
    logarithm[a] = i;
    powers[i] = a;
    // Multiply by w and reduce w^7 = 2w+2 in the packed basis.
    int high = a / (field_order / 5);
    a = (a % (field_order / 5)) * 5;
    a = 25 * (a / 25) + 5 * ((a / 5 + 2 * high) % 5) + (2 * high) % 5;
  }
  require(a == 1, "field generator has the wrong order");
  // addition_log[i] is the logarithm of (1+w^i), with -1 for zero.
  for (int i = 0; i < period; i++) {
    a = powers[i];
    addition_log[i] = logarithm[a - a % 5 + (a + 1) % 5];
  }
}

struct Field {
  int exponent;
  Field(int v = 0) : exponent(logarithm[(v % 5 + 5) % 5]) {}
  static Field from_log(int exponent) {
    Field f;
    f.exponent = exponent;
    return f;
  }
  static Field unpack(int u) { return from_log(logarithm.at(u)); }
  int pack() const { return exponent < 0 ? 0 : powers[exponent]; }
  explicit operator bool() const { return exponent >= 0; }
  bool operator==(Field y) const { return exponent == y.exponent; }
  Field operator-() const {
    return exponent < 0 ? *this
                        : from_log(reduce_exponent(exponent + period / 2));
  }
  Field operator+(Field y) const {
    if (exponent < 0)
      return y;
    if (y.exponent < 0)
      return *this;
    int d = y.exponent - exponent;
    if (d < 0)
      d += period;
    int z = addition_log[d];
    return z < 0 ? Field() : from_log(reduce_exponent(z + exponent));
  }
  Field operator-(Field y) const { return *this + (-y); }
  Field operator*(Field y) const {
    return exponent < 0 || y.exponent < 0
               ? Field()
               : from_log(reduce_exponent(exponent + y.exponent));
  }
  Field inv() const {
    require(exponent >= 0, "division by zero");
    return from_log(exponent == 0 ? 0 : period - exponent);
  }
  Field pow(unsigned int power) const {
    if (power == 0)
      return Field(1);
    if (exponent < 0)
      return Field();
    return from_log((static_cast<long long>(exponent) * power) % period);
  }
  void operator+=(Field y) { *this = *this + y; }
  void operator-=(Field y) { *this = *this - y; }
};

using Matrix = vector<vector<Field>>;
Matrix zero_matrix(int r, int c) { return Matrix(r, vector<Field>(c)); }
// Reduce the first n columns, applying all operations to the augmented part.
// For a square leading block the return value is its original determinant.
Field row_reduce(Matrix &a, int n, vector<int> *pivot_columns = nullptr) {
  int r = 0;
  Field det(1);
  for (int j = 0; j < n && r < (int)a.size(); j++) {
    int k = r;
    while (k < (int)a.size() && !a[k][j])
      ++k;
    if (k == (int)a.size())
      continue;
    if (k != r) {
      swap(a[r], a[k]);
      det = -det;
    }
    det = det * a[r][j];
    Field scale = a[r][j].inv();
    for (int i = j; i < (int)a[r].size(); i++)
      a[r][i] = a[r][i] * scale;
    for (int k2 = 0; k2 < (int)a.size(); k2++)
      if (k2 != r && a[k2][j]) {
        scale = a[k2][j];
        for (int i = j; i < (int)a[r].size(); i++)
          a[k2][i] -= scale * a[r][i];
      }
    if (pivot_columns)
      pivot_columns->push_back(j);
    ++r;
  }
  return r == n ? det : Field();
}
Field determinant(Matrix a) {
  int n = a.size();
  return row_reduce(a, n);
}

const array<pair<int, int>, 9> entries = {
    {{0, 1}, {0, 2}, {0, 3}, {1, 1}, {1, 2}, {1, 3}, {2, 2}, {2, 3}, {3, 3}}};
using Vector = vector<Field>;
using SymmetricMatrix = array<array<Field, 4>, 4>;
SymmetricMatrix lift_tangent(const Vector &u) {
  SymmetricMatrix a{};
  for (int k = 0; k < 9; k++) {
    auto [i, j] = entries[k];
    a[j][i] = a[i][j] = u[k];
    a[0][0] -= (i == j ? Field(1) : Field(2)) * u[k];
  }
  return a;
}

using Triple = array<Field, 3>;
// Linear and quadratic coefficients in the direction X of per(J+sB+tX).
pair<Triple, Triple> polar_values(const SymmetricMatrix &b,
                                  const SymmetricMatrix &x) {
  Field coeff[4][3]{};
  array<int, 4> perm = {0, 1, 2, 3};
  do {
    Field term[5][3]{};
    term[0][0] = 1;
    for (int i = 0; i < 4; ++i) {
      Field s = b[i][perm[i]], t = x[i][perm[i]];
      for (int a = i + 1; a >= 0; --a)
        for (int c = min(2, i + 1 - a); c >= 0; --c) {
          if (a)
            term[a][c] += s * term[a - 1][c];
          if (c)
            term[a][c] += t * term[a][c - 1];
        }
    }
    for (int j = 0; j < 3; j++) {
      coeff[j + 1][1] += term[j + 1][1];
      coeff[j][2] += term[j][2];
    }
  } while (next_permutation(perm.begin(), perm.end()));
  return {{coeff[1][1], coeff[2][1], coeff[3][1]},
          {coeff[0][2], coeff[1][2], coeff[2][2]}};
}

using QuadraticForms = array<Matrix, 3>;
// Select a frame in which D,H are the last two coordinates of W. The returned
// scalar converts its volume to the fixed determinant line of the ambient
// tangent space.
void compute_frame(const array<Field, 5> &coordinates, QuadraticForms &grams,
                   Field &volume, int offset) {
  auto [x0, x1, y0, y1, y2] = coordinates;
  Field x2 = -x0 - x1;
  Vector b(9);
  b[0] = y2;
  b[1] = x0;
  b[2] = y1;
  b[4] = x1;
  b[5] = y0;
  b[7] = x2;
  Field sum = y0 + y1 + y2;
  require(sum == Field(1), "sample must have y0+y1+y2=1");
  b[3] = Field(3) * sum - Field(2) * (b[0] + b[4] + b[5]);
  b[6] = Field(3) * sum - Field(2) * (b[1] + b[4] + b[7]);
  b[8] = Field(3) * sum - Field(2) * (b[2] + b[5] + b[7]);
  SymmetricMatrix B = lift_tangent(b);
  Matrix m = zero_matrix(9, 18);
  for (int i = 0; i < 9; i++) {
    Vector unit(9);
    unit[i] = 1;
    SymmetricMatrix direction = lift_tangent(unit);
    auto linear = polar_values(B, direction).first;
    for (int j = 0; j < 3; j++)
      m[j][i] = linear[j];
    m[7][i] = direction[0][0] + direction[1][1] + direction[3][3];
    m[8][i] = direction[0][2] + direction[1][2] + direction[2][3];
    m[i][9 + i] = 1;
  }
  // B belongs to the polar kernel and to the kernels of D and H.
  for (int r : {0, 1, 2, 7, 8}) {
    Field value;
    for (int i = 0; i < 9; ++i)
      value += m[r][i] * b[i];
    require(!value, "sample direction lies outside the required polar kernel");
  }
  // The first three inverse columns lift the polar quotient. Replacing its
  // fourth inverse column by B multiplies the basis determinant by gauge(B).
  // The last five inverse columns then give a frame for ker(polars)/<B>.
  int gauge = offset;
  while (!b[gauge])
    gauge = (gauge + 1) % 9;
  m[3][gauge] = 1;
  for (int i = 0; i < 9; i++)
    for (int j = i + 1; j < 9; j++)
      for (int k = j + 1; k < 9; k++) {
        Matrix a = m;
        a[4][(i + offset) % 9] = 1;
        a[5][(j + offset) % 9] = 1;
        a[6][(k + offset) % 9] = 1;
        Field frame_determinant = row_reduce(a, 9);
        if (!frame_determinant)
          continue;
        volume = frame_determinant * b[gauge].inv();
        vector<Vector> frame(5, Vector(9));
        array<Triple, 5> diagonal_values{};
        for (int r = 0; r < 5; r++) {
          for (int c = 0; c < 9; c++)
            frame[r][c] = a[c][9 + 4 + r];
          diagonal_values[r] = polar_values(B, lift_tangent(frame[r])).second;
        }
        for (auto &q : grams)
          q = zero_matrix(5, 5);
        for (int r = 0; r < 5; r++)
          for (int j = 0; j < 3; j++)
            grams[j][r][r] = diagonal_values[r][j];
        for (int r = 0; r < 5; r++)
          for (int t = r + 1; t < 5; t++) {
            Vector v = frame[r];
            for (int c = 0; c < 9; c++)
              v[c] += frame[t][c];
            auto cross = polar_values(B, lift_tangent(v)).second;
            for (int j = 0; j < 3; j++)
              grams[j][r][t] = grams[j][t][r] =
                  Field(3) *
                  (cross[j] - diagonal_values[r][j] - diagonal_values[t][j]);
          }
        return;
      }
  throw runtime_error("D,H do not extend to a frame of the corrected kernel");
}

// In the affine chart H=0, D=1 the three affine coordinates have 35
// monomials up to degree four. The leading 15 are the degree-four monomials.
using Monomial = array<int, 3>;
vector<Monomial> monomials;
int monomial_indices[5][5][5];
int index_of(const Monomial &p) { return monomial_indices[p[0]][p[1]][p[2]]; }
Monomial multiply_monomials(Monomial p, const Monomial &q) {
  for (int j = 0; j < 3; j++)
    p[j] += q[j];
  return p;
}
int degree(Monomial p) { return p[0] + p[1] + p[2]; }
void initialize_monomials() {
  for (int d = 4; d >= 0; --d)
    for (int x = d; x >= 0; --x)
      for (int y = d - x; y >= 0; --y) {
        Monomial m = {x, y, d - x - y};
        monomial_indices[x][y][m[2]] = monomials.size();
        monomials.push_back(m);
      }
}

using AffineQuadrics = array<Vector, 3>;
// Macaulay's degree-four determinant for three homogeneous ternary quadrics.
// Rows/columns divisible by two distinct squares form the extraneous minor.
Field resultant_at_infinity(const AffineQuadrics &q) {
  Matrix a = zero_matrix(15, 15);
  vector<int> mixed;
  for (int i = 0; i < 15; i++) {
    Monomial p = monomials[i];
    int k = 0;
    while (p[k] < 2)
      ++k;
    if (count_if(p.begin(), p.end(), [](int a) { return a >= 2; }) > 1)
      mixed.push_back(i);
    p[k] -= 2;
    for (int j = 0; j < 35; j++)
      if (degree(monomials[j]) == 2)
        a[i][index_of(multiply_monomials(p, monomials[j]))] = q[k][j];
  }
  Matrix extra = zero_matrix(mixed.size(), mixed.size());
  for (int i = 0; i < (int)mixed.size(); i++)
    for (int j = 0; j < (int)mixed.size(); j++)
      extra[i][j] = a[mixed[i]][mixed[j]];
  Field d = determinant(extra);
  require(static_cast<bool>(d),
          "Macaulay formula has a zero denominator in this frame");
  return determinant(a) * d.inv();
}

using Operator = array<array<Field, 8>, 8>;
Operator compose(const Operator &a, const Operator &b) {
  Operator c{};
  for (int i = 0; i < 8; i++)
    for (int j = 0; j < 8; j++)
      for (int k = 0; k < 8; k++)
        c[i][j] += a[i][k] * b[k][j];
  return c;
}
void add_scaled(Operator &a, const Operator &b, Field s) {
  if (s)
    for (int i = 0; i < 8; i++)
      for (int j = 0; j < 8; j++)
        a[i][j] += s * b[i][j];
}

// Construct multiplication by each of the five coordinates on H=0,D=1.
array<Operator, 5> position_operators(const AffineQuadrics &q) {
  // Row-reduce all monomial multiples of the three quadrics through degree
  // four. The nonpivot columns form the basis of the affine intersection
  // algebra.
  Matrix rows;
  for (int k = 0; k < 3; k++)
    for (auto &m : monomials)
      if (degree(m) <= 2) {
        Vector row(35);
        for (int j = 0; j < 35; j++)
          if (q[k][j])
            row[index_of(multiply_monomials(m, monomials[j]))] = q[k][j];
        rows.push_back(row);
      }
  vector<int> pivot_columns;
  row_reduce(rows, 35, &pivot_columns);
  require(pivot_columns.size() == 27,
          "quadratic section does not have quotient dimension eight in degree "
          "four");
  vector<int> basis_columns;
  for (int j = 0; j < 35; j++)
    if (!binary_search(pivot_columns.begin(), pivot_columns.end(), j))
      basis_columns.push_back(j);
  array<Operator, 5> positions{};
  for (int i = 0; i < 8; i++) {
    positions[3][i][i] = 1;
    for (int k = 0; k < 3; k++) {
      Monomial m = monomials[basis_columns[i]];
      require(degree(m) < 4, "basis monomial degree exceeds three");
      m[k]++;
      int p = index_of(m);
      auto it = find(basis_columns.begin(), basis_columns.end(), p);
      if (it != basis_columns.end())
        positions[k][i][it - basis_columns.begin()] = 1;
      else {
        int at = lower_bound(pivot_columns.begin(), pivot_columns.end(), p) -
                 pivot_columns.begin();
        require(at < static_cast<int>(pivot_columns.size()) &&
                    pivot_columns[at] == p,
                "monomial has no reduction");
        for (int j = 0; j < 8; j++)
          positions[k][i][j] = -rows[at][basis_columns[j]];
      }
    }
  }
  return positions;
}

Triple evaluate(const array<Field, 5> &coordinates, int offset) {
  QuadraticForms grams;
  Field volume;
  compute_frame(coordinates, grams, volume, offset);
  AffineQuadrics q;
  for (auto &v : q)
    v.resize(35);
  for (int k = 0; k < 3; k++)
    for (int i = 0; i < 4; i++)
      for (int j = 0; j < 4; j++) {
        Monomial m{};
        if (i < 3)
          m[i]++;
        if (j < 3)
          m[j]++;
        q[k][index_of(m)] += grams[k][i][j];
      }
  Field boundary_resultant = resultant_at_infinity(q);
  require(static_cast<bool>(boundary_resultant),
          "section has a point at infinity in D=1");
  auto positions = position_operators(q);
  // The five position operators represent (z0,z1,z2,1,0). Use them to
  // evaluate the three bilinear polar rows in the eight-dimensional algebra.
  Operator polar[3][5]{};
  for (int k = 0; k < 3; k++)
    for (int j = 0; j < 5; j++)
      for (int i = 0; i < 4; i++)
        add_scaled(polar[k][j], positions[i], grams[k][i][j]);
  // D is the fourth coordinate. Expanding the cofactors along that row
  // leaves the three-by-three minors on the four indicated columns.
  const array<int, 4> cofactor_columns = {0, 1, 2, 4};
  array<Operator, 5> cofactor{};
  for (int omit = 0; omit < 4; omit++) {
    array<int, 3> cols{};
    int l = 0;
    for (int j = 0; j < 4; j++)
      if (j != omit)
        cols[l++] = cofactor_columns[j];
    do {
      auto [a, b, c] = cols;
      int inversions = (a > b) + (a > c) + (b > c) + omit;
      add_scaled(cofactor[cofactor_columns[omit]],
                 compose(compose(polar[0][a], polar[1][b]), polar[2][c]),
                 Field(inversions % 2 ? -1 : 1));
    } while (next_permutation(cols.begin(), cols.end()));
  }
  array<Operator, 3> sextics{};
  for (int i : cofactor_columns)
    for (int j : cofactor_columns)
      if (i <= j) {
        auto v = compose(cofactor[i], cofactor[j]);
        for (int k = 0; k < 3; k++)
          add_scaled(sextics[k], v, grams[k][i][j] * Field(i == j ? 1 : 2));
      }
  // Poisson gives B_D^6 times the norm of the sextic. The divided
  // resultant removes B_D^2. A frame change contributes its volume to
  // the power 48 when the result is expressed in the fixed ambient volume.
  Field scale = volume.pow(48) * boundary_resultant.pow(4);
  Triple result;
  for (int k = 0; k < 3; k++) {
    Matrix a = zero_matrix(8, 8);
    for (int i = 0; i < 8; i++)
      copy(sextics[k][i].begin(), sextics[k][i].end(), a[i].begin());
    result[k] = scale * determinant(a);
  }
  return result;
}

int replay() {
  initialize_field();
  initialize_monomials();
  string line;
  int count = 0;
  while (getline(cin, line)) {
    ++count;
    try {
      istringstream input(line);
      array<int, 5> packed;
      array<Field, 5> coordinates;
      for (int i = 0; i < 5; i++) {
        require(static_cast<bool>(input >> packed[i]),
                "expected five packed field elements");
        require(packed[i] >= 0 && packed[i] < field_order,
                "packed value outside [0,78124]");
        coordinates[i] = Field::unpack(packed[i]);
      }
      string extra;
      require(!(input >> extra), "unexpected trailing input");
      // Relabel the three incident/opposite edge pairs and verify every
      // section value in two frames for each labeling. Offsets 0 and 5
      // start the gauge search at the nonzero edges y2 and y0.
      array<Field, 3> x{coordinates[0], coordinates[1],
                        -coordinates[0] - coordinates[1]};
      array<Field, 3> y{coordinates[2], coordinates[3], coordinates[4]};
      const array<int, 3> identity{0, 1, 2};
      auto permutation = identity;
      Triple result;
      do {
        auto [a, b, c] = permutation;
        const array<Field, 5> relabeled{x[a], x[b], y[a], y[b], y[c]};
        const auto value = evaluate(relabeled, 0);
        require(value == evaluate(relabeled, 5),
                "resultants disagree between the two frames");
        if (permutation == identity)
          result = value;
        else
          require(result == value,
                  "resultants disagree between edge permutations");
      } while (next_permutation(permutation.begin(), permutation.end()));
      for (auto value : packed)
        cout << value << ' ';
      cout << result[0].pack() << ' ' << result[1].pack() << ' '
           << result[2].pack() << '\n';
    } catch (const exception &err) {
      throw runtime_error("sample " + to_string(count) + ": " + err.what());
    }
  }
  require(cin.eof(), "failed to read input");
  require(count > 0, "expected at least one sample");
  cout.flush();
  require(static_cast<bool>(cout), "could not write results");
  cerr << count << " evaluations\n";
  return 0;
}
} // namespace

int main() {
  try {
    return replay();
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
