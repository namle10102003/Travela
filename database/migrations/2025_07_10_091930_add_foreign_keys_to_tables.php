<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // Add foreign key: tbl_booking.userId -> tbl_users.userId
        Schema::table('tbl_booking', function (Blueprint $table) {
            $table->foreign('userId')->references('userId')->on('tbl_users')->onDelete('cascade');
        });

        // Add foreign key: tbl_images.tourId -> tbl_tours.tourId  
        Schema::table('tbl_images', function (Blueprint $table) {
            $table->foreign('tourId')->references('tourId')->on('tbl_tours')->onDelete('cascade');
        });

        // Add foreign key: tbl_timeline.tourId -> tbl_tours.tourId
        Schema::table('tbl_timeline', function (Blueprint $table) {
            $table->foreign('tourId')->references('tourId')->on('tbl_tours')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        // Drop foreign keys in reverse order
        Schema::table('tbl_timeline', function (Blueprint $table) {
            $table->dropForeign(['tourId']);
        });

        Schema::table('tbl_images', function (Blueprint $table) {
            $table->dropForeign(['tourId']);
        });

        Schema::table('tbl_booking', function (Blueprint $table) {
            $table->dropForeign(['userId']);
        });
    }
};
