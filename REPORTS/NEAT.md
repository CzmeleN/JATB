NEAT pętla
1. tworzy populacje prostych sieci 
2. dla każdej sieci zimerz jej fitness 
3. podziel sieci na gatunki (podobne do siebie)
4. z najlepszych w każdym gatunku stwórz potomstwo (krzyżowanie i mutacje)
5. go to 2. 

każda sieć jest zapisywana jako lista genemów:
* geny węzłów
* geny połączeń: skąd, dokąd, waga, numer innowacji, czy jest aktywny

mutacje:
* zmiana wagi: lekki przesunięcie wagi / losowanie od nowa
* dodanie połączenia: między dwoma niepołączonymi wcześniej węzłami 
* dodanie węzła: istniejące połączenie A -> B zostaje zastąpione A -> nowy -> B
    tak że jeśli A -(w)-> B to potem A-(1)-> nowy -(W)-> B 


każdy nowe połącznie dostaje unikalny numer innowacji. Jeśli w tym samym pokoleniu dwie sieci niezależnie dodadzą to samo połaczenie np (3) -> (1), to dosają ten sam numer

krzyżowanie:
| numer innowacji | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| rodzic A (fitness 120) | 0.5 | -1.0 | 0.7 | 0.8 | 0.2 | | | 0.9
| rodzic B (fitness 80) | 0.3 | -0.4 | | 0.8 | | 1.1 | -0.6 | 

1. ustalamy zakres każdego rodzica, czyli największy numer innowacji: A->8, B->7
2. dzielimy geny na 3 grupy:
    * pasujące (ten sam numer u obu rodziców) - 1, 2, 4
    * rozłączne (tylko u jednego z rodziców, ale numer mieści się w min z zakresów): 3, 5
    * nadmiarowe (występują tylko u jednego rodzica z tym większym zakresem): 8 

robienie dziecka: 
* pasujące geny wybieramy losowo (50%) z A lub B 
* rozłączne i nadmiarowe: tylko od lepszego rodzica (tutaj A)

dodatkowo jeśli gen był wyłączony u któregoś z rodziców, w dziecku zostaje wyłączony z dużym ppb (w paperze 75%)

neat dzieli populacje na gatunki na podstawie odległości między genami:
$$
\delta = \frac{c_1 E}{N} + \frac{c_2 D}{N} + c_3 \cdot \overline{W}
$$

* $E$ - liczba genów nadmiarowych
* $D$ - liczba genów rozłącznych
* $W$ - średnia różnica wag w genach pasujących
* $N$ - liczba genów w większym genomie 

w pracy NeuroEvolution of Augmenting Topologies, Stanley i Miikkulainen, 2002
$ c_1 = c_2 = 1, \ \ c_3 = 0.4 $ oraz $ \delta \leq 3.0 $  by były tym samym gatunkiem

zieci rywalizują wewnątrz swojego gatunku:
fitness każdej sieci dzieli się przez liczbę sieci w gatunku 
gatunki, które przz wiele pokoleń się nie poprawiają wymierają (są usunięte)


do tego wejścia i wyjścia są takie same w każdym genomi (stała liczba, te same id), dla tego podział na psujące, rozłączne i nadmiarowe dotyczą genów połączeń (węzły ykryte wchodzą do gry pośrednio, przez połączenia)

jak powstaje nowy węzeł:
węzeł ukryty powstaje tylko przez mutacje, ktora rozcina istniejace połączenie, np:
genom ma połączenie z wejścia 3 do wyjścia 20 o numerze innowacji 7 i wadze 0.6
* stare połączenie: z numerem innowacji 7 (3 -> 20) i wagą 0.6 zostaje wyłączone 
* nowe połączenie do węzła: z numerem innowacji 11 (powiedzmy przykładowy numer to 11) (3->25) z wagą 1.0 zostaje właczone
* nowe połączenie z węzła: z numerem innowacji 12 (powiedzmy przykładowy numer to 12) (25-> 20) z wagą 0.6 zostaje włączone

Funkcja aktywacji 
wszystkei węzły ukryte i wyjściowe w paperze używają tej samej sigmoidy
$$
    \sigma(x) = \frac{1}{1 + e^{-4{,}9x}}
$$