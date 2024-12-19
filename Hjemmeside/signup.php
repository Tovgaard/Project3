<?php
header('Content-type: text/plain; charset=utf-8');
// Databaseforbindelse
$servername = "34.32.58.98";
$username = "root";
$password = "Snk75zsg";
$dbname = "DHdatabase";

// Opret forbindelse til databasen
$conn = new mysqli($servername, $username, $password, $dbname);
// Tjek om forbindelsen er oprettet korrekt
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$conn->set_charset("utf8");

// Når formularen er sendt
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $navn = $_POST['navn'];
    $tlfnummer = $_POST['tlfnummer'];
    $discNavn = $_POST['discNavn'];
    $email = $_POST['email'];
    $primPlatform = $_POST['primPlatform'];
    $ppSubscribers = $_POST['ppSubscribers'];

    // Forbered og bind
    $stmt = $conn->prepare("INSERT INTO Personer (navn, tlfnummer, discNavn, email, primPlatform, ppSubscribers) VALUES (?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("sssssi", $navn, $tlfnummer, $discNavn, $email, $primPlatform, $ppSubscribers);

    // Eksekver statement
    if ($stmt->execute()) {
        $personID = $stmt->insert_id; // Få den indsatte PersonID

        // Hvis der er en ekstra platform, kan vi indsætte den i ØvrigePlatforme
        if (!empty($_POST['øvPlatforme'])) {
            $øvPlatforme = $_POST['øvPlatforme'];
            $stmt2 = $conn->prepare("INSERT INTO ØvrigePlatforme (PersonID, øvPlatforme) VALUES (?, ?)");
            $stmt2->bind_param("is", $personID, $øvPlatforme);
            $stmt2->execute();
        }

        // Omdiriger til takkesiden
        header("Location: thankyou.html");
        exit();
    } else {
        echo "Fejl ved indsættelse af data: " . $stmt->error;
    }

    // Luk statement
    $stmt->close();
}

// Luk forbindelsen
$conn->close();
?>