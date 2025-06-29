<?php

namespace App\Models\clients;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class Booking extends Model
{
    use HasFactory;

    protected $table = 'tbl_booking';

    public function createBooking($data)
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

    public function cancelBooking($bookingId){
        return DB::table($this->table)
        ->where('bookingId', $bookingId)
        ->update([
            'bookingStatus' => 'c',
            'updated_at' => now()
        ]);
    }


    public function checkBooking($tourId, $userId)
    {
        return DB::table($this->table)
        ->where('tourId', $tourId)
        ->where('userId', $userId)
        ->where('bookingStatus', 'f')
        ->exists(); // Trả về true nếu bản ghi tồn tại, false nếu không tồn tại
    }
}
