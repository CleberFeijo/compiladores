from lex import lexer

# Test it out
data = """
const TAM == 10;
      MSG == "digite as notas do aluno";
      
type vetor == array [15] of integer;
     aluno == record

            nota1 : real;
            nota2 : real
        end;
        
var A, B, C, D : integer;
    E : vetor;
    F : aluno;
    
procedure lerDados
begin
    write MSG;
    read F.nota1;
    read F.nota2;
end

function fatorial(a:integer) : integer
var i,result : integer;
begin
    i := 1;
    result:=1;
    while i < a do
    begin
        result:=result*i;
        i:=i+1;
    end;
    return result;
end

function exp(a: real; b: real) : real
var i,result : integer;
begin
    i := 1;
    result := a;
    if b = 0 then : result := 1
    else : while i < b do
    begin
        result := a * a;
        i := i + 1;
    end;
    return result;
end

function maior(a : vetor) : integer
var i : integer;
begin
    i := 0;
    result := a[0];
    while i < 15 do
    begin
        if a[i] > result then : result := a[i];
        i := i + 1;
    end;
    return result;
end

function menor(a : vetor) : integer
var i, result : integer;
begin
    i := 0;
    result := a[0];
    while i < 15 do
    begin
        if a[i] < result then : result := a[i];
        i := i + 1;
    end
    return result;
end

function media(a : vetor) : integer
var m : integer;
begin
    m := maior(a) + menor(a);
    return m / 2;
end

begin
    A:=TAM + 20;
    B := fatorial(A);
    C := exp(A,B);
    D := media(E);
    lerDados();
end
"""

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    print(tok)


# from yacc import parser
# data = "3 + 4 * 5 - 2"
# result = parser.parse(data)
# print(result)

