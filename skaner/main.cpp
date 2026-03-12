#include <string>
#include <iostream>

using namespace std;

string input;
int pos = 0;

void skipWhitespace() {
    while (pos < input.size() && isspace(input[pos])) {
        pos++;
    }
}

void skaner() {
    skipWhitespace();

    if (pos >= input.size()) {
        cout << "\n(EOF,EOF)" << endl;
        return;
    }

    char c = input[pos];

    //liczba
    if (isdigit(c)) {
        string num;
        int start = pos;

        while (pos < input.size() && isdigit(input[pos])) {
            num += input[pos];
            pos++;
        }

        cout << "(INT," << num << ")" << endl;
        return;
    }
    //identyfikator
    if (isalpha(c)) {
        string id;
        int start = pos;

        while (pos < input.size() && isalpha(input[pos])) {
            id += input[pos];
            pos++;
        }

        cout << "(ID," << id << ")";
        return;
    }
    //dzialania
    switch(c) {
        case '+':
            cout << "(PLUS,+)" << endl;
            pos++;
            break;
        case '-':
            cout << "(MINUS,-)" << endl;
            pos++;
            break;
        case '*':
            cout << "(MUL,*)" << endl;
            pos++;
            break;
        case '/':
            cout << "(DIV,/)" << endl;
            pos++;
            break;
        case '(':
            cout << "(LPAREN,()" << endl;
            pos++;
            break;
        case ')':
            cout << "(RPAREN,))" << endl;
            pos++;
            break;
        default:
            cout << "BLAD na pozycji " << pos << ": " << c << endl;
            pos++;
    }
}

int main() {
    cout << "Podaj wyrazenie: ";
    getline(cin, input);

    while (pos < input.size()) {
        skaner();
    }

    cout << "(EOF,EOF)" << endl;
}
