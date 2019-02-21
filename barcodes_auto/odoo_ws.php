<?php

error_reporting(-1);

require_once('ripcord/ripcord.php');

class Results {

private $results;

function __construct($results = array()){
    $this->results = $results;
}

function fetchone(){
    return isset($this->results[0]) ? $this->results[0] : FALSE;
}

function fetchall(){
    return $this->results;
}

function is_empty(){
    return count($this->results) > 0 ? FALSE : TRUE;
}

}

class ModManager {

private $logger;
private $cm;

private $ws_url  = 'http://erp.gi:8062';
private $ws_db   = 'odoo8_P8062';
private $ws_user = 'jcvazquez@gi.com';
private $ws_pass = 'Smoogzor123';

private $common;
private $models;
private $uid;

function __construct(){

    $this->init();

}

private function init(){

    $this->common = ripcord::client("$this->ws_url/xmlrpc/2/common");
    $this->models = ripcord::client("$this->ws_url/xmlrpc/2/object");

    $this->uid = $this->common->authenticate($this->ws_db, $this->ws_user, $this->ws_pass, array());

}

function ws_create($model, $values){

    $result = $this->models->execute_kw($this->ws_db, $this->uid, $this->ws_pass,
    $model, 'create',
        array(
            $values
        )
    );

    if(is_array($result))
        echo $result['faultString'];

    return $result;

}

function ws_update($model, $id, $values){

    $result = $this->models->execute_kw($this->ws_db, $this->uid, $this->ws_pass,
    $model, 'write',
        array(
            array($id),
            $values
        )
    );

    if(is_array($result))
        echo $result['faultString'];

    return $result;

}

function ws_search($model, $domain = array(), $limits = array()){

    $ids = $this->models->execute_kw($this->ws_db, $this->uid, $this->ws_pass,
        $model, 'search',
        array(
            $domain
        ),
        $limits
    );

    return new Results($ids);

}

function ws_search_read($model, $domain, $limits = array()){

    $ids = $this->models->execute_kw($this->ws_db, $this->uid, $this->ws_pass,
        $model, 'search_read',
        array(
            $domain
        ),
        $limits
    );

    return new Results($ids);

}

function ws_unlink($model, $unlink_ids = array()){

    $ids = $this->models->execute_kw($this->ws_db, $this->uid, $this->ws_pass,
        $model, 'unlink',
        array(
            $unlink_ids
        )
    );

    return $ids;

}

}