DQN (Deep Q-Learning), skrót
paper: Mnih i in., *Playing Atari with Deep Reinforcement Learning*, 2013, [arXiv:1312.5602](https://arxiv.org/abs/1312.5602)

idea: sieć Q(s, a) przewiduje, ile nagrody jeszcze zbierzemy, jeśli w stanie s zrobimy akcję a, a potem będziemy grać dobrze.
jak znamy Q, to jazda jest prosta: w każdym kroku bierzemy akcję z największym Q.

co znaczy co:
* s - stan, czyli wejście sieci: 18 liczb z gry albo obraz (do ustalenia, patrz „wejście sieci” niżej)
* a - akcja: indeks 0..8 z `ACTIONS` w `jatb/bot/actions.py` (gaz / nic / hamulec × lewo / prosto / prawo)
* r - nagroda za jeden krok: postęp wzdłuż linii centralnej trasy prowadzącej do mety, czyli o ile w tym kroku przesunął się rzut auta na tę linię (do przodu > 0, do tyłu < 0); im szybciej jedziemy, tym większe r w każdym kroku
* s' - stan po kroku, done - czy epizod się skończył
* krok - 50 ms: akcję trzymamy przez 5 ticków fizyki (po 10 ms), czyli 20 decyzji na sekundę
* γ (gamma) - jak bardzo liczy się przyszłość, u nas 0.99: agent patrzy ok. 100 kroków ≈ 5 s do przodu
* ε (epsilon) - szansa na losową akcję zamiast najlepszej (eksploracja), maleje w trakcie treningu
* replay memory D - bufor ostatnich N przejść (s, a, r, s', done), z niego losujemy dane do nauki

wejście sieci (do ustalenia, zależy od tego, skąd bot ma wiedzieć, co go lokalnie czeka, np. zakręt w prawo):
* wariant A, 18 liczb z gry (prędkości, obrót, bieg, skręt kół, kąt i odległość od środka drogi, najbliższe zakręty):
    * informację o tym, co przed nami, liczymy sami z danych mapy
    * wystarczy MLP 18 → 128 → 128 → 9, ReLU (`DQN` w `jatb/trainer/dqn_agent.py`)
* wariant B, obraz z gry:
    * sieć sama „widzi”, co ją czeka, nie musimy tego liczyć z mapy
    * jak w paperze: CNN, obraz w skali szarości 84×84, 4 ostatnie klatki naraz (z jednej nie widać ruchu)
    * warstwy: conv 16 filtrów 8×8, stride 4 → conv 32 filtry 4×4, stride 2 → fc 256 → 9 wyjść
    * droższe obliczeniowo i wolniej się uczy (paper: 10 mln klatek na grę)
* wariant C, oba naraz: obraz przez CNN + liczby z gry (prędkość itp.) doklejone przed warstwami fc

sieć (w każdym wariancie):
* wyjście: 9 liczb, czyli Q dla każdej akcji naraz (jeden forward), ostatnia warstwa liniowa
* kolejności `ACTIONS` nie zmieniamy: indeks akcji = numer wyjścia sieci = to, co siedzi w buforze

DQN pętla
1. weź stan s z gry
2. z ppb ε wybierz losową akcję, wpp. a = argmax Q(s, ·)
3. wyślij akcję do gry, po 50 ms odczytaj s', r, done
4. zapisz (s, a, r, s', done) w D
5. wylosuj z D minibatch (np. 64 przejścia)
6. dla każdego przejścia policz cel:
    * y = r, jeśli done
    * y = r + γ · max Q_target(s', ·), wpp.
7. krok gradientu, żeby Q(s, a) zbliżyło się do y (loss Huber / MSE)
8. lekko przesuń sieć target w stronę głównej sieci
9. go to 1. (po done: restart wyścigu)

```
błąd TD:  δ = r + γ · max_a' Q_target(s', a') − Q(s, a)
update:   wagi przesuwamy tak, żeby δ → 0
```

przykład: auto przed zakrętem, sieć daje Q = [.., gaz+prosto: 12.0, gaz+lewo: 10.5, ..], więc jedzie prosto, ale uderza w ścianę.
auto stoi, więc postęp r ≈ 0, a s' to stan „po zderzeniu” z niskim Q, więc y wychodzi dużo mniejsze niż 12.0 i Q(gaz+prosto) w tym stanie spada.
następnym razem wygrywa gaz+lewo. informacja o ścianie cofa się tak krok po kroku do wcześniejszych stanów.

po co replay memory:
* każde przejście jest używane wiele razy (jazda kosztuje czas symulacji)
* kolejne kroki co 50 ms są prawie identyczne, a losowanie z bufora łamie tę korelację
* sieć nie wpada w pętlę „uczę się tylko na tym, co sama teraz robię”
* przez to uczymy się na starych danych, czyli algorytm musi być off-policy, więc Q-learning

po co sieć target: cel y liczymy osobną, wolniej zmienianą kopią sieci (soft update, τ = 0.005), żeby cel nie uciekał przy każdym kroku.
w paperze z 2013 jej nie ma, doszła w wersji z 2015.

jak to u nas wygląda:
* `jatb/bot/actions.py` - 9 akcji
* `jatb/game/Game.py` - `make_step` wysyła akcję, robi krok 50 ms, zwraca obserwację, nagrodę i is_finished
* `jatb/scheduler` - `Transition(state, action, reward, next_state, done)`, `collect_steps` zbiera kroki z kilku instancji gry naraz do jednego bufora
* TODO `jatb/trainer/dqn_agent.py` - sieć, ε-greedy (`select_action`), update z siecią target (`update`); jest szkic, jeszcze niezacommitowany
* `jatb/trainer/dqn_trainer.py` - pętla: zbierz kroki → wrzuć do bufora → update'y (bufor jeszcze TODO)
* hiperparametry: γ = 0.99, lr = 3e-4 (AdamW), batch 64, ε od 0.9 do 0.01

paper vs my:
| | paper (Atari) | my (TMNF) |
| --- | --- | --- |
| wejście | 4 klatki 84×84 | 18 liczb albo obraz (do ustalenia) |
| akcje | 4–18 | 9 |
| krok | co 4 klatki (~67 ms) | 50 ms |
| nagroda | zmiana wyniku w grze, przycięta do {−1, 0, 1} | postęp wzdłuż linii centralnej w kroku, nie przycinamy, najwyżej skalujemy (wielkość postępu = prędkość) |
| ε | 1 → 0.1 liniowo, potem stałe 0.1 | 0.9 → 0.01 wykładniczo |
| batch / optymalizator | 32 / RMSProp | 64 / AdamW |

na co uważać:
* limit czasu ≠ koniec: przy timeoucie nie ustawiamy done = True w celu (auto mogło jechać dalej), done tylko przy mecie lub wypadnięciu
* suma postępu za cały przejazd = długość trasy, niezależnie od czasu, więc za szybkość nagradza tylko γ < 1 (postęp zdobyty wcześniej jest więcej wart) i limit czasu
* wypadnięcie / utknięcie nie daje kary wprost, bot traci tylko przyszły postęp; jeśli to za słaby sygnał, można dodać osobną karę
* za mało update'ów: w paperze na każde nowe przejście przypada 32 próbki z bufora, u nas teraz 64 na 200 kroków
* fizyka TMNF jest deterministyczna, więc bot może „wykuć” jedną trasę: losowe starty (miejsce, prędkość, obrót) i ewaluacja z małym ε
* γ zależy od długości kroku: krótszy krok przy tym samym γ = krótszy horyzont w sekundach
