<?php
require "../bootstrap.php";
error_reporting(E_ALL & ~E_NOTICE);

use Src\Controller\SensorController;

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: OPTIONS,GET,POST,PUT,DELETE");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

$logger = new Monolog\Logger('automatic_gym');
$logger->pushHandler(new Monolog\Handler\StreamHandler(__DIR__ . './../var/general.log', Monolog\Logger::DEBUG));

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$uri = explode('/', $uri);

$requestMethod = $_SERVER["REQUEST_METHOD"];

$logger->debug("uri: " . $_SERVER['REQUEST_URI'] . " method:" . $_SERVER["REQUEST_METHOD"]);

if ($uri[2] !== 'sensor') {
    $controller = new SensorController($dbConnection, $requestMethod, $logger);
    $controller->processRequest();
}

header("HTTP/1.1 404 Not Found");
exit();

?>
