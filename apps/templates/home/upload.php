<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $targetDirectory = "uploads/"; // Specify the folder where you want to save the uploaded files

    if (!file_exists($targetDirectory)) {
        mkdir($targetDirectory, 0777, true);
    }

    if (isset($_FILES["file"])) {
        $targetFile = $targetDirectory . basename($_FILES["file"]["name"]);
        if (move_uploaded_file($_FILES["file"]["tmp_name"], $targetFile)) {
            echo "File uploaded successfully!";
        } else {
            echo "Sorry, there was an error uploading your file.";
        }
    } else {
        echo "Please select a file to upload.";
    }
}
?>
