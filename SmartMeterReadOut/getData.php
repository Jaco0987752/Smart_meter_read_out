<?php
setlocale(LC_TIME, 'NL_nl');

$timestamps = array();
$tariffs = array();

// Special function to parse a parameter savely.
function getParameter(string $str)
{
    if (isset($_GET[$str]) && $_GET[$str] != null) {
        return htmlspecialchars_decode($_GET[$str], ENT_QUOTES);
    }
    return null;
}

// Connect to the sql database.
$pdo = new PDO('mysql:host=localhost;dbname=dataBaseName', 'user', 'password', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ,
    PDO::ATTR_EMULATE_PREPARES => false
]);

// Get the mode(day/month)
$mode = getParameter('mode');
// If the mode in month, get the data from de month
if ($mode == "month") {
    $date = date_create();
    // The timeoffset enables us to walk forwards and backwards, strarting from this month.  
    $TimeOffset = (int)getParameter("TimeOffset");
    if ($TimeOffset) {
        date_add($date, date_interval_create_from_date_string((string)$TimeOffset . " month"));
    }

    $MonthToShow = date_format($date, "F Y");
    // The start of the month.
    $startOfMonth = date_format($date, "Y-m-0");
    // Calculate the end of the month.
    date_add($date, date_interval_create_from_date_string("1 month"));
    $stopOfMonth = date_format($date, "Y-m-0");

    // Fetch the information from the database.
    $query = $pdo->query("SELECT * FROM `energyDayTable` where timestamp BETWEEN '" . $startOfMonth . " 00:00:00' and '" . $stopOfMonth . " 23:59:59'");
    $list = $query->fetchAll();
    $previous = null;

    // Loop through all the items.
    foreach ($list as $item) {
        $energy = $item->deliveredToClientHigh + $item->deliveredToClientLow -($item->deliveredByClientHigh + $item->deliveredByClientLow);
        $timestamp = new DateTime($item->timestamp);
        $timestamp->sub(new DateInterval("P1D"));
        $item->timestamp = $timestamp->format('Y-m-d');

        // If a previous variable exists, then subtrack the previous from the current.
        if ($previous!=null) {
            $energyUsage = $energy - $previous;
            array_push($timestamps, $item->timestamp);
            array_push($tariffs, $energyUsage);
        }
        if ($energy > 0) {
            $previous = $energy;
        }
    }
    // Make an object and put the information in it.
    $objectToSend = new stdClass();
    $objectToSend->title = "energieverbruik " . $MonthToShow ;
    $objectToSend->labels = $timestamps;
    $objectToSend->data = $tariffs;

} else {
    // Determine the day.
    $day = (int)getParameter('TimeOffset');
    if ($day) {
        $date = date_create();
        date_add($date, date_interval_create_from_date_string((string)$day . " day"));
        $dayToShow = date_format($date, 'Y-m-d');
    } else {
        $dayToShow = date('Y-m-d');
    }

    // Fetch the information from the database.
    $query = $pdo->query("SELECT * FROM `energyTariffTable` where timestamp BETWEEN '" . $dayToShow . " 00:00:00' and '" . $dayToShow . " 23:59:59'");
    $list = $query->fetchAll();

    // Loop through the list.
    foreach ($list as $item) {
        $time = new DateTime($item->timestamp);
        $item->timestamp = $time->format("H-i");
        array_push($timestamps, $item->timestamp);
        array_push($tariffs, $item->tariff);
    }
    $objectToSend = new stdClass();
    $objectToSend->title = "energieverbruik " . (string)$dayToShow;
    $objectToSend->labels = $timestamps;
    $objectToSend->data = $tariffs;
}

// Convert all php objects to json.
echo json_encode($objectToSend);