<?php

namespace App\Models\admin;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class AdminModel extends Model
{
    use HasFactory;

    protected $table = 'tbl_admin';

    public function getAdmin($username = null){
        if ($username) {
            return DB::table($this->table)->where('username', $username)->first();
        }
        return DB::table($this->table)->first();
    }

    public function updateAdmin($username, $data){
        return DB::table($this->table)
        ->where('username', $username)
        ->update($data);
    }
}
