# DQN (Deep Q-Network) dla TMNF

źródła:
* Mnih i in., *Playing Atari with Deep Reinforcement Learning*, 2013, [arXiv:1312.5602](https://arxiv.org/abs/1312.5602)
* Mnih i in., *Human-level control through deep reinforcement learning*, Nature 2015, [doi:10.1038/nature14236](https://doi.org/10.1038/nature14236) (sieć target)

wzory są w blokach kodu (Unicode zamiast LaTeX-a), żeby czytały się w każdym podglądzie markdowna

---

## 1. wprowadzenie

### 1.1 setup

* agent = auto, środowisko = TMNF przez TMInterface
* krok = 50 ms czasu gry (5 ticków fizyki po 10 ms), czyli 20 decyzji na sekundę. w każdym kroku:
    * `s` - stan, wejście sieci: wektor liczb z input handlera (`InputHandler0`, 18 liczb)
    * `a` - akcja, którą wybieramy (sekcja 1.2)
    * `r` - nagroda za ten krok, liczona z dwóch kolejnych stanów gry (`IRewardFunction`)
    * `s'` - stan po kroku
    * `done` - czy epizod się skończył
* przejście = `(s, a, r, s', done)`, to jest jednostka danych, na której się uczymy
* epizod = jeden przejazd: od startu do mety, wypadnięcia albo limitu czasu
* zwrot (return) = suma nagród od teraz do końca, przyszłe nagrody ważone przez `γ`:

```
G_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + ...        0 ≤ γ < 1
```

* `γ` mówi, jak daleko agent patrzy w przyszłość: horyzont ≈ `1 / (1 − γ)` kroków. przy `γ = 0.99` to 100 kroków ≈ 5 s jazdy. horyzont w sekundach zależy od długości kroku, więc zmiana kroku = zmiana horyzontu
* cel agenta: wybierać akcje tak, żeby oczekiwany zwrot był jak największy

### 1.2 akcje

* zbiór akcji jest skończony: K akcji, akcja to indeks `0..K−1`
* sieć ma K wyjść, jedno na każdą akcję, więc numer wyjścia = numer akcji = to, co trafia do bufora. kolejności akcji nie wolno zmieniać w trakcie treningu
* akcja to **stała kombinacja klawiszy** (pełny gaz, pełny skręt), trzymana przez cały krok (50 ms)

teraz w kodzie: `OutputHandler0`, K = 6

| indeks | akcja |
| --- | --- |
| 0 | gaz, prosto |
| 1 | lewo (bez gazu) |
| 2 | prawo (bez gazu) |
| 3 | gaz + lewo |
| 4 | gaz + prawo |
| 5 | nic |

* w grze znak gazu jest odwrotny (do przodu < 0, hamulec > 0), odwraca go `CommManager.send_gas`

---

## 2. Q-learning, idea

uczymy się wartości pary stan-akcja:

```
Q(s, a) = oczekiwany zwrot, jeśli w stanie s zrobimy akcję a, a potem będziemy grać optymalnie
```

jak znamy Q, to polityka jest za darmo, bierzemy akcję z największym Q:

```
π(s) = argmax_a Q(s, a)
```

optymalne Q spełnia równanie Bellmana: wartość teraz = nagroda teraz + zdyskontowana wartość najlepszej akcji w następnym stanie

```
Q*(s, a) = E[ r + γ · max_a' Q*(s', a') ]
```

Q-learning: po każdym przejściu przesuwamy `Q(s, a)` w stronę nagrody + wartości najlepszej akcji w następnym stanie:

```
Q(s, a) ← Q(s, a) + α · ( r + γ · max_a' Q(s', a') − Q(s, a) )        α - learning rate
```

najważniejsza własność: **off-policy**. cel używa `max_a' Q(s', a')`, a nie akcji, którą faktycznie zrobiliśmy potem. dlatego można się uczyć z przejść zebranych dowolną polityką: losową, starszą wersją sieci, z innego przejazdu. to pozwala trzymać przejścia w buforze i używać ich wiele razy

---

## 3. DQN, learning objective

### 3.1 wybór akcji: ε-greedy

```
a = losowa akcja (jednostajnie z K)        z ppb ε
a = argmax_a Q_θ(s, a)                     wpp.
```

* „zgodnie z polityką” = puść `s` przez sieć, weź wyjście z największą wartością
* ε na początku ≈ 1 (prawie losowo), potem maleje, coraz częściej jedzie sieć
* bez eksploracji sieć nigdy nie sprawdzi akcji, które dziś uważa za gorsze

### 3.2 loss

na batchu B przejść `(s_j, a_j, r_j, s'_j, done_j)` z bufora:

```
Loss(θ) = (1/B) · Σ_j  ℓ( Q_θ(s_j, a_j) − y_j )          B - rozmiar batcha

y_j = r_j                                       jeśli done_j
y_j = r_j + γ · max_a' Q_θ⁻(s'_j, a')           wpp.
```

**learning objective**: minimalizujemy `Loss(θ)`, czyli przesuwamy `Q_θ(s, a)` w stronę `y`. gdy loss → 0, Q spełnia równanie Bellmana na danych z bufora

* `θ` - wagi sieci Q, `θ⁻` - wagi **sieci target**, wolniej zmienianej kopii sieci głównej. dzięki niej cel nie ucieka przy każdym update'cie
* `done` tu znaczy **koniec prawdziwy** (meta, wypadnięcie). przy limicie czasu liczymy cel normalnie (z `max Q(s')`), bo auto mogło jechać dalej (`terminated` vs `truncated`)
* `y` traktujemy jak stałą: liczymy bez gradientu

### 3.3 sieć target

* plan: najpierw zwykły DQN jak w 2013 (bez sieci target, cel liczony tą samą siecią, `θ⁻ = θ`), potem wersja z 2015 z siecią target i soft updatem
* hard update (2015): co C update'ów kopiujemy całe wagi, `θ⁻ ← θ`
* soft update (z DDPG, Lillicrap i in., 2015): po każdym update'cie `θ⁻ ← τ·θ + (1 − τ)·θ⁻`, np. τ = 0.005
* oba działają, to tylko hiperparametr

### 3.4 replay buffer

bufor ostatnich M przejść, z którego losujemy batche. po co:

* każde przejście jest używane wiele razy (jazda kosztuje czas symulacji)
* kolejne kroki są prawie identyczne, losowanie z bufora łamie tę korelację
* sieć nie uczy się tylko na tym, co sama teraz robi (bez tego łatwo o oscylacje)
* działa, bo Q-learning jest off-policy (sekcja 2)

---

## 4. dwie pętle

podział ról:

```
Game         jedna gra, jedno auto: reset, make_step(akcja) → (s', r, done)
Scheduler    pula gier: puszcza politykę na wszystkich, oddaje przejścia (s, a, r, s', done)
DQNTrainer   bierze przejścia od schedulera → replay buffer → update sieci
DQNAgent     sieć Q: policy(s) (ε-greedy) i update(batch)
```

bufor i update siedzą w trenerze, a nie w schedulerze, żeby scheduler został wspólny z NEAT

### 4.1 pętla zbierania (scheduler, w każdej grze)

```
s = reset()
N razy (łącznie ze wszystkich gier):
    a = policy(s)                         # ε-greedy
    s', r, done = make_step(a)            # 50 ms gry (opcjonalnie potem pauza)
    zapisz (s, a, r, s', done)
    s = reset() jeśli koniec przejazdu, wpp. s'
```

* stan dla polityki pochodzi z poprzedniego kroku: `make_step` wysyła akcję, czeka 50 ms czasu gry i oddaje stan, który z niej wyszedł
* N to **suma kroków ze wszystkich gier** na jedną rundę. przy 4 grach i N = 200 każda gra robi 50 kroków (2,5 s jazdy)
* runda nie kończy się razem z przejazdem: gry mogą być w połowie trasy, po update'ach jadą dalej już nową siecią

### 4.2 pętla treningu (DQNTrainer)

```
DQNTrainer.train():
    powtarzaj:
        przejścia = scheduler.collect_steps(agent.policy, N)          # jazda (4.1)
        buffer.extend(przejścia)
        U razy: agent.update(buffer.sample(64))                       # nauka
```

* `agent.update(batch)`: cel y, loss, backprop, krok optymalizatora, update sieci target (sekcja 3)
* na początku warmup: nie uczymy, dopóki w buforze jest mniej przejść niż batch
* U = liczba update'ów w jednej rundzie. każdy update to **osobny losowy batch** z całego bufora
* update nie czeka na koniec przejazdu: sieć zmienia się co rundę, przejazdy toczą się dalej
* wersja synchroniczna: najpierw jazda, potem nauka. najprostsza i poprawna, od niej zaczynamy

**replay ratio**, czyli ile razy (średnio) każde nowe przejście trafi do treningu, ważniejsze niż samo N:

```
replay ratio = U · B / N          B - rozmiar batcha (tu 64)
```

---

## 5. ustalenia

**nagroda** (plan): postęp wzdłuż linii centralnej trasy, czyli o ile w tym kroku przesunął się rzut auta na tę linię (do przodu > 0, do tyłu < 0)
* suma postępu za cały przejazd = długość trasy, niezależnie od czasu. za szybkość nagradza więc tylko `γ < 1` (postęp zdobyty wcześniej jest więcej wart) i limit czasu
* wypadnięcie / utknięcie nie daje kary wprost, bot traci tylko przyszły postęp. jeśli to za słaby sygnał, osobna kara
* nie przycinamy do znaku (wtedy szybka i wolna jazda dawałyby to samo), najwyżej skalujemy, żeby typowe `|r|` było rzędu 1

**koniec epizodu**: `terminated` (meta, wypadnięcie) idzie do celu jako `done`, `truncated` (limit czasu) tylko resetuje grę

**losowe starty**: jako dodatek, nie zamiennik
* plus: bot od początku widzi całą trasę, nie tylko pierwsze zakręty, i mniej „wykuwa” jedną trajektorię (fizyka jest deterministyczna)
* ale auto musi też uczyć się własnych konsekwencji z ciągłej jazdy (za szybki wjazd w zakręt po własnym rozpędzeniu się)
* start z sensownego stanu (pozycja, prędkość, obrót), np. ze stanów zapisanych w poprzednich przejazdach, nie z dowolnego miejsca
* np. 70–80% przejazdów od startu, 20–30% od losowego zapisanego stanu
* TMInterface 2.2.1 to umożliwia (sprawdzone w API, jeszcze nie na żywo):
    * w pluginie: `sim.SaveState()` → `SimulationState`, `sim.RewindToState(state)`; stan można zamienić na bajty (`ToArray()`) i odtworzyć z bajtów, więc pulę stanów startowych może trzymać Python
    * bez zmian w pluginie: komendy konsoli `save_state plik.bin` / `load_state plik.bin` przez nasze `EXECUTE` (pliki w `Documents/TMInterface/States`)
    * ograniczenie: nie da się zapisać ani wczytać stanu w czasie odliczania i po mecie

**NEAT a ta architektura**:
* wspólne: pula gier, krok 50 ms, reset. scheduler ma dwie metody: `run_episodes(policies)` → wynik każdego przejazdu (NEAT bierze fitness), `collect_steps(policy, N)` → przejścia (DQN wrzuca je do bufora)
* różnica: w NEAT każda gra jedzie innym osobnikiem, w DQN wszystkie tą samą siecią
* NEAT nie potrzebuje osobnego learnera: ewolucja potrzebuje fitness całej populacji naraz (bariera po generacji) i trwa milisekundy. ma sens tylko równoległa ocena: pula gier + kolejka osobników
* losowe starty w NEAT: wszystkie osobniki w generacji muszą startować z tych samych miejsc, inaczej fitness jest nieporównywalny

**na później**:
* osobny proces learnera: gry ciągle jeżdżą (każda z lokalną kopią sieci) i wrzucają przejścia, learner ciągle trenuje, wagi trafiają do gier co przejazd. tak (z pamięci, niesprawdzone) robił Linesight. szybsze, ale bardziej skomplikowane
* IQN: sieć przewiduje rozkład zwrotu (kwantyle) zamiast jednej liczby Q
