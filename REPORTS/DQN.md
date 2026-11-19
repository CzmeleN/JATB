# DQN (Deep Q-Network) dla TMNF

źródła:
* Mnih i in., *Playing Atari with Deep Reinforcement Learning*, 2013, [arXiv:1312.5602](https://arxiv.org/abs/1312.5602)
* Mnih i in., *Human-level control through deep reinforcement learning*, Nature 2015, [doi:10.1038/nature14236](https://doi.org/10.1038/nature14236) (sieć target)

---

## 1. wprowadzenie

### 1.1 setup

* agent = auto, środowisko = TMNF przez TMInterface
* krok = 50 ms czasu gry (5 ticków fizyki po 10 ms), czyli 20 decyzji na sekundę. w każdym kroku:
    * $s$ - stan, wejście sieci: wektor liczb z input handlera (`InputHandler0`, 18 liczb)
    * $a$ - akcja, którą wybieramy (sekcja 1.2)
    * $r$ - nagroda za ten krok, liczona z dwóch kolejnych stanów gry (`IRewardFunction`)
    * $s'$ - stan po kroku
    * `done` - czy epizod się skończył
* przejście = $(s, a, r, s', \text{done})$, to jest jednostka danych, na której się uczymy
* epizod = jeden przejazd: od startu do mety, wypadnięcia albo limitu czasu
* zwrot (return) = suma nagród od teraz do końca, przyszłe nagrody ważone przez $\gamma$:

$$G_t = r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \dots \qquad 0 \le \gamma < 1$$

* $\gamma$ mówi, jak daleko agent patrzy w przyszłość: horyzont $\approx \frac{1}{1 - \gamma}$ kroków. przy $\gamma = 0.99$ to 100 kroków $\approx$ 5 s jazdy. horyzont w sekundach zależy od długości kroku, więc zmiana kroku = zmiana horyzontu
* cel agenta: wybierać akcje tak, żeby oczekiwany zwrot był jak największy

### 1.2 akcje

* zbiór akcji jest skończony: $K$ akcji, akcja to indeks $0, \dots, K - 1$
* sieć ma $K$ wyjść, jedno na każdą akcję, więc numer wyjścia = numer akcji = to, co trafia do bufora. kolejności akcji nie wolno zmieniać w trakcie treningu
* akcja to **stała kombinacja klawiszy** (pełny gaz, pełny skręt), trzymana przez cały krok (50 ms)

teraz w kodzie: `OutputHandler0`, $K = 6$

| indeks | akcja |
| --- | --- |
| 0 | gaz, prosto |
| 1 | lewo (bez gazu) |
| 2 | prawo (bez gazu) |
| 3 | gaz + lewo |
| 4 | gaz + prawo |
| 5 | nic |

---

## 2. Q-learning, idea

uczymy się wartości pary stan-akcja: $Q(s, a)$ = oczekiwany zwrot, jeśli w stanie $s$ zrobimy akcję $a$, a potem będziemy grać optymalnie

jak znamy $Q$, to polityka jest za darmo, bierzemy akcję z największym $Q$:

$$\pi(s) = \arg\max_a Q(s, a)$$

optymalne $Q$ spełnia równanie Bellmana: wartość teraz = nagroda teraz + zdyskontowana wartość najlepszej akcji w następnym stanie

$$Q^\ast(s, a) = \mathbb{E}\left[ r + \gamma \max_{a'} Q^\ast(s', a') \right]$$

Q-learning: po każdym przejściu przesuwamy $Q(s, a)$ w stronę nagrody + wartości najlepszej akcji w następnym stanie ($\alpha$ - learning rate):

$$Q(s, a) \leftarrow Q(s, a) + \alpha \left( r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right)$$

najważniejsza własność: **off-policy**. cel używa $\max_{a'} Q(s', a')$, a nie akcji, którą faktycznie zrobiliśmy potem. dlatego można się uczyć z przejść zebranych dowolną polityką: losową, starszą wersją sieci, z innego przejazdu. to pozwala trzymać przejścia w buforze i używać ich wiele razy

---

## 3. DQN, learning objective

### 3.1 wybór akcji: $\varepsilon$-greedy

* z ppb $\varepsilon$: losowa akcja (jednostajnie z $K$)
* wpp.: zgodnie z polityką, $a = \arg\max_a Q_\theta(s, a)$, czyli puść $s$ przez sieć i weź wyjście z największą wartością
* $\varepsilon$ na początku $\approx 1$ (prawie losowo), potem maleje, coraz częściej jedzie sieć
* bez eksploracji sieć nigdy nie sprawdzi akcji, które dziś uważa za gorsze

### 3.2 loss

na batchu $B$ przejść $(s, a, r, s', \text{done})$ z bufora:

$$\text{Loss}(\theta) = \frac{1}{B} \sum_{j=1}^{B} \ell\left( Q_\theta(s_j, a_j) - y_j \right)$$

$$y_j = r_j + (1 - \text{done}_j) \cdot \gamma \max_{a'} Q_{\theta^-}(s'_j, a')$$

`done` to 0 albo 1, więc na końcu epizodu zostaje samo $r_j$

**learning objective**: minimalizujemy $\text{Loss}(\theta)$, czyli przesuwamy $Q_\theta(s, a)$ w stronę $y$. gdy $\text{Loss} \to 0$, $Q$ spełnia równanie Bellmana na danych z bufora

* $\theta$ - wagi sieci $Q$, $\theta^-$ - wagi **sieci target**, wolniej zmienianej kopii sieci głównej. dzięki niej cel nie ucieka przy każdym update'cie
* `done` tu znaczy **koniec prawdziwy** (meta, wypadnięcie). przy limicie czasu liczymy cel normalnie, z $\max_{a'} Q(s', a')$, bo auto mogło jechać dalej (`terminated` vs `truncated`)
* $y$ traktujemy jak stałą: liczymy bez gradientu

### 3.3 sieć target

* plan: najpierw zwykły DQN jak w 2013 (bez sieci target, cel liczony tą samą siecią, $\theta^- = \theta$), potem wersja z 2015 z siecią target i soft updatem
* hard update (2015): co $C$ update'ów kopiujemy całe wagi, $\theta^- \leftarrow \theta$
* soft update (z DDPG, Lillicrap i in., 2015): po każdym update'cie $\theta^- \leftarrow \tau \theta + (1 - \tau) \theta^-$, np. $\tau = 0.005$
* oba działają, to tylko hiperparametr

### 3.4 replay buffer

bufor ostatnich $M$ przejść, z którego losujemy batche. po co:

* każde przejście jest używane wiele razy (jazda kosztuje czas symulacji)
* kolejne kroki są prawie identyczne, losowanie z bufora łamie tę korelację
* sieć nie uczy się tylko na tym, co sama teraz robi (bez tego łatwo o oscylacje)
* działa, bo Q-learning jest off-policy (sekcja 2)

### 3.5 pętla treningu

w kółko:
1. zbierz $N$ kroków polityką $\varepsilon$-greedy, przejścia wrzuć do bufora
2. $U$ razy: update na osobnym losowym batchu ($B = 64$) z bufora

* update = cel $y$, loss, backprop, krok optymalizatora, update sieci target
* warmup: nie uczymy, dopóki w buforze jest mniej przejść niż batch
* **replay ratio**, czyli ile razy (średnio) każde nowe przejście trafi do treningu, jest ważniejsze niż samo $N$:

$$\text{replay ratio} = \frac{U \cdot B}{N}$$

---

## 4. propozycje (do ustalenia)

**nagroda**: postęp wzdłuż linii centralnej trasy, czyli o ile w tym kroku przesunął się rzut auta na tę linię (do przodu > 0, do tyłu < 0)
* suma postępu za cały przejazd = długość trasy, niezależnie od czasu. za szybkość nagradza więc tylko $\gamma < 1$ (postęp zdobyty wcześniej jest więcej wart) i limit czasu
* wypadnięcie / utknięcie nie daje kary wprost, bot traci tylko przyszły postęp. jeśli to za słaby sygnał, osobna kara
* nie przycinamy do znaku (wtedy szybka i wolna jazda dawałyby to samo), najwyżej skalujemy, żeby typowe $|r|$ było rzędu 1

**koniec epizodu**: `terminated` (meta, wypadnięcie) idzie do celu jako `done`, `truncated` (limit czasu) tylko resetuje grę

**losowe starty**: jako dodatek, nie zamiennik
* plus: bot od początku widzi całą trasę, nie tylko pierwsze zakręty, i mniej "wykuwa" jedną trajektorię (fizyka jest deterministyczna)
* ale auto musi też uczyć się własnych konsekwencji z ciągłej jazdy (za szybki wjazd w zakręt po własnym rozpędzeniu się)
* start z sensownego stanu (pozycja, prędkość, obrót), np. ze stanów zapisanych w poprzednich przejazdach, nie z dowolnego miejsca
* np. 70-80% przejazdów od startu, 20-30% od losowego zapisanego stanu
* TMInterface 2.2.1 to umożliwia (sprawdzone w API, jeszcze nie na żywo):
    * w pluginie: `sim.SaveState()` zwraca `SimulationState`, `sim.RewindToState(state)`; stan można zamienić na bajty (`ToArray()`) i odtworzyć z bajtów, więc pulę stanów startowych może trzymać Python
    * bez zmian w pluginie: komendy konsoli `save_state plik.bin` / `load_state plik.bin` przez nasze `EXECUTE` (pliki w `Documents/TMInterface/States`)
    * ograniczenie: nie da się zapisać ani wczytać stanu w czasie odliczania i po mecie

**na później**:
* osobny proces learnera, jak w Linesight: boty grają w grę (każdy z lokalną kopią sieci) i wrzucają przejścia do bufora, a learner w tym czasie się uczy i regularnie przekazuje botom nowe wagi
* IQN: sieć przewiduje rozkład zwrotu (kwantyle) zamiast jednej liczby Q
