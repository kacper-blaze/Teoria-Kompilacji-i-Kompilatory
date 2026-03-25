#include <cctype>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_set>

using namespace std;

enum class TokenType {
    Keyword,
    Identifier,
    Number,
    String,
    Comment,
    Operator,
    Delimiter,
    Whitespace,
    Unknown,
    End
};

struct Token {
    TokenType type;
    string lexeme;
};

class Lexer {
  public:
    explicit Lexer(string source) : source_(move(source)) {}

    Token nextToken() {
        if (isAtEnd()) {
            return {TokenType::End, ""};
        }

        char c = peek();

        if (isspace(static_cast<unsigned char>(c))) {
            return consumeWhitespace();
        }

        if (isalpha(static_cast<unsigned char>(c)) || c == '_') {
            return consumeIdentifierOrKeyword();
        }

        if (isdigit(static_cast<unsigned char>(c))) {
            return consumeNumber();
        }

        if (c == '"') {
            return consumeString();
        }

        if (c == '/') {
            if (peekNext() == '/') {
                return consumeLineComment();
            }
            if (peekNext() == '*') {
                return consumeBlockComment();
            }
        }

        if (isOperatorStart(c)) {
            return consumeOperator();
        }

        if (isDelimiter(c)) {
            return consumeDelimiter();
        }

        return consumeUnknown();
    }

  private:
    string source_;
    size_t pos_ = 0;

    static bool isOperatorStart(char c) {
        const string ops = "+-*/%=!<>&|";
        return ops.find(c) != string::npos;
    }

    static bool isDelimiter(char c) {
        const string delimiters = "(){}[];,.:";
        return delimiters.find(c) != string::npos;
    }

    bool isAtEnd() const {
        return pos_ >= source_.size();
    }

    char peek() const {
        return isAtEnd() ? '\0' : source_[pos_];
    }

    char peekNext() const {
        return (pos_ + 1 >= source_.size()) ? '\0' : source_[pos_ + 1];
    }

    char advance() {
        return source_[pos_++];
    }

    Token consumeWhitespace() {
        size_t start = pos_;
        while (!isAtEnd() && isspace(static_cast<unsigned char>(peek()))) {
            advance();
        }
        return {TokenType::Whitespace, source_.substr(start, pos_ - start)};
    }

    Token consumeIdentifierOrKeyword() {
        static const unordered_set<string> keywords = {
            "if", "else", "while", "for", "return", "int", "float",
            "bool", "true", "false", "void", "function", "var"};

        size_t start = pos_;
        while (!isAtEnd()) {
            char c = peek();
            if (isalnum(static_cast<unsigned char>(c)) || c == '_') {
                advance();
            } else {
                break;
            }
        }

        string lexeme = source_.substr(start, pos_ - start);
        if (keywords.count(lexeme) != 0) {
            return {TokenType::Keyword, lexeme};
        }
        return {TokenType::Identifier, lexeme};
    }

    Token consumeNumber() {
        size_t start = pos_;
        while (!isAtEnd() && isdigit(static_cast<unsigned char>(peek()))) {
            advance();
        }

        if (!isAtEnd() && peek() == '.' && isdigit(static_cast<unsigned char>(peekNext()))) {
            advance();
            while (!isAtEnd() && isdigit(static_cast<unsigned char>(peek()))) {
                advance();
            }
        }

        return {TokenType::Number, source_.substr(start, pos_ - start)};
    }

    Token consumeString() {
        size_t start = pos_;
        advance();

        while (!isAtEnd()) {
            if (peek() == '\\') {
                advance();
                if (!isAtEnd()) {
                    advance();
                }
                continue;
            }
            if (peek() == '"') {
                advance();
                return {TokenType::String, source_.substr(start, pos_ - start)};
            }
            advance();
        }

        return {TokenType::Unknown, source_.substr(start, pos_ - start)};
    }

    Token consumeLineComment() {
        size_t start = pos_;
        advance();
        advance();
        while (!isAtEnd() && peek() != '\n') {
            advance();
        }
        return {TokenType::Comment, source_.substr(start, pos_ - start)};
    }

    Token consumeBlockComment() {
        size_t start = pos_;
        advance();
        advance();

        while (!isAtEnd()) {
            if (peek() == '*' && peekNext() == '/') {
                advance();
                advance();
                return {TokenType::Comment, source_.substr(start, pos_ - start)};
            }
            advance();
        }

        return {TokenType::Unknown, source_.substr(start, pos_ - start)};
    }

    Token consumeOperator() {
        size_t start = pos_;
        char first = advance();

        if (!isAtEnd()) {
            char second = peek();
            bool isTwoChar =
                (first == '=' && second == '=') ||
                (first == '!' && second == '=') ||
                (first == '<' && second == '=') ||
                (first == '>' && second == '=') ||
                (first == '&' && second == '&') ||
                (first == '|' && second == '|');
            if (isTwoChar) {
                advance();
            }
        }

        return {TokenType::Operator, source_.substr(start, pos_ - start)};
    }

    Token consumeDelimiter() {
        size_t start = pos_;
        advance();
        return {TokenType::Delimiter, source_.substr(start, pos_ - start)};
    }

    Token consumeUnknown() {
        size_t start = pos_;
        advance();
        return {TokenType::Unknown, source_.substr(start, pos_ - start)};
    }
};

string readAllText(const string &path) {
    ifstream in(path, ios::binary);
    if (!in) {
        throw runtime_error("Nie mozna otworzyc pliku wejsciowego: " + path);
    }
    return string((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
}

string escapeHtml(const string &text) {
    string escaped;
    escaped.reserve(text.size());
    for (char c : text) {
        switch (c) {
            case '&': escaped += "&amp;"; break;
            case '<': escaped += "&lt;"; break;
            case '>': escaped += "&gt;"; break;
            case '"': escaped += "&quot;"; break;
            default: escaped += c; break;
        }
    }
    return escaped;
}

string tokenClass(TokenType type) {
    switch (type) {
        case TokenType::Keyword: return "tok-keyword";
        case TokenType::Identifier: return "tok-identifier";
        case TokenType::Number: return "tok-number";
        case TokenType::String: return "tok-string";
        case TokenType::Comment: return "tok-comment";
        case TokenType::Operator: return "tok-operator";
        case TokenType::Delimiter: return "tok-delimiter";
        case TokenType::Unknown: return "tok-unknown";
        default: return "";
    }
}

string generateHtml(const string &source) {
    Lexer lexer(source);
    string body;

    while (true) {
        Token token = lexer.nextToken();
        if (token.type == TokenType::End) {
            break;
        }

        if (token.type == TokenType::Whitespace) {
            body += escapeHtml(token.lexeme);
            continue;
        }

        string cssClass = tokenClass(token.type);
        body += "<span class=\"" + cssClass + "\">" + escapeHtml(token.lexeme) + "</span>";
    }

    return
        "<!DOCTYPE html>\n"
        "<html lang=\"pl\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\" />\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
        "  <title>Pokolorowany kod</title>\n"
        "  <style>\n"
        "    body { background: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; margin: 24px; }\n"
        "    pre { white-space: pre; margin: 0; }\n"
        "    .tok-keyword { color: #569cd6; font-weight: bold; }\n"
        "    .tok-identifier { color: #9cdcfe; }\n"
        "    .tok-number { color: #b5cea8; }\n"
        "    .tok-string { color: #ce9178; }\n"
        "    .tok-comment { color: #6a9955; font-style: italic; }\n"
        "    .tok-operator { color: #d4d4d4; }\n"
        "    .tok-delimiter { color: #dcdcaa; }\n"
        "    .tok-unknown { color: #f44747; text-decoration: underline; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <pre>" + body + "</pre>\n"
        "</body>\n"
        "</html>\n";
}

void writeAllText(const string &path, const string &content) {
    ofstream out(path, ios::binary);
    if (!out) {
        throw runtime_error("Nie mozna zapisac pliku wyjsciowego: " + path);
    }
    out << content;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        cerr << "Uzycie: skaner <plik_wejsciowy> <plik_wyjsciowy_html>" << endl;
        return 1;
    }

    try {
        const string inputPath = argv[1];
        const string outputPath = argv[2];

        string source = readAllText(inputPath);
        string html = generateHtml(source);
        writeAllText(outputPath, html);

        cout << "Wygenerowano plik HTML: " << outputPath << endl;
    } catch (const exception &ex) {
        cerr << "Blad: " << ex.what() << endl;
        return 1;
    }

    return 0;
}
