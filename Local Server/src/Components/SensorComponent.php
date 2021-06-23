<?php

namespace Src\Components;

use PDOException;

class SensorComponent
{

    private $db = null;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function create(array $input)
    {
        $statement = "
            INSERT INTO sensor_data
                (user_id,device_id,time,time2,weight,distance,accelerometer_array,gyroscope_array)
            VALUES
                (:user_id,:device_id,:time,:time2,:weight,:distance,:accelerometer_array,:gyroscope_array);
        ";

        $statement = $this->db->prepare($statement);
        $statement->execute(array(
            'user_id' => $input['u_id'],
            'device_id' => $input['d_id'],
            'time' => !empty($input['t']) ? $input['t'] : null,
            'time2' => !empty($input['t2']) ? $input['t2'] : null,
            'weight' => !empty($input['w']) ? $input['w'] : null,
            'distance' => !empty($input['d']) ? $input['d'] : null,
            'accelerometer_array' => !empty($input['a']) ? json_encode($input['a']) : null,
            'gyroscope_array' => !empty($input['g']) ? json_encode($input['g']) : null,
        ));
        return $statement->rowCount();
    }
}