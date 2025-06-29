<?php

namespace App\Models\clients;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class Checkout extends Model
{
    use HasFactory;

    protected $table = 'tbl_checkout';

    public function createCheckout($data)
    {
        // Thêm timestamps nếu chưa có
        if (!isset($data['created_at'])) {
            $data['created_at'] = now();
        }
        if (!isset($data['updated_at'])) {
            $data['updated_at'] = now();
        }
        
        // Chèn dữ liệu và trả về ID của bản ghi vừa tạo
        return DB::table($this->table)->insertGetId($data);
    }
}
