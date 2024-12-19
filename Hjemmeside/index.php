<?php
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

// Hent navnet fra URL-parametren
if (isset($_GET['name'])) {
    $name = $_GET['name'];

    // Forbered SQL-forespørgsel
    $sql = "SELECT * FROM users WHERE name = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $name);
    $stmt->execute();
    $result = $stmt->get_result();

    // Hvis navnet findes i databasen, returner det som JSON
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        echo json_encode(['success' => true, 'name' => $row['name']]);
    } else {
        // Hvis navnet ikke findes, returner fejlsvar
        echo json_encode(['success' => false]);
    }

    $stmt->close();
} else {
    // Hvis navnet ikke er sendt med i anmodningen
    echo json_encode(['success' => false, 'message' => 'Navn mangler!']);
}

// Luk forbindelsen
$conn->close();
?>
