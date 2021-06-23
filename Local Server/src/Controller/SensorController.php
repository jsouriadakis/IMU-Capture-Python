<?php

namespace Src\Controller;

use Src\Components\SensorComponent;
use Monolog;

class SensorController
{
    private $requestMethod;
    private $sensorComponent;

    /** @var Monolog\Logger */
    private $logger;

    public function __construct($db, $requestMethod, Monolog\Logger $logger)
    {
        $this->requestMethod = $requestMethod;
        $this->sensorComponent = new SensorComponent($db);
        $this->logger = $logger;
    }

    public function processRequest()
    {
        switch ($this->requestMethod) {
            case 'GET':
                $response = $this->testGet();
                break;
            case 'POST':
                $response = $this->storeSensorDataFromRequest();
                break;
            case 'PUT':
                break;
            case 'DELETE':
                break;
            default:
                $response = $this->notFoundResponse();
                break;
        }
        header($response['status_code_header']);
        if ($response['body']) {
            echo $response['body'];
        }
    }

    private function testGet()
    {
        $response['status_code_header'] = 'HTTP/1.1 201 Created';
        $response['body'] = "okay";
        return $response;
    }

    private function storeSensorDataFromRequest()
    {
        $input = (array)json_decode(file_get_contents('php://input'), true);
        // file_put_contents('input.txt',file_get_contents('php://input'));
        if (!$this->validateData($input)) {
            $this->logger->error("Invalid input data");
            $this->logger->error($input);
            return $this->unprocessableEntityResponse();
        }
        $this->logger->debug(print_r($input, true));
        try {
            $this->sensorComponent->create($input);
            $this->logger->debug("Successfully inserted into DB!");
            $response['status_code_header'] = 'HTTP/1.1 201 Created';
            $response['body'] = null;
        } catch (\Exception $e) {
            $this->logger->error($e->getMessage() . PHP_EOL . $e->getTraceAsString());
            $response['status_code_header'] = 'HTTP/1.1 500 Internal Server Error';
            $response['body'] = null;
        }

        return $response;
    }

    private function validateData($input)
    {
        //TODO create Validation rules
        if (!isset($input['u_id'])) {
            return false;
        }
        if (!isset($input['d_id'])) {
            return false;
        }
        if (!isset($input['t'])) {
            return false;
        }
        if (!isset($input['w'])) {
            return false;
        }
        if (!isset($input['d'])) {
            return false;
        }
        if (!isset($input['a'])) {
            return false;
        }
        if (!isset($input['g'])) {
            return false;
        }
        return true;
    }
//
//    private function getUser($id)
//    {
//        $result = $this->personGateway->find($id);
//        if (!$result) {
//            return $this->notFoundResponse();
//        }
//        $response['status_code_header'] = 'HTTP/1.1 200 OK';
//        $response['body'] = json_encode($result);
//        return $response;
//    }
//
//    private function updateUserFromRequest($id)
//    {
//        $result = $this->personGateway->find($id);
//        if (!$result) {
//            return $this->notFoundResponse();
//        }
//        $input = (array)json_decode(file_get_contents('php://input'), true);
//        if (!$this->validatePerson($input)) {
//            return $this->unprocessableEntityResponse();
//        }
//        $this->personGateway->update($id, $input);
//        $response['status_code_header'] = 'HTTP/1.1 200 OK';
//        $response['body'] = null;
//        return $response;
//    }
//
//    private function deleteUser($id)
//    {
//        $result = $this->personGateway->find($id);
//        if (!$result) {
//            return $this->notFoundResponse();
//        }
//        $this->personGateway->delete($id);
//        $response['status_code_header'] = 'HTTP/1.1 200 OK';
//        $response['body'] = null;
//        return $response;
//    }


    private function unprocessableEntityResponse()
    {
        $response['status_code_header'] = 'HTTP/1.1 422 Unprocessable Entity';
        $response['body'] = json_encode([
            'error' => 'Invalid input'
        ]);
        return $response;
    }

    private function notFoundResponse()
    {
        $response['status_code_header'] = 'HTTP/1.1 404 Not Found';
        $response['body'] = null;
        return $response;
    }
}
