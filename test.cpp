#include <iostream>
#include <vector>
#include <stdexcept>
#include <algorithm>

int highComplexity(int a, int b, int c, int d) {
    int result = 0;

    // bloco 1: vários if/else encadeados e operações booleanas
    if (a > b && c < d || (a == 0 && d != 0)) {
        result += a * b - c;
    } else if (a < b && (c > d || d == 0)) {
        result -= b * c;
    } else {
        result += std::abs(a - d);
    }

    // bloco 2: primeiro for com if/else, switch e try/catch
    for (int i = 0; i < a; ++i) {
        if (i % 2 == 0) {
            if ((b & 1) && c > 0) {
                result ^= i;
            } else if (!(b & 1) && c < 0) {
                result |= i;
            } else {
                result &= i;
            }
        } else if (i % 3 == 0) {
            result += i;
        } else {
            result -= i;
        }

        switch (i % 5) {
            case 0:  result += 5;    break;
            case 1:  result -= 5;    break;
            case 2:  result *= 2;    break;
            case 3:  result /= (i == 0 ? 1 : i); break;
            default: result %= (i + 1);          break;
        }

        try {
            if (d == 0) throw std::invalid_argument("d==0");
            result += b / d;
        } catch (const std::invalid_argument &e) {
            result -= c;
        }

        if (result > 1000) {
            result %= 1000;
        } else if (result < -1000) {
            result = -result;
        }
    }

    // bloco 3: while com vários ramos
    int j = b;
    while (j > 0) {
        if (c > 0) {
            if (j % 2 == 0) result += j;
            else            result -= j;
        } else if (c < 0) {
            if (j % 3 == 0) result *= j;
            else            result /= (j == 0 ? 1 : j);
        } else {
            result ^= j;
        }
        --j;
    }

    // bloco 4: loop sobre vetor com if/else
    std::vector<int> data = {a, b, c, d};
    for (auto &val : data) {
        if (val > 0) {
            val = val * 2;
        } else if (val < 0) {
            val = -val;
        } else {
            val = 1;
        }
        result += val;
    }

    // bloco 5: expressão ternária e várias condições booleanas
    result += (a > b && b > c) ? a
             : (b > c ? b : c);

    // bloco 6: loop extra para inflar ainda mais a complexidade
    for (int k = 0; k < d + 3; ++k) {
        if      (k == a) result += a;
        else if (k == b) result -= b;
        else if (k == c) result *= c;
        else             result ^= k;
    }

    return result;
}

int main() {
    int a = 4, b = 7, c = -3, d = 0;
    std::cout << "Complexity result: "
              << highComplexity(a, b, c, d)
              << std::endl;
    return 0;
}