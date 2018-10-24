<?php

error_reporting(-1);

require_once('odoo_ws.php');

class OdooManager {

private $ws;

function __construct(){
    $this->ws = new ModManager();
}

function create_task($user, $us, $description, $reviewer = FALSE){

    $user_ids = $this->ws->ws_search('res.users', array(
        array('login', '=', $user)
    ));

    if($user_ids->is_empty())
        return 'USER NOT FOUND';

    $us_ids = $this->ws->ws_search_read('project.scrum.us', array(
        array('name', 'like', $us)
    ));

    if($us_ids->is_empty())
        return 'US NOT FOUND';

    $us_id = $us_ids->fetchone();

    $task_type_ids = $this->ws->ws_search('project.task.type', array(
        array('name', '=', 'Done')
    ));

    if($task_type_ids->is_empty())
        return 'TASK TYPE NOT FOUND';

    $values = array(
        'name' => $description,
        'user_id' => $user_ids->fetchone(),
        'us_id' => $us_id['id'],
        'sprint_id' => $us_id['sprint_ids'][0],
        'project_id' => $us_id['project_id'][0],
        'stage_id' => $task_type_ids->fetchone()
    );

    if($reviewer){

        $reviewer_ids = $this->ws->ws_search('res.users', array(
            array('login', '=', $reviewer)
        ));

        if($reviewer_ids->is_empty())
            return 'REVIEWER NOT FOUND';

        $values['reviewer_id'] = $reviewer_ids->fetchone();

    }

    $this->ws->ws_create('project.task', $values);

}

}

$om = new OdooManager();

$start_pos = strpos($argv[1], "[");
$end_pos = strpos($argv[1], "]");
$overflow = 1;

$us_name = substr($argv[1], $start_pos + $overflow,  $end_pos - $start_pos - $overflow);

$result = $om->create_task('jcvazquez@gi.com', $us_name, $argv[1], 'joreynoso@gi.com');

echo $result ? $result."\n" : '';