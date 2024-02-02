1. Projektowanie Interfejsu
Użyj QDragDrop do umożliwienia przeciągania i upuszczania plików do aplikacji.
Stwórz dwa przyciski, każdy reprezentujący różne polecenie do wykonania na serwerze.
Możesz także dodać pole tekstowe lub etykietę do wyświetlania ścieżki przesłanego pliku 
lub statusu przesyłania.

2. Implementacja Logiki Przesyłania
Po kliknięciu odpowiedniego przycisku, aplikacja powinna przesłać plik na serwer FTP. Tutaj możesz 
użyć biblioteki ftplib w Pythonie.
Przesłany plik powinien być automatycznie dodawany do kolejki zadań na serwerze. Możesz to osiągnąć, 
definiując logikę serwera, która będzie nasłuchiwać na nowe pliki i dodawać je do kolejki.

3. Kolejkowanie i Wykonywanie Zadań
Na serwerze możesz utworzyć prostą kolejkę zadań, używając np. listy w Pythonie, gdzie każde zadanie 
będzie zawierać ścieżkę do pliku i typ analizy.
Użyj modułu subprocess do uruchamiania poleceń solvera w oparciu o elementy w kolejce. Pamiętaj, aby 
sprawdzać, czy poprzedni proces się zakończył, zanim rozpoczniesz kolejny.