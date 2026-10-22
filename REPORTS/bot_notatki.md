## pierwszy bot 
* [link](https://www.youtube.com/watch?v=a8Bo2DHrrow)
* tu są opcje:
    1. supervised learning
    2. genetic algorithm (NEAT)

* problemy:
    AI nie ma pamięci o paie i nie umie przewidywać następnego ruchu 

* 8 inputs:
    * wall distances
    * speed 

* 3 outputs:
    * left 
    * right 
    * accelerate

* fitnes functions:
    1. dystans przejechany przez auto
    2. czas zarejestrowany na każdym check poincie

* idee:
    * ustawiamy timmer z czasem który ma nasz bot na przejechanie toru, najpierw mały, tak by przyśpieszyć uczenie się
    * popatrz sobie na Q-learing yosh wspominał coś o nim

## drugi bot 
* [link](https://www.youtube.com/watch?v=i1XqbUrarEg) tutaj autka mają nie uderzyć ściany 
* używa NEAT 
* każda generacja ma 200 autek 

## trzeci bot 
* [link](https://youtu.be/iZIPowqm-fo?si=8Cx2Zw89f5hwW-yM) tutaj autka mają jeźcić po rurze

* inputs:
    * position_x - pozycja na rurze
    * position_y
    * speed
    * acceleration
    * yaw
    * pitch 
    * roll 

* potem jeszcze jak rury sie zaginają do inputu dodaje:
    * dystans do zakrętu 
    * kierunkek za zakrętem 

* output
    * kierunek jak na joysticku 
    * accelerate 
    * potem jeszcze dodał brake, o którym nie wspominał na początku 

* używa `openplanet` do komunikacji python <-> trackmania
* algorytm: 
    * NEAT (średni wynik)
    * Q-learing (średni wynik)
    * supervised learning (całkiem całkiem)

* fitnes functions:
    1. dystans przejechany na rurze 
    2. dystans przejechany na rurze, jeśli dojedzie do końca to dodatkowe punkty za czas 

## czwarty bot
* [link](https://youtu.be/SX08NT55YhA?si=xZ7CaixV1Ihlt97G) zwykła jazda 
* input (wygląda jakby miało 8 wartości): coś zaawansowanego, mało o tym mówi. ale na pewno ma:
    * speed 
    * acceleration 
    * jak auto jest pozycjonowane na segmęcie drogi przez którą obecnie jedzie 
    * informacja o tym co jest przed nim - jak długi odcinek drogi, dwa następne skrętwy w którą strone 

* output: autko może wybrać jedną z 6 akcji (tak jakby rało na klawiaturze) - narazie nie dodaje hamowania by uproscić model 
    * nic
    * strzałka prawo 
    * strzałka leto 
    * strzałka góra 
    * strzałka góra + lewo
    * strzałka góra + prawo

* idee:
    * wcześniej porytnywaliśmy poty na podstawie np ostatecznego czasu w którym przejechał trase, nie dając mu informacji 
        o tym jak osbie radził gdzieś po środku, można wprowadzić reward 
    * próbujemy nauczyć model by przewidywał przyszłość, niezawdze wiekszy reward teraz da ostatecznie najlepszy wynik 
    * zaczynamy nazde w randomowym miejscu z randomową prędkością i randomową rotacją - dzięki temu nie mamy overfitingu i 
        model uczy sie generalizacji 

* reward:
    1. jak szybko jedzie nasze autko 

* tutaj używamy TMInterface, dzieki któremu może przyśpieszyć czas w grze 

* algorytm: 
    Deep-Q-Learning - dla każdego możliwego inputu model próbuje przewidzieć reward dla niego 


## piąty bot 
* [link](https://www.youtube.com/watch?v=Dw3BZ6O_8LY) - zwykłą jazda 
* input:
    * speed 
    * acceleration 
    * turning rate
    * lateral velocity 
    * distance to center line 
    * angle to centerline 
    * next curve distance 
    * next curve direction 

* output 
    * accelerate 
    * steer 

* idee:
    * nie dodawanie opcji hamowania upraszcza model 
    * z drugiej strony jak będzie dubrze szło to kiedyś dodajmy hamowanie, na pewnoe nie na początek 
    * można dodać kiedyś bonus za neo-drift, by zachęcić model by driftował 
    * [mamy link do mapy](https://tmnf.exchange/tracksearch?query=author%3a+yoshtm)

* input #2 - 20 wartości
    * speed 
    * acceleration 
    * turning rate 
    * lateral velocity 
    * distance to cneter line 
    * angle to center line 
    * d1 - dystans do kolejnego zakrętu
    * d2 - dystans do kolejnego kolejnego zakrętu
    * d3 
    * c1 - w ktorą strone jest kolejny zakręt 
    * c2 - w którą stronę jest kolejny kolejny zakręt 
    * c3
    * pitch 
    * roll 
    * wheels contact (4 inputs)
    * wheels sliding (4 inputs)

## szusty bot 
* [link](https://www.youtube.com/watch?v=kojH8a7BW04) - znowu jazda po rurach 
* input 
    * speed 
    * acceleration 
    * turning rate 
    * lateral position 
    * vertical poisition 
    * yaw 
    * pitch 
    * roll 

* input #2 
    * speed 
    * acceleration 
    * turning rate
    * lateral position 
    * vertical position 
    * yaw 
    * pitch 
    * roll 
    * corner distance 
    * next corner distance 
    * next corner direction 
    * close to finish - specjalnie pod daną mape, przez to że końcówka jest niefajna
    * wheels contact (4 inputs)
    * wheels sliding (4 inputs)


* output:
    * accelerate
    * brake 
    * steer 

* idee 
    * yosh nie za dużo actions / sec, bo mówił że próbował zwiększyć to do 33 akcji / sec (nie pomogło), możliwe że wcześniej miał jakieś ~15 akcji / sec

## siudmy bot 
* [link](https://www.youtube.com/watch?v=NUl6QikjR04) - nauk noseboost
* input
    * velocity x, y, z (3 inputs)
    * rotation x, y, z (3 inputs)
    * angular velocity x, y, z (3 inputs)
    * gear
    * turning rate
    * height 
    * track x, y, dir (3 inputs)
    * wheels contact (4 inputs)
    * wheels sliding (4 inputs)

* input #x dodatkowe info, w sumie nieistotne dla nas 
    

* idee
    * można przetestować PPO 
    

## ósmy bot 
* [link](https://www.youtube.com/watch?v=zFLQU70QstY) - bicie wr 
* input
    * velocity x, y, z (3 inputs)
    * rotation x, y, z (3 inputs)
    * angular velocity x, y, z (3 inputs)
    * gear
    * turning rate
    * wheels contact (4 inputs)
    * wheels sliding (4 inputs)
    * centerline lateral distance 
    * centerline vertical distance 
    * progress 

* info
    * używa update outputu do gry 20 razy na sekunde 

## dziewiaty bot 
* [link](https://www.youtube.com/watch?v=1AGVABna3xQ) - kolejne bicie wr 
* input
    * velocity x, y, z (3 inputs)
    * rotation x, y, z (3 inputs)
    * angular velocity x, y, z (3 inputs)
    * gear
    * turning rate
    * wheels contact (4 inputs)
    * wheels sliding (4 inputs)

* nie mówi że dodawał do inputu (ale pewnie dodał):
    * centerline lateral distance 
    * centerline vertical distance 
    * progress 