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
    error_log("Connection failed: " . $conn->connect_error);
    echo json_encode(['success' => false, 'message' => 'Connection failed: ' . $conn->connect_error]);
    exit();
}

// Hent navnet fra URL-parametren
if (isset($_GET['navn'])) {
    $name = $_GET['navn'];

    // Forbered SQL-forespørgsel
    $sql = "SELECT navn, discNavn FROM Personer WHERE navn = ?";
    $stmt = $conn->prepare($sql);
    if ($stmt === false) {
        error_log("Prepare failed: " . $conn->error);
        echo json_encode(['success' => false, 'message' => 'Prepare failed: ' . $conn->error]);
        exit();
    }
    $stmt->bind_param("s", $name);
    $stmt->execute();
    $result = $stmt->get_result();

    // Hvis navnet findes i databasen, returner det som JSON
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        error_log("Name found: " . $row['navn']);
        echo json_encode(['success' => true, 'navn' => $row['navn'], 'discNavn' => $row['discNavn']]);
    } else {
        // Hvis navnet ikke findes, returner fejlsvar
        error_log("Name not found: " . $name);
        echo json_encode(['success' => false, 'message' => 'Navn ikke fundet.']);
    }

    $stmt->close();
} else {
    // Hvis navnet ikke er sendt med i anmodningen
    error_log("Name parameter missing");
    echo json_encode(['success' => false, 'message' => 'Navn mangler!']);
}

// Luk forbindelsen
$conn->close();
?>