# Report 01

## Ustalony temat

- Bot do Trackmanii Nations Forever w oparciu o RL
    - celem jest przejście 15 tras na poziomie białym
    - jeśli uda nam się to osiągnąć, zajmiemy się douczaniem aby pobijać czasy na kolejne medale
    - gra jest odpalana przez wine, bot natywnie pod linuxem
    - do otrzymywania info z gry wykorzystujemy TMLoader z TMInterface i customowy skrypt

## Progress

- Zaplanowaliśmy architekturę umożliwiającą zarządzanie botem oraz instancją gry
- Utworzyliśmy plugin do TMInterface umożliwiający zczytywanie danych oraz wysyłanie komend do gry
- Utworzyliśmy moduł w pythonie komunikujący się z w/w pluginem przez socket
- Udało nam się odpalić bota (Random Walk) bez jakiegokolwiek inputu z naszej strony

## Narzędzia

- jedynym zewnętrznym narzędziem które używamy jest TMInterface, reszta narzędzi jest autorska

## Źródła wiedzy

- Większość wiedzy o tym co potrzebujemy do projektu czerpiemy z kanału na youtube Yosh, przeanalizowaliśmy jego twórczość i wyciągneliśmy wnioski [notatki](/REPORTS/bot_notatki.md)

## Plany na przyszłość

- dodać 2 algorytmy by nauczyć naszego bota jazdy - DQN i NEAT
- dostęp do informacji o mapie po której porusza się bot, takich jak odległość od lini która przebiega przez środek mapy,która pozwoli botowa na zorientowanie się czy jedzie prawodłowo oraz za ile i w którą stronę jest następny zakręt